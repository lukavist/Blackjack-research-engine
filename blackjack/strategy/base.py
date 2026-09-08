"""Strategy interface and decision types for Blackjack."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from blackjack.core.actions import Action
from blackjack.core.card import Card
from blackjack.core.hand import Hand
from blackjack.core.rules import BlackjackRules


@dataclass(frozen=True, slots=True)
class CountState:
    """Snapshot of card counting metrics at the moment of a decision."""

    running_count: int
    true_count: float
    estimated_decks_remaining: float
    cards_seen: int


class Strategy(ABC):
    """Abstract base class for all Blackjack playing strategies."""

    @abstractmethod
    def decide(
        self,
        hand: Hand,
        dealer_upcard: Card,
        valid_actions: list[Action],
        rules: BlackjackRules,
        count_state: CountState | None = None,
    ) -> Action:
        """Choose an action (HIT, STAND, DOUBLE, SPLIT, SURRENDER) for the player's active hand.

        Args:
            hand: The active player hand.
            dealer_upcard: The dealer's face-up card.
            valid_actions: The legal actions available in the current game state.
            rules: The active table rules.
            count_state: Optional snapshot of running and true counts.

        Returns:
            The chosen Action, which must be contained in valid_actions.
        """
        pass

    def decide_insurance(
        self,
        rules: BlackjackRules,
        count_state: CountState | None = None,
    ) -> bool:
        """Decide whether to accept insurance when the dealer shows an Ace.

        By default, basic strategy players never take insurance (negative expectation).
        Count-based strategies may take insurance at high positive true counts (e.g. TC >= +3).
        """
        return False
