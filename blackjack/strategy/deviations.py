"""Illustrious 18 and Fab Four index deviations for Hi-Lo card counting.

The deviation table (``DEVIATIONS``) is the single source of truth for every
index play in the engine. It is consumed directly by :class:`HiLoDeviationStrategy`
below, and is also exported verbatim to JSON by ``scripts/generate_strategy_data.py``
for the TypeScript dashboard (``src/lib/strategyAdvisor.ts``), so the two never
drift apart. If you add or change a deviation, edit only this table.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from blackjack.core.actions import Action
from blackjack.core.card import Card
from blackjack.core.hand import Hand
from blackjack.core.rules import BlackjackRules
from blackjack.strategy.base import CountState
from blackjack.strategy.basic_strategy import BasicStrategy

HandKind = Literal["hard", "pair10"]
Comparator = Literal[">=", "<"]
RuleCondition = Literal["s17_only", "h17_only", None]


@dataclass(frozen=True)
class Deviation:
    """One Illustrious 18 / Fab Four index play.

    ``hand_kind`` + ``hand_value`` identify the player hand this applies to:
    - ("hard", 16) -> any hard 16
    - ("pair10", 0) -> any two-card ten-value pair (10-10, K-Q, etc.)
    Surrender deviations reuse ``hand_kind="hard"`` since Fab Four hands are
    always hard totals on the initial two cards.
    """

    index: str  # e.g. "I18-2", "FF-1"
    description: str
    hand_kind: HandKind
    hand_value: int
    dealer_upcard: int  # 2-10, 11 for Ace
    action: Action
    comparator: Comparator
    threshold: float
    requires_action: Action
    rule_condition: RuleCondition = None

    def applies_to_rules(self, rules: BlackjackRules) -> bool:
        if self.rule_condition == "s17_only":
            return not rules.dealer_hits_soft_17
        if self.rule_condition == "h17_only":
            return rules.dealer_hits_soft_17
        return True

    def triggered(self, true_count: float) -> bool:
        if self.comparator == ">=":
            return true_count >= self.threshold
        return true_count < self.threshold

    def to_dict(self) -> dict:
        d = asdict(self)
        d["action"] = self.action.value
        d["requires_action"] = self.requires_action.value
        return d


# Don Schlesinger's Illustrious 18 (playing deviations) + Fab Four (surrender deviations).
# Insurance (Illustrious 18 #1) is handled separately in `decide_insurance` below since it
# is not a HIT/STAND/DOUBLE/SPLIT/SURRENDER decision.
DEVIATIONS: list[Deviation] = [
    Deviation("I18-2", "16 vs 10: Stand at TC >= 0", "hard", 16, 10, Action.STAND, ">=", 0.0, Action.STAND),
    Deviation("I18-3", "15 vs 10: Stand at TC >= +4", "hard", 15, 10, Action.STAND, ">=", 4.0, Action.STAND),
    Deviation("I18-4", "10,10 vs 5: Split at TC >= +5", "pair10", 0, 5, Action.SPLIT, ">=", 5.0, Action.SPLIT),
    Deviation("I18-5", "10,10 vs 6: Split at TC >= +4", "pair10", 0, 6, Action.SPLIT, ">=", 4.0, Action.SPLIT),
    Deviation("I18-6", "10 vs 10: Double at TC >= +4", "hard", 10, 10, Action.DOUBLE, ">=", 4.0, Action.DOUBLE),
    Deviation("I18-7", "12 vs 3: Stand at TC >= +2", "hard", 12, 3, Action.STAND, ">=", 2.0, Action.STAND),
    Deviation("I18-8", "12 vs 2: Stand at TC >= +3", "hard", 12, 2, Action.STAND, ">=", 3.0, Action.STAND),
    Deviation("I18-9", "11 vs A: Double at TC >= +1 (S17)", "hard", 11, 11, Action.DOUBLE, ">=", 1.0, Action.DOUBLE, "s17_only"),
    Deviation("I18-10", "9 vs 2: Double at TC >= +1", "hard", 9, 2, Action.DOUBLE, ">=", 1.0, Action.DOUBLE),
    Deviation("I18-11", "10 vs A: Double at TC >= +4", "hard", 10, 11, Action.DOUBLE, ">=", 4.0, Action.DOUBLE),
    Deviation("I18-12", "9 vs 7: Double at TC >= +3", "hard", 9, 7, Action.DOUBLE, ">=", 3.0, Action.DOUBLE),
    Deviation("I18-13", "16 vs 9: Stand at TC >= +5", "hard", 16, 9, Action.STAND, ">=", 5.0, Action.STAND),
    # Negative-index deviations: Basic Strategy stands here; deviate to Hit once the
    # count drops low enough that standing is no longer favorable.
    Deviation("I18-14", "13 vs 2: Hit at TC < -1", "hard", 13, 2, Action.HIT, "<", -1.0, Action.HIT),
    Deviation("I18-15", "12 vs 4: Hit at TC < 0", "hard", 12, 4, Action.HIT, "<", 0.0, Action.HIT),
    Deviation("I18-16", "12 vs 5: Hit at TC < -2", "hard", 12, 5, Action.HIT, "<", -2.0, Action.HIT),
    Deviation("I18-17", "12 vs 6: Hit at TC < -1", "hard", 12, 6, Action.HIT, "<", -1.0, Action.HIT),
    Deviation("I18-18", "13 vs 3: Hit at TC < -2", "hard", 13, 3, Action.HIT, "<", -2.0, Action.HIT),
    # Fab Four surrender deviations (require late surrender to be offered).
    Deviation("FF-1", "14 vs 10: Surrender at TC >= +3", "hard", 14, 10, Action.SURRENDER, ">=", 3.0, Action.SURRENDER),
    Deviation("FF-2", "15 vs 9: Surrender at TC >= +2", "hard", 15, 9, Action.SURRENDER, ">=", 2.0, Action.SURRENDER),
    Deviation("FF-3", "15 vs A: Surrender at TC >= +1 (S17)", "hard", 15, 11, Action.SURRENDER, ">=", 1.0, Action.SURRENDER, "s17_only"),
]


class HiLoDeviationStrategy(BasicStrategy):
    """Extends BasicStrategy with Illustrious 18 and Fab Four index deviations.

    Deviations override standard basic strategy choices when the True Count (TC)
    crosses designated index thresholds. All deviation thresholds live in
    ``DEVIATIONS`` above.
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

            for dev in DEVIATIONS:
                if dev.dealer_upcard != up_val:
                    continue
                if dev.requires_action not in valid_actions:
                    continue
                if not dev.applies_to_rules(rules):
                    continue

                if dev.hand_kind == "pair10":
                    if not (hand.is_pair and hand.cards and hand.cards[0].is_ten_value):
                        continue
                    if dev.requires_action == Action.SPLIT and not hand.can_split:
                        continue
                else:  # hard totals (also covers Fab Four surrenders, which are 2-card hard totals)
                    if hand.is_soft or hand.value != dev.hand_value:
                        continue
                    if dev.action == Action.SURRENDER:
                        if not rules.late_surrender or len(hand.cards) != 2:
                            continue

                if not dev.triggered(tc):
                    continue

                return dev.action

        # Fallback to standard Basic Strategy
        return super().decide(hand, dealer_upcard, valid_actions, rules, count_state)
