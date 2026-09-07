import re
from rapidfuzz import fuzz
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def normalize_phone(phone: str) -> str:
    """Normalize phone to remove spaces and standardize +234/0 prefix"""
    if not isinstance(phone, str):
        return ""
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    if phone.startswith('+234'):
        phone = '0' + phone[4:]
    return phone

def compute_similarity(record_a: dict, record_b: dict) -> float:
    """
    rapidfuzz weighted score: 
    0.4 name ratio + 0.3 normalized phone + 0.3 exact BVN
    """
    # Name match (0.4)
    name_a = str(record_a.get('name', '')).strip().lower()
    name_b = str(record_b.get('name', '')).strip().lower()
    name_score = fuzz.token_sort_ratio(name_a, name_b) / 100.0
    
    # Phone match (0.3)
    phone_a = normalize_phone(str(record_a.get('phone', '')))
    phone_b = normalize_phone(str(record_b.get('phone', '')))
    phone_score = 1.0 if (phone_a and phone_b and phone_a == phone_b) else 0.0
    
    # BVN match (0.3)
    bvn_a = str(record_a.get('bvn', '')).strip()
    bvn_b = str(record_b.get('bvn', '')).strip()
    bvn_score = 1.0 if (bvn_a and bvn_b and bvn_a == bvn_b) else 0.0
    
    return (0.4 * name_score) + (0.3 * phone_score) + (0.3 * bvn_score)

def local_match_records(records: list[dict]) -> list[dict]:
    """
    Greedy clustering; surviving record = golden record; store confidence.
    Thresholds: ≥0.95 merge, 0.75–0.95 review flag, <0.75 distinct
    """
    clusters = []
    
    for record in records:
        best_match = None
        best_score = -1
        
        for cluster in clusters:
            # Compare against the golden record of the cluster
            score = compute_similarity(record, cluster['golden_record'])
            if score > best_score:
                best_score = score
                best_match = cluster
                
        if best_match and best_score >= 0.95:
            # Merge into existing cluster
            best_match['source_records'].append(record)
            # Update confidence if higher
            if best_score > best_match['match_confidence']:
                best_match['match_confidence'] = best_score
        else:
            # Create new cluster
            # For review flags, we can just note if it was between 0.75 and 0.95
            needs_review = (0.75 <= best_score < 0.95) if best_score != -1 else False
            clusters.append({
                'golden_record': record.copy(),
                'match_confidence': 1.0, # Self match
                'source_records': [record],
                'needs_review': needs_review
            })
            
    return clusters
