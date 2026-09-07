"""
Governance Engine — Multi-sig approval for treasury operations.
"""
import uuid
from datetime import datetime


class GovernanceEngine:
    REQUIRED_SIGNERS = 2  # 2-of-3 multi-sig for large swaps

    def __init__(self):
        self._proposals = {}  # in-memory store

    def create_proposal(self, cooperative: str, amount_ngn: float, target_token: str, initiator: str):
        pid = f"GOV-{uuid.uuid4().hex[:8].upper()}"
        proposal = {
            "proposal_id": pid,
            "cooperative": cooperative,
            "amount_ngn": amount_ngn,
            "target_token": target_token,
            "initiator": initiator,
            "approvals": [initiator],  # initiator counts as first approval
            "required_approvals": self.REQUIRED_SIGNERS,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }
        self._proposals[pid] = proposal
        return proposal

    def approve(self, proposal_id: str, approver: str):
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            raise ValueError(f"Proposal {proposal_id} not found")
        if proposal["status"] != "pending":
            raise ValueError(f"Proposal {proposal_id} is already {proposal['status']}")
        if approver in proposal["approvals"]:
            raise ValueError(f"{approver} has already approved this proposal")

        proposal["approvals"].append(approver)

        if len(proposal["approvals"]) >= proposal["required_approvals"]:
            proposal["status"] = "approved"
            proposal["approved_at"] = datetime.utcnow().isoformat()
        return proposal

    def get_pending(self, cooperative: str = None):
        results = []
        for p in self._proposals.values():
            if p["status"] == "pending":
                if cooperative is None or p["cooperative"] == cooperative:
                    results.append(p)
        return results
