import pytest
from backend.intelligence.matcher import compute_similarity, local_match_records
# Assuming fraud will be in backend.intelligence.fraud
# We'll write the test for fraud here as well, per requirements.

def test_matcher_exact_duplicate():
    record_a = {
        "member_id": "M1",
        "name": "Chinedu Okeke",
        "phone": "+2348031234567",
        "bvn": "12345678901"
    }
    # Duplicate with minor phone format variance and trailing space
    record_b = {
        "member_id": "M2",
        "name": "Chinedu Okeke   ",
        "phone": "08031234567",
        "bvn": "12345678901 "
    }
    
    score = compute_similarity(record_a, record_b)
    assert score >= 0.95
    
    clusters = local_match_records([record_a, record_b])
    assert len(clusters) == 1
    assert len(clusters[0]['source_records']) == 2
    assert clusters[0]['match_confidence'] >= 0.95

def test_matcher_distinct():
    record_a = {
        "member_id": "M1",
        "name": "Chinedu Okeke",
        "phone": "+2348031234567",
        "bvn": "12345678901"
    }
    record_b = {
        "member_id": "M3",
        "name": "Ngozi Eze",
        "phone": "08059998888",
        "bvn": "98765432109"
    }
    
    score = compute_similarity(record_a, record_b)
    assert score < 0.75
    
    clusters = local_match_records([record_a, record_b])
    assert len(clusters) == 2

# Test for fraud R001 will fail until fraud module is implemented, 
# but we can stub it and implement it right after.
# Wait, let's implement the fraud test so that we fulfill the requirement: 
# "fraud R001 rule catches an exact duplicate txn"

def test_fraud_r001_duplicate_txn():
    from backend.intelligence.fraud import score_transactions
    import pandas as pd
    
    # R001: duplicate txn same member+amount+minute
    txns = [
        {
            "step": 10, # PaySim step (hours), let's just assume same minute logic applies here, 
                        # actually PaySim step is hours, but rule says "minute".
                        # We might need to use a timestamp or interpret step as minute for R001.
                        # Let's say step is the time index.
            "nameOrig": "M1",
            "amount_ngn": 50000,
            "type": "TRANSFER",
            "isFraud": 0
        },
        {
            "step": 10,
            "nameOrig": "M1",
            "amount_ngn": 50000,
            "type": "TRANSFER",
            "isFraud": 0
        }
    ]
    df = pd.DataFrame(txns)
    alerts = score_transactions(df)
    
    # We expect one alert for R001
    r001_alerts = [a for a in alerts if a['rule_id'] == 'R001']
    assert len(r001_alerts) >= 1
    assert r001_alerts[0]['member'] == 'M1'
