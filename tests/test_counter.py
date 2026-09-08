"""Unit tests for Hi-Lo card counter and observer integration."""

import unittest

from blackjack.core.actions import Action
from blackjack.core.card import Card, Rank, Suit
from blackjack.core.game import Game
from blackjack.core.rules import BlackjackRules
from blackjack.core.shoe import Shoe
from blackjack.strategy.hi_lo import HiLoCounter


class TestHiLoCounter(unittest.TestCase):
    """Verifies card counting metrics and specifications."""

    def test_single_card_hi_lo_tags(self) -> None:
        """Low cards +1, neutral 0, high cards -1."""
        counter = HiLoCounter(num_decks=1)
        self.assertEqual(counter.card_value(Card(rank=Rank.TWO, suit=Suit.HEARTS)), 1)
        self.assertEqual(counter.card_value(Card(rank=Rank.SIX, suit=Suit.SPADES)), 1)
        self.assertEqual(counter.card_value(Card(rank=Rank.SEVEN, suit=Suit.CLUBS)), 0)
        self.assertEqual(counter.card_value(Card(rank=Rank.EIGHT, suit=Suit.DIAMONDS)), 0)
        self.assertEqual(counter.card_value(Card(rank=Rank.NINE, suit=Suit.HEARTS)), 0)
        self.assertEqual(counter.card_value(Card(rank=Rank.TEN, suit=Suit.SPADES)), -1)
        self.assertEqual(counter.card_value(Card(rank=Rank.KING, suit=Suit.CLUBS)), -1)
        self.assertEqual(counter.card_value(Card(rank=Rank.ACE, suit=Suit.DIAMONDS)), -1)

    def test_spec_section_63_counting_sequence(self) -> None:
        """Requirement Section 63: Sequence [2, 5, K, A, 7, 9] yields tags [+1, +1, -1, -1, 0, 0] = 0."""
        counter = HiLoCounter(num_decks=6)
        sequence = [
            Card(rank=Rank.TWO, suit=Suit.SPADES),    # +1
            Card(rank=Rank.FIVE, suit=Suit.HEARTS),   # +1 -> +2
            Card(rank=Rank.KING, suit=Suit.CLUBS),    # -1 -> +1
            Card(rank=Rank.ACE, suit=Suit.DIAMONDS),  # -1 -> 0
            Card(rank=Rank.SEVEN, suit=Suit.SPADES),  #  0 -> 0
            Card(rank=Rank.NINE, suit=Suit.CLUBS),    #  0 -> 0
        ]
        for card in sequence:
            counter.observe(card)

        self.assertEqual(counter.running_count, 0)
        self.assertEqual(counter.cards_seen, 6)

    def test_spec_section_64_true_count(self) -> None:
        """Requirement Section 64: RC = +6 with 3 decks remaining yields TC = +2.0."""
        counter = HiLoCounter(num_decks=6)
        # Directly set running count to test true count math
        counter.running_count = 6
        tc = counter.true_count(decks_remaining=3.0)
        self.assertAlmostEqual(tc, 2.0, places=4)

    def test_full_single_deck_is_balanced_zero(self) -> None:
        """A complete 52-card standard deck must sum to exactly zero in Hi-Lo."""
        counter = HiLoCounter(num_decks=1)
        shoe = Shoe(num_decks=1, penetration=0.95, seed=123)
        cards = shoe.cards.copy()
        self.assertEqual(len(cards), 52)
        counter.observe_cards(cards)
        self.assertEqual(counter.running_count, 0)

    def test_observer_receives_cards_without_hole_card_leak(self) -> None:
        """Observer callback attached to Game receives player cards and upcard, but hole card only at dealer turn."""
        counter = HiLoCounter(num_decks=6)

        cards = [
            Card(rank=Rank.FIVE, suit=Suit.SPADES),   # P1: +1
            Card(rank=Rank.SIX, suit=Suit.HEARTS),    # D1: +1 (upcard)
            Card(rank=Rank.TEN, suit=Suit.CLUBS),     # P2: -1 -> P total = 15
            Card(rank=Rank.KING, suit=Suit.DIAMONDS), # D2: -1 (hole card)
            Card(rank=Rank.TWO, suit=Suit.CLUBS),     # D hit: +1 (6 + 10 + 2 = 18)
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)
        game.add_observer(counter.as_observer_callback())

        # Deal initial round
        game.start_round(bet=10.0)

        # Before player action, exactly 3 cards should have been observed (P1, D1, P2)
        # P1 (+1), D1 (+1), P2 (-1) => RC = +1
        self.assertEqual(counter.cards_seen, 3)
        self.assertEqual(counter.running_count, 1)

        # Player stands -> Dealer turn begins and reveals hole card (D2: King, -1) and draws 2 (+1)
        game.step(Action.STAND)

        # Total seen should now be 5 cards: P1, D1, P2, D2, D3
        # (+1) + (+1) + (-1) + (-1) + (+1) = +1
        self.assertEqual(counter.cards_seen, 5)
        self.assertEqual(counter.running_count, 1)


if __name__ == "__main__":
    unittest.main()
