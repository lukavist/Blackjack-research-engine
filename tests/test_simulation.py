"""Unit tests for Monte Carlo simulation engine."""

import unittest

from blackjack.betting.strategies import FlatBetting, SpreadBetting
from blackjack.core.rules import BlackjackRules
from blackjack.simulation.runner import SimulationRunner
from blackjack.strategy.basic_strategy import BasicStrategy
from blackjack.strategy.deviations import HiLoDeviationStrategy
from blackjack.strategy.hi_lo import HiLoCounter


class TestSimulation(unittest.TestCase):
    """Verifies simulation runner execution, statistics tracking, and reproducibility."""

    def test_reproducible_simulation_run(self) -> None:
        """Identical seeds must yield identical statistics and trajectories."""
        rules = BlackjackRules.standard_vegas_s17()
        runner1 = SimulationRunner(
            rules=rules,
            strategy=BasicStrategy(),
            betting_strategy=FlatBetting(10.0),
            starting_bankroll=10_000.0,
            seed=42,
        )
        runner2 = SimulationRunner(
            rules=rules,
            strategy=BasicStrategy(),
            betting_strategy=FlatBetting(10.0),
            starting_bankroll=10_000.0,
            seed=42,
        )

        stats1 = runner1.run(num_rounds=500)
        stats2 = runner2.run(num_rounds=500)

        self.assertEqual(stats1.rounds_played, stats2.rounds_played)
        self.assertEqual(stats1.net_profit, stats2.net_profit)
        self.assertEqual(stats1.wins, stats2.wins)
        self.assertEqual(stats1.losses, stats2.losses)
        self.assertEqual(stats1.pushes, stats2.pushes)
        self.assertEqual(stats1.total_wagered, stats2.total_wagered)

    def test_hi_lo_counting_simulation(self) -> None:
        """Simulation with HiLoCounter and HiLoDeviationStrategy executes without errors."""
        rules = BlackjackRules.standard_vegas_s17()
        counter = HiLoCounter(num_decks=rules.num_decks)
        runner = SimulationRunner(
            rules=rules,
            strategy=HiLoDeviationStrategy(),
            betting_strategy=SpreadBetting(base_unit=10.0),
            counter=counter,
            starting_bankroll=10_000.0,
            seed=101,
        )

        stats = runner.run(num_rounds=1_000)
        self.assertEqual(stats.rounds_played, 1_000)
        self.assertGreater(stats.hands_played, 1_000)
        self.assertGreater(stats.total_wagered, 10_000.0)
        self.assertGreater(len(stats.trajectory), 1)


if __name__ == "__main__":
    unittest.main()
