"""Concrete betting strategies: Flat betting, count-based spread, and Kelly Criterion."""

from __future__ import annotations

import math
from typing import Mapping

from blackjack.betting.base import BettingStrategy
from blackjack.strategy.base import CountState


class FlatBetting(BettingStrategy):
    """Constant wager sizing regardless of card count or bankroll."""

    def __init__(self, bet_amount: float = 10.0) -> None:
        if bet_amount <= 0:
            raise ValueError(f"bet_amount must be positive, got {bet_amount}")
        self.bet_amount = float(bet_amount)

    def get_bet(self, count_state: CountState | None = None, current_bankroll: float | None = None) -> float:
        if current_bankroll is not None and current_bankroll < self.bet_amount:
            return max(0.0, current_bankroll)
        return self.bet_amount


class SpreadBetting(BettingStrategy):
    """True Count-based spread betting strategy.

    Configurable spread table mapping floored True Count to multiplier of base unit:
    Default 1-to-8 spread:
        TC <= 1 -> 1 unit
        TC == 2 -> 2 units
        TC == 3 -> 4 units
        TC >= 4 -> 8 units
    """

    def __init__(
        self,
        base_unit: float = 10.0,
        spread: Mapping[int, float] | None = None,
        min_bet: float | None = None,
        max_bet: float | None = None,
    ) -> None:
        if base_unit <= 0:
            raise ValueError(f"base_unit must be positive, got {base_unit}")
        self.base_unit = float(base_unit)
        self.min_bet = float(min_bet) if min_bet is not None else base_unit
        self.max_bet = float(max_bet) if max_bet is not None else (base_unit * 16.0)

        # Default standard 1-to-8 spread
        if spread is None:
            self.spread: dict[int, float] = {
                1: 1.0,
                2: 2.0,
                3: 4.0,
                4: 8.0,
            }
        else:
            self.spread = dict(spread)

    def get_bet(self, count_state: CountState | None = None, current_bankroll: float | None = None) -> float:
        if count_state is None:
            bet = self.min_bet
        else:
            # Standard casino practice: floor the true count
            tc_int = int(math.floor(count_state.true_count))
            sorted_keys = sorted(self.spread.keys())

            if tc_int <= sorted_keys[0]:
                multiplier = self.spread[sorted_keys[0]]
            elif tc_int >= sorted_keys[-1]:
                multiplier = self.spread[sorted_keys[-1]]
            else:
                # Direct match or highest key <= tc_int
                applicable_keys = [k for k in sorted_keys if k <= tc_int]
                best_key = applicable_keys[-1] if applicable_keys else sorted_keys[0]
                multiplier = self.spread[best_key]

            bet = self.base_unit * multiplier

        # Clamp between min_bet and max_bet
        bet = max(self.min_bet, min(bet, self.max_bet))

        # Check bankroll limits if provided
        if current_bankroll is not None and current_bankroll < bet:
            return max(0.0, current_bankroll)

        return round(bet, 2)


class KellyBetting(BettingStrategy):
    """Fractional Kelly Criterion betting based on card counting edge.

    Advantage estimation:
        Player Edge ≈ base_advantage + (True Count * 0.005)
    Optimal Kelly fraction:
        wager = bankroll * (Edge / Variance) * fraction
    """

    def __init__(
        self,
        min_bet: float = 10.0,
        max_bet: float = 200.0,
        fraction: float = 0.5,  # Half-Kelly for risk mitigation
        base_advantage: float = -0.005,  # Base house edge approx ~0.5% under standard rules
        advantage_per_tc: float = 0.005,  # Each TC point yields ~0.5% edge shift
        variance: float = 1.32,  # Typical Blackjack single hand variance
    ) -> None:
        self.min_bet = float(min_bet)
        self.max_bet = float(max_bet)
        self.fraction = float(fraction)
        self.base_advantage = float(base_advantage)
        self.advantage_per_tc = float(advantage_per_tc)
        self.variance = float(variance)

    def get_bet(self, count_state: CountState | None = None, current_bankroll: float | None = None) -> float:
        if current_bankroll is None or current_bankroll <= 0:
            return self.min_bet

        tc = count_state.true_count if count_state is not None else 0.0
        edge = self.base_advantage + (tc * self.advantage_per_tc)

        if edge <= 0:
            # House has the edge: bet table minimum
            return self.min_bet

        # Fractional Kelly sizing
        kelly_fraction = (edge / self.variance) * self.fraction
        recommended = current_bankroll * kelly_fraction
        clamped = max(self.min_bet, min(recommended, self.max_bet))

        if current_bankroll < clamped:
            return max(0.0, current_bankroll)

        return round(clamped, 2)
