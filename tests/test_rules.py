"""Unit tests for BlackjackRules validation and standard presets."""

import unittest

from blackjack.core.rules import BlackjackRules


class TestRules(unittest.TestCase):
    """Test rule constraints, edge validation, and factory presets."""

    def test_default_rules(self) -> None:
        """Default rules must follow standard Vegas 6-deck S17 rules."""
        rules = BlackjackRules()
        self.assertEqual(rules.num_decks, 6)
        self.assertEqual(rules.penetration, 0.75)
        self.assertFalse(rules.dealer_hits_soft_17)
        self.assertEqual(rules.blackjack_payout, 1.5)
        self.assertTrue(rules.double_allowed)
        self.assertTrue(rules.double_after_split)
        self.assertTrue(rules.late_surrender)
        self.assertFalse(rules.surrender_against_ace)

    def test_presets(self) -> None:
        """Presets must initialize valid rules instances with expected flags."""
        s17 = BlackjackRules.standard_vegas_s17()
        self.assertFalse(s17.dealer_hits_soft_17)

        h17 = BlackjackRules.standard_h17()
        self.assertTrue(h17.dealer_hits_soft_17)

        single = BlackjackRules.single_deck_classic()
        self.assertEqual(single.num_decks, 1)
        self.assertFalse(single.double_after_split)

    def test_invalid_rules_raise(self) -> None:
        """Rules with invalid parameters must raise ValueError."""
        with self.assertRaises(ValueError):
            BlackjackRules(num_decks=0)

        with self.assertRaises(ValueError):
            BlackjackRules(penetration=1.5)

        with self.assertRaises(ValueError):
            BlackjackRules(blackjack_payout=-1.0)

        with self.assertRaises(ValueError):
            BlackjackRules(min_bet=100.0, max_bet=50.0)


if __name__ == "__main__":
    unittest.main()
