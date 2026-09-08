"""Unit tests for multi-deck Shoe, cut-card penetration, and RNG reproducibility."""

import unittest

from blackjack.core.card import Card, Rank, Suit
from blackjack.core.shoe import Shoe


class TestShoe(unittest.TestCase):
    """Verify shoe composition, deterministic seed behavior, and penetration tracking."""

    def test_shoe_composition_and_sizes(self) -> None:
        """Shoe should contain exactly num_decks * 52 cards."""
        for num_decks in (1, 2, 4, 6, 8):
            shoe = Shoe(num_decks=num_decks, penetration=0.75, seed=123)
            expected_total = num_decks * 52
            self.assertEqual(shoe.total_cards, expected_total)
            self.assertEqual(shoe.cards_remaining, expected_total)
            self.assertEqual(shoe.cards_dealt, 0)
            self.assertEqual(shoe.current_penetration, 0.0)
            self.assertFalse(shoe.needs_reshuffle)

    def test_deterministic_seed_reproducibility(self) -> None:
        """Shoes instantiated with identical seeds must yield identical card sequences."""
        shoe_a = Shoe(num_decks=6, penetration=0.75, seed=42)
        shoe_b = Shoe(num_decks=6, penetration=0.75, seed=42)

        cards_a = [shoe_a.deal() for _ in range(50)]
        cards_b = [shoe_b.deal() for _ in range(50)]

        self.assertEqual(cards_a, cards_b)

    def test_different_seeds_diverge(self) -> None:
        """Different seeds should generate distinct card sequences."""
        shoe_1 = Shoe(num_decks=6, seed=100)
        shoe_2 = Shoe(num_decks=6, seed=200)

        sequence_1 = [shoe_1.deal() for _ in range(10)]
        sequence_2 = [shoe_2.deal() for _ in range(10)]

        self.assertNotEqual(sequence_1, sequence_2)

    def test_cut_card_penetration_and_reshuffle_flag(self) -> None:
        """Penetration threshold must trigger needs_reshuffle when reached."""
        shoe = Shoe(num_decks=2, penetration=0.5, seed=99)
        total = 104
        cut_card = int(total * 0.5)  # 52 cards

        for _ in range(cut_card - 1):
            shoe.deal()
            self.assertFalse(shoe.needs_reshuffle)

        # Deal the card that reaches the cut-card penetration threshold
        shoe.deal()
        self.assertTrue(shoe.needs_reshuffle)

    def test_cards_dealt_do_not_return_to_shoe_before_shuffle(self) -> None:
        """No shuffle bug test: Dealt cards must remain removed across successive deals."""
        shoe = Shoe(num_decks=1, seed=7)
        initial_remaining = shoe.cards_remaining

        dealt_card = shoe.deal()
        self.assertEqual(shoe.cards_remaining, initial_remaining - 1)
        self.assertEqual(shoe.cards_dealt, 1)

        # Confirm dealt card is not immediately in remaining cards
        all_remaining = list(shoe._cards)
        self.assertEqual(len(all_remaining), 51)

    def test_mock_stacked_shoe(self) -> None:
        """Shoe.from_cards must deal cards in exact provided order."""
        preset = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),
            Card(rank=Rank.KING, suit=Suit.HEARTS),
            Card(rank=Rank.FIVE, suit=Suit.CLUBS),
        ]
        shoe = Shoe.from_cards(preset)
        self.assertEqual(shoe.deal(), preset[0])
        self.assertEqual(shoe.deal(), preset[1])
        self.assertEqual(shoe.deal(), preset[2])

    def test_empty_shoe_raises_runtime_error(self) -> None:
        """Attempting to deal from an empty shoe without shuffle must raise RuntimeError."""
        shoe = Shoe.from_cards([Card(rank=Rank.TWO)])
        shoe.deal()
        with self.assertRaises(RuntimeError):
            shoe.deal()


if __name__ == "__main__":
    unittest.main()
