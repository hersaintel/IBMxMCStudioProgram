"""
Crypto Oracle — FX rates and stablecoin quote engine.
"""

def get_exchange_rates():
    """Return current FX and stablecoin rates (simulated)."""
    return {
        "NGN_USD": 1520.0,
        "USDT_NGN": 1520.0,
        "USDC_NGN": 1525.0,
        "cNGN_NGN": 1520.0,
        "fee_pct": 0.5,
        "network": "Polygon",
    }


def calculate_quote(amount_ngn: float, target_token: str = "USDT"):
    """Calculate conversion quote with fee breakdown."""
    rates = get_exchange_rates()

    if target_token == "USDT":
        rate = rates["USDT_NGN"]
    elif target_token == "USDC":
        rate = rates["USDC_NGN"]
    elif target_token == "cNGN":
        rate = rates["cNGN_NGN"]
    else:
        rate = rates["USDT_NGN"]

    fee_pct = rates["fee_pct"]
    fee_ngn = amount_ngn * (fee_pct / 100)
    net_ngn = amount_ngn - fee_ngn
    token_amount = net_ngn / rate

    return {
        "amount_ngn": amount_ngn,
        "target_token": target_token,
        "rate": rate,
        "fee_pct": fee_pct,
        "fee_ngn": round(fee_ngn, 2),
        "net_ngn": round(net_ngn, 2),
        "estimated_tokens": round(token_amount, 4),
        "network": rates["network"],
    }
