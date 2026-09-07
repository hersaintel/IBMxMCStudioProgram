from typing import Dict, Any, List
from backend.services.watsonx import watsonx_service

CBN_FX_YTD_LIMIT_USD = 200000.00  # CBN regulatory limit

def calculate_fx_vulnerability_score(entity: Dict[str, Any], forecast_spread_30d: float) -> float:
    """
    Calculates the FX Vulnerability Score (0-100).
    Considers:
      - currency_exposure_ratio (0.0 to 1.0)
      - predicted 30-day spread percentage
      - import category penalties
    """
    exposure_meta = entity.get("exposure_metadata", {})
    comp_meta = entity.get("compliance_metadata", {})
    
    exposure_ratio = exposure_meta.get("currency_exposure_ratio", 0.5)
    import_tags = comp_meta.get("import_category_tags", [])
    
    # Base is exposure percentage
    score = exposure_ratio * 60
    
    # Impact of spread forecast
    score += forecast_spread_30d * 1.5
    
    # Import tag adjustments
    for tag in import_tags:
        if "RESTRICTED" in tag or "ELECTRONICS" in tag:
            score += 15
        elif "AGRIC" in tag:
            score -= 10
            
    return max(0.0, min(100.0, round(score, 1)))

def calculate_aml_compliance_score(entity: Dict[str, Any]) -> float:
    """
    Calculates the AML & Compliance Risk Score (0-100).
    Considers:
      - YTD allocations vs CBN regulatory limit ($200k)
      - Number of consolidated linked wallets (smurfing check)
      - Absence of valid Form M
    """
    comp_meta = entity.get("compliance_metadata", {})
    consolidated = entity.get("consolidated_attributes", {})
    
    ytd_allocated = comp_meta.get("total_fx_allocated_ytd_usd", 0.0)
    linked_wallets_count = len(consolidated.get("linked_wallets", []))
    has_form_m = comp_meta.get("has_valid_form_m", True)
    
    # Base: YTD limit utilization (max 60 points)
    limit_utilization = (ytd_allocated / CBN_FX_YTD_LIMIT_USD) * 60
    score = limit_utilization
    
    # Smurfing penalty (multiple wallets indicate layering attempts)
    if linked_wallets_count >= 3:
        score += 20
    elif linked_wallets_count == 2:
        score += 10
        
    # Form M penalty (import documentation)
    if not has_form_m:
        score += 25
        
    return max(0.0, min(100.0, round(score, 1)))

async def generate_entity_risk_profile(entity: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merges Match 360 entity data with Watsonx analysis to output the complete
    FX Vulnerability and Compliance Risk Profile.
    """
    entity_id = entity.get("entity_id", "ent_generic")
    
    # Fetch latest forecast details
    forecast = await watsonx_service.get_fx_forecast()
    spread_30d = forecast["predictions"]["30_day_spread_pct"]
    
    # Calculate scores
    fx_score = calculate_fx_vulnerability_score(entity, spread_30d)
    aml_score = calculate_aml_compliance_score(entity)
    
    # Query Watsonx for specific entity explanation
    prompt = (
        f"You are a regulatory auditor. Explain why entity {entity.get('consolidated_attributes', {}).get('primary_name')} "
        f"with YTD FX Allocation of ${entity.get('compliance_metadata', {}).get('total_fx_allocated_ytd_usd')} "
        f"and {len(entity.get('consolidated_attributes', {}).get('linked_wallets', []))} linked wallets has "
        f"an FX Vulnerability score of {fx_score}% and an AML score of {aml_score}%."
    )
    explanation = await watsonx_service.generate_text(prompt, max_tokens=150)
    
    # Compile vulnerability factors
    factors = []
    exposure = entity.get("exposure_metadata", {}).get("currency_exposure_ratio", 0.5)
    if exposure > 0.7:
        factors.append(f"High Naira exposure ratio ({int(exposure * 100)}% of assets in NGN)")
    if spread_30d > 15:
        factors.append(f"Widening NGN/USD parallel market spread (30-day forecast: {spread_30d}%)")
    
    tags = entity.get("compliance_metadata", {}).get("import_category_tags", [])
    for tag in tags:
        if "RESTRICTED" in tag:
            factors.append(f"Category '{tag}' is subject to central bank FX purchase bans")
            
    # Compile AML flags
    flags = []
    ytd = entity.get("compliance_metadata", {}).get("total_fx_allocated_ytd_usd", 0.0)
    if ytd > CBN_FX_YTD_LIMIT_USD:
        flags.append(f"YTD Allocations (${ytd:,.2f}) exceed CBN regulatory cap (${CBN_FX_YTD_LIMIT_USD:,.2f})")
    if len(entity.get("consolidated_attributes", {}).get("linked_wallets", [])) >= 3:
        flags.append("Multi-wallet integration (3+ links): High risk of Smurfing patterns")
    if not entity.get("compliance_metadata", {}).get("has_valid_form_m", True):
        flags.append("Missing valid CBN Form M documentation")

    return {
        "entity_id": entity_id,
        "name": entity.get("consolidated_attributes", {}).get("primary_name"),
        "fx_vulnerability_score": fx_score,
        "aml_compliance_score": aml_score,
        "vulnerability_factors": factors if factors else ["No major vulnerability factors"],
        "aml_flags": flags if flags else ["No compliance flags raised"],
        "granite_explanation": explanation
    }
