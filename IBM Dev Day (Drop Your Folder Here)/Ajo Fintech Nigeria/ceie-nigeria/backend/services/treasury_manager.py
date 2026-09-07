"""
Treasury Manager — Ledger + Portfolio tracking for SACCO stablecoin hedging.
"""
import csv, os, uuid, logging
from datetime import datetime

from backend.services.crypto_oracle import calculate_quote, get_exchange_rates
from backend.intelligence.governance import GovernanceEngine
from backend.services.onramp_adapter import OnrampAdapter

logger = logging.getLogger(__name__)
LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "treasury_ledger.csv")


class TreasuryManager:
    def __init__(self):
        self.governance = GovernanceEngine()
        self.onramp = OnrampAdapter()
        self._ensure_ledger()

    # ------------------------------------------------------------------
    def _ensure_ledger(self):
        os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
        if not os.path.exists(LEDGER_PATH):
            with open(LEDGER_PATH, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "cooperative", "direction", "amount_ngn",
                    "amount_token", "token", "rate", "fee_ngn",
                    "tx_hash", "status", "initiator"
                ])

    # ------------------------------------------------------------------
    def get_portfolio_summary(self):
        rates = get_exchange_rates()
        ledger = self._read_ledger()

        total_ngn_in = sum(float(r["amount_ngn"]) for r in ledger if r["direction"] == "BUY" and r["status"] == "settled")
        total_token_out = sum(float(r["amount_token"]) for r in ledger if r["direction"] == "BUY" and r["status"] == "settled")
        total_usdt = sum(float(r["amount_token"]) for r in ledger if r["direction"] == "BUY" and r["status"] == "settled" and r["token"] == "USDT")
        total_usdc = sum(float(r["amount_token"]) for r in ledger if r["direction"] == "BUY" and r["status"] == "settled" and r["token"] == "USDC")
        total_cngn = sum(float(r["amount_token"]) for r in ledger if r["direction"] == "BUY" and r["status"] == "settled" and r["token"] == "cNGN")

        stablecoin_usd_value = total_usdt + total_usdc + (total_cngn / rates.get("cNGN_NGN", 1520))

        inflation_rate = 33.95
        annual_saved = stablecoin_usd_value * rates.get("NGN_USD", 1520) * (inflation_rate / 100)

        return {
            "total_fiat_deployed_ngn": total_ngn_in,
            "stablecoin_reserves_usd": round(stablecoin_usd_value, 2),
            "holdings": {
                "USDT": round(total_usdt, 4),
                "USDC": round(total_usdc, 4),
                "cNGN": round(total_cngn, 4),
            },
            "current_rates": rates,
            "current_inflation_rate": inflation_rate,
            "annual_purchasing_power_saved_ngn": round(annual_saved, 2),
            "total_swaps": len([r for r in ledger if r["status"] == "settled"]),
        }

    # ------------------------------------------------------------------
    def initiate_swap(self, cooperative: str, amount_ngn: float, target_token: str = "USDT", initiator: str = "Treasurer"):
        quote = calculate_quote(amount_ngn, target_token)

        # Multi-sig gate for >= ₦1,000,000
        MULTISIG_THRESHOLD = 1_000_000
        if amount_ngn >= MULTISIG_THRESHOLD:
            proposal = self.governance.create_proposal(
                cooperative=cooperative,
                amount_ngn=amount_ngn,
                target_token=target_token,
                initiator=initiator,
            )
            return {
                "status": "pending_approval",
                "message": f"Swap of ₦{amount_ngn:,.2f} requires multi-sig approval (threshold: ₦{MULTISIG_THRESHOLD:,.2f}).",
                "proposal": proposal,
                "quote": quote,
            }

        # Direct settlement for smaller amounts
        result = self.onramp.settle(cooperative, amount_ngn, target_token)
        self._write_ledger_row(
            cooperative=cooperative,
            direction="BUY",
            amount_ngn=amount_ngn,
            amount_token=result["amount_received"],
            token=target_token,
            rate=quote["rate"],
            fee_ngn=quote["fee_ngn"],
            tx_hash=result["tx_hash"],
            status="settled",
            initiator=initiator,
        )
        logger.info(f"Swap settled: {result['swap_id']} -> {result['amount_received']} {target_token}")
        return {"status": "settled", "result": result, "quote": quote}

    # ------------------------------------------------------------------
    def approve_and_execute_swap(self, proposal_id: str, approver: str):
        proposal = self.governance.approve(proposal_id, approver)
        if proposal["status"] == "approved":
            result = self.onramp.settle(
                proposal["cooperative"],
                proposal["amount_ngn"],
                proposal["target_token"],
            )
            quote = calculate_quote(proposal["amount_ngn"], proposal["target_token"])
            self._write_ledger_row(
                cooperative=proposal["cooperative"],
                direction="BUY",
                amount_ngn=proposal["amount_ngn"],
                amount_token=result["amount_received"],
                token=proposal["target_token"],
                rate=quote["rate"],
                fee_ngn=quote["fee_ngn"],
                tx_hash=result["tx_hash"],
                status="settled",
                initiator=proposal["initiator"],
            )
            return {"status": "settled", "result": result, "proposal": proposal}
        return {"status": proposal["status"], "proposal": proposal}

    # ------------------------------------------------------------------
    def get_ledger_history(self):
        return self._read_ledger()

    # ------------------------------------------------------------------
    def _read_ledger(self):
        if not os.path.exists(LEDGER_PATH):
            return []
        with open(LEDGER_PATH, "r") as f:
            return list(csv.DictReader(f))

    def _write_ledger_row(self, **kwargs):
        with open(LEDGER_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(),
                kwargs.get("cooperative", ""),
                kwargs.get("direction", "BUY"),
                kwargs.get("amount_ngn", 0),
                kwargs.get("amount_token", 0),
                kwargs.get("token", "USDT"),
                kwargs.get("rate", 0),
                kwargs.get("fee_ngn", 0),
                kwargs.get("tx_hash", ""),
                kwargs.get("status", "settled"),
                kwargs.get("initiator", ""),
            ])
