"""Representation of a standard playing card and blackjack point evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Rank(str, Enum):
    """Card ranks recognized in standard 52-card blackjack decks."""

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

    @property
    def blackjack_value(self) -> int:
        """Return the default blackjack numerical point value.

        Ace defaults to 11. Hand evaluation handles soft reduction to 1.
        """
        if self in (Rank.JACK, Rank.QUEEN, Rank.KING, Rank.TEN):
            return 10
        if self == Rank.ACE:
            return 11
        return int(self.value)

    @classmethod
    def from_str(cls, rank_str: str) -> Rank:
        """Parse rank from standard string representations (e.g. '2', '10', 'A', 'K')."""
        normalized = rank_str.strip().upper()
        for r in cls:
            if r.value == normalized:
                return r
        if normalized in ("T", "10"):
            return cls.TEN
        raise ValueError(f"Invalid rank string: '{rank_str}'. Expected one of {[r.value for r in cls]}")


class Suit(str, Enum):
    """Playing card suits."""

    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"

    @classmethod
    def from_str(cls, suit_str: str) -> Suit:
        """Parse suit from common symbols or letters (e.g. 'S', 'H', 'D', 'C')."""
        mapping = {
            "S": cls.SPADES,
            "H": cls.HEARTS,
            "D": cls.DIAMONDS,
            "C": cls.CLUBS,
            "♠": cls.SPADES,
            "♥": cls.HEARTS,
            "♦": cls.DIAMONDS,
            "♣": cls.CLUBS,
            "SPADES": cls.SPADES,
            "HEARTS": cls.HEARTS,
            "DIAMONDS": cls.DIAMONDS,
            "CLUBS": cls.CLUBS,
        }
        normalized = suit_str.strip().upper()
        if normalized in mapping:
            return mapping[normalized]
        raise ValueError(f"Invalid suit: '{suit_str}'")


@dataclass(frozen=True, slots=True)
class Card:
    """Immutable playing card with rank, optional suit, and blackjack value."""

    rank: Rank
    suit: Suit = Suit.SPADES

    @property
    def value(self) -> int:
        """Default blackjack value of this card (2-10, 10 for J/Q/K, 11 for Ace)."""
        return self.rank.blackjack_value

    @property
    def blackjack_value(self) -> int:
        """Alias for value."""
        return self.rank.blackjack_value

    @property
    def is_ace(self) -> bool:
        """Whether this card is an Ace."""
        return self.rank == Rank.ACE

    @property
    def is_ten_value(self) -> bool:
        """Whether this card has a point value of 10 (10, J, Q, K)."""
        return self.value == 10

    @classmethod
    def from_string(cls, card_str: str) -> Card:
        """Create a Card from strings like 'Ah', '10s', 'Kd', '7c', or just 'A', '10'."""
        cleaned = card_str.strip()
        if not cleaned:
            raise ValueError("Card string cannot be empty")

        if len(cleaned) == 1:
            return cls(rank=Rank.from_str(cleaned), suit=Suit.SPADES)

        # Check if last char is a suit letter
        potential_suit = cleaned[-1]
        potential_rank = cleaned[:-1]
        try:
            suit = Suit.from_str(potential_suit)
            rank = Rank.from_str(potential_rank)
            return cls(rank=rank, suit=suit)
        except ValueError:
            # Maybe the whole string is the rank
            rank = Rank.from_str(cleaned)
            return cls(rank=rank, suit=Suit.SPADES)

    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"

    def __repr__(self) -> str:
        return f"Card({self.rank.value}{self.suit.value})"
