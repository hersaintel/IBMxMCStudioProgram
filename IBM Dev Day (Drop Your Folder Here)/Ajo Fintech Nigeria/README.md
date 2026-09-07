# 🪙 Ajo (CEIE) — Community Economic Intelligence Engine
### *Empowering African Cooperatives with AI, Identity Intelligence, and Inflation-Resistant Treasuries*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![NDPA Compliant](https://img.shields.io/badge/NDPA-Compliant%20Privacy-success.svg)](#privacy--ndpa-compliance)

---

## 👥 Contributors
- **Damian Munene**
- **Steve Ogolla**
- **Cynthia Moraa**
- **Peter Youngren**

---

## 🌍 The Story Behind Ajo: Why This Matters

Across Nigeria and West Africa, long before modern commercial banks existed, our communities relied on a timeless system of mutual trust: **Ajo** (also known as *Esusu* or *Adashe*). 

Market women, artisans, farmers, and cooperative members gather every week to pool their hard-earned money. When it’s your turn, you receive a lump sum to expand your shop, pay school fees, buy harvest equipment, or weather an emergency. It is communal finance in its purest, most resilient form.

**Yet today, grassroots cooperatives face three existential threats:**

1. **💸 Runaway Inflation & Currency Devaluation**: With inflation hovering above 30%, cash sitting in traditional accounts rapidly loses purchasing power before members even receive their payouts.
2. **🎭 Identity Fragmentation & Cooperative Fraud**: A bad actor can take a loan from Cooperative A, default, and walk into Cooperative B under a slightly altered name or phone format without detection.
3. **⚖️ Regulatory & Governance Blindspots**: Cooperatives struggle with transparent governance, CBN (Central Bank of Nigeria) FX quotas, and compliance with privacy regulations like the **NDPA (Nigeria Data Protection Act)**.

> **Ajo (CEIE)** bridges the gap between centuries-old grassroots trust and cutting-edge financial technology. It empowers cooperatives with **master data entity resolution**, **AI-driven fraud & AML detection**, and **transparent, inflation-hedging treasury management**.

---

## 💡 What Ajo Does

```
                              ┌───────────────────────────────────┐
                              │     Grassroots Cooperative        │
                              │     (Ajo / Esusu / SACCO)         │
                              └─────────────────┬─────────────────┘
                                                │ Raw data & transactions
                                                ▼
 ╔═════════════════════════════════════════════════════════════════════════════════════╗
 ║                     Ajo Community Economic Intelligence Engine                     ║
 ║                                                                                     ║
 ║   1. Master Data Entity Matching       2. ML Fraud & Smurfing Defense              ║
 ║      • Deduplicates member records        • Isolation Forest anomaly scoring        ║
 ║      • Resolves aliases & phone typos     • High-frequency transaction flags        ║
 ║      • Builds NDPA Golden Records         • Cross-cooperative identity risk         ║
 ║                                                                                     ║
 ║   3. Stablecoin Inflation Hedge        4. Multi-Signature Governance                ║
 ║      • Converts idle fiat to USDT/USDC    • Democratic proposal voting              ║
 ║      • Live World Bank & Oracle rates     • No single-person treasury control       ║
 ║      • Preserves member buying power      • Immutable audit logs                    ║
 ╚═════════════════════════════════════════════════════════════════════════════════════╝
                                                │
                                                ▼
                ┌───────────────────────────────┴───────────────────────────────┐
                ▼                                                               ▼
   📊 Cooperative Executive Portal                                 🏛️ Regulator & Compliance View
   • Inflation loss saved live tracker                             • AML smurfing monitor & alerts
   • One-click multi-sig swap proposals                            • CBN $200k FX quota tracking
   • Member risk profiles & insights                               • Entity network graphs
```

---

## 🛠️ How It Works (Under the Hood)

### 1. 🪪 Identity Resolution & Golden Records (MDM)
- **The Problem**: A member registered as *"Oluwaseun Adeyemi"* in Lagos might register as *"Seun Adeyemi"* in Ibadan with an extra space in their phone number.
- **The Fix**: The engine runs hybrid entity resolution powered by **IBM Match 360** (with a high-performance **Local Fuzzy-Matching fallback**). It matches phonetic name variations, masked BVNs, and contact hashes, consolidating scattered records into a single verifiable **"Golden Record"** while masking PII to remain fully NDPA compliant.

### 2. 🛡️ AI-Powered Fraud & AML Detection
- **Isolation Forest ML Model**: Scans real-time transaction volumes and frequencies to isolate anomalous spikes and abnormal loan requests.
- **Rule-Based Heuristic Engines**:
  - **Rule R001**: Rapid duplicate transactions within suspicious time windows.
  - **Rule R002 / R003**: Structuring / Smurfing detection across multiple linked cooperative wallets.
  - **Rule R004**: High-risk unverified identity flags routed directly from the MDM engine.

### 3. 📈 Inflation-Hedging Treasury (DeFi / Stablecoin Layer)
- **Real-Time Macro Oracle**: Integrates live **World Bank API** inflation feeds and real-time exchange rates (NGN, USDT, USDC, cNGN).
- **Purchasing Power Preservation**: Calculates the exact real-value decay of holding Naira in reserve versus holding audited stablecoins, projecting annual purchasing power saved for members.

### 4. 🤝 Democratic Multi-Sig Governance
- **No Rogue Treasurers**: Swapping cooperative funds into stablecoins cannot be done by a single individual.
- **On-Chain / Ledger Multi-Sig**: A treasurer proposes a swap -> notifications are triggered -> executive board members must review and sign off before any funds move through the on-ramp adapter.

