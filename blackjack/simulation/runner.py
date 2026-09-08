"""High-speed simulation runner for Blackjack strategy evaluation."""

from __future__ import annotations

import math
from typing import Callable

from blackjack.betting.base import BettingStrategy
from blackjack.betting.strategies import FlatBetting
from blackjack.core.actions import Action
from blackjack.core.game import Game
from blackjack.core.result import RoundResult
from blackjack.core.rules import BlackjackRules
from blackjack.core.shoe import Shoe
from blackjack.simulation.stats import SimulationStats
from blackjack.strategy.base import CountState, Strategy
from blackjack.strategy.basic_strategy import BasicStrategy
from blackjack.strategy.hi_lo import HiLoCounter


class SimulationRunner:
    """Executes monte carlo simulations across hundreds of thousands of hands."""

    def __init__(
        self,
        rules: BlackjackRules | None = None,
        strategy: Strategy | None = None,
        betting_strategy: BettingStrategy | None = None,
        counter: HiLoCounter | None = None,
        starting_bankroll: float = 10_000.0,
        stop_on_ruin: bool = True,
        seed: int | None = None,
    ) -> None:
        self.rules: BlackjackRules = rules if rules is not None else BlackjackRules.standard_vegas_s17()
        self.strategy: Strategy = strategy if strategy is not None else BasicStrategy()
        self.betting_strategy: BettingStrategy = betting_strategy if betting_strategy is not None else FlatBetting(10.0)
        self.counter: HiLoCounter | None = counter
        self.starting_bankroll: float = starting_bankroll
        self.stop_on_ruin: bool = stop_on_ruin
        self.seed: int | None = seed

    def run(
        self,
        num_rounds: int = 100_000,
        trajectory_sample_interval: int = 500,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> SimulationStats:
        """Runs the simulation for num_rounds or until bankroll reaches zero."""
        shoe = Shoe(num_decks=self.rules.num_decks, penetration=self.rules.penetration, seed=self.seed)
        game = Game(rules=self.rules, shoe=shoe)

        if self.counter is not None:
            self.counter.reset()
            game.add_card_observer(self.counter.as_observer_callback())

        bankroll = self.starting_bankroll
        peak_bankroll = bankroll
        max_drawdown = 0.0

        stats = SimulationStats(
            starting_bankroll=self.starting_bankroll,
            max_bankroll=bankroll,
            min_bankroll=bankroll,
            trajectory=[(0, bankroll)],
        )

        last_shuffle_count = shoe.shuffle_count

        for round_idx in range(1, num_rounds + 1):
            if self.stop_on_ruin and bankroll <= 0:
                break

            # Handle shoe reshuffle detection to reset count
            if shoe.shuffle_count != last_shuffle_count:
                if self.counter is not None:
                    self.counter.reset()
                last_shuffle_count = shoe.shuffle_count

            # 1. Determine wager from betting strategy
            count_state = self.counter.get_state() if self.counter is not None else None
            bet = self.betting_strategy.get_bet(count_state=count_state, current_bankroll=bankroll)
            if bet <= 0:
                if self.stop_on_ruin:
                    break
                bet = 1.0

            stats.total_wagered += bet

            # 2. Deal initial cards
            round_state = game.start_round(bet=bet)

            # 3. Check insurance if dealer shows Ace and insurance offered
            if round_state.insurance_offered and not round_state.insurance_settled:
                count_state = self.counter.get_state() if self.counter is not None else None
                wants_insurance = self.strategy.decide_insurance(self.rules, count_state=count_state)
                if wants_insurance:
                    stats.insurance_taken += 1
                game.handle_insurance(wants_insurance)

            # 4. Play all player hands until completed
            while not round_state.is_completed:
                current_hand = round_state.current_hand
                upcard = round_state.dealer_upcard
                valid_actions = game.get_valid_actions()

                if not current_hand or not upcard or not valid_actions:
                    break

                count_state = self.counter.get_state() if self.counter is not None else None
                action = self.strategy.decide(
                    hand=current_hand,
                    dealer_upcard=upcard,
                    valid_actions=valid_actions,
                    rules=self.rules,
                    count_state=count_state,
                )

                if action == Action.DOUBLE:
                    stats.doubles += 1
                elif action == Action.SPLIT:
                    stats.splits += 1
                elif action == Action.SURRENDER:
                    stats.surrenders += 1

                round_state = game.step(action)

            # 5. Settle round results
            settlement = round_state.settlement
            if settlement is not None:
                net = settlement.net_profit
                bankroll += net
                stats.net_profit += net
                stats.rounds_played += 1
                stats.hands_played += len(settlement.hand_settlements)

                for hs in settlement.hand_settlements:
                    if hs.result == RoundResult.BLACKJACK:
                        stats.blackjacks += 1
                        stats.wins += 1
                    elif hs.result == RoundResult.WIN:
                        stats.wins += 1
                    elif hs.result == RoundResult.LOSS:
                        stats.losses += 1
                    elif hs.result == RoundResult.PUSH:
                        stats.pushes += 1
                    elif hs.result == RoundResult.SURRENDER:
                        stats.losses += 1

                if settlement.insurance_profit > 0:
                    stats.insurance_won += 1

            # Track peak, drawdown, and trajectory
            if bankroll > peak_bankroll:
                peak_bankroll = bankroll
            dd = peak_bankroll - bankroll
            if dd > max_drawdown:
                max_drawdown = dd

            if bankroll > stats.max_bankroll:
                stats.max_bankroll = bankroll
            if bankroll < stats.min_bankroll:
                stats.min_bankroll = bankroll

            if round_idx % trajectory_sample_interval == 0:
                stats.trajectory.append((round_idx, round(bankroll, 2)))
                if progress_callback:
                    progress_callback(round_idx, num_rounds)

        stats.final_bankroll = bankroll
        stats.max_drawdown = max_drawdown
        stats.trajectory.append((stats.rounds_played, round(bankroll, 2)))
        return stats
