"""Blackjack Round/Game engine implementing complete casino dealing, action and settlement rules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from blackjack.core.actions import Action
from blackjack.core.card import Card
from blackjack.core.hand import Hand, HandStatus
from blackjack.core.result import HandSettlement, RoundResult, RoundSettlement
from blackjack.core.rules import BlackjackRules
from blackjack.core.shoe import Shoe

# Observer callback for cards revealed to the table: callback(card, is_hole_card_reveal: bool)
CardObserver = Callable[[Card, bool], None]


@dataclass
class RoundState:
    """Snapshot of an active or concluded blackjack round."""

    player_hands: list[Hand] = field(default_factory=list)
    dealer_hand: Hand = field(default_factory=Hand)
    current_hand_idx: int = 0
    insurance_offered: bool = False
    insurance_bet: float = 0.0
    insurance_settled: bool = False
    is_completed: bool = False
    settlement: RoundSettlement | None = None
    log_messages: list[str] = field(default_factory=list)

    @property
    def current_hand(self) -> Hand | None:
        """Return the active player hand or None if all hands are resolved."""
        if 0 <= self.current_hand_idx < len(self.player_hands):
            return self.player_hands[self.current_hand_idx]
        return None

    @property
    def dealer_upcard(self) -> Card | None:
        """Dealer's first face-up card visible to all participants."""
        if self.dealer_hand.cards:
            return self.dealer_hand.cards[0]
        return None

    @property
    def dealer_hole_card_revealed(self) -> bool:
        """True if the dealer's hole card has been turned face up."""
        return self.is_completed or len(self.dealer_hand.cards) > 2


