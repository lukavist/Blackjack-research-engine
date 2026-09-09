"""Multi-deck Shoe implementation with cut-card penetration tracking and deterministic seeding."""

from __future__ import annotations

import random
from typing import Sequence

from blackjack.core.card import Card, Rank, Suit


class Shoe:
    """Multi-deck shoe that deals cards continuously until reaching penetration depth."""

    def __init__(
        self,
        num_decks: int = 6,
        penetration: float = 0.75,
        seed: int | None = None,
    ) -> None:
        if num_decks < 1:
            raise ValueError(f"num_decks must be >= 1, got {num_decks}")
        if not (0.1 <= penetration <= 0.99):
            raise ValueError(f"penetration must be between 0.1 and 0.99, got {penetration}")

        self.num_decks: int = num_decks
        self.penetration: float = penetration
        self.seed: int | None = seed
        self._rng: random.Random = random.Random(seed)

        self._all_cards: list[Card] = []
        self._dealt_cards: list[Card] = []
        self._cards: list[Card] = []  # active deck stack, pop() deals from end

        self.total_initial_cards: int = self.num_decks * 52
        self.cut_card_threshold: int = int(self.total_initial_cards * self.penetration)
        self.shuffle_count: int = 0
        self.is_stacked: bool = False

        self.shuffle()

    def _build_standard_decks(self) -> list[Card]:
        """Generate num_decks * 52 standard playing cards."""
        cards: list[Card] = []
        for _ in range(self.num_decks):
            for suit in Suit:
                for rank in Rank:
                    cards.append(Card(rank=rank, suit=suit))
        return cards

    def shuffle(self) -> None:
        """Collect all cards, reset deal pointers, and shuffle using deterministic RNG."""
        self._cards = self._build_standard_decks()
        self._rng.shuffle(self._cards)
        self._dealt_cards.clear()
        self.shuffle_count += 1

    def deal(self) -> Card:
        """Deal one card from the shoe.

        Raises:
            RuntimeError: If the shoe is completely empty.
        """
        if not self._cards:
            # Cards are totally exhausted. The Shoe never auto-reshuffles mid-round
            # (that would corrupt card-counting state), so callers must check
            # `needs_reshuffle` between rounds and call `shuffle()` themselves.
            raise RuntimeError("Shoe is completely empty. Reshuffle required.")

        card = self._cards.pop()
        self._dealt_cards.append(card)
        return card

    @property
    def cards(self) -> list[Card]:
        """Read-only copy of cards remaining in the shoe."""
        return list(self._cards)

    @property
    def cards_remaining(self) -> int:
        """Number of cards remaining in the shoe ready to be dealt."""
        return len(self._cards)

    @property
    def cards_dealt(self) -> int:
        """Total count of cards dealt from this shoe since last shuffle."""
        return len(self._dealt_cards)

    @property
    def total_cards(self) -> int:
        """Total cards in a full fresh shoe."""
        return self.total_initial_cards

    @property
    def current_penetration(self) -> float:
        """Proportion of the shoe that has been dealt (0.0 to 1.0)."""
        if self.total_initial_cards == 0:
            return 0.0
        return self.cards_dealt / self.total_initial_cards

    @property
    def needs_reshuffle(self) -> bool:
        """True if the number of cards dealt has reached or passed the penetration cut card."""
        if self.is_stacked:
            return False
        return self.cards_dealt >= self.cut_card_threshold or (self.cards_remaining < 15 and self.total_cards > 52)

    @property
    def estimated_decks_remaining(self) -> float:
        """Estimated number of full 52-card decks remaining in the shoe (used for true count)."""
        return max(self.cards_remaining / 52.0, 0.5)

    @classmethod
    def from_cards(
        cls,
        cards: Sequence[Card],
        penetration: float = 0.75,
        seed: int | None = None,
    ) -> Shoe:
        """Create a mock / stacked shoe from an explicit sequence of cards (for testing).

        Cards are dealt in the order passed: first element is dealt first.
        """
        instance = cls.__new__(cls)
        instance.num_decks = max(1, len(cards) // 52)
        instance.penetration = penetration
        instance.seed = seed
        instance._rng = random.Random(seed)
        instance.total_initial_cards = len(cards)
        instance.cut_card_threshold = int(instance.total_initial_cards * penetration)
        instance.shuffle_count = 1
        instance.is_stacked = True
        instance._dealt_cards = []
        # Reversing so pop() yields elements in original list order:
        instance._cards = list(reversed(cards))
        return instance

    def peek_next(self) -> Card | None:
        """Inspect the next card without dealing it (used strictly for test harnesses)."""
        if not self._cards:
            return None
        return self._cards[-1]

    def __len__(self) -> int:
        return len(self._cards)

    def __repr__(self) -> str:
        return (
            f"Shoe(num_decks={self.num_decks}, remaining={self.cards_remaining}/{self.total_initial_cards}, "
            f"penetration={self.current_penetration:.1%}, reshuffle={self.needs_reshuffle})"
        )
