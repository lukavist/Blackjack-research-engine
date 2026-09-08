"""Unit tests for Basic Strategy and Illustrious 18 Deviations."""

import unittest

from blackjack.core.actions import Action
from blackjack.core.card import Card, Rank, Suit
from blackjack.core.hand import Hand
from blackjack.core.rules import BlackjackRules
from blackjack.strategy.base import CountState
from blackjack.strategy.basic_strategy import BasicStrategy
from blackjack.strategy.deviations import HiLoDeviationStrategy


class TestStrategy(unittest.TestCase):
    """Verifies mathematically sound decision-making under Basic Strategy and Deviations."""

    def setUp(self) -> None:
        self.bs = BasicStrategy()
        self.dev = HiLoDeviationStrategy()
        self.rules_s17 = BlackjackRules.standard_vegas_s17()
        self.rules_h17 = BlackjackRules.standard_h17()

    def _hand(self, *ranks: Rank) -> Hand:
        hand = Hand()
        for r in ranks:
            hand.add_card(Card(rank=r, suit=Suit.SPADES))
        return hand

    def _upcard(self, rank: Rank) -> Card:
        return Card(rank=rank, suit=Suit.HEARTS)

    # --- BASIC STRATEGY: PAIR SPLITTING ---

    def test_always_split_aces_and_eights(self) -> None:
        """A,A and 8,8 must always be split vs any dealer upcard."""
        for up in [Rank.TWO, Rank.SIX, Rank.SEVEN, Rank.TEN, Rank.ACE]:
            aces = self._hand(Rank.ACE, Rank.ACE)
            eights = self._hand(Rank.EIGHT, Rank.EIGHT)
            upcard = self._upcard(up)
            valid = [Action.HIT, Action.STAND, Action.SPLIT]

            self.assertEqual(self.bs.decide(aces, upcard, valid, self.rules_s17), Action.SPLIT)
            self.assertEqual(self.bs.decide(eights, upcard, valid, self.rules_s17), Action.SPLIT)

    def test_never_split_tens_or_fives(self) -> None:
        """Tens (or face pairs) and 5,5 must never be split in standard basic strategy."""
        tens = self._hand(Rank.TEN, Rank.KING)
        fives = self._hand(Rank.FIVE, Rank.FIVE)
        upcard = self._upcard(Rank.SIX)
        valid = [Action.HIT, Action.STAND, Action.DOUBLE, Action.SPLIT]

        self.assertEqual(self.bs.decide(tens, upcard, valid, self.rules_s17), Action.STAND)
        # 5,5 vs 6 should double
        self.assertEqual(self.bs.decide(fives, upcard, valid, self.rules_s17), Action.DOUBLE)

    def test_nines_split_vs_two_to_six_and_eight_nine(self) -> None:
        """9,9 splits vs 2-6, 8, 9; stands vs 7, 10, A."""
        nines = self._hand(Rank.NINE, Rank.NINE)
        valid = [Action.HIT, Action.STAND, Action.SPLIT]

        # Splits
        self.assertEqual(self.bs.decide(nines, self._upcard(Rank.FIVE), valid, self.rules_s17), Action.SPLIT)
        self.assertEqual(self.bs.decide(nines, self._upcard(Rank.EIGHT), valid, self.rules_s17), Action.SPLIT)
        self.assertEqual(self.bs.decide(nines, self._upcard(Rank.NINE), valid, self.rules_s17), Action.SPLIT)

        # Stands
        self.assertEqual(self.bs.decide(nines, self._upcard(Rank.SEVEN), valid, self.rules_s17), Action.STAND)
        self.assertEqual(self.bs.decide(nines, self._upcard(Rank.TEN), valid, self.rules_s17), Action.STAND)
        self.assertEqual(self.bs.decide(nines, self._upcard(Rank.ACE), valid, self.rules_s17), Action.STAND)

    # --- BASIC STRATEGY: SOFT TOTALS ---

    def test_soft_eighteen_decisions(self) -> None:
        """A,7 (Soft 18): Double vs 3-6, Stand vs 2, 7, 8, Hit vs 9, 10, A."""
        soft18 = self._hand(Rank.ACE, Rank.SEVEN)
        valid_with_double = [Action.HIT, Action.STAND, Action.DOUBLE]
        valid_no_double = [Action.HIT, Action.STAND]

        # Double vs 5
        self.assertEqual(self.bs.decide(soft18, self._upcard(Rank.FIVE), valid_with_double, self.rules_s17), Action.DOUBLE)
        # Fallback to Stand vs 5 if double not allowed
        self.assertEqual(self.bs.decide(soft18, self._upcard(Rank.FIVE), valid_no_double, self.rules_s17), Action.STAND)

        # Stand vs 7
        self.assertEqual(self.bs.decide(soft18, self._upcard(Rank.SEVEN), valid_with_double, self.rules_s17), Action.STAND)

        # Hit vs 10
        self.assertEqual(self.bs.decide(soft18, self._upcard(Rank.TEN), valid_with_double, self.rules_s17), Action.HIT)

    def test_soft_nineteen_h17_vs_s17(self) -> None:
        """A,8 (Soft 19) stands vs 6 in S17, but doubles vs 6 in H17."""
        soft19 = self._hand(Rank.ACE, Rank.EIGHT)
        upcard = self._upcard(Rank.SIX)
        valid = [Action.HIT, Action.STAND, Action.DOUBLE]

        self.assertEqual(self.bs.decide(soft19, upcard, valid, self.rules_s17), Action.STAND)
        self.assertEqual(self.bs.decide(soft19, upcard, valid, self.rules_h17), Action.DOUBLE)

    # --- BASIC STRATEGY: HARD TOTALS ---

    def test_hard_seventeen_plus_stands(self) -> None:
        """Hard 17-20 stands vs any dealer upcard."""
        for rank in [Rank.TEN, Rank.ACE, Rank.SIX]:
            upcard = self._upcard(rank)
            hand17 = self._hand(Rank.TEN, Rank.SEVEN)
            valid = [Action.HIT, Action.STAND]
            self.assertEqual(self.bs.decide(hand17, upcard, valid, self.rules_s17), Action.STAND)

    def test_hard_eleven_always_doubles(self) -> None:
        """Hard 11 doubles vs 2-10 in S17, or hits if double disallowed."""
        hand11 = self._hand(Rank.SIX, Rank.FIVE)
        upcard = self._upcard(Rank.SIX)

        self.assertEqual(self.bs.decide(hand11, upcard, [Action.HIT, Action.STAND, Action.DOUBLE], self.rules_s17), Action.DOUBLE)
        # If double not valid (e.g. 3 cards): Hit
        self.assertEqual(self.bs.decide(hand11, upcard, [Action.HIT, Action.STAND], self.rules_s17), Action.HIT)

    def test_hard_sixteen_surrender_or_hit(self) -> None:
        """Hard 16 surrenders vs 10 if allowed; otherwise hits."""
        hand16 = self._hand(Rank.TEN, Rank.SIX)
        upcard = self._upcard(Rank.TEN)

        self.assertEqual(self.bs.decide(hand16, upcard, [Action.HIT, Action.STAND, Action.SURRENDER], self.rules_s17), Action.SURRENDER)
        self.assertEqual(self.bs.decide(hand16, upcard, [Action.HIT, Action.STAND], self.rules_s17), Action.HIT)

    # --- DEVIATIONS: ILLUSTRIOUS 18 & FAB FOUR ---

    def test_deviation_insurance_at_true_count_three(self) -> None:
        """Illustrious 18 #1: Insurance declined at TC < 3, accepted at TC >= +3."""
        low_count = CountState(running_count=4, true_count=2.0, estimated_decks_remaining=2.0, cards_seen=208)
        high_count = CountState(running_count=9, true_count=3.0, estimated_decks_remaining=3.0, cards_seen=156)

        self.assertFalse(self.dev.decide_insurance(self.rules_s17, low_count))
        self.assertTrue(self.dev.decide_insurance(self.rules_s17, high_count))

    def test_deviation_sixteen_vs_ten_stand_at_zero(self) -> None:
        """Illustrious 18 #2: 16 vs 10 Hits at TC < 0, but Stands at TC >= 0."""
        hand16 = self._hand(Rank.TEN, Rank.SIX)
        upcard = self._upcard(Rank.TEN)
        valid = [Action.HIT, Action.STAND]

        neg_count = CountState(running_count=-3, true_count=-1.0, estimated_decks_remaining=3.0, cards_seen=156)
        zero_count = CountState(running_count=0, true_count=0.0, estimated_decks_remaining=3.0, cards_seen=156)
        pos_count = CountState(running_count=6, true_count=2.0, estimated_decks_remaining=3.0, cards_seen=156)

        self.assertEqual(self.dev.decide(hand16, upcard, valid, self.rules_s17, neg_count), Action.HIT)
        self.assertEqual(self.dev.decide(hand16, upcard, valid, self.rules_s17, zero_count), Action.STAND)
        self.assertEqual(self.dev.decide(hand16, upcard, valid, self.rules_s17, pos_count), Action.STAND)

    def test_deviation_fifteen_vs_ten_stand_at_plus_four(self) -> None:
        """Illustrious 18 #3: 15 vs 10 Hits at TC < 4, but Stands at TC >= +4."""
        hand15 = self._hand(Rank.TEN, Rank.FIVE)
        upcard = self._upcard(Rank.TEN)
        valid = [Action.HIT, Action.STAND]

        count_3 = CountState(running_count=6, true_count=3.0, estimated_decks_remaining=2.0, cards_seen=208)
        count_4 = CountState(running_count=8, true_count=4.0, estimated_decks_remaining=2.0, cards_seen=208)

        self.assertEqual(self.dev.decide(hand15, upcard, valid, self.rules_s17, count_3), Action.HIT)
        self.assertEqual(self.dev.decide(hand15, upcard, valid, self.rules_s17, count_4), Action.STAND)

    def test_deviation_tens_vs_five_split_at_plus_five(self) -> None:
        """Illustrious 18 #4: 10,10 vs 5 Stands at TC < 5, Splits at TC >= +5."""
        tens = self._hand(Rank.TEN, Rank.TEN)
        upcard = self._upcard(Rank.FIVE)
        valid = [Action.HIT, Action.STAND, Action.SPLIT]

        count_4 = CountState(running_count=8, true_count=4.0, estimated_decks_remaining=2.0, cards_seen=208)
        count_5 = CountState(running_count=10, true_count=5.0, estimated_decks_remaining=2.0, cards_seen=208)

        self.assertEqual(self.dev.decide(tens, upcard, valid, self.rules_s17, count_4), Action.STAND)
        self.assertEqual(self.dev.decide(tens, upcard, valid, self.rules_s17, count_5), Action.SPLIT)

    def test_fab_four_fourteen_vs_ten_surrender(self) -> None:
        """Fab Four: 14 vs 10 Hits at TC < 3, Surrenders at TC >= +3."""
        hand14 = self._hand(Rank.TEN, Rank.FOUR)
        upcard = self._upcard(Rank.TEN)
        valid = [Action.HIT, Action.STAND, Action.SURRENDER]

        count_2 = CountState(running_count=4, true_count=2.0, estimated_decks_remaining=2.0, cards_seen=208)
        count_3 = CountState(running_count=6, true_count=3.0, estimated_decks_remaining=2.0, cards_seen=208)

        self.assertEqual(self.dev.decide(hand14, upcard, valid, self.rules_s17, count_2), Action.HIT)
        self.assertEqual(self.dev.decide(hand14, upcard, valid, self.rules_s17, count_3), Action.SURRENDER)


if __name__ == "__main__":
    unittest.main()