class Game:
    """Manages a single round or continuous sequence of blackjack rounds."""

    def __init__(
        self,
        rules: BlackjackRules | None = None,
        shoe: Shoe | None = None,
        debug: bool = False,
        card_observers: list[CardObserver] | None = None,
    ) -> None:
        self.rules: BlackjackRules = rules if rules is not None else BlackjackRules.standard_vegas_s17()
        self.shoe: Shoe = shoe if shoe is not None else Shoe(num_decks=self.rules.num_decks, penetration=self.rules.penetration)
        self.debug: bool = debug
        self.card_observers: list[CardObserver] = card_observers or []
        self.current_state: RoundState | None = None
        self.round_counter: int = 0

    def add_card_observer(self, observer: CardObserver) -> None:
        """Attach a card observer (e.g. Card Counter) notified when cards become visible."""
        if observer not in self.card_observers:
            self.card_observers.append(observer)

    def add_observer(self, observer: CardObserver) -> None:
        """Alias for add_card_observer."""
        self.add_card_observer(observer)

    def _notify_card_visible(self, card: Card, is_hole_card: bool = False) -> None:
        """Broadcast card visibility to registered observers without leaking unseen hole cards."""
        for obs in self.card_observers:
            obs(card, is_hole_card)

    def _log(self, msg: str) -> None:
        """Append to round log and print if debug mode is active."""
        if self.current_state is not None:
            self.current_state.log_messages.append(msg)
        if self.debug:
            print(msg)

    def start_round(self, bet: float) -> RoundState:
        """Begin a new round with the specified initial wager."""
        if bet < self.rules.min_bet or bet > self.rules.max_bet:
            raise ValueError(
                f"Bet {bet} is outside allowed limits [{self.rules.min_bet}, {self.rules.max_bet}]"
            )

        if self.shoe.needs_reshuffle:
            self._log("--- Reshuffle triggered (penetration threshold reached) ---")
            self.shoe.shuffle()

        self.round_counter += 1
        state = RoundState()
        self.current_state = state

        self._log(f"\n=== Round #{self.round_counter} (Bet: ${bet:.2f}) ===")

        # Initial deal order: Player 1, Dealer 1 (upcard), Player 2, Dealer 2 (hole card)
        p_card1 = self.shoe.deal()
        self._notify_card_visible(p_card1, is_hole_card=False)

        d_upcard = self.shoe.deal()
        self._notify_card_visible(d_upcard, is_hole_card=False)

        p_card2 = self.shoe.deal()
        self._notify_card_visible(p_card2, is_hole_card=False)

        # Dealer hole card is dealt face down - observers are NOT notified yet!
        d_hole_card = self.shoe.deal()

        initial_player_hand = Hand(cards=[p_card1, p_card2], bet=bet)
        dealer_hand = Hand(cards=[d_upcard, d_hole_card], bet=0.0)

        state.player_hands = [initial_player_hand]
        state.dealer_hand = dealer_hand

        self._log(f"Player: {p_card1.rank.value}, {p_card2.rank.value} ({initial_player_hand.value})")
        self._log(f"Dealer: {d_upcard.rank.value}, ?")

        # Check Insurance availability: dealer shows Ace
        if self.rules.insurance_allowed and d_upcard.is_ace:
            state.insurance_offered = True
            self._log("Dealer shows Ace. Insurance is offered.")
            return state

        # Check for immediate naturals (Blackjack peek)
        dealer_has_bj = dealer_hand.is_blackjack
        player_has_bj = initial_player_hand.is_blackjack

        # Dealer peeks for blackjack if upcard is 10-value or Ace
        if d_upcard.is_ten_value or d_upcard.is_ace:
            if dealer_has_bj or player_has_bj:
                self._resolve_immediate_naturals(player_has_bj, dealer_has_bj)
                return state
        elif player_has_bj:
            # Dealer upcard is 2-9; cannot have BJ. Player BJ wins immediately!
            self._resolve_immediate_naturals(player_has_bj=True, dealer_has_bj=False)
            return state

        return state

    def handle_insurance(self, take_insurance: bool) -> None:
        """Process player's insurance decision when dealer shows Ace."""
        state = self._require_active_state()
        if not state.insurance_offered or state.insurance_settled:
            raise ValueError("Insurance is not available in current state.")

        initial_bet = state.player_hands[0].bet
        if take_insurance:
            state.insurance_bet = initial_bet * 0.5
            self._log(f"Player takes Insurance for ${state.insurance_bet:.2f}")
        else:
            self._log("Player declines Insurance.")

        state.insurance_settled = True

        dealer_has_bj = state.dealer_hand.is_blackjack
        player_has_bj = state.player_hands[0].is_blackjack

        if dealer_has_bj or player_has_bj:
            if dealer_has_bj:
                self._log("Dealer reveals Blackjack!")
            self._resolve_immediate_naturals(
                player_has_bj=player_has_bj,
                dealer_has_bj=dealer_has_bj,
            )

    def _resolve_immediate_naturals(self, player_has_bj: bool, dealer_has_bj: bool) -> None:
        """Settle round when one or both participants hold natural Blackjack."""
        state = self._require_active_state()
        state.is_completed = True

        # Reveal dealer hole card to observers now
        d_hole = state.dealer_hand.cards[1]
        self._notify_card_visible(d_hole, is_hole_card=True)
        self._log(f"Dealer reveals hole card: {d_hole} (Dealer: {state.dealer_hand.value})")

        hand = state.player_hands[0]
        hand_settlements: list[HandSettlement] = []

        # Insurance settlement
        ins_profit = 0.0
        if state.insurance_bet > 0:
            if dealer_has_bj:
                # 2:1 payout on insurance bet
                ins_profit = state.insurance_bet * self.rules.insurance_payout
                self._log(f"Insurance WINS +${ins_profit:.2f} (2:1)")
            else:
                ins_profit = -state.insurance_bet
                self._log(f"Insurance LOSES -${state.insurance_bet:.2f}")

        if player_has_bj and dealer_has_bj:
            hand.status = HandStatus.BLACKJACK
            settlement = HandSettlement.create(
                result=RoundResult.PUSH,
                wager=hand.bet,
                blackjack_payout=self.rules.blackjack_payout,
                cards_summary=str(hand),
                actions_taken=[str(a) for a in hand.actions],
            )
            hand_settlements.append(settlement)
            self._log("Result: PUSH (Both Player and Dealer hold Blackjack)")
        elif player_has_bj and not dealer_has_bj:
            hand.status = HandStatus.BLACKJACK
            settlement = HandSettlement.create(
                result=RoundResult.BLACKJACK,
                wager=hand.bet,
                blackjack_payout=self.rules.blackjack_payout,
                cards_summary=str(hand),
                actions_taken=[str(a) for a in hand.actions],
            )
            hand_settlements.append(settlement)
            self._log(f"Result: BLACKJACK! Profit: +${settlement.profit:.2f}")
        elif dealer_has_bj and not player_has_bj:
            settlement = HandSettlement.create(
                result=RoundResult.LOSS,
                wager=hand.bet,
                blackjack_payout=self.rules.blackjack_payout,
                cards_summary=str(hand),
                actions_taken=[str(a) for a in hand.actions],
            )
            hand_settlements.append(settlement)
            self._log(f"Result: LOSS (Dealer Blackjack). Profit: -${hand.bet:.2f}")

        state.settlement = RoundSettlement(
            hands=hand_settlements,
            dealer_summary=str(state.dealer_hand),
            dealer_value=state.dealer_hand.value,
            dealer_bust=state.dealer_hand.is_bust,
            insurance_bet=state.insurance_bet,
            insurance_profit=ins_profit,
        )

    def get_valid_actions(self, hand_idx: int | None = None) -> list[Action]:
        """Return legal actions for the specified hand index (or current hand)."""
        state = self._require_active_state()
        if state.is_completed:
            return []

        idx = state.current_hand_idx if hand_idx is None else hand_idx
        if not (0 <= idx < len(state.player_hands)):
            return []

        hand = state.player_hands[idx]
        if hand.status != HandStatus.ACTIVE:
            return []

        actions: list[Action] = [Action.STAND, Action.HIT]

        # Double Down: allowed on initial 2 cards (or after split if DAS allowed)
        if len(hand.cards) == 2 and self.rules.double_allowed:
            if not hand.is_from_split or self.rules.double_after_split:
                actions.append(Action.DOUBLE)

        # Splitting: exactly 2 cards, equal rank or equal ten-value, within split limit
        if (
            len(hand.cards) == 2
            and hand.can_split
            and len(state.player_hands) <= self.rules.max_splits
        ):
            # If aces were already split and resplitting aces is forbidden:
            if not (hand.is_split_aces and not self.rules.resplit_aces):
                actions.append(Action.SPLIT)

        # Late Surrender: exactly 2 cards, first hand, no prior actions, allowed by rules
        if (
            len(hand.cards) == 2
            and self.rules.late_surrender
            and not hand.is_from_split
            and len(hand.actions) == 0
            and idx == 0
        ):
            # Check surrender against dealer Ace rule
            if not (state.dealer_upcard and state.dealer_upcard.is_ace and not self.rules.surrender_against_ace):
                actions.append(Action.SURRENDER)

        return actions

    def step(self, action: Action) -> RoundState:
        """Execute player action on the active hand and advance the round."""
        state = self._require_active_state()
        if state.is_completed:
            raise RuntimeError("Round is already completed.")

        hand = state.current_hand
        if hand is None or hand.status != HandStatus.ACTIVE:
            raise RuntimeError("No active hand awaiting player action.")

        valid = self.get_valid_actions(state.current_hand_idx)
        if action not in valid:
            raise ValueError(f"Action '{action}' is invalid. Valid actions: {[a.value for a in valid]}")

        hand.record_action(action)
        self._log(f"Action: {action.value}")

        if action == Action.STAND:
            hand.status = HandStatus.STOOD
            self._advance_to_next_hand_or_dealer()

        elif action == Action.HIT:
            new_card = self.shoe.deal()
            self._notify_card_visible(new_card, is_hole_card=False)
            hand.add_card(new_card)
            self._log(f"Player draws {new_card} -> {hand}")

            if hand.is_bust:
                hand.status = HandStatus.BUSTED
                self._log(f"Hand #{state.current_hand_idx + 1} BUSTED ({hand.value})")
                self._advance_to_next_hand_or_dealer()
            elif hand.value == 21:
                hand.status = HandStatus.STOOD
                self._log(f"Hand #{state.current_hand_idx + 1} reached 21. Standing automatically.")
                self._advance_to_next_hand_or_dealer()

        elif action == Action.DOUBLE:
            # Wager doubled, exactly one card dealt, stand automatically
            hand.bet *= 2
            new_card = self.shoe.deal()
            self._notify_card_visible(new_card, is_hole_card=False)
            hand.add_card(new_card)
            self._log(f"Player doubles (${hand.bet:.2f}), draws {new_card} -> {hand}")

            if hand.is_bust:
                hand.status = HandStatus.BUSTED
                self._log(f"Hand #{state.current_hand_idx + 1} BUSTED on double ({hand.value})")
            else:
                hand.status = HandStatus.DOUBLED

            self._advance_to_next_hand_or_dealer()

        elif action == Action.SURRENDER:
            hand.status = HandStatus.SURRENDERED
            self._log(f"Player surrenders hand. Forfeits half wager (${hand.bet * 0.5:.2f})")
            self._advance_to_next_hand_or_dealer()

        elif action == Action.SPLIT:
            self._execute_split(hand)

        return state

    def _execute_split(self, hand: Hand) -> None:
        """Split pair hand into two independent hands and deal initial replacement card to each."""
        state = self._require_active_state()
        card1 = hand.cards[0]
        card2 = hand.cards[1]
        is_splitting_aces = card1.is_ace

        # Create two hands inheriting original bet
        h1 = Hand(
            cards=[card1],
            bet=hand.bet,
            is_from_split=True,
            is_split_aces=is_splitting_aces,
        )
        h2 = Hand(
            cards=[card2],
            bet=hand.bet,
            is_from_split=True,
            is_split_aces=is_splitting_aces,
        )

        # Replace original hand with h1, and insert h2 right after
        curr_idx = state.current_hand_idx
        state.player_hands[curr_idx] = h1
        state.player_hands.insert(curr_idx + 1, h2)

        # Deal one card to h1
        c_new1 = self.shoe.deal()
        self._notify_card_visible(c_new1, is_hole_card=False)
        h1.add_card(c_new1)

        # Deal one card to h2
        c_new2 = self.shoe.deal()
        self._notify_card_visible(c_new2, is_hole_card=False)
        h2.add_card(c_new2)

        self._log(f"Split executed! Hand 1: {h1}, Hand 2: {h2}")

        # If splitting aces and rule split_aces_one_card is set: both hands stand immediately
        if is_splitting_aces and self.rules.split_aces_one_card:
            h1.status = HandStatus.STOOD
            h2.status = HandStatus.STOOD
            self._log("Split Aces receive exactly 1 card each and stand automatically.")
            self._advance_to_next_hand_or_dealer()
        else:
            # Continue playing current hand (h1)
            if h1.value == 21:
                h1.status = HandStatus.STOOD
                self._advance_to_next_hand_or_dealer()

    def _advance_to_next_hand_or_dealer(self) -> None:
        """Move cursor to the next active player hand, or transition to dealer's turn."""
        state = self._require_active_state()
        state.current_hand_idx += 1

        # Skip any already stood/busted hands (e.g. from split aces auto-stand)
        while (
            state.current_hand_idx < len(state.player_hands)
            and state.player_hands[state.current_hand_idx].status != HandStatus.ACTIVE
        ):
            state.current_hand_idx += 1

        if state.current_hand_idx >= len(state.player_hands):
            # All player hands resolved -> Dealer turn
            self._play_dealer_turn()

    def _play_dealer_turn(self) -> None:
        """Dealer reveals hole card, hits according to table rules (S17/H17), and settles."""
        state = self._require_active_state()
        state.is_completed = True

        # Reveal dealer's hole card to all observers
        d_hole = state.dealer_hand.cards[1]
        self._notify_card_visible(d_hole, is_hole_card=True)
        self._log(f"\nDealer reveals: {state.dealer_hand.cards[0].rank.value}, {d_hole.rank.value} ({state.dealer_hand.value})")

        # Optimization check: if all player hands busted or surrendered, dealer doesn't draw
        non_busted_active_hands = [
            h for h in state.player_hands
            if h.status not in (HandStatus.BUSTED, HandStatus.SURRENDERED)
        ]

        if non_busted_active_hands:
            # Dealer draws cards according to S17 / H17
            while True:
                val = state.dealer_hand.value
                if val < 17:
                    draw = True
                elif val == 17 and state.dealer_hand.is_soft and self.rules.dealer_hits_soft_17:
                    draw = True
                else:
                    draw = False

                if not draw:
                    break

                new_card = self.shoe.deal()
                self._notify_card_visible(new_card, is_hole_card=False)
                state.dealer_hand.add_card(new_card)
                self._log(f"Dealer hits: {new_card} (Total: {state.dealer_hand.value})")

        if state.dealer_hand.is_bust:
            self._log(f"Dealer BUSTS with {state.dealer_hand.value}!")
        else:
            self._log(f"Dealer stands with {state.dealer_hand.value}")

        self._settle_round()

    def _settle_round(self) -> None:
        """Calculate final outcomes, payouts, and net profits across all hands."""
        state = self._require_active_state()
        dealer = state.dealer_hand
        d_val = dealer.value
        d_bust = dealer.is_bust

        hand_settlements: list[HandSettlement] = []

        for i, hand in enumerate(state.player_hands):
            p_val = hand.value
            p_bust = hand.is_bust

            if hand.status == HandStatus.SURRENDERED:
                res = RoundResult.SURRENDER
            elif p_bust:
                res = RoundResult.LOSS
            elif d_bust:
                res = RoundResult.WIN
            elif p_val > d_val:
                res = RoundResult.WIN
            elif p_val < d_val:
                res = RoundResult.LOSS
            else:
                res = RoundResult.PUSH

            settlement = HandSettlement.create(
                result=res,
                wager=hand.bet,
                blackjack_payout=self.rules.blackjack_payout,
                cards_summary=str(hand),
                actions_taken=[str(a) for a in hand.actions],
                is_split=hand.is_from_split,
            )
            hand_settlements.append(settlement)
            self._log(
                f"Hand #{i + 1}: {settlement.result.value} | Bet: ${settlement.wager:.2f} | Profit: ${settlement.profit:+.2f}"
            )

        state.settlement = RoundSettlement(
            hands=hand_settlements,
            dealer_summary=str(dealer),
            dealer_value=d_val,
            dealer_bust=d_bust,
            insurance_bet=state.insurance_bet,
            insurance_profit=-state.insurance_bet if state.insurance_bet > 0 else 0.0,
        )
        self._log(
            f"Round Total Profit: ${state.settlement.total_profit:+.2f} (Total Wagered: ${state.settlement.total_wagered:.2f})"
        )

    def play_one_round_manual(
        self,
        bet: float,
        action_callback: Callable[[RoundState, list[Action]], Action],
    ) -> RoundSettlement:
        """Helper to play through a complete round programmatically using a callback."""
        state = self.start_round(bet)

        if state.insurance_offered and not state.insurance_settled:
            # Default pass insurance in simple callback unless callback handles it
            self.handle_insurance(take_insurance=False)

        while not state.is_completed:
            valid_actions = self.get_valid_actions()
            if not valid_actions:
                break
            chosen_action = action_callback(state, valid_actions)
            self.step(chosen_action)

        if state.settlement is None:
            raise RuntimeError("Round completed but settlement was not generated.")
        return state.settlement

    def _require_active_state(self) -> RoundState:
        """Ensure a round is currently initialized."""
        if self.current_state is None:
            raise RuntimeError("No round has been started. Call start_round() first.")
        return self.current_state
