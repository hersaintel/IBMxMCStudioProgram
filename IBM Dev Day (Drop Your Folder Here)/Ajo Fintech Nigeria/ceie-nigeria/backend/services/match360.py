import httpx
import logging
from typing import Dict, Any, List
from backend.config import settings

logger = logging.getLogger(__name__)

# Prepopulated mock database for demonstration and verification when USE_MOCK_SERVICES is True
MOCK_GOLDEN_ENTITIES: Dict[str, Dict[str, Any]] = {
    "ent_sme_00921": {
        "entity_id": "ent_sme_00921",
        "consolidated_attributes": {
            "bvn": "22289104722",
            "cac_number": "RC1827364",
            "pos_merchant_ids": ["MP_MID_98213", "OP_MID_8812"],
            "primary_name": "Oluwaseun Adeyemi",
            "alternate_names": ["Seun Ade", "O. Adeyemi"],
            "linked_wallets": [
                {"source": "OPay_POS", "wallet_id": "op_wallet_338"},
                {"source": "Moniepoint", "wallet_id": "mp_wallet_982"},
                {"source": "GTBank", "account_id": "gtb_019283746"}
            ]
        },
        "compliance_metadata": {
            "total_fx_allocated_ytd_usd": 185000.00,
            "cbn_compliance_tier": "Yellow",
            "import_category_tags": ["AGRIC_FERTILIZER", "RESTRICTED_STEEL_IMPORTS"],
            "has_valid_form_m": True
        },
        "exposure_metadata": {
            "currency_exposure_ratio": 0.78,
            "naira_holdings_ngn": 45000000.00,
            "fx_holdings_usd": 15000.00,
            "deposit_drop_ratio": 0.38
        },
        "fx_profile": {
            "primary_conversion_method": "P2P_Crypto",
            "secondary_conversion_method": "BDC_Aboki",
            "estimated_cost_of_capital_markup_pct": 11.2,
            "stablecoin_velocity_usd_per_mo": 12000.00,
            "source_liquidity_reliance": {
                "crypto_p2p_weight": 0.70,
                "bdc_cash_weight": 0.20,
                "official_nafem_weight": 0.10
            }
        }
    },
    "ent_sme_00922": {
        "entity_id": "ent_sme_00922",
        "consolidated_attributes": {
            "bvn": "22299884433",
            "cac_number": "RC9837462",
            "pos_merchant_ids": ["OP_MID_55104"],
            "primary_name": "Chidi Nwachukwu",
            "alternate_names": ["C. Nwachukwu", "Chidi Nwac"],
            "linked_wallets": [
                {"source": "OPay_POS", "wallet_id": "op_wallet_551"},
                {"source": "GTBank", "account_id": "gtb_022831029"}
            ]
        },
        "compliance_metadata": {
            "total_fx_allocated_ytd_usd": 245000.00,
            "cbn_compliance_tier": "Red",
            "import_category_tags": ["ELECTRONICS_IMPORT"],
            "has_valid_form_m": False
        },
        "exposure_metadata": {
            "currency_exposure_ratio": 0.95,
            "naira_holdings_ngn": 82000000.00,
            "fx_holdings_usd": 4000.00,
            "deposit_drop_ratio": 0.55
        },
        "fx_profile": {
            "primary_conversion_method": "BDC_Aboki",
            "secondary_conversion_method": "P2P_Crypto",
            "estimated_cost_of_capital_markup_pct": 12.1,
            "stablecoin_velocity_usd_per_mo": 24000.00,
            "source_liquidity_reliance": {
                "crypto_p2p_weight": 0.30,
                "bdc_cash_weight": 0.65,
                "official_nafem_weight": 0.05
            }
        }
    },
    "ent_sme_00923": {
        "entity_id": "ent_sme_00923",
        "consolidated_attributes": {
            "bvn": "22211223344",
            "cac_number": "RC4738291",
            "pos_merchant_ids": [],
            "primary_name": "Amina Bello",
            "alternate_names": ["A. Bello"],
            "linked_wallets": [
                {"source": "Moniepoint", "wallet_id": "mp_wallet_104"},
                {"source": "AccessBank", "account_id": "acc_002837465"}
            ]
        },
        "compliance_metadata": {
            "total_fx_allocated_ytd_usd": 45000.00,
            "cbn_compliance_tier": "Green",
            "import_category_tags": ["AGRIC_GRAINS"],
            "has_valid_form_m": True
        },
        "exposure_metadata": {
            "currency_exposure_ratio": 0.35,
            "naira_holdings_ngn": 12000000.00,
            "fx_holdings_usd": 25000.00,
            "deposit_drop_ratio": 0.08
        },
        "fx_profile": {
            "primary_conversion_method": "Domiciliary_Bank",
            "secondary_conversion_method": "Neobank_Virtual",
            "estimated_cost_of_capital_markup_pct": 1.5,
            "stablecoin_velocity_usd_per_mo": 1500.00,
            "source_liquidity_reliance": {
                "crypto_p2p_weight": 0.10,
                "bdc_cash_weight": 0.10,
                "official_nafem_weight": 0.80
            }
        }
    }
}

