"""Unit tests for Hand point evaluation, Ace soft/hard dynamics, and bust detection."""

import unittest

from blackjack.core.card import Card, Rank, Suit
from blackjack.core.hand import Hand, HandStatus


class TestHand(unittest.TestCase):
    """Rigorous evaluation of Hand point calculations, soft aces, and status flags."""

    def test_ace_plus_six_is_soft_17(self) -> None:
        """A + 6 = 17 soft."""
        hand = Hand()
        hand.add_card(Card(rank=Rank.ACE, suit=Suit.SPADES))
        hand.add_card(Card(rank=Rank.SIX, suit=Suit.HEARTS))
        self.assertEqual(hand.value, 17)
        self.assertTrue(hand.is_soft)
        self.assertFalse(hand.is_hard)
        self.assertFalse(hand.is_bust)

    def test_ace_plus_six_plus_ten_is_hard_17(self) -> None:
        """A + 6 + 10 = 17 hard (Ace reduced from 11 to 1)."""
        hand = Hand()
        hand.add_card(Card(rank=Rank.ACE, suit=Suit.SPADES))
        hand.add_card(Card(rank=Rank.SIX, suit=Suit.HEARTS))
        hand.add_card(Card(rank=Rank.TEN, suit=Suit.CLUBS))
        self.assertEqual(hand.value, 17)
        self.assertFalse(hand.is_soft)
        self.assertTrue(hand.is_hard)
        self.assertFalse(hand.is_bust)

    def test_pair_of_aces_is_soft_12(self) -> None:
        """A + A = 12 soft (one Ace is 11, one Ace is 1)."""
        hand = Hand()
        hand.add_card(Card(rank=Rank.ACE, suit=Suit.SPADES))
        hand.add_card(Card(rank=Rank.ACE, suit=Suit.HEARTS))
        self.assertEqual(hand.value, 12)
        self.assertTrue(hand.is_soft)
        self.assertFalse(hand.is_bust)
        self.assertTrue(hand.is_pair)

    def test_two_aces_plus_nine_is_soft_21(self) -> None:
        """A + A + 9 = 21 soft (11 + 1 + 9 = 21)."""
        hand = Hand()
        hand.add_card(Card(rank=Rank.ACE, suit=Suit.SPADES))
        hand.add_card(Card(rank=Rank.ACE, suit=Suit.HEARTS))
        hand.add_card(Card(rank=Rank.NINE, suit=Suit.DIAMONDS))
        self.assertEqual(hand.value, 21)
        self.assertTrue(hand.is_soft)
        self.assertFalse(hand.is_bust)
        # Not a natural blackjack because 3 cards
        self.assertFalse(hand.is_blackjack)

    def test_three_sevens_is_hard_21(self) -> None:
        """7 + 7 + 7 = 21 hard."""
        hand = Hand()
        hand.add_card(Card(rank=Rank.SEVEN, suit=Suit.SPADES))
        hand.add_card(Card(rank=Rank.SEVEN, suit=Suit.HEARTS))
        hand.add_card(Card(rank=Rank.SEVEN, suit=Suit.CLUBS))
        self.assertEqual(hand.value, 21)
        self.assertFalse(hand.is_soft)
        self.assertTrue(hand.is_hard)
        self.assertFalse(hand.is_blackjack)

    def test_four_aces_dynamics(self) -> None:
        """A + A + A + A = 14 soft; + 10 = 14 hard."""
        hand = Hand()
        for suit in Suit:
            hand.add_card(Card(rank=Rank.ACE, suit=suit))
        self.assertEqual(hand.value, 14)
        self.assertTrue(hand.is_soft)

        hand.add_card(Card(rank=Rank.TEN, suit=Suit.SPADES))
        # Now 1 + 1 + 1 + 1 + 10 = 14 hard
        self.assertEqual(hand.value, 14)
        self.assertFalse(hand.is_soft)
        self.assertTrue(hand.is_hard)

    def test_bust_detection(self) -> None:
        """10 + 9 + 5 = 24 bust."""
        hand = Hand()
        hand.add_card(Card(rank=Rank.TEN, suit=Suit.SPADES))
        hand.add_card(Card(rank=Rank.NINE, suit=Suit.HEARTS))
        hand.add_card(Card(rank=Rank.FIVE, suit=Suit.CLUBS))
        self.assertEqual(hand.value, 24)
        self.assertTrue(hand.is_bust)
        self.assertEqual(hand.status, HandStatus.BUSTED)

    def test_natural_blackjack(self) -> None:
        """A + K and A + 10 are natural blackjacks; 3-card 21 is not."""
        bj1 = Hand()
        bj1.add_card(Card(rank=Rank.ACE, suit=Suit.SPADES))
        bj1.add_card(Card(rank=Rank.KING, suit=Suit.HEARTS))
        self.assertTrue(bj1.is_blackjack)

        bj2 = Hand()
        bj2.add_card(Card(rank=Rank.TEN, suit=Suit.DIAMONDS))
        bj2.add_card(Card(rank=Rank.ACE, suit=Suit.CLUBS))
        self.assertTrue(bj2.is_blackjack)

        three_card_21 = Hand()
        three_card_21.add_card(Card(rank=Rank.SEVEN))
        three_card_21.add_card(Card(rank=Rank.SEVEN))
        three_card_21.add_card(Card(rank=Rank.SEVEN))
        self.assertFalse(three_card_21.is_blackjack)

    def test_split_hand_cannot_be_natural_blackjack(self) -> None:
        """A 21 achieved on a split hand counts as 21, not a 3:2 natural blackjack."""
        split_hand = Hand(is_from_split=True)
        split_hand.add_card(Card(rank=Rank.ACE))
        split_hand.add_card(Card(rank=Rank.JACK))
        self.assertEqual(split_hand.value, 21)
        self.assertFalse(split_hand.is_blackjack)

    def test_pair_and_ten_pair_detection(self) -> None:
        """Equal ranks are pairs; K-Q is a ten pair (can split in standard casino rules)."""
        pair_8 = Hand()
        pair_8.add_card(Card(rank=Rank.EIGHT, suit=Suit.SPADES))
        pair_8.add_card(Card(rank=Rank.EIGHT, suit=Suit.HEARTS))
        self.assertTrue(pair_8.is_pair)
        self.assertTrue(pair_8.can_split)

        kq = Hand()
        kq.add_card(Card(rank=Rank.KING, suit=Suit.SPADES))
        kq.add_card(Card(rank=Rank.QUEEN, suit=Suit.HEARTS))
        self.assertFalse(kq.is_pair)
        self.assertTrue(kq.is_ten_pair)
        self.assertTrue(kq.can_split)


if __name__ == "__main__":
    unittest.main()
