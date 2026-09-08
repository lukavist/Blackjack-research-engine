"""Betting strategy interfaces and algorithms."""

from __future__ import annotations

from abc import ABC, abstractmethod

from blackjack.strategy.base import CountState


class BettingStrategy(ABC):
    """Abstract base class for Blackjack betting strategies."""

    @abstractmethod
    def get_bet(self, count_state: CountState | None = None, current_bankroll: float | None = None) -> float:
        """Calculate the wager amount for the next round.

        Args:
            count_state: Current True Count / Running Count state.
            current_bankroll: Optional player bankroll to constrain max bet.

        Returns:
            The dollar amount to wager (must be >= minimum table bet).
        """
        pass
