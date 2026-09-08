"""Unit tests for Card and Rank implementations."""

import unittest

from blackjack.core.card import Card, Rank, Suit


class TestCard(unittest.TestCase):
    """Test standard rank values, blackjack point valuations, and string representations."""

    def test_numerical_ranks(self) -> None:
        """Ranks 2 through 10 must return matching numerical point values."""
        for num in range(2, 11):
            rank = Rank.from_str(str(num))
            card = Card(rank=rank)
            self.assertEqual(card.value, num)
            self.assertFalse(card.is_ace)
            if num == 10:
                self.assertTrue(card.is_ten_value)
            else:
                self.assertFalse(card.is_ten_value)

    def test_face_cards(self) -> None:
        """Jack, Queen, and King must all evaluate to 10 points."""
        for face in ["J", "Q", "K"]:
            rank = Rank.from_str(face)
            card = Card(rank=rank)
            self.assertEqual(card.value, 10)
            self.assertTrue(card.is_ten_value)
            self.assertFalse(card.is_ace)

    def test_ace_initial_value(self) -> None:
        """Ace by default evaluates to 11 points."""
        ace = Card(rank=Rank.ACE, suit=Suit.SPADES)
        self.assertEqual(ace.value, 11)
        self.assertTrue(ace.is_ace)
        self.assertFalse(ace.is_ten_value)

    def test_card_parsing(self) -> None:
        """Cards can be cleanly parsed from alphanumeric representations."""
        c1 = Card.from_string("Ah")
        self.assertEqual(c1.rank, Rank.ACE)
        self.assertEqual(c1.suit, Suit.HEARTS)

        c2 = Card.from_string("10s")
        self.assertEqual(c2.rank, Rank.TEN)
        self.assertEqual(c2.suit, Suit.SPADES)

        c3 = Card.from_string("Kd")
        self.assertEqual(c3.rank, Rank.KING)
        self.assertEqual(c3.suit, Suit.DIAMONDS)

        c4 = Card.from_string("7")
        self.assertEqual(c4.rank, Rank.SEVEN)

    def test_invalid_rank_raises(self) -> None:
        """Attempting to construct an invalid card rank must raise ValueError."""
        with self.assertRaises(ValueError):
            Rank.from_str("15")

        with self.assertRaises(ValueError):
            Card.from_string("Zz")


if __name__ == "__main__":
    unittest.main()
