import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import datetime

def score_transactions(txns: pd.DataFrame, members_df: pd.DataFrame = None, flagged_members: set = None) -> list[dict]:
    """
    Score transactions for fraud using IsolationForest and Rule-based engine.
    txns: DataFrame containing transactions
    members_df: DataFrame containing member details (for R002)
    flagged_members: Set of member_ids flagged as duplicates in MDM (for R004)
    """
    alerts = []
    if txns.empty:
        return alerts
        
    df = txns.copy()
    
    # 1. Feature Engineering for ML
    df['hour_of_day'] = df['step'] % 24
    freq = df.groupby('nameOrig').size().reset_index(name='txn_frequency_per_member')
    df = df.merge(freq, on='nameOrig', how='left')
    
    # 2. Isolation Forest Anomaly Score
    features = ['amount_ngn', 'txn_frequency_per_member', 'hour_of_day']
    # Fill any NaNs to be safe
    X = df[features].fillna(0)
    
    clf = IsolationForest(contamination=0.01, random_state=42)
    # Fit and predict. Returns -1 for anomalies/outliers and 1 for inliers.
    # We'll map the decision_function to a 0-1 anomaly score
    clf.fit(X)
    scores = clf.decision_function(X) # lower is more anomalous
    
    # Normalize scores to 0-1 where 1 is highest anomaly
    # decision_function typically ranges from -0.5 to 0.5 roughly.
    # Let's invert and normalize
    score_min, score_max = scores.min(), scores.max()
    if score_max > score_min:
        normalized_scores = (score_max - scores) / (score_max - score_min)
    else:
        normalized_scores = np.zeros(len(scores))
        
    df['anomaly_score'] = normalized_scores
    
    # We will need cooperative data for R002
    if members_df is not None and not members_df.empty:
        df = df.merge(members_df[['member_id', 'cooperative']], left_on='nameOrig', right_on='member_id', how='left')
    else:
        df['cooperative'] = 'Unknown'
        
    flagged_members = flagged_members or set()
    
    # Pre-calculate cooperative stats for R002
    coop_stats = {}
    if 'cooperative' in df.columns:
        coop_stats = df.groupby('cooperative')['amount_ngn'].agg(['mean', 'std']).fillna(0).to_dict('index')

    # Sort by step to help with time-based rules
    df = df.sort_values(by=['nameOrig', 'step'])

    # Track withdrawals for R003
    withdrawal_types = ['CASH_OUT', 'TRANSFER', 'DEBIT']
    
    # Process row by row for rules (or vectorized where possible, but loop is simpler for alerts generation)
    # To avoid slow iteration on huge datasets, we'll vectorize what we can.
    
    # R001: duplicate txn same member+amount+minute (step as minute proxy)
    df['is_duplicate_txn'] = df.duplicated(subset=['nameOrig', 'amount_ngn', 'step'], keep=False)
    
    # Iterate and generate alerts
    # To keep it fast, we only generate alerts if conditions are met. We can filter the df first.
    
    for idx, row in df.iterrows():
        member = row['nameOrig']
        amount = row['amount_ngn']
        score = row['anomaly_score']
        step = row['step']
        coop = row.get('cooperative', 'Unknown')
        
        # Determine Severity
        is_high = score > 0.9 or amount > 500000
        severity = "high" if is_high else ("medium" if score > 0.7 else "low")
        
        # We only generate alerts for specific rules.
        
        # R001
        if row['is_duplicate_txn']:
            alerts.append({
                "title": "Duplicate Transaction",
                "member": member,
                "severity": severity,
                "reason": "Multiple transactions with exact same amount in same time window.",
                "rule_id": "R001",
                "timestamp": f"Day {step // 24} Hr {step % 24}",
                "anomaly_score": round(score, 3)
            })
            
        # R002
        if coop in coop_stats:
            c_mean = coop_stats[coop]['mean']
            c_std = coop_stats[coop]['std']
            if c_std > 0 and amount > (c_mean + 3 * c_std):
                alerts.append({
                    "title": "Abnormal Amount for Cooperative",
                    "member": member,
                    "severity": severity,
                    "reason": f"Amount {amount:,.2f} exceeds 3 sigma for {coop} cooperative.",
                    "rule_id": "R002",
                    "timestamp": f"Day {step // 24} Hr {step % 24}",
                    "anomaly_score": round(score, 3)
                })
                
        # R004
        if member in flagged_members:
            alerts.append({
                "title": "Identity Risk",
                "member": member,
                "severity": "high", # Enforce high for identity risk
                "reason": "Transaction from member flagged as duplicate/suspicious in MDM.",
                "rule_id": "R004",
                "timestamp": f"Day {step // 24} Hr {step % 24}",
                "anomaly_score": round(score, 3)
            })
            
    # R003: sudden balance drain (3+ withdrawals in 24h)
    withdrawals = df[df['type'].isin(withdrawal_types)].copy()
    if not withdrawals.empty:
        # Group by member and use rolling window on step
        for member, group in withdrawals.groupby('nameOrig'):
            # This is naive but works for hackathon: check if any 3 txns happen within 24 steps
            steps = group['step'].values
            for i in range(len(steps) - 2):
                if steps[i+2] - steps[i] <= 24:
                    score = group.iloc[i+2]['anomaly_score']
                    amount = group.iloc[i+2]['amount_ngn']
                    is_high = score > 0.9 or amount > 500000
                    severity = "high" if is_high else "medium"
                    alerts.append({
                        "title": "Sudden Balance Drain",
                        "member": member,
                        "severity": severity,
                        "reason": "3 or more withdrawals within a 24-hour window.",
                        "rule_id": "R003",
                        "timestamp": f"Day {steps[i+2] // 24} Hr {steps[i+2] % 24}",
                        "anomaly_score": round(score, 3)
                    })
                    break # One alert per member for this pattern is usually enough
                    
    # Sort alerts by severity (high > medium > low) and anomaly score
    severity_rank = {"high": 3, "medium": 2, "low": 1}
    alerts.sort(key=lambda x: (severity_rank.get(x['severity'], 0), x['anomaly_score']), reverse=True)
    
    return alerts
