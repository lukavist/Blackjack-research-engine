"""Illustrious 18 and Fab Four index deviations for Hi-Lo card counting."""

from __future__ import annotations

from blackjack.core.actions import Action
from blackjack.core.card import Card, Rank
from blackjack.core.hand import Hand
from blackjack.core.rules import BlackjackRules
from blackjack.strategy.base import CountState
from blackjack.strategy.basic_strategy import BasicStrategy


class HiLoDeviationStrategy(BasicStrategy):
    """Extends BasicStrategy with Illustrious 18 and Fab Four index deviations.

    Deviations override standard basic strategy choices when the True Count (TC)
    crosses designated index thresholds.
    """

    def decide_insurance(
        self,
        rules: BlackjackRules,
        count_state: CountState | None = None,
    ) -> bool:
        """Illustrious 18 #1: Take insurance when True Count >= +3.0."""
        if not rules.insurance_allowed:
            return False
        if count_state is None:
            return False
        return count_state.true_count >= 3.0

    def decide(
        self,
        hand: Hand,
        dealer_upcard: Card,
        valid_actions: list[Action],
        rules: BlackjackRules,
        count_state: CountState | None = None,
    ) -> Action:
        """Evaluates index deviations first; falls back to standard basic strategy."""
        if count_state is not None:
            tc = count_state.true_count
            up_val = self._dealer_upcard_value(dealer_upcard)

            # --- FAB FOUR SURRENDER DEVIATIONS ---
            if rules.late_surrender and Action.SURRENDER in valid_actions and len(hand.cards) == 2 and not hand.is_soft:
                val = hand.value
                # 14 vs 10: Surrender at TC >= +3
                if val == 14 and up_val == 10 and tc >= 3.0:
                    return Action.SURRENDER
                # 15 vs 9: Surrender at TC >= +2
                if val == 15 and up_val == 9 and tc >= 2.0:
                    return Action.SURRENDER
                # 15 vs A: Surrender at TC >= +1 (in S17 games where basic strategy hits)
                if val == 15 and up_val == 11 and not rules.dealer_hits_soft_17 and tc >= 1.0:
                    return Action.SURRENDER

            # --- ILLUSTRIOUS 18 PLAYING DEVIATIONS ---
            # 4. Pair of 10s vs 5: Split at TC >= +5
            # 5. Pair of 10s vs 6: Split at TC >= +4
            if hand.is_pair and hand.cards[0].is_ten_value and Action.SPLIT in valid_actions:
                if up_val == 5 and tc >= 5.0:
                    return Action.SPLIT
                if up_val == 6 and tc >= 4.0:
                    return Action.SPLIT

            # Hard totals deviations
            if not hand.is_soft:
                val = hand.value

                # 2. 16 vs 10: Stand at TC >= 0 (BS says Hit)
                if val == 16 and up_val == 10:
                    if tc >= 0.0 and Action.STAND in valid_actions:
                        return Action.STAND

                # 3. 15 vs 10: Stand at TC >= +4 (BS says Hit)
                if val == 15 and up_val == 10:
                    if tc >= 4.0 and Action.STAND in valid_actions:
                        return Action.STAND

                # 6. 10 vs 10: Double at TC >= +4 (BS says Hit)
                if val == 10 and up_val == 10 and Action.DOUBLE in valid_actions:
                    if tc >= 4.0:
                        return Action.DOUBLE

                # 11. 10 vs A: Double at TC >= +4 (BS says Hit)
                if val == 10 and up_val == 11 and Action.DOUBLE in valid_actions:
                    if tc >= 4.0:
                        return Action.DOUBLE

                # 7. 12 vs 3: Stand at TC >= +2 (BS says Hit)
                if val == 12 and up_val == 3:
                    if tc >= 2.0 and Action.STAND in valid_actions:
                        return Action.STAND

                # 8. 12 vs 2: Stand at TC >= +3 (BS says Hit)
                if val == 12 and up_val == 2:
                    if tc >= 3.0 and Action.STAND in valid_actions:
                        return Action.STAND

                # 9. 11 vs A: Double at TC >= +1 in S17 (BS says Hit)
                if val == 11 and up_val == 11 and not rules.dealer_hits_soft_17 and Action.DOUBLE in valid_actions:
                    if tc >= 1.0:
                        return Action.DOUBLE

                # 10. 9 vs 2: Double at TC >= +1 (BS says Hit)
                if val == 9 and up_val == 2 and Action.DOUBLE in valid_actions:
                    if tc >= 1.0:
                        return Action.DOUBLE

                # 12. 9 vs 7: Double at TC >= +3 (BS says Hit)
                if val == 9 and up_val == 7 and Action.DOUBLE in valid_actions:
                    if tc >= 3.0:
                        return Action.DOUBLE

                # 13. 16 vs 9: Stand at TC >= +5 (BS says Hit)
                if val == 16 and up_val == 9:
                    if tc >= 5.0 and Action.STAND in valid_actions:
                        return Action.STAND

                # Negative index deviations (Hit when TC drops below threshold)
                # 14. 13 vs 2: Hit if TC < -1 (BS says Stand)
                if val == 13 and up_val == 2:
                    if tc < -1.0 and Action.HIT in valid_actions:
                        return Action.HIT

                # 18. 13 vs 3: Hit if TC < -2 (BS says Stand)
                if val == 13 and up_val == 3:
                    if tc < -2.0 and Action.HIT in valid_actions:
                        return Action.HIT

                # 15. 12 vs 4: Hit if TC < 0 (BS says Stand)
                if val == 12 and up_val == 4:
                    if tc < 0.0 and Action.HIT in valid_actions:
                        return Action.HIT

                # 16. 12 vs 5: Hit if TC < -2 (BS says Stand)
                if val == 12 and up_val == 5:
                    if tc < -2.0 and Action.HIT in valid_actions:
                        return Action.HIT

                # 17. 12 vs 6: Hit if TC < -1 (BS says Stand)
                if val == 12 and up_val == 6:
                    if tc < -1.0 and Action.HIT in valid_actions:
                        return Action.HIT

        # Fallback to standard Basic Strategy
        return super().decide(hand, dealer_upcard, valid_actions, rules, count_state)
