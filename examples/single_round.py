"""Example script demonstrating a single round of Blackjack in full debug mode."""

import os
import sys

# Ensure repository root is on Python module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blackjack.core.actions import Action
from blackjack.core.card import Card, Rank, Suit
from blackjack.core.game import Game
from blackjack.core.rules import BlackjackRules
from blackjack.core.shoe import Shoe


def main() -> None:
    print("==================================================")
    print("  BLACKJACK RESEARCH ENGINE — SINGLE ROUND DEMO   ")
    print("==================================================")

    # 1. Deterministic demo matching Section 41 specification:
    print("\n--- Demonstration 1: Trace from Spec Section 41 ---")
    stacked_cards = [
        Card(rank=Rank.TEN, suit=Suit.SPADES),   # P1: 10
        Card(rank=Rank.FIVE, suit=Suit.HEARTS),  # D1: 5 (upcard)
        Card(rank=Rank.SIX, suit=Suit.CLUBS),    # P2: 6 -> Player total = 16
        Card(rank=Rank.KING, suit=Suit.DIAMONDS),# D2: K -> Dealer hole card (5+10=15)
        Card(rank=Rank.THREE, suit=Suit.HEARTS), # Player HIT: 3 -> 10+6+3 = 19
        Card(rank=Rank.FOUR, suit=Suit.CLUBS),   # Dealer HIT: 4 -> 15+4 = 19 (Push) or if D had 10+4=14...
    ]
    shoe_spec = Shoe.from_cards(stacked_cards)
    game_spec = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=shoe_spec, debug=True)

    game_spec.start_round(bet=10.0)
    game_spec.step(Action.HIT)
    game_spec.step(Action.STAND)

    # 2. Random 6-deck shoe round with S17 rules
    print("\n--- Demonstration 2: Random 6-Deck Live Round (Seed=42) ---")
    live_shoe = Shoe(num_decks=6, penetration=0.75, seed=42)
    live_game = Game(rules=BlackjackRules.standard_vegas_s17(), shoe=live_shoe, debug=True)

    state = live_game.start_round(bet=25.0)
    if state.insurance_offered:
        live_game.handle_insurance(take_insurance=False)

    while not state.is_completed:
        valid = live_game.get_valid_actions()
        curr_hand = state.current_hand
        print(f"Current valid decisions: {[a.value for a in valid]}")

        # Basic decision rule for demo: hit on < 17, stand on >= 17
        if curr_hand and curr_hand.value < 17 and Action.HIT in valid:
            action = Action.HIT
        else:
            action = Action.STAND

        live_game.step(action)

    print("\nFinal Round Settlement Summary:")
    settlement = state.settlement
    if settlement:
        print(f"Outcome: {settlement.primary_result.value}")
        print(f"Net Profit: ${settlement.total_profit:+.2f}")
        print(f"Total Wagered: ${settlement.total_wagered:.2f}")


if __name__ == "__main__":
    main()
