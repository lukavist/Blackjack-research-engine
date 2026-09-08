"""Configurable Blackjack table rules and standard presets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BlackjackRules:
    """Table rules configuration governing player options, dealer logic, and payouts."""

    num_decks: int = 6
    penetration: float = 0.75
    dealer_hits_soft_17: bool = False  # False = S17 (dealer stands on soft 17), True = H17
    blackjack_payout: float = 1.5      # 3:2 payout = 1.5; 6:5 payout = 1.2
    double_allowed: bool = True        # Double allowed on any initial 2 cards
    double_after_split: bool = True    # DAS
    late_surrender: bool = True        # Late surrender allowed
    surrender_against_ace: bool = False  # By default surrender unavailable against dealer Ace
    insurance_allowed: bool = True     # Insurance offered when dealer shows Ace
    insurance_payout: float = 2.0      # Standard 2:1 insurance payout
    max_splits: int = 3                # Max split times (e.g. 3 splits = up to 4 hands)
    split_aces_one_card: bool = True   # Split aces receive exactly one card and stand
    resplit_aces: bool = False         # Re-splitting aces allowed
    min_bet: float = 1.0
    max_bet: float = 10_000.0

    def __post_init__(self) -> None:
        if self.num_decks < 1:
            raise ValueError(f"num_decks must be >= 1, got {self.num_decks}")
        if not (0.1 <= self.penetration <= 0.95):
            raise ValueError(f"penetration must be between 0.1 and 0.95, got {self.penetration}")
        if self.blackjack_payout <= 0:
            raise ValueError(f"blackjack_payout must be > 0, got {self.blackjack_payout}")
        if self.min_bet <= 0:
            raise ValueError(f"min_bet must be > 0, got {self.min_bet}")
        if self.max_bet < self.min_bet:
            raise ValueError(f"max_bet ({self.max_bet}) cannot be less than min_bet ({self.min_bet})")

    @classmethod
    def standard_vegas_s17(cls, num_decks: int = 6, penetration: float = 0.75) -> BlackjackRules:
        """Standard 6-deck Vegas Strip rules: S17, 3:2 BJ, DAS, Late Surrender."""
        return cls(
            num_decks=num_decks,
            penetration=penetration,
            dealer_hits_soft_17=False,
            blackjack_payout=1.5,
            double_allowed=True,
            double_after_split=True,
            late_surrender=True,
            surrender_against_ace=False,
            insurance_allowed=True,
        )

    @classmethod
    def standard_h17(cls, num_decks: int = 6, penetration: float = 0.75) -> BlackjackRules:
        """Standard H17 rules: Dealer hits soft 17, 3:2 BJ, DAS, Late Surrender."""
        return cls(
            num_decks=num_decks,
            penetration=penetration,
            dealer_hits_soft_17=True,
            blackjack_payout=1.5,
            double_allowed=True,
            double_after_split=True,
            late_surrender=True,
            surrender_against_ace=False,
            insurance_allowed=True,
        )

    @classmethod
    def single_deck_classic(cls) -> BlackjackRules:
        """Single-deck classic: S17, 3:2 BJ, no surrender, DAS disabled, 65% penetration."""
        return cls(
            num_decks=1,
            penetration=0.65,
            dealer_hits_soft_17=False,
            blackjack_payout=1.5,
            double_allowed=True,
            double_after_split=False,
            late_surrender=False,
            surrender_against_ace=False,
            insurance_allowed=True,
        )
