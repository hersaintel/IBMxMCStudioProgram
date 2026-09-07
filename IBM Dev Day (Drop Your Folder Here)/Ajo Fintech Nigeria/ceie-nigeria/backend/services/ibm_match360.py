import os
import time
import requests
import logging

logger = logging.getLogger(__name__)

class IBMMatch360Client:
    def __init__(self):
        self.api_key = os.environ.get("IBM_MATCH360_API_KEY")
        self.instance_id = os.environ.get("IBM_SERVICE_INSTANCE_ID")
        self.base_url = "https://api.dataplatform.cloud.ibm.com/v1" # Example base URL for Match 360
        self.token = None
        self.token_expiry = 0
        
    def _get_token(self):
        if self.token and time.time() < self.token_expiry:
            return self.token
            
        logger.info("Fetching IAM token for IBM Match 360...")
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        
        # Retry logic for 401/429/5xx
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, data=data)
                response.raise_for_status()
                result = response.json()
                self.token = result['access_token']
                # Usually expires in 3600s, add a buffer
                self.token_expiry = time.time() + result.get('expires_in', 3600) - 60
                return self.token
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to get IAM token (attempt {attempt+1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    raise
                    
    def _get_headers(self):
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
    def bulk_load(self, records: list[dict]):
        logger.info(f"Bulk loading {len(records)} records to IBM Match 360...")
        # Stub for the actual Match 360 ingestion API
        url = f"{self.base_url}/mdm/v1/data/records?instance_id={self.instance_id}"
        
        payload = {"records": records}
        for attempt in range(3):
            try:
                # Assuming POST for bulk load
                # Note: This is a prototype representation of the real API
                # response = requests.post(url, headers=self._get_headers(), json=payload)
                # response.raise_for_status()
                # return response.json()
                
                # Mocking the network call for the hackathon prototype since we don't have real keys
                time.sleep(1)
                return {"status": "success", "job_id": "job123"}
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to bulk load (attempt {attempt+1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def trigger_match(self):
        logger.info("Triggering IBM Match 360 matching job...")
        # Stub for match trigger
        for attempt in range(3):
            try:
                # url = f"{self.base_url}/mdm/v1/matching/jobs?instance_id={self.instance_id}"
                # response = requests.post(url, headers=self._get_headers())
                # response.raise_for_status()
                time.sleep(1)
                return {"status": "completed"}
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to trigger match (attempt {attempt+1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    raise

    def get_golden_records(self):
        logger.info("Fetching golden records from IBM Match 360...")
        # Stub for fetching golden records
        for attempt in range(3):
            try:
                # url = f"{self.base_url}/mdm/v1/entities?instance_id={self.instance_id}"
                # response = requests.get(url, headers=self._get_headers())
                # response.raise_for_status()
                time.sleep(1)
                return [] # return empty to let the adapter know we need fallback if no real data
            except requests.exceptions.RequestException as e:
                logger.warning(f"Failed to fetch golden records (attempt {attempt+1}): {e}")
                if attempt < 2:
                    time.sleep(2 ** attempt)
                else:
                    raise
