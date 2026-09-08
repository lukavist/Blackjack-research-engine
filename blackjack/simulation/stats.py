"""Statistical aggregation and performance metrics for Blackjack simulations."""

from __future__ import annotations

from dataclasses import dataclass, field
import math


@dataclass
class SimulationStats:
    """Aggregates round outcomes and financial performance metrics."""

    rounds_played: int = 0
    hands_played: int = 0
    total_wagered: float = 0.0
    net_profit: float = 0.0
    starting_bankroll: float = 0.0
    final_bankroll: float = 0.0

    wins: int = 0
    losses: int = 0
    pushes: int = 0
    blackjacks: int = 0
    surrenders: int = 0
    doubles: int = 0
    splits: int = 0
    insurance_taken: int = 0
    insurance_won: int = 0

    max_bankroll: float = 0.0
    min_bankroll: float = 0.0
    max_drawdown: float = 0.0
    peak_to_trough_drawdown: float = 0.0

    # Downsampled trajectory snapshots for visualization (round, bankroll)
    trajectory: list[tuple[int, float]] = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        """Percentage of decisive (non-push) hands won by the player."""
        decisive = self.wins + self.losses
        if decisive == 0:
            return 0.0
        return (self.wins / decisive) * 100.0

    @property
    def ev_per_hand(self) -> float:
        """Expected net profit per round played."""
        if self.rounds_played == 0:
            return 0.0
        return self.net_profit / self.rounds_played

    @property
    def roi_percent(self) -> float:
        """Return on Investment (net profit / total amount wagered * 100)."""
        if self.total_wagered == 0:
            return 0.0
        return (self.net_profit / self.total_wagered) * 100.0

    @property
    def average_bet(self) -> float:
        """Average initial wager per round."""
        if self.rounds_played == 0:
            return 0.0
        return self.total_wagered / self.rounds_played
