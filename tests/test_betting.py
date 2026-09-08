"""Unit tests for betting strategies."""

import unittest

from blackjack.betting.strategies import FlatBetting, KellyBetting, SpreadBetting
from blackjack.strategy.base import CountState


class TestBetting(unittest.TestCase):
    """Verifies bankroll management and count-based wager sizing."""

    def test_flat_betting(self) -> None:
        """Flat betting always returns configured base bet, or bankroll if insufficient."""
        flat = FlatBetting(bet_amount=25.0)
        self.assertEqual(flat.get_bet(), 25.0)
        self.assertEqual(flat.get_bet(current_bankroll=1000.0), 25.0)
        # Bankroll limitation
        self.assertEqual(flat.get_bet(current_bankroll=15.0), 15.0)

    def test_spread_betting_scale(self) -> None:
        """Spread betting scales bets across True Count tiers (1-to-8 spread)."""
        spread = SpreadBetting(base_unit=10.0)

        # TC <= 1 -> 1 unit ($10)
        state_neg = CountState(running_count=-4, true_count=-1.5, estimated_decks_remaining=2.5, cards_seen=182)
        state_one = CountState(running_count=2, true_count=1.0, estimated_decks_remaining=2.0, cards_seen=208)
        self.assertEqual(spread.get_bet(state_neg), 10.0)
        self.assertEqual(spread.get_bet(state_one), 10.0)

        # TC == 2 -> 2 units ($20)
        state_two = CountState(running_count=4, true_count=2.0, estimated_decks_remaining=2.0, cards_seen=208)
        self.assertEqual(spread.get_bet(state_two), 20.0)

        # TC == 3 -> 4 units ($40)
        state_three = CountState(running_count=6, true_count=3.0, estimated_decks_remaining=2.0, cards_seen=208)
        self.assertEqual(spread.get_bet(state_three), 40.0)

        # TC >= 4 -> 8 units ($80)
        state_four = CountState(running_count=8, true_count=4.2, estimated_decks_remaining=2.0, cards_seen=208)
        self.assertEqual(spread.get_bet(state_four), 80.0)

    def test_kelly_betting(self) -> None:
        """Kelly criterion bets table minimum when edge <= 0, and scales with edge & bankroll."""
        kelly = KellyBetting(min_bet=10.0, max_bet=250.0, fraction=0.5)

        # Negative count -> house edge -> min bet
        state_neg = CountState(running_count=-4, true_count=-2.0, estimated_decks_remaining=2.0, cards_seen=208)
        self.assertEqual(kelly.get_bet(state_neg, current_bankroll=5000.0), 10.0)

        # High positive count -> edge > 0 -> sized proportionally to bankroll
        # edge = -0.005 + (4 * 0.005) = +0.015 (1.5% edge)
        # kelly = (0.015 / 1.32) * 0.5 ≈ 0.00568
        # on 10,000 bankroll ≈ $56.82
        state_pos = CountState(running_count=8, true_count=4.0, estimated_decks_remaining=2.0, cards_seen=208)
        bet = kelly.get_bet(state_pos, current_bankroll=10000.0)
        self.assertGreater(bet, 30.0)
        self.assertLess(bet, 100.0)


if __name__ == "__main__":
    unittest.main()
