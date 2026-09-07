from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import logging
from typing import List, Any, Dict

from backend.services.mdm_adapter import MDMAdapter
from backend.services.world_bank import get_nigeria_inflation
from backend.intelligence.fraud import score_transactions
from backend.ingest import run_ingestion
from backend.services.treasury_manager import TreasuryManager
from backend.services.crypto_oracle import calculate_quote, get_exchange_rates
from backend.services.match360 import match360_service
from backend.services.watsonx import watsonx_service
from backend.services.risk import generate_entity_risk_profile, CBN_FX_YTD_LIMIT_USD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Community Economic Intelligence Engine (CEIE) API",
    description="Nigeria-focused economic intelligence platform integrating Match 360 and Watsonx.ai",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mdm = MDMAdapter()
treasury = TreasuryManager()

# --- Pydantic Models ---

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

class SwapRequest(BaseModel):
    cooperative: str
    amount_ngn: float
    target_token: str = "USDT"
    initiator: str = "Treasurer"

class ApprovalRequest(BaseModel):
    proposal_id: str
    approver: str


# ============================================================
#  SECTION 1: Original CEIE Cooperative Intelligence Endpoints
# ============================================================

@app.get("/")
def read_root():
    return {
        "status": "online",
        "engine": "Community Economic Intelligence Engine (CEIE)",
        "docs_url": "/docs"
    }

