import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Set USE_MOCK_SERVICES to True if real credentials are not supplied
    USE_MOCK_SERVICES: bool = os.getenv("USE_MOCK_SERVICES", "True").lower() in ("true", "1", "yes")
    
    # IBM Watsonx Credentials
    IBM_CLOUD_API_KEY: str = os.getenv("IBM_CLOUD_API_KEY", "")
    WATSONX_PROJECT_ID: str = os.getenv("WATSONX_PROJECT_ID", "")
    WATSONX_REGION: str = os.getenv("WATSONX_REGION", "us-south")
    
    # IBM Match 360 Credentials
    MATCH360_ROUTE: str = os.getenv("MATCH360_ROUTE", "")
    MATCH360_CRN: str = os.getenv("MATCH360_CRN", "")
    
    # Port / Host
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

settings = Settings()
