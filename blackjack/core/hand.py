"""Hand representation with robust Ace evaluation, state tracking, and soft/hard logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from blackjack.core.actions import Action
from blackjack.core.card import Card, Rank


class HandStatus(str, Enum):
    """Lifecycle status of a blackjack hand."""

    ACTIVE = "ACTIVE"
    STOOD = "STOOD"
    DOUBLED = "DOUBLED"
    BUSTED = "BUSTED"
    BLACKJACK = "BLACKJACK"
    SURRENDERED = "SURRENDERED"


@dataclass
class Hand:
    """A blackjack hand containing cards, wager, dynamic evaluation, and action history."""

    cards: list[Card] = field(default_factory=list)
    bet: float = 0.0
    status: HandStatus = HandStatus.ACTIVE
    actions: list[Action] = field(default_factory=list)
    is_from_split: bool = False
    is_split_aces: bool = False

    def add_card(self, card: Card) -> None:
        """Add a card to this hand and refresh status."""
        if not isinstance(card, Card):
            raise TypeError(f"Expected Card instance, got {type(card).__name__}")
        self.cards.append(card)
        if self.is_bust:
            self.status = HandStatus.BUSTED

    @property
    def value(self) -> int:
        """Calculate current point total, reducing Aces from 11 to 1 to avoid busting."""
        total = sum(c.value for c in self.cards)
        ace_count = sum(1 for c in self.cards if c.is_ace)

        # Each Ace is initially counted as 11 in Card.value.
        # If total exceeds 21 and we have Aces, convert Ace from 11 to 1 (reducing total by 10)
        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1

        return total

    @property
    def is_soft(self) -> bool:
        """Return True if and only if at least one Ace is currently counted as 11.

        Softness means a 10-point cushion exists: drawing a 10 will not bust the hand.
        """
        raw_total = sum(c.value for c in self.cards)
        ace_count = sum(1 for c in self.cards if c.is_ace)

        if ace_count == 0 or raw_total > 21:
            # Check how many aces remain counted as 11
            adjusted = raw_total
            soft_aces = ace_count
            while adjusted > 21 and soft_aces > 0:
                adjusted -= 10
                soft_aces -= 1
            return soft_aces > 0

        return ace_count > 0

    @property
    def is_hard(self) -> bool:
        """Return True if hand is hard (no Ace or all Aces are counted as 1)."""
        return not self.is_soft

    @property
    def is_bust(self) -> bool:
        """Return True if total point value exceeds 21."""
        return self.value > 21

    @property
    def is_blackjack(self) -> bool:
        """Return True if initial 2 cards total 21 (natural blackjack).

        By standard casino rules, hands resulting from split are treated as 21, not blackjack.
        """
        if self.is_from_split:
            return False
        return len(self.cards) == 2 and self.value == 21

    @property
    def is_pair(self) -> bool:
        """Return True if exactly 2 cards have the identical rank (e.g. 8-8, A-A)."""
        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank

    @property
    def is_ten_pair(self) -> bool:
        """Return True if exactly 2 cards both have value 10 (e.g. K-Q, 10-J)."""
        return len(self.cards) == 2 and self.cards[0].is_ten_value and self.cards[1].is_ten_value

    @property
    def can_split(self) -> bool:
        """Whether the hand is currently eligible for splitting (2 cards of equal rank/value)."""
        return len(self.cards) == 2 and (self.is_pair or self.is_ten_pair)

    @property
    def can_double(self) -> bool:
        """Whether the hand is eligible for double down (exactly 2 cards and active)."""
        return len(self.cards) == 2 and self.status == HandStatus.ACTIVE

    def record_action(self, action: Action) -> None:
        """Record an action in the hand's historical log."""
        self.actions.append(action)

    def __len__(self) -> int:
        return len(self.cards)

    def __str__(self) -> str:
        cards_repr = ", ".join(str(c) for c in self.cards)
        desc = "soft" if self.is_soft else "hard"
        bj = " [BLACKJACK]" if self.is_blackjack else ""
        bust = " [BUST]" if self.is_bust else ""
        return f"[{cards_repr}] = {self.value} ({desc}){bj}{bust}"

    def __repr__(self) -> str:
        return f"Hand(cards={self.cards!r}, bet={self.bet}, status={self.status.value}, value={self.value})"
