"""Comprehensive unit tests for the Game engine using deterministic stacked shoes."""

import unittest

from blackjack.core.actions import Action
from blackjack.core.card import Card, Rank, Suit
from blackjack.core.game import Game
from blackjack.core.hand import HandStatus
from blackjack.core.result import RoundResult
from blackjack.core.rules import BlackjackRules
from blackjack.core.shoe import Shoe


class TestGame(unittest.TestCase):
    """Rigorous end-to-end tests for all round outcomes, player decisions, and dealer rules."""

    def test_player_natural_blackjack(self) -> None:
        """Player receives A + K, Dealer receives 9 + 8. Player wins 3:2 (+1.5 * bet)."""
        # Deal sequence: P1, D1, P2, D2
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),    # P1
            Card(rank=Rank.NINE, suit=Suit.HEARTS),   # D1
            Card(rank=Rank.KING, suit=Suit.DIAMONDS), # P2 -> Player Blackjack
            Card(rank=Rank.EIGHT, suit=Suit.CLUBS),   # D2 -> Dealer 17
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=100.0)
        self.assertTrue(state.is_completed)
        self.assertIsNotNone(state.settlement)
        settlement = state.settlement

        self.assertEqual(settlement.primary_result, RoundResult.BLACKJACK)
        self.assertEqual(settlement.total_profit, 150.0)
        self.assertEqual(settlement.hands[0].wager, 100.0)

    def test_dealer_natural_blackjack(self) -> None:
        """Player receives 10 + 8 (18), Dealer receives J + A (BJ). Dealer peeks and settles immediately."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),   # P1
            Card(rank=Rank.JACK, suit=Suit.DIAMONDS),# D1 (shows 10-value)
            Card(rank=Rank.EIGHT, suit=Suit.CLUBS),  # P2
            Card(rank=Rank.ACE, suit=Suit.HEARTS),   # D2 (Dealer BJ)
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=50.0)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.settlement.primary_result, RoundResult.LOSS)
        self.assertEqual(state.settlement.total_profit, -50.0)

    def test_both_blackjack_pushes(self) -> None:
        """Both player and dealer hold natural Blackjack (dealer shows King) -> Push (profit = 0.0)."""
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),    # P1
            Card(rank=Rank.KING, suit=Suit.CLUBS),    # D1 (shows King)
            Card(rank=Rank.TEN, suit=Suit.DIAMONDS),  # P2
            Card(rank=Rank.ACE, suit=Suit.HEARTS),    # D2 (Ace hole card)
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=100.0)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.settlement.primary_result, RoundResult.PUSH)
        self.assertEqual(state.settlement.total_profit, 0.0)

    def test_player_stand_and_win(self) -> None:
        """Player stands with 20 (10 + 10). Dealer has 10 + 8 (18) and stands. Player wins."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),  # P1
            Card(rank=Rank.TEN, suit=Suit.HEARTS),  # D1
            Card(rank=Rank.TEN, suit=Suit.CLUBS),   # P2 -> 20
            Card(rank=Rank.EIGHT, suit=Suit.DIAMONDS),# D2 -> 18
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=20.0)
        self.assertFalse(state.is_completed)

        game.step(Action.STAND)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.settlement.primary_result, RoundResult.WIN)
        self.assertEqual(state.settlement.total_profit, 20.0)

    def test_player_hit_and_bust(self) -> None:
        """Player has 10 + 6 (16), hits, draws 7 -> 23 BUST. Player loses immediately."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),   # P1
            Card(rank=Rank.SEVEN, suit=Suit.HEARTS), # D1
            Card(rank=Rank.SIX, suit=Suit.CLUBS),    # P2 -> 16
            Card(rank=Rank.TEN, suit=Suit.DIAMONDS), # D2 -> 17
            Card(rank=Rank.SEVEN, suit=Suit.SPADES), # P draw 1 -> 23
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=25.0)
        game.step(Action.HIT)

        self.assertTrue(state.is_completed)
        self.assertEqual(state.settlement.primary_result, RoundResult.LOSS)
        self.assertEqual(state.settlement.total_profit, -25.0)

    def test_player_double_down_win(self) -> None:
        """Player has 5 + 6 (11), doubles ($10 -> $20), draws 10 -> 21. Dealer has 18. Player wins $20."""
        cards = [
            Card(rank=Rank.FIVE, suit=Suit.SPADES),  # P1
            Card(rank=Rank.EIGHT, suit=Suit.HEARTS), # D1
            Card(rank=Rank.SIX, suit=Suit.CLUBS),    # P2 -> 11
            Card(rank=Rank.TEN, suit=Suit.DIAMONDS), # D2 -> 18
            Card(rank=Rank.TEN, suit=Suit.SPADES),   # P double draw -> 21
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=10.0)
        self.assertIn(Action.DOUBLE, game.get_valid_actions())

        game.step(Action.DOUBLE)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.player_hands[0].status, HandStatus.DOUBLED)
        self.assertEqual(state.player_hands[0].bet, 20.0)
        self.assertEqual(state.settlement.primary_result, RoundResult.WIN)
        self.assertEqual(state.settlement.total_profit, 20.0)

    def test_dealer_s17_stands_on_soft_17(self) -> None:
        """Under S17 rules, dealer with A + 6 (soft 17) must stand."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),  # P1
            Card(rank=Rank.ACE, suit=Suit.HEARTS),  # D1 -> Ace
            Card(rank=Rank.NINE, suit=Suit.CLUBS),  # P2 -> 19
            Card(rank=Rank.SIX, suit=Suit.DIAMONDS),# D2 -> 6 (Dealer soft 17)
            Card(rank=Rank.FIVE, suit=Suit.SPADES), # Extra card that should NOT be drawn!
        ]
        shoe = Shoe.from_cards(cards)
        rules = BlackjackRules(dealer_hits_soft_17=False)
        game = Game(rules=rules, shoe=shoe)

        state = game.start_round(bet=10.0)
        game.step(Action.STAND)

        self.assertEqual(state.dealer_hand.value, 17)
        self.assertEqual(len(state.dealer_hand.cards), 2)
        self.assertEqual(state.settlement.primary_result, RoundResult.WIN)

    def test_dealer_h17_hits_soft_17(self) -> None:
        """Under H17 rules, dealer with A + 6 (soft 17) must hit."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),  # P1
            Card(rank=Rank.ACE, suit=Suit.HEARTS),  # D1 -> Ace
            Card(rank=Rank.NINE, suit=Suit.CLUBS),  # P2 -> 19
            Card(rank=Rank.SIX, suit=Suit.DIAMONDS),# D2 -> 6 (Soft 17)
            Card(rank=Rank.THREE, suit=Suit.SPADES),# Dealer hits 3 -> Soft 20!
        ]
        shoe = Shoe.from_cards(cards)
        rules = BlackjackRules(dealer_hits_soft_17=True)
        game = Game(rules=rules, shoe=shoe)

        state = game.start_round(bet=10.0)
        game.step(Action.STAND)

        self.assertEqual(state.dealer_hand.value, 20)
        self.assertEqual(len(state.dealer_hand.cards), 3)
        self.assertEqual(state.settlement.primary_result, RoundResult.LOSS)

    def test_late_surrender(self) -> None:
        """Player surrenders 16 vs dealer 10. Player forfeits half wager."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),   # P1
            Card(rank=Rank.TEN, suit=Suit.HEARTS),   # D1
            Card(rank=Rank.SIX, suit=Suit.CLUBS),    # P2 -> 16
            Card(rank=Rank.EIGHT, suit=Suit.DIAMONDS),# D2 -> 18
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=40.0)
        self.assertIn(Action.SURRENDER, game.get_valid_actions())

        game.step(Action.SURRENDER)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.settlement.primary_result, RoundResult.SURRENDER)
        self.assertEqual(state.settlement.total_profit, -20.0)

    def test_insurance_won_when_dealer_has_bj(self) -> None:
        """Player takes insurance against dealer Ace. Dealer has Blackjack -> Insurance pays 2:1."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),   # P1
            Card(rank=Rank.ACE, suit=Suit.HEARTS),   # D1 (shows Ace)
            Card(rank=Rank.NINE, suit=Suit.CLUBS),   # P2 -> 19
            Card(rank=Rank.JACK, suit=Suit.DIAMONDS),# D2 -> Dealer BJ!
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=100.0)
        self.assertTrue(state.insurance_offered)

        game.handle_insurance(take_insurance=True)
        self.assertTrue(state.is_completed)

        # Hand lost (-$100), Insurance won $50 * 2 = +$100 -> Net round profit = $0
        self.assertEqual(state.settlement.insurance_profit, 100.0)
        self.assertEqual(state.settlement.total_profit, 0.0)

    def test_pair_splitting_creates_two_independent_hands(self) -> None:
        """Player splits 8-8. Both hands receive a card and can be played separately."""
        cards = [
            Card(rank=Rank.EIGHT, suit=Suit.SPADES), # P1 (8)
            Card(rank=Rank.SEVEN, suit=Suit.HEARTS), # D1 (7)
            Card(rank=Rank.EIGHT, suit=Suit.CLUBS),  # P2 (8)
            Card(rank=Rank.TEN, suit=Suit.DIAMONDS), # D2 (17)
            # Cards dealt on split:
            Card(rank=Rank.TEN, suit=Suit.HEARTS),   # To hand 1 -> 8 + 10 = 18
            Card(rank=Rank.NINE, suit=Suit.SPADES),  # To hand 2 -> 8 + 9 = 17
        ]
        shoe = Shoe.from_cards(cards)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        state = game.start_round(bet=25.0)
        self.assertIn(Action.SPLIT, game.get_valid_actions())

        game.step(Action.SPLIT)
        self.assertEqual(len(state.player_hands), 2)
        self.assertEqual(state.player_hands[0].value, 18)
        self.assertEqual(state.player_hands[1].value, 17)

        # Stand on hand 1 (18)
        game.step(Action.STAND)
        # Stand on hand 2 (17)
        game.step(Action.STAND)

        self.assertTrue(state.is_completed)
        # Dealer has 7 + 10 = 17
        # Hand 1: 18 vs 17 -> WIN (+$25)
        # Hand 2: 17 vs 17 -> PUSH ($0)
        self.assertEqual(state.settlement.hands[0].result, RoundResult.WIN)
        self.assertEqual(state.settlement.hands[1].result, RoundResult.PUSH)
        self.assertEqual(state.settlement.total_profit, 25.0)

    def test_split_aces_receive_one_card_and_stand(self) -> None:
        """Aces split receive exactly one card and auto-stand under split_aces_one_card rule."""
        cards = [
            Card(rank=Rank.ACE, suit=Suit.SPADES),   # P1
            Card(rank=Rank.NINE, suit=Suit.HEARTS),  # D1
            Card(rank=Rank.ACE, suit=Suit.CLUBS),   # P2
            Card(rank=Rank.EIGHT, suit=Suit.DIAMONDS),# D2 -> 17
            # Draw on split:
            Card(rank=Rank.NINE, suit=Suit.DIAMONDS),# Hand 1: A + 9 = 20
            Card(rank=Rank.EIGHT, suit=Suit.SPADES), # Hand 2: A + 8 = 19
        ]
        shoe = Shoe.from_cards(cards)
        rules = BlackjackRules(split_aces_one_card=True)
        game = Game(rules=rules, shoe=shoe)

        state = game.start_round(bet=50.0)
        game.step(Action.SPLIT)

        # After split, both hands auto-stood and dealer played out (17)
        self.assertTrue(state.is_completed)
        self.assertEqual(state.player_hands[0].value, 20)
        self.assertEqual(state.player_hands[1].value, 19)
        self.assertEqual(state.settlement.hands[0].result, RoundResult.WIN)
        self.assertEqual(state.settlement.hands[1].result, RoundResult.WIN)
        self.assertEqual(state.settlement.total_profit, 100.0)

    def test_hole_card_not_leaked_to_observer_until_dealer_turn(self) -> None:
        """Observer must not see the hole card before player completes their actions."""
        cards = [
            Card(rank=Rank.TEN, suit=Suit.SPADES),  # P1
            Card(rank=Rank.FIVE, suit=Suit.HEARTS), # D1
            Card(rank=Rank.SIX, suit=Suit.CLUBS),   # P2
            Card(rank=Rank.JACK, suit=Suit.DIAMONDS),# D2 (hole card)
            Card(rank=Rank.FOUR, suit=Suit.HEARTS), # P hit
            Card(rank=Rank.THREE, suit=Suit.CLUBS), # Dealer hit: 5 + 10 + 3 = 18
        ]
        shoe = Shoe.from_cards(cards)
        observed_cards: list[tuple[Card, bool]] = []

        def observer(c: Card, is_hole: bool) -> None:
            observed_cards.append((c, is_hole))

        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)
        game.add_card_observer(observer)

        state = game.start_round(bet=10.0)
        # At start of round, observed cards must be P1, D1, P2 only (3 cards)
        self.assertEqual(len(observed_cards), 3)
        self.assertFalse(any(c.rank == Rank.JACK for c, _ in observed_cards))

        game.step(Action.HIT)  # P draws 4 -> 20. Stood.
        game.step(Action.STAND)

        # Now round is completed, hole card (Jack) should be observed with is_hole=True
        self.assertTrue(state.is_completed)
        hole_observations = [c for c, is_hole in observed_cards if is_hole]
        self.assertEqual(len(hole_observations), 1)
        self.assertEqual(hole_observations[0].rank, Rank.JACK)

    def test_shoe_persists_across_multiple_rounds(self) -> None:
        """No shuffle bug: shoe does NOT reshuffle between consecutive rounds."""
        shoe = Shoe(num_decks=6, penetration=0.75, seed=55)
        game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe)

        # Round 1
        state1 = game.start_round(bet=10.0)
        while not state1.is_completed:
            game.step(Action.STAND)

        dealt_after_r1 = shoe.cards_dealt
        self.assertGreaterEqual(dealt_after_r1, 4)

        # Round 2
        state2 = game.start_round(bet=10.0)
        while not state2.is_completed:
            game.step(Action.STAND)

        dealt_after_r2 = shoe.cards_dealt
        self.assertGreater(dealt_after_r2, dealt_after_r1)
        self.assertEqual(shoe.shuffle_count, 1)  # Has not reshuffled yet


if __name__ == "__main__":
    unittest.main()