@app.post("/ingest")
def ingest_data():
    """Generates synthetic data and runs MDM ingest"""
    try:
        counts = run_ingestion()
        members_df = pd.read_csv("data/members_dirty.csv")
        mdm_result = mdm.ingest_members(members_df)
        return {
            "status": "success",
            "counts": counts,
            "mdm_mode": mdm_result["mode"]
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/golden-records")
def get_golden_records():
    """Return golden records from MDM"""
    return mdm.get_golden_records()

@app.get("/stats")
def get_stats():
    """Return overall stats"""
    raw_count = 0
    txn_count = 0
    if os.path.exists("data/members_dirty.csv"):
        raw_count = len(pd.read_csv("data/members_dirty.csv"))
    if os.path.exists("data/transactions.csv"):
        txn_count = len(pd.read_csv("data/transactions.csv"))
    golden_records = mdm.get_golden_records()
    golden_count = len(golden_records)
    merged = raw_count - golden_count if golden_count > 0 else 0
    return {
        "raw_count": raw_count,
        "golden_count": golden_count,
        "merged": merged,
        "txn_count": txn_count
    }

@app.get("/fraud/alerts")
def get_fraud_alerts():
    """Return fraud alerts sorted by severity"""
    if not os.path.exists("data/transactions.csv"):
        return []
    txns_df = pd.read_csv("data/transactions.csv")
    members_df = pd.read_csv("data/members_dirty.csv") if os.path.exists("data/members_dirty.csv") else None
    flagged_members = set()
    golden_records = mdm.get_golden_records()
    for g in golden_records:
        if len(g.get('source_records', [])) > 1:
            for r in g.get('source_records', []):
                flagged_members.add(r['member_id'])
    alerts = score_transactions(txns_df, members_df, flagged_members)
    return alerts

@app.get("/macro")
def get_macro():
    """Return World Bank inflation data"""
    return get_nigeria_inflation()

@app.post("/query", response_model=QueryResponse)
def query_intent(request: QueryRequest):
    """Simple intent parsing for NLP query endpoint"""
    q = request.question.lower()

    if "fraud" in q or "alert" in q:
        alerts = get_fraud_alerts()
        high_alerts = sum(1 for a in alerts if a['severity'] == 'high')
        return QueryResponse(answer=f"There are currently {len(alerts)} total fraud alerts, with {high_alerts} critical (high severity) ones. Please check the Fraud Alerts tab for details.")

    elif "inflation" in q or "macro" in q:
        data = get_nigeria_inflation()
        try:
            latest = [item for item in data[1] if item.get('value') is not None][0]
            val = round(latest['value'], 2)
            year = latest['date']
            return QueryResponse(answer=f"The latest recorded inflation for Nigeria is {val}% (Year {year}), according to World Bank data.")
        except Exception:
            return QueryResponse(answer="I could not retrieve the exact latest inflation number, please check the Macro tab.")

    elif "member" in q or "raw" in q:
        stats = get_stats()
        return QueryResponse(answer=f"We have {stats['raw_count']} raw member records in the system.")

    elif "duplicate" in q or "match" in q or "mdm" in q:
        stats = get_stats()
        return QueryResponse(answer=f"The MDM process merged {stats['merged']} duplicate records, resulting in {stats['golden_count']} golden records.")

    elif "treasury" in q or "stablecoin" in q or "usdt" in q or "usdc" in q or "hedge" in q or "swap" in q:
        summary = treasury.get_portfolio_summary()
        return QueryResponse(answer=f"SACCO Treasury holds ${summary['stablecoin_reserves_usd']:,.2f} in USD stablecoins across cooperatives, safeguarding ₦{summary['annual_purchasing_power_saved_ngn']:,.2f} in member purchasing power against Nigeria's {summary['current_inflation_rate']}% inflation.")

    else:
        return QueryResponse(answer="I am the CEIE AI assistant. Ask about fraud alerts, inflation, members, entity resolution, stablecoin treasury, or FX vulnerability.")


# ============================================================
#  SECTION 2: Treasury & Stablecoin Hedging Endpoints
# ============================================================

@app.get("/treasury/summary")
def get_treasury_summary():
    """Return SACCO fiat vs. stablecoin reserves and inflation hedge metrics"""
    return treasury.get_portfolio_summary()

@app.get("/treasury/quote")
def get_treasury_quote(amount_ngn: float = 500000.0, target_token: str = "USDT"):
    """Calculate conversion quote and fee breakdown"""
    return calculate_quote(amount_ngn, target_token)

@app.post("/treasury/swap")
def initiate_swap(request: SwapRequest):
    """Initiate NGN to stablecoin conversion (triggers multi-sig if >= ₦1M)"""
    try:
        result = treasury.initiate_swap(
            cooperative=request.cooperative,
            amount_ngn=request.amount_ngn,
            target_token=request.target_token,
            initiator=request.initiator
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/treasury/approve")
def approve_swap(request: ApprovalRequest):
    """Approve a pending multi-sig treasury swap proposal"""
    try:
        result = treasury.approve_and_execute_swap(
            proposal_id=request.proposal_id,
            approver=request.approver
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/treasury/pending")
def get_pending_proposals(cooperative: str = None):
    """Get pending multi-sig proposals awaiting officer signature"""
    return treasury.governance.get_pending(cooperative)

@app.get("/treasury/history")
def get_treasury_history():
    """Get full ledger audit trail of on-chain / on-ramp swaps"""
    return treasury.get_ledger_history()


# ============================================================
#  SECTION 3: Ajo- IBM Match 360 / Watsonx / Risk / FX Endpoints
# ============================================================

@app.post("/api/records", status_code=201)
async def ingest_record(record: Dict[str, Any]):
    """Ingests a new raw wallet/bank record into Match 360"""
    try:
        res = await match360_service.post_record(record)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/entities", response_model=List[Dict[str, Any]])
async def get_all_entities():
    """Retrieve all golden entity records resolved by Match 360"""
    return await match360_service.list_all_entities()

@app.get("/api/entities/{entity_id}")
async def get_entity_profile(entity_id: str):
    """Retrieve a single golden record profile from Match 360"""
    try:
        entity = await match360_service.get_entity(entity_id)
        return entity
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found: {str(e)}")

@app.get("/api/fx-forecast")
async def get_fx_forecast():
    """Get NGN/USD parallel market spread projections from Watsonx.ai Granite Model"""
    try:
        forecast = await watsonx_service.get_fx_forecast()
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk-assessment/{entity_id}")
async def get_entity_risk_assessment(entity_id: str):
    """Retrieves full FX Vulnerability and AML compliance risk scoring for an entity"""
    try:
        entity = await match360_service.get_entity(entity_id)
        risk_profile = await generate_entity_risk_profile(entity)
        return risk_profile
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts/compliance")
async def get_regulator_compliance_alerts():
    """Exposes alerts on systemic AML and FX breaches for regulators"""
    try:
        entities = await match360_service.list_all_entities()
        alerts = []
        for ent in entities:
            profile = await generate_entity_risk_profile(ent)
            ytd = ent.get("compliance_metadata", {}).get("total_fx_allocated_ytd_usd", 0.0)
            if profile["aml_compliance_score"] >= 50 or ytd >= CBN_FX_YTD_LIMIT_USD:
                alerts.append({
                    "entity_id": ent["entity_id"],
                    "name": profile["name"],
                    "cac_number": ent["consolidated_attributes"].get("cac_number"),
                    "bvn": ent["consolidated_attributes"].get("bvn"),
                    "aml_risk_score": profile["aml_compliance_score"],
                    "cbn_tier": ent["compliance_metadata"].get("cbn_compliance_tier"),
                    "total_fx_allocated_ytd": ytd,
                    "flags": profile["aml_flags"],
                    "explanation": profile["granite_explanation"]
                })
        return {
            "total_breaches": len(alerts),
            "cbn_ytd_limit_usd": CBN_FX_YTD_LIMIT_USD,
            "violations": alerts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/alerts/cooperative/{coop_id}")
async def get_cooperative_alerts(coop_id: str):
    """Exposes localized inflation, default risk warning, and hedging alerts for cooperatives"""
    try:
        lga_inflation = [
            {"lga": "Kano Municipal", "state": "Kano", "cpi_increase_pct": 34.2, "status": "Critical"},
            {"lga": "Alimosho", "state": "Lagos", "cpi_increase_pct": 28.5, "status": "High"},
            {"lga": "Kaduna North", "state": "Kaduna", "cpi_increase_pct": 31.8, "status": "Critical"},
            {"lga": "Ibadan North", "state": "Oyo", "cpi_increase_pct": 22.4, "status": "Moderate"}
        ]
        entities = await match360_service.list_all_entities()
        hedging_alerts = []
        default_warnings = []
        for ent in entities:
            profile = await generate_entity_risk_profile(ent)
            fx_vulnerability = profile["fx_vulnerability_score"]
            if fx_vulnerability >= 60:
                hedging_alerts.append({
                    "entity_id": ent["entity_id"],
                    "name": profile["name"],
                    "vulnerability_score": fx_vulnerability,
                    "exposure_ratio": ent["exposure_metadata"].get("currency_exposure_ratio"),
                    "recommendation": f"Convert NGN {ent['exposure_metadata'].get('naira_holdings_ngn'):,.2f} reserves to stable USD assets immediately."
                })
            if fx_vulnerability >= 75 and not ent["compliance_metadata"].get("has_valid_form_m", True):
                default_warnings.append({
                    "entity_id": ent["entity_id"],
                    "name": profile["name"],
                    "factors": profile["vulnerability_factors"],
                    "risk_warning": "High risk of default on dollar-denominated supply chain payments."
                })
        forecast = await watsonx_service.get_fx_forecast()
        return {
            "coop_id": coop_id,
            "forecast_spreads": forecast["predictions"],
            "market_analysis": forecast["granite_analysis"],
            "micro_inflation_lga": lga_inflation,
            "hedging_alerts": hedging_alerts,
            "loan_default_warnings": default_warnings
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fx/rates")
def get_fx_rates():
    """Returns official NAFEM rates and parallel market (BDC, P2P) rates"""
    return {
        "nafem_official": 1600.00,
        "parallel_bdc": 1795.00,
        "p2p_crypto_usdt": 1780.00,
        "neobank_remit": 1750.00
    }

@app.get("/api/fx/calculator")
def run_fx_calculator(amount_usd: float = 10000.00, entity_id: str = "ent_sme_00921"):
    """Simulates conversion of a USD amount across different rails"""
    rates = {
        "nafem_official": 1600.00,
        "parallel_bdc": 1795.00,
        "p2p_crypto_usdt": 1780.00,
        "neobank_remit": 1750.00
    }
    dom_return = amount_usd * rates["nafem_official"]
    neo_return = amount_usd * rates["neobank_remit"]
    p2p_return = amount_usd * rates["p2p_crypto_usdt"]
    bdc_return = amount_usd * rates["parallel_bdc"]
    max_return = bdc_return
    return {
        "usd_amount": amount_usd,
        "entity_id": entity_id,
        "channels": [
            {
                "channel_name": "Official Domiciliary Account (NAFEM)",
                "rate": rates["nafem_official"],
                "total_returned_ngn": dom_return,
                "friction_index": "High (3-5 business days processing)",
                "compliance_rating": "Green",
                "exchange_loss_ngn": max_return - dom_return,
                "arbitrage_savings_ngn": 0.0,
            },
            {
                "channel_name": "Inward Remittance Neobanks (Grey/Geegpay)",
                "rate": rates["neobank_remit"],
                "total_returned_ngn": neo_return,
                "friction_index": "Medium (1-2 hours delay)",
                "compliance_rating": "Yellow",
                "exchange_loss_ngn": max_return - neo_return,
                "arbitrage_savings_ngn": neo_return - dom_return,
            },
            {
                "channel_name": "P2P Crypto Stablecoins (USDT/USDC)",
                "rate": rates["p2p_crypto_usdt"],
                "total_returned_ngn": p2p_return,
                "friction_index": "Low (10-15 minutes, 24/7)",
                "compliance_rating": "Red",
                "exchange_loss_ngn": max_return - p2p_return,
                "arbitrage_savings_ngn": p2p_return - dom_return,
            },
            {
                "channel_name": "Street BDCs (Cash Abokis)",
                "rate": rates["parallel_bdc"],
                "total_returned_ngn": bdc_return,
                "friction_index": "Low-Medium (cash handling)",
                "compliance_rating": "Yellow",
                "exchange_loss_ngn": 0.0,
                "arbitrage_savings_ngn": bdc_return - dom_return,
            }
        ]
    }

@app.get("/api/watsonx/spread-forecast")
async def get_watsonx_spread_forecast():
    """Gets Watsonx Granite Time Series spread prediction analysis"""
    try:
        res = await watsonx_service.get_spread_forecast()
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/entities/{entity_id}/fx-profile")
async def get_entity_fx_profile(entity_id: str):
    """Retrieve Match 360 resolved shadow FX profile for an entity"""
    try:
        entity = await match360_service.get_entity(entity_id)
        if "fx_profile" in entity:
            return {
                "entity_id": entity_id,
                "name": entity["consolidated_attributes"]["primary_name"],
                "fx_profile": entity["fx_profile"]
            }
        raise HTTPException(status_code=404, detail="FX Profile not found on entity")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
