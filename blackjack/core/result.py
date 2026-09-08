"""Round and hand outcome representations and payout calculation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RoundResult(str, Enum):
    """Categorical outcome of a resolved hand."""

    WIN = "WIN"
    LOSS = "LOSS"
    PUSH = "PUSH"
    BLACKJACK = "BLACKJACK"
    SURRENDER = "SURRENDER"

    def default_multiplier(self, blackjack_payout: float = 1.5) -> float:
        """Return standard net profit multiplier relative to the active bet on the hand.

        WIN: +1.0
        LOSS: -1.0
        PUSH: 0.0
        BLACKJACK: +blackjack_payout (typically +1.5 for 3:2)
        SURRENDER: -0.5
        """
        if self == RoundResult.WIN:
            return 1.0
        if self == RoundResult.LOSS:
            return -1.0
        if self == RoundResult.PUSH:
            return 0.0
        if self == RoundResult.BLACKJACK:
            return blackjack_payout
        if self == RoundResult.SURRENDER:
            return -0.5
        raise ValueError(f"Unknown round result: {self}")


@dataclass(slots=True)
class HandSettlement:
    """Detailed settlement for a single hand within a round."""

    result: RoundResult
    wager: float
    profit: float
    cards_summary: str
    actions_taken: list[str]
    is_split: bool = False

    @classmethod
    def create(
        cls,
        result: RoundResult,
        wager: float,
        blackjack_payout: float,
        cards_summary: str,
        actions_taken: list[str],
        is_split: bool = False,
    ) -> HandSettlement:
        """Calculate net profit based on result type and active wager."""
        mult = result.default_multiplier(blackjack_payout=blackjack_payout)
        profit = wager * mult
        return cls(
            result=result,
            wager=wager,
            profit=profit,
            cards_summary=cards_summary,
            actions_taken=actions_taken,
            is_split=is_split,
        )


@dataclass(slots=True)
class RoundSettlement:
    """Overall settlement for an entire round (including potential splits and insurance)."""

    hands: list[HandSettlement]
    dealer_summary: str
    dealer_value: int
    dealer_bust: bool
    insurance_bet: float = 0.0
    insurance_profit: float = 0.0

    @property
    def total_wagered(self) -> float:
        """Total capital placed at risk during the round (all hands + insurance)."""
        return sum(h.wager for h in self.hands) + self.insurance_bet

    @property
    def total_profit(self) -> float:
        """Net monetary gain or loss across all hands and insurance."""
        return sum(h.profit for h in self.hands) + self.insurance_profit

    @property
    def net_profit(self) -> float:
        """Alias for total_profit."""
        return self.total_profit

    @property
    def hand_settlements(self) -> list[HandSettlement]:
        """Alias for hands."""
        return self.hands

    @property
    def primary_result(self) -> RoundResult:
        """Representative result for single-hand rounds or first hand."""
        if not self.hands:
            return RoundResult.PUSH
        return self.hands[0].result
