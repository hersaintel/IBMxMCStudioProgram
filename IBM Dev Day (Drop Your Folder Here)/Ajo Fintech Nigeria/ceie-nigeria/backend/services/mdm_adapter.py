import os
import logging
import pandas as pd
from backend.services.ibm_match360 import IBMMatch360Client
from backend.intelligence.matcher import local_match_records

logger = logging.getLogger(__name__)

class MDMAdapter:
    def __init__(self):
        self.api_key = os.environ.get("IBM_MATCH360_API_KEY")
        self.instance_id = os.environ.get("IBM_SERVICE_INSTANCE_ID")
        self.client = IBMMatch360Client() if self.api_key and self.instance_id else None
        
        # State to hold local matcher results
        self._golden_records = []

    def ingest_members(self, df: pd.DataFrame) -> dict:
        records = df.to_dict('records')
        
        if self.client:
            try:
                logger.info("Using IBM Match 360 for Entity Resolution.")
                self.client.bulk_load(records)
                self.client.trigger_match()
                golden = self.client.get_golden_records()
                if golden:
                    self._golden_records = golden
                    return {"mode": "IBM Match 360", "status": "success"}
                else:
                    raise Exception("IBM Match 360 returned empty records, falling back.")
            except Exception as e:
                logger.error(f"IBM Match 360 failed: {e}. Falling back to local matcher.")
                self._fallback_to_local(records)
                return {"mode": "Local Matcher (Fallback)", "status": "success"}
        else:
            logger.info("No IBM credentials found. Using local matcher for Entity Resolution.")
            self._fallback_to_local(records)
            return {"mode": "Local Matcher", "status": "success"}

    def _fallback_to_local(self, records: list[dict]):
        self._golden_records = local_match_records(records)

    def get_golden_records(self) -> list[dict]:
        return self._golden_records
