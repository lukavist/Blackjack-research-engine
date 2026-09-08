"""Mathematically verified Blackjack Basic Strategy engine for multi-deck games."""

from __future__ import annotations

from blackjack.core.actions import Action
from blackjack.core.card import Card, Rank
from blackjack.core.hand import Hand
from blackjack.core.rules import BlackjackRules
from blackjack.strategy.base import CountState, Strategy


class BasicStrategy(Strategy):
    """Standard Basic Strategy implementation.

    Adapts dynamically to table configurations:
    - S17 vs H17 (Dealer stands/hits on soft 17)
    - DAS (Double After Split)
    - Late Surrender
    """

    def decide(
        self,
        hand: Hand,
        dealer_upcard: Card,
        valid_actions: list[Action],
        rules: BlackjackRules,
        count_state: CountState | None = None,
    ) -> Action:
        """Determines the mathematically optimal action under Basic Strategy."""
        if not valid_actions:
            return Action.STAND

        up_val = self._dealer_upcard_value(dealer_upcard)

        # 1. Check Surrender if legal and available
        if rules.late_surrender and Action.SURRENDER in valid_actions:
            if self._should_surrender(hand, up_val, rules):
                return Action.SURRENDER

        # 2. Check Pair Splitting if legal and available
        if Action.SPLIT in valid_actions and hand.can_split:
            if self._should_split(hand, up_val, rules):
                return Action.SPLIT

        # 3. Check Soft Totals (hand has an Ace counted as 11)
        if hand.is_soft and hand.value <= 21:
            action = self._decide_soft(hand, up_val, rules, valid_actions)
            if action in valid_actions:
                return action
            if action == Action.DOUBLE and Action.HIT in valid_actions:
                return Action.HIT

        # 4. Check Hard Totals
        action = self._decide_hard(hand, up_val, rules, valid_actions)
        if action in valid_actions:
            return action
        if action == Action.DOUBLE and Action.HIT in valid_actions:
            return Action.HIT

        # Fallback to legal action
        if Action.STAND in valid_actions and hand.value >= 12:
            return Action.STAND
        if Action.HIT in valid_actions:
            return Action.HIT
        return valid_actions[0]

    def _dealer_upcard_value(self, card: Card) -> int:
        """Returns dealer upcard value: 2-10 for numbers/face, 11 for Ace."""
        if card.is_ace:
            return 11
        return card.blackjack_value

    def _should_surrender(self, hand: Hand, up_val: int, rules: BlackjackRules) -> bool:
        """Determines late surrender eligibility."""
        # Surrender is only permitted on initial two-card hand
        if len(hand.cards) != 2 or hand.is_soft:
            return False

        val = hand.value
        # If hand is a pair of 8s, splitting is almost universally preferred over surrender
        if hand.is_pair and hand.cards[0].rank == Rank.EIGHT and rules.double_after_split:
            return False

        if val == 16:
            # 16 surrenders vs 9, 10, A
            return up_val in (9, 10, 11)
        if val == 15:
            # 15 surrenders vs 10; and vs A under H17
            if up_val == 10:
                return True
            if up_val == 11 and rules.dealer_hits_soft_17:
                return True
        if val == 17 and rules.dealer_hits_soft_17 and up_val == 11:
            # 17 surrenders vs A under H17
            return True

        return False

    def _should_split(self, hand: Hand, up_val: int, rules: BlackjackRules) -> bool:
        """Pair splitting strategy based on upcard and DAS rule."""
        c1 = hand.cards[0]
        rank = c1.rank
        das = rules.double_after_split

        # Aces and 8s: Always split
        if rank == Rank.ACE or rank == Rank.EIGHT:
            return True

        # 10s and Face cards: Never split
        if c1.is_ten_value:
            return False

        # 5s: Never split (double instead)
        if rank == Rank.FIVE:
            return False

        # 9s: Split vs 2-6, 8, 9 (Stand vs 7, 10, A)
        if rank == Rank.NINE:
            return up_val in (2, 3, 4, 5, 6, 8, 9)

        # 7s: Split vs 2-7
        if rank == Rank.SEVEN:
            return 2 <= up_val <= 7

        # 6s:
        # DAS: Split vs 2-6
        # No DAS: Split vs 3-6
        if rank == Rank.SIX:
            if das:
                return 2 <= up_val <= 6
            return 3 <= up_val <= 6

        # 4s:
        # DAS: Split vs 5, 6
        # No DAS: Never split
        if rank == Rank.FOUR:
            return das and (up_val in (5, 6))

        # 2s and 3s:
        # DAS: Split vs 2-7
        # No DAS: Split vs 4-7
        if rank in (Rank.TWO, Rank.THREE):
            if das:
                return 2 <= up_val <= 7
            return 4 <= up_val <= 7

        return False

    def _decide_soft(
        self,
        hand: Hand,
        up_val: int,
        rules: BlackjackRules,
        valid_actions: list[Action],
    ) -> Action:
        """Decision table for Soft hands (A,2 through A,9+)."""
        val = hand.value
        can_double = Action.DOUBLE in valid_actions

        # Soft 20+ (A,9+): Always Stand
        if val >= 20:
            return Action.STAND

        # Soft 19 (A,8):
        if val == 19:
            # Under H17, double vs 6
            if rules.dealer_hits_soft_17 and up_val == 6 and can_double:
                return Action.DOUBLE
            return Action.STAND

        # Soft 18 (A,7):
        if val == 18:
            # Double vs 3-6 (or 2-6 under H17)
            if can_double:
                if rules.dealer_hits_soft_17 and (2 <= up_val <= 6):
                    return Action.DOUBLE
                if not rules.dealer_hits_soft_17 and (3 <= up_val <= 6):
                    return Action.DOUBLE
            # Stand vs 2 through 8 (including 3-6 when doubling is not permitted)
            if 2 <= up_val <= 8:
                return Action.STAND
            # Hit vs 9, 10, A
            return Action.HIT

        # Soft 17 (A,6):
        if val == 17:
            if can_double and (3 <= up_val <= 6):
                return Action.DOUBLE
            return Action.HIT

        # Soft 16 (A,5) & Soft 15 (A,4):
        if val in (15, 16):
            if can_double and (4 <= up_val <= 6):
                return Action.DOUBLE
            return Action.HIT

        # Soft 14 (A,3) & Soft 13 (A,2):
        if val in (13, 14):
            if can_double and (5 <= up_val <= 6):
                return Action.DOUBLE
            return Action.HIT

        return Action.HIT

    def _decide_hard(
        self,
        hand: Hand,
        up_val: int,
        rules: BlackjackRules,
        valid_actions: list[Action],
    ) -> Action:
        """Decision table for Hard hands (5 through 20)."""
        val = hand.value
        can_double = Action.DOUBLE in valid_actions

        # Hard 17+: Always Stand
        if val >= 17:
            return Action.STAND

        # Hard 13 - 16:
        # Stand vs 2-6, Hit vs 7-A
        if 13 <= val <= 16:
            if 2 <= up_val <= 6:
                return Action.STAND
            return Action.HIT

        # Hard 12:
        # Stand vs 4-6, Hit vs 2, 3, 7-A
        if val == 12:
            if 4 <= up_val <= 6:
                return Action.STAND
            return Action.HIT

        # Hard 11:
        # Always Double vs 2-10 (and vs A under H17)
        if val == 11:
            if can_double:
                if rules.dealer_hits_soft_17:
                    return Action.DOUBLE
                if up_val <= 10:
                    return Action.DOUBLE
            return Action.HIT

        # Hard 10:
        # Double vs 2-9, Hit vs 10, A
        if val == 10:
            if can_double and (2 <= up_val <= 9):
                return Action.DOUBLE
            return Action.HIT

        # Hard 9:
        # Double vs 3-6, Hit vs 2, 7-A
        if val == 9:
            if can_double and (3 <= up_val <= 6):
                return Action.DOUBLE
            return Action.HIT

        # Hard 5-8: Always Hit
        return Action.HIT
