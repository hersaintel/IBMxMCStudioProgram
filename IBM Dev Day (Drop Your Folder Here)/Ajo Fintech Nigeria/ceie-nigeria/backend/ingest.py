import os
import random
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

fake = Faker('en_NG')
Faker.seed(42)
random.seed(42)

COOPERATIVES = ["Enugu", "Lagos", "Kano", "Anambra", "Kaduna"]

def generate_base_members(n=500):
    members = []
    for i in range(n):
        members.append({
            "member_id": f"M{10000+i}",
            "name": fake.name(),
            "phone": fake.phone_number(),
            "bvn": str(random.randint(10000000000, 99999999999)),
            "nin": str(random.randint(10000000000, 99999999999)),
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "cooperative": random.choice(COOPERATIVES),
            "joined_date": fake.date_between(start_date="-5y", end_date="today").isoformat()
        })
    return members

def inject_dirty_duplicates(base_members, n=60):
    duplicates = []
    # Pick n random members to duplicate
    members_to_dup = random.sample(base_members, n)
    for i, m in enumerate(members_to_dup):
        dup = m.copy()
        dup["member_id"] = f"M9000{i}" # new id for the duplicate record
        
        # apply random corruption
        corruption_type = random.choice(["uppercase", "phone_variance", "swapped_name", "trailing_space", "all"])
        
        if corruption_type in ["uppercase", "all"]:
            dup["name"] = dup["name"].upper()
        if corruption_type in ["phone_variance", "all"]:
            if dup["phone"].startswith("+234"):
                dup["phone"] = "0" + dup["phone"][4:]
            elif dup["phone"].startswith("0"):
                dup["phone"] = "+234" + dup["phone"][1:]
        if corruption_type in ["swapped_name", "all"]:
            parts = dup["name"].split(" ")
            if len(parts) >= 2:
                dup["name"] = f"{parts[1]} {parts[0]}" + (" ".join(parts[2:]) if len(parts) > 2 else "")
        if corruption_type in ["trailing_space", "all"]:
            dup["name"] = dup["name"] + "   "
            dup["bvn"] = dup["bvn"] + " "
            
        duplicates.append(dup)
    return duplicates

def generate_transactions(members, n=20000):
    """Generate synthetic PaySim-like transactions"""
    logger.info("Generating synthetic transactions...")
    txns = []
    types = ["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
    
    member_ids = [m["member_id"] for m in members]
    
    for i in range(n):
        # Is this a fraudulent transaction?
        is_fraud = 1 if random.random() < 0.02 else 0 
        
        txn_type = random.choice(types)
        
        if is_fraud:
            amount = random.uniform(500000, 2000000) # High amounts for fraud
        else:
            amount = random.uniform(100, 50000) * (random.randint(1, 10))
            
        amount_ngn = amount * 450
        
        txns.append({
            "step": random.randint(1, 744), # PaySim hours
            "type": txn_type,
            "amount_ngn": amount_ngn,
            "nameOrig": random.choice(member_ids),
            "nameDest": f"M{random.randint(50000, 99999)}" if random.random() < 0.5 else random.choice(member_ids),
            "isFraud": is_fraud,
            "channel": txn_type # Added channel from type
        })
    return pd.DataFrame(txns)

def download_or_generate_paysim(members):
    # Try downloading from a known public raw URL or fallback
    # Since kaggle requires auth, we'll just generate the synthetic dataset directly
    # to guarantee the demo never blocks.
    try:
        df = generate_transactions(members)
        df.to_csv("data/transactions.csv", index=False)
        logger.info(f"Generated {len(df)} transactions to data/transactions.csv")
    except Exception as e:
        logger.error(f"Failed to generate transactions: {e}")

def run_ingestion():
    logger.info("Starting data ingestion...")
    base_members = generate_base_members(500)
    duplicates = inject_dirty_duplicates(base_members, 60)
    
    all_members = base_members + duplicates
    random.shuffle(all_members)
    
    members_df = pd.DataFrame(all_members)
    members_df.to_csv("data/members_dirty.csv", index=False)
    logger.info(f"Generated {len(members_df)} members (500 base + 60 duplicates) to data/members_dirty.csv")
    
    download_or_generate_paysim(all_members)
    logger.info("Data ingestion complete.")
    
    return {
        "members_count": len(members_df),
        "transactions_count": 20000
    }

if __name__ == "__main__":
    run_ingestion()
