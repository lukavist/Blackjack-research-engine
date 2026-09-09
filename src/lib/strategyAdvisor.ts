/**
 * Client-side Strategy Advisor and Hi-Lo helpers.
 *
 * IMPORTANT: this file does NOT reimplement basic strategy or Illustrious 18 /
 * Fab Four logic. All of that lives in `blackjack/strategy/` (Python) and is
 * exported to `strategyData.generated.json` by `scripts/generate_strategy_data.py`.
 * This module only looks values up in that table and applies the same
 * legal-action fallback the Python engine uses. If you need to change a
 * strategy decision, change the Python source and regenerate the JSON --
 * never hand-edit the numbers here.
 */
import strategyData from './strategyData.generated.json';

export interface AdvisorResult {
  recommendedAction: 'HIT' | 'STAND' | 'DOUBLE' | 'SPLIT' | 'SURRENDER';
  isDeviation: boolean;
  reason: string;
}

type Action = AdvisorResult['recommendedAction'];

interface HandDecisionRow {
  initial: Action;
  noSurrender: Action;
  hitOnly: Action;
}

interface Deviation {
  index: string;
  description: string;
  hand_kind: 'hard' | 'pair10';
  hand_value: number;
  dealer_upcard: number;
  action: Action;
  comparator: '>=' | '<';
  threshold: number;
  requires_action: string;
  rule_condition: 's17_only' | 'h17_only' | null;
}

interface StrategyData {
  dealerUpcards: number[];
  hard: Record<string, Record<string, Record<string, HandDecisionRow>>>;
  soft: Record<string, Record<string, Record<string, HandDecisionRow>>>;
  pairs: Record<string, Record<string, Record<string, Action>>>;
  deviations: Deviation[];
  insurance: { action: 'TAKE'; trueCountThreshold: number };
}

const DATA = strategyData as unknown as StrategyData;

export function getHiLoTag(rank: string): number {
  if (['2', '3', '4', '5', '6'].includes(rank)) return 1;
  if (['7', '8', '9'].includes(rank)) return 0;
  return -1; // 10, J, Q, K, A
}

export function calculateDecksRemaining(totalCards: number, cardsSeen: number): number {
  const cardsLeft = Math.max(totalCards - cardsSeen, 0);
  return Math.max(cardsLeft / 52, 0.5);
}

export function calculateTrueCount(runningCount: number, decksRemaining: number): number {
  return runningCount / Math.max(decksRemaining, 0.5);
}

/** Should insurance be taken? Mirrors HiLoDeviationStrategy.decide_insurance. */
export function shouldTakeInsurance(insuranceAllowed: boolean, trueCount: number): boolean {
  return insuranceAllowed && trueCount >= DATA.insurance.trueCountThreshold;
}

function rulesKey(rules: { dealerHitsSoft17: boolean; doubleAfterSplit: boolean; lateSurrender: boolean }): string {
  const h17 = rules.dealerHitsSoft17 ? 'h17' : 's17';
  const das = rules.doubleAfterSplit ? 'das' : 'nodas';
  const ls = rules.lateSurrender ? 'ls' : 'nols';
  return `${h17}_${das}_${ls}`;
}

/** Maps a card's rank to the pair-table key used in strategyData.generated.json. */
function pairRankKey(rank: string, value: number): string {
  if (rank === 'A') return 'A';
  if (value === 10) return '10'; // 10, J, Q, K all share one pair-strategy row
  return rank;
}

export function adviseAction(
  playerHand: { cards: { rank: string; value: number }[]; isSoft: boolean; value: number; canSplit?: boolean },
  dealerUpcard: { rank: string; value: number } | null,
  validActions: string[],
  rules: { dealerHitsSoft17: boolean; doubleAfterSplit: boolean; lateSurrender: boolean },
  trueCount: number = 0
): AdvisorResult | null {
  if (!dealerUpcard || playerHand.cards.length === 0) return null;

  const upVal = dealerUpcard.rank === 'A' ? 11 : dealerUpcard.value;
  const pCards = playerHand.cards;
  const pVal = playerHand.value;
  const canDouble = validActions.includes('DOUBLE');
  const canSplit = validActions.includes('SPLIT');
  const canSurrender = validActions.includes('SURRENDER');
  const key = rulesKey(rules);

  // --- 1. ILLUSTRIOUS 18 / FAB FOUR DEVIATIONS ---
  // Same precedence as HiLoDeviationStrategy.decide(): deviations are checked
  // before falling back to plain basic strategy.
  const isTenPair = pCards.length === 2 && pCards[0].value === 10 && pCards[1].value === 10;

  for (const dev of DATA.deviations) {
    if (dev.dealer_upcard !== upVal) continue;
    if (!validActions.includes(dev.requires_action)) continue;
    if (dev.rule_condition === 's17_only' && rules.dealerHitsSoft17) continue;
    if (dev.rule_condition === 'h17_only' && !rules.dealerHitsSoft17) continue;

    if (dev.hand_kind === 'pair10') {
      if (!isTenPair) continue;
      if (dev.requires_action === 'SPLIT' && !canSplit) continue;
    } else {
      if (playerHand.isSoft || pVal !== dev.hand_value) continue;
      if (dev.action === 'SURRENDER' && (!canSurrender || pCards.length !== 2)) continue;
    }

    const triggered = dev.comparator === '>=' ? trueCount >= dev.threshold : trueCount < dev.threshold;
    if (!triggered) continue;

    return { recommendedAction: dev.action, isDeviation: true, reason: `${dev.index}: ${dev.description}` };
  }

  // --- 2. PAIR SPLITTING (BASIC STRATEGY) ---
  const isPair = pCards.length === 2 && (pCards[0].rank === pCards[1].rank || isTenPair);
  if (isPair && canSplit) {
    const rankKey = pairRankKey(pCards[0].rank, pCards[0].value);
    const action = DATA.pairs[key]?.[rankKey]?.[String(upVal)];
    if (action) {
      return {
        recommendedAction: action,
        isDeviation: false,
        reason: action === 'SPLIT'
          ? `Basic Strategy: Split ${rankKey},${rankKey} vs ${upVal === 11 ? 'A' : upVal}`
          : `Basic Strategy: ${action} on ${rankKey},${rankKey} vs ${upVal === 11 ? 'A' : upVal}`,
      };
    }
  }

  // --- 3. HARD / SOFT TOTALS (BASIC STRATEGY LOOKUP) ---
  const table = playerHand.isSoft ? DATA.soft[key] : DATA.hard[key];
  const row = table?.[String(pVal)]?.[String(upVal)];
  if (!row) {
    // Value outside the generated range (e.g. already-busted or a fresh
    // single-card hand); default to the conservative play.
    return { recommendedAction: 'HIT', isDeviation: false, reason: `Basic Strategy: Hit on ${pVal}` };
  }

  const context: keyof HandDecisionRow = pCards.length !== 2 ? 'hitOnly' : canSurrender ? 'initial' : canDouble ? 'noSurrender' : 'hitOnly';
  const action = row[context];
  const kind = playerHand.isSoft ? `Soft ${pVal}` : `Hard ${pVal}`;
  return { recommendedAction: action, isDeviation: false, reason: `Basic Strategy: ${action} on ${kind} vs ${upVal === 11 ? 'A' : upVal}` };
}
