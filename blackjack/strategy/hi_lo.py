"""Hi-Lo Card Counting system with running count and true count calculation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from blackjack.core.card import Card, Rank
from blackjack.strategy.base import CountState


class HiLoCounter:
    """Standard Hi-Lo card counting implementation.

    Point values:
        2, 3, 4, 5, 6     -> +1
        7, 8, 9           ->  0
        10, J, Q, K, A    -> -1

    Properties:
        - Balanced system (sum over 52-card deck == 0)
        - Running Count (RC): algebraic sum of observed card values.
        - True Count (TC): RC divided by estimated remaining decks.
    """

    def __init__(self, num_decks: int = 6) -> None:
        self.num_decks = num_decks
        self.total_cards = num_decks * 52
        self.running_count: int = 0
        self.cards_seen: int = 0

    def reset(self) -> None:
        """Reset the counter (called upon shoe reshuffle)."""
        self.running_count = 0
        self.cards_seen = 0

    @staticmethod
    def card_value(card: Card) -> int:
        """Returns the Hi-Lo tag for a single card."""
        rank = card.rank
        if rank in (Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX):
            return 1
        if rank in (Rank.SEVEN, Rank.EIGHT, Rank.NINE):
            return 0
        return -1  # 10, J, Q, K, A

    def observe(self, card: Card, is_hole_card: bool = False) -> None:
        """Observe an exposed card and update count metrics."""
        self.running_count += self.card_value(card)
        self.cards_seen += 1

    def observe_cards(self, cards: list[Card]) -> None:
        """Observe a batch of exposed cards."""
        for card in cards:
            self.observe(card)

    def estimated_decks_remaining(self) -> float:
        """Computes remaining decks based on observed cards, bounded to at least 0.5 deck."""
        cards_left = max(self.total_cards - self.cards_seen, 0)
        decks = cards_left / 52.0
        return max(decks, 0.5)

    def true_count(self, decks_remaining: float | None = None) -> float:
        """Calculates True Count = Running Count / Remaining Decks.

        Args:
            decks_remaining: Optional explicit remaining deck estimate.
                             If omitted, calculated automatically from cards_seen.
        """
        dr = decks_remaining if decks_remaining is not None else self.estimated_decks_remaining()
        dr = max(dr, 0.5)
        return self.running_count / dr

    def get_state(self, decks_remaining: float | None = None) -> CountState:
        """Produces an immutable snapshot of the current count state."""
        dr = decks_remaining if decks_remaining is not None else self.estimated_decks_remaining()
        tc = self.true_count(dr)
        return CountState(
            running_count=self.running_count,
            true_count=tc,
            estimated_decks_remaining=dr,
            cards_seen=self.cards_seen,
        )

    def as_observer_callback(self) -> Callable[[Card, bool], None]:
        """Returns a callback compatible with Game.add_observer.

        The Game only invokes this callback when cards are legitimately revealed,
        ensuring strict prevention of hole-card leakage.
        """
        def _callback(card: Card, is_hole_card: bool) -> None:
            self.observe(card, is_hole_card)

        return _callback
