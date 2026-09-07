"""
On-Ramp Adapter — Simulated settlement for stablecoin purchases.
"""
import uuid, logging

logger = logging.getLogger(__name__)


class OnrampAdapter:
    """Simulates Polygon on-ramp settlement for prototype."""

    def settle(self, cooperative: str, amount_ngn: float, target_token: str = "USDT"):
        swap_id = f"SWP-{uuid.uuid4().hex[:8].upper()}"
        # Simulated conversion
        rate_map = {"USDT": 1520.0, "USDC": 1525.0, "cNGN": 1520.0}
        rate = rate_map.get(target_token, 1520.0)
        fee_pct = 0.5
        net_ngn = amount_ngn * (1 - fee_pct / 100)
        amount_received = round(net_ngn / rate, 4)

        # Simulated on-chain tx hash
        tx_hash = f"0x{uuid.uuid4().hex}"

        logger.info(f"Swap settled successfully: {swap_id} -> {amount_received} {target_token}")

        return {
            "swap_id": swap_id,
            "cooperative": cooperative,
            "amount_ngn": amount_ngn,
            "amount_received": amount_received,
            "target_token": target_token,
            "network": "Polygon",
            "tx_hash": tx_hash,
            "status": "settled",
        }