### 5. 🤖 watsonx.ai Natural Language Copilot
- Cooperatives and regulators can ask plain-English questions:
  - *"What is our total FX exposure this month?"*
  - *"Show all high-severity fraud alerts in the northern district."*
  - *"How much purchasing power have we protected this quarter?"*

---

## 📂 Project Architecture

```
IBM Dev Day (Drop Your Folder Here)/Ajo Fintech Nigeria/
├── README.md                     # Main Project Documentation & Architecture
├── README-checklist.md           # Submission Checklist
├── README-vulnerability.md       # Vulnerability & Threat Assessment
│
├── ceie-nigeria/                 # Core Python Backend & Intelligence Engine
│   ├── backend/
│   │   ├── intelligence/         # Machine Learning & Analytics
│   │   │   ├── fraud.py          # Isolation Forest + Heuristic rules (R001-R004)
│   │   │   ├── governance.py     # Multi-sig proposal & approval engine
│   │   │   └── matcher.py        # Rapidfuzz & Greedy clustering entity matcher
│   │   ├── services/             # Adapters & External Integrations
│   │   │   ├── crypto_oracle.py  # Exchange rate calculations & quotes
│   │   │   ├── ibm_match360.py   # IBM Cloud Match 360 connector
│   │   │   ├── mdm_adapter.py    # Master Data Management orchestrator
│   │   │   ├── onramp_adapter.py # Fiat-to-Crypto liquidity onramp
│   │   │   ├── risk.py           # CBN compliance & FX vulnerability scoring
│   │   │   ├── treasury_manager.py# Ledger accounting & portfolio tracker
│   │   │   ├── watsonx.py        # IBM watsonx.ai LLM agent
│   │   │   └── world_bank.py     # World Bank macro indicators (Inflation, GDP)
│   │   ├── ingest.py             # Synthetic cooperative data generator & ingest
│   │   └── main.py               # FastAPI REST endpoints
│   ├── frontend/                 # Streamlit Prototype UI
│   └── requirements.txt          # Python dependencies
│
└── ceie-dashboard/               # Modern Executive React + Tailwind Web App
    ├── src/
    │   ├── components/
    │   │   ├── RegulatorView.jsx   # AML, CBN Quota ($200k limit), Smurfing Graph
    │   │   ├── CooperativeView.jsx # Treasury reserves, Multi-sig swaps, Fraud feeds
    │   │   └── CalculatorView.jsx  # Interactive Inflation vs Hedge Simulator
    │   ├── App.jsx               # Dashboard orchestrator & IBM status monitors
    │   └── index.css             # Tailored dark-mode styling & tokens
    ├── package.json
    └── vite.config.js
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & **npm**

---

### Step 1: Start the Backend (CEIE Engine)

1. Open your terminal and navigate to the backend directory:
   ```bash
   cd "IBM Dev Day (Drop Your Folder Here)/Ajo Fintech Nigeria/ceie-nigeria"
   ```

2. Create and activate a virtual environment:
   - **Linux / macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables (optional — local fallbacks work out of the box!):
   ```bash
   cp .env.example .env
   ```

5. Ingest data and start the FastAPI server:
   ```bash
   python backend/ingest.py
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   > 🚀 Backend API will be live at: **`http://localhost:8000`** (Interactive Docs: `http://localhost:8000/docs`)

---

### Step 2: Launch the Modern React Web Dashboard

1. In a new terminal tab, navigate to the dashboard directory:
   ```bash
   cd "IBM Dev Day (Drop Your Folder Here)/Ajo Fintech Nigeria/ceie-dashboard"
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   > 🌟 Dashboard will be running at: **`http://localhost:5173`**

---

### Optional: Streamlit Prototype
If you prefer testing via the Streamlit interface:
```bash
cd "IBM Dev Day (Drop Your Folder Here)/Ajo Fintech Nigeria/ceie-nigeria"
streamlit run frontend/app.py
```

---

## 🎯 Key User Personas & Walkthrough

| User Persona | What They Care About | How Ajo Solves It |
| :--- | :--- | :--- |
| **👩🏾‍💼 Cooperative Treasurer** *(e.g., Alaba Market Association)* | Protecting member contributions from 30%+ inflation without putting funds at risk. | Can initiate a multi-sig stablecoin hedge proposal, view purchasing power saved in real time, and audit all transactions transparently. |
| **👨🏾‍⚖️ Cooperative President / Trustee** | Preventing embezzlement or unauthorized fund movement. | Receives push notifications for treasury swaps; must digitally sign off before any funds are converted. |
| **🏛️ Regulator & Compliance Officer** *(e.g., CBN, SEC, Cooperative Federation)* | Ensuring cooperatives aren't being exploited for smurfing, money laundering, or illegal FX hoarding. | Accesses the **Regulator View** to track aggregate CBN FX quotas ($200k YTD cap), investigate flagged smurfing rings, and review compliance scores. |
| **👥 Everyday Member** | Trusting that their savings are safe, accounted for, and retain their value when it's their turn to get paid. | Guaranteed verified identity, zero duplicate loan scams draining the pool, and an inflation-hedged payout. |

---

## 🔒 Privacy & NDPA Compliance

We take financial privacy seriously. Under the **Nigeria Data Protection Act (NDPA)**:
- **Bank Verification Numbers (BVN)** and phone numbers are strictly hashed and masked (e.g. `222***8901`).
- Matching algorithms compare cryptographic hashes and phonetic tokens, ensuring sensitive identity credentials are never exposed in raw text.
- Comprehensive audit trails record every merge decision, dispute flag, and multi-sig approval.

---

## 🤝 Contributing & Community

Ajo was built with the belief that financial technology should serve the many, not just the few. We welcome contributions from developers, economists, cooperative leaders, and security researchers.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License
Distributed under the **MIT License**. Built with ❤️ for community wealth and resilience.