class Match360Service:
    def __init__(self):
        self.use_mock = settings.USE_MOCK_SERVICES
        self.api_key = settings.IBM_CLOUD_API_KEY
        self.crn = settings.MATCH360_CRN
        self.route = settings.MATCH360_ROUTE.rstrip('/')

    async def get_iam_token(self) -> str:
        if self.use_mock:
            return "mock_iam_token_match360"
        
        async with httpx.AsyncClient() as client:
            url = "https://iam.cloud.ibm.com/identity/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                "apikey": self.api_key
            }
            try:
                response = await client.post(url, headers=headers, data=data)
                response.raise_for_status()
                return response.json().get("access_token", "")
            except Exception as e:
                logger.error(f"Error fetching IAM token: {e}")
                raise e

    async def post_record(self, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ingests a member record into Match 360"""
        if self.use_mock:
            # Add or update mock data
            record_id = record_data.get("record_id", "rec_temp")
            bvn = record_data.get("attributes", {}).get("bvn", "00000000000")
            name = record_data.get("attributes", {}).get("name", "Unknown Name")
            
            # Simple simulation of updating/creating a golden entity
            entity_id = f"ent_sme_{bvn[-5:]}" if len(bvn) >= 5 else "ent_sme_generic"
            
            if entity_id not in MOCK_GOLDEN_ENTITIES:
                MOCK_GOLDEN_ENTITIES[entity_id] = {
                    "entity_id": entity_id,
                    "consolidated_attributes": {
                        "bvn": bvn,
                        "cac_number": record_data.get("attributes", {}).get("cac_number", "Unregistered"),
                        "primary_name": name,
                        "alternate_names": [name],
                        "linked_wallets": [{"source": record_data.get("record_source", "Unknown"), "wallet_id": record_id}]
                    },
                    "compliance_metadata": {
                        "total_fx_allocated_ytd_usd": 10000.0,
                        "cbn_compliance_tier": "Green",
                        "import_category_tags": ["GENERAL_COMMERCE"],
                        "has_valid_form_m": True
                    },
                    "exposure_metadata": {
                        "currency_exposure_ratio": 0.5,
                        "naira_holdings_ngn": 5000000.0,
                        "fx_holdings_usd": 5000.0
                    }
                }
            return {"status": "success", "record_id": record_id, "resolved_entity_id": entity_id}

        # Real API Ingestion
        token = await self.get_iam_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "crn": self.crn
        }
        url = f"{self.route}/mdm-data/v1/records"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=record_data)
            response.raise_for_status()
            return response.json()

    async def get_entity(self, entity_id: str) -> Dict[str, Any]:
        """Retrieves a consolidated golden record of an entity"""
        if self.use_mock:
            entity = MOCK_GOLDEN_ENTITIES.get(entity_id)
            if not entity:
                # Return a default mock entity if not found
                return MOCK_GOLDEN_ENTITIES["ent_sme_00921"]
            return entity

        # Real API Retrieval
        token = await self.get_iam_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "crn": self.crn
        }
        url = f"{self.route}/mdm-data/v1/entities/{entity_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def list_all_entities(self) -> List[Dict[str, Any]]:
        """Utility method to get all entities (mainly for mock dashboards)"""
        return list(MOCK_GOLDEN_ENTITIES.values())

match360_service = Match360Service()
