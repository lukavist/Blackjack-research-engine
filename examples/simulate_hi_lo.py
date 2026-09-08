"""Comparative simulation: Basic Strategy (Flat Bet) vs Hi-Lo Card Counting (Spread Bet)."""

from __future__ import annotations

import os
import sys
import time

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from blackjack.betting.strategies import FlatBetting, SpreadBetting
from blackjack.core.rules import BlackjackRules
from blackjack.simulation.runner import SimulationRunner
from blackjack.strategy.basic_strategy import BasicStrategy
from blackjack.strategy.deviations import HiLoDeviationStrategy
from blackjack.strategy.hi_lo import HiLoCounter


def run_comparison(rounds: int = 50_000) -> None:
    rules = BlackjackRules.standard_vegas_s17()

    print("=" * 70)
    print(f"BLACKJACK MONTE CARLO SIMULATION: {rounds:,} ROUNDS")
    print(f"Rules: 6 Decks, S17, DAS, Late Surrender, 3:2 BJ, 75% Penetration")
    print("=" * 70)

    # 1. Basic Strategy with Flat $10 Bet
    print(f"\n[1/2] Running Basic Strategy (Flat $10 Bet)...")
    start_t = time.perf_counter()
    runner_bs = SimulationRunner(
        rules=rules,
        strategy=BasicStrategy(),
        betting_strategy=FlatBetting(10.0),
        starting_bankroll=20_000.0,
        seed=42,
    )
    stats_bs = runner_bs.run(num_rounds=rounds)
    dur_bs = time.perf_counter() - start_t
    print(f"Completed in {dur_bs:.2f}s ({rounds / dur_bs:,.0f} hands/sec)")

    # 2. Hi-Lo Counting with 1-to-8 Spread & Illustrious 18 Deviations
    print(f"\n[2/2] Running Hi-Lo Card Counting (1-to-8 Spread + Illustrious 18)...")
    start_t = time.perf_counter()
    counter = HiLoCounter(num_decks=rules.num_decks)
    spread = {1: 1.0, 2: 2.0, 3: 4.0, 4: 8.0}  # $10 min to $80 max
    runner_hilo = SimulationRunner(
        rules=rules,
        strategy=HiLoDeviationStrategy(),
        betting_strategy=SpreadBetting(base_unit=10.0, spread=spread),
        counter=counter,
        starting_bankroll=20_000.0,
        seed=42,
    )
    stats_hilo = runner_hilo.run(num_rounds=rounds)
    dur_hilo = time.perf_counter() - start_t
    print(f"Completed in {dur_hilo:.2f}s ({rounds / dur_hilo:,.0f} hands/sec)")

    print("\n" + "=" * 70)
    print("COMPARATIVE PERFORMANCE SUMMARY")
    print("=" * 70)
    print(f"{'Metric':<30} | {'Basic Strategy (Flat)':<18} | {'Hi-Lo (1-8 Spread)':<18}")
    print("-" * 70)
    print(f"{'Rounds Played':<30} | {stats_bs.rounds_played:<18,d} | {stats_hilo.rounds_played:<18,d}")
    print(f"{'Hands Played':<30} | {stats_bs.hands_played:<18,d} | {stats_hilo.hands_played:<18,d}")
    print(f"{'Total Wagered':<30} | ${stats_bs.total_wagered:<17,.2f} | ${stats_hilo.total_wagered:<17,.2f}")
    print(f"{'Average Bet':<30} | ${stats_bs.average_bet:<17.2f} | ${stats_hilo.average_bet:<17.2f}")
    print(f"{'Net Profit / Loss':<30} | ${stats_bs.net_profit:<17,.2f} | ${stats_hilo.net_profit:<17,.2f}")
    print(f"{'EV per Round':<30} | ${stats_bs.ev_per_hand:<17.3f} | ${stats_hilo.ev_per_hand:<17.3f}")
    print(f"{'Player ROI / Edge %':<30} | {stats_bs.roi_percent:<17.2f}% | {stats_hilo.roi_percent:<17.2f}%")
    print(f"{'Win Rate (decisive)':<30} | {stats_bs.win_rate:<17.2f}% | {stats_hilo.win_rate:<17.2f}%")
    print(f"{'Max Drawdown':<30} | ${stats_bs.max_drawdown:<17,.2f} | ${stats_hilo.max_drawdown:<17,.2f}")
    print(f"{'Final Bankroll':<30} | ${stats_bs.final_bankroll:<17,.2f} | ${stats_hilo.final_bankroll:<17,.2f}")
    print(f"{'Insurance Taken / Won':<30} | {stats_bs.insurance_taken} / {stats_bs.insurance_won:<10} | {stats_hilo.insurance_taken} / {stats_hilo.insurance_won:<10}")
    print("=" * 70)


if __name__ == "__main__":
    run_comparison(rounds=50_000)
