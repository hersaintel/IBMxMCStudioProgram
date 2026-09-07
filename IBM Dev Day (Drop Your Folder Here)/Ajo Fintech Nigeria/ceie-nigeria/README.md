# CEIE Nigeria Hackathon Prototype
Cooperative Economic Intelligence Platform

## Architecture

```
+-------------------------------------------------------------+
|                     Streamlit Frontend                      |
|  [Overview] [MDM/Entity] [Fraud Alerts] [Macro & Query]     |
+------------------------------+------------------------------+
                               | REST API (FastAPI)
+------------------------------v------------------------------+
|                        Backend API                          |
|  +----------------+  +-----------------+  +--------------+  |
|  | Ingestion &    |  | Fraud Intel     |  | MDM Adapter  |  |
|  | Data Gen       |  | (IsoForest)     |  |              |  |
|  +----------------+  +-----------------+  +------+-------+  |
|                                                  |          |
+--------------------------------------------------|----------+
                                                   |
              +------------------------------------+--------------------------+
              |                                                               |
+-------------v--------------+                                  +-------------v--------------+
| Local Matcher (Fallback)   |                                  | IBM Match 360 (Optional)   |
| Rapidfuzz + Greedy Cluster |                                  | IAM Auth + Bulk Load       |
+----------------------------+                                  +----------------------------+
```

## Setup (3 Steps)

1. **Clone & Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   ```

2. **Environment Variables**
   ```bash
   cp .env.example .env
   # Add IBM_MATCH360_API_KEY and IBM_SERVICE_INSTANCE_ID if you have them.
   # Otherwise, the app gracefully falls back to the local entity resolution.
   ```

3. **Run Application**
   ```bash
   ./run.sh
   # On Windows PowerShell, you can run the commands inside run.sh manually:
   # pip install -r requirements.txt
   # python backend/ingest.py
   # start uvicorn backend.main:app --port 8000
   # streamlit run frontend/app.py
   ```

## 3-Minute Demo Script

1. **Overview Tab (0:00 - 0:45)**
   - "Welcome to CEIE Nigeria. We ingest raw member data from various cooperatives and transaction logs."
   - "Notice the NDPA Compliant Member Directory. PII like phone numbers and BVNs are automatically masked."

2. **Member Identity / MDM (0:45 - 1:30)**
   - "Data often contains duplicates (e.g. slight name variations, phone formatting)."
   - "Click 'Run Matching & Ingestion'. This routes data to our IBM Match 360 adapter (or our local fuzzy-matching fallback)."
   - "Notice how it merged duplicates and shows us the Golden Records table with confidence scores and 'Needs Review' flags."

3. **Fraud Intelligence (1:30 - 2:15)**
   - "Switch to the Fraud Alerts tab. We use an Isolation Forest ML model combined with rule-based heuristics."
   - "Expand the high-severity alerts. You'll see rule R001 (duplicate transactions) and R004 (Identity Risk from MDM)."
   - "This stops cooperative fraud in its tracks."

4. **Macro Intelligence (2:15 - 3:00)**
   - "Switch to the Macro Intelligence tab. We pull live inflation data from the World Bank."
   - "Type 'how many fraud alerts are there' in the Ask CEIE Agent box to show the NLP intent parser dynamically querying our intelligence layer."
   - "Thank you for watching!"
