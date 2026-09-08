/**
 * Client-side Strategy Advisor and Hi-Lo Calculation
 * Directly mirrors the mathematical logic in python blackjack/strategy/
 */

export interface AdvisorResult {
  recommendedAction: 'HIT' | 'STAND' | 'DOUBLE' | 'SPLIT' | 'SURRENDER';
  isDeviation: boolean;
  reason: string;
}

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

export function adviseAction(
  playerHand: { cards: { rank: string; value: number }[]; isSoft: boolean; value: number; canSplit?: boolean },
  dealerUpcard: { rank: string; value: number } | null,
  validActions: string[],
  rules: { dealerHitsSoft17: boolean; doubleAfterSplit: boolean; lateSurrender: boolean },
  trueCount: number = 0
): AdvisorResult | null {
  if (!dealerUpcard || playerHand.cards.length === 0) return null;

  const upVal = dealerUpcard.rank === 'A' ? 11 : dealerUpcard.value;
  const tc = trueCount;
  const pCards = playerHand.cards;
  const pVal = playerHand.value;
  const canDouble = validActions.includes('DOUBLE');
  const canSplit = validActions.includes('SPLIT');
  const canSurrender = validActions.includes('SURRENDER');

  // --- 1. FAB FOUR SURRENDERS ---
  if (canSurrender && pCards.length === 2 && !playerHand.isSoft) {
    if (pVal === 14 && upVal === 10 && tc >= 3.0) {
      return { recommendedAction: 'SURRENDER', isDeviation: true, reason: 'Fab Four: Surrender 14 vs 10 at TC ≥ +3' };
    }
    if (pVal === 15 && upVal === 9 && tc >= 2.0) {
      return { recommendedAction: 'SURRENDER', isDeviation: true, reason: 'Fab Four: Surrender 15 vs 9 at TC ≥ +2' };
    }
    if (pVal === 15 && upVal === 11 && !rules.dealerHitsSoft17 && tc >= 1.0) {
      return { recommendedAction: 'SURRENDER', isDeviation: true, reason: 'Fab Four: Surrender 15 vs A at TC ≥ +1' };
    }
    // Basic strategy surrenders
    if (pVal === 16 && (upVal === 9 || upVal === 10 || upVal === 11)) {
      return { recommendedAction: 'SURRENDER', isDeviation: false, reason: 'Basic Strategy: Surrender 16 vs 9, 10, A' };
    }
    if (pVal === 15 && (upVal === 10 || (upVal === 11 && rules.dealerHitsSoft17))) {
      return { recommendedAction: 'SURRENDER', isDeviation: false, reason: 'Basic Strategy: Surrender 15 vs 10 (or A under H17)' };
    }
  }

  // --- 2. PAIR SPLITS & ILLUSTRIOUS 18 PAIR DEVIATIONS ---
  const isPair = pCards.length === 2 && (pCards[0].rank === pCards[1].rank || (pCards[0].value === 10 && pCards[1].value === 10));
  if (isPair && canSplit) {
    const c1 = pCards[0];
    const r = c1.rank;

    // Illustrious 18 #4 & #5: 10-10 vs 5/6 split
    if (c1.value === 10) {
      if (upVal === 5 && tc >= 5.0) {
        return { recommendedAction: 'SPLIT', isDeviation: true, reason: 'Illustrious 18 #4: Split 10,10 vs 5 at TC ≥ +5' };
      }
      if (upVal === 6 && tc >= 4.0) {
        return { recommendedAction: 'SPLIT', isDeviation: true, reason: 'Illustrious 18 #5: Split 10,10 vs 6 at TC ≥ +4' };
      }
    }

    if (r === 'A' || r === '8') {
      return { recommendedAction: 'SPLIT', isDeviation: false, reason: `Basic Strategy: Always split ${r},${r}` };
    }
    if (r === '9') {
      if ([2, 3, 4, 5, 6, 8, 9].includes(upVal)) {
        return { recommendedAction: 'SPLIT', isDeviation: false, reason: 'Basic Strategy: Split 9,9 vs 2-6, 8, 9' };
      }
      return { recommendedAction: 'STAND', isDeviation: false, reason: 'Basic Strategy: Stand 9,9 vs 7, 10, A' };
    }
    if (r === '7' && upVal >= 2 && upVal <= 7) {
      return { recommendedAction: 'SPLIT', isDeviation: false, reason: 'Basic Strategy: Split 7,7 vs 2-7' };
    }
    if (r === '6') {
      const maxUp = rules.doubleAfterSplit ? 6 : 6;
      const minUp = rules.doubleAfterSplit ? 2 : 3;
      if (upVal >= minUp && upVal <= maxUp) {
        return { recommendedAction: 'SPLIT', isDeviation: false, reason: `Basic Strategy: Split 6,6 vs ${minUp}-6` };
      }
    }
    if (r === '4' && rules.doubleAfterSplit && (upVal === 5 || upVal === 6)) {
      return { recommendedAction: 'SPLIT', isDeviation: false, reason: 'Basic Strategy: Split 4,4 vs 5, 6 with DAS' };
    }
    if ((r === '2' || r === '3')) {
      const minUp = rules.doubleAfterSplit ? 2 : 4;
      if (upVal >= minUp && upVal <= 7) {
        return { recommendedAction: 'SPLIT', isDeviation: false, reason: `Basic Strategy: Split ${r},${r} vs ${minUp}-7` };
      }
    }
  }

  // --- 3. ILLUSTRIOUS 18 HARD TOTAL DEVIATIONS ---
  if (!playerHand.isSoft) {
    if (pVal === 16 && upVal === 10) {
      if (tc >= 0.0) return { recommendedAction: 'STAND', isDeviation: true, reason: 'Illustrious 18 #2: Stand 16 vs 10 at TC ≥ 0' };
      return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit 16 vs 10 at TC < 0' };
    }
    if (pVal === 15 && upVal === 10) {
      if (tc >= 4.0) return { recommendedAction: 'STAND', isDeviation: true, reason: 'Illustrious 18 #3: Stand 15 vs 10 at TC ≥ +4' };
      return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit 15 vs 10 at TC < +4' };
    }
    if (pVal === 10 && upVal === 10 && canDouble && tc >= 4.0) {
      return { recommendedAction: 'DOUBLE', isDeviation: true, reason: 'Illustrious 18 #6: Double 10 vs 10 at TC ≥ +4' };
    }
    if (pVal === 10 && upVal === 11 && canDouble && tc >= 4.0) {
      return { recommendedAction: 'DOUBLE', isDeviation: true, reason: 'Illustrious 18 #11: Double 10 vs A at TC ≥ +4' };
    }
    if (pVal === 12 && upVal === 3) {
      if (tc >= 2.0) return { recommendedAction: 'STAND', isDeviation: true, reason: 'Illustrious 18 #7: Stand 12 vs 3 at TC ≥ +2' };
      return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit 12 vs 3 at TC < +2' };
    }
    if (pVal === 12 && upVal === 2) {
      if (tc >= 3.0) return { recommendedAction: 'STAND', isDeviation: true, reason: 'Illustrious 18 #8: Stand 12 vs 2 at TC ≥ +3' };
      return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit 12 vs 2 at TC < +3' };
    }
    if (pVal === 11 && upVal === 11 && !rules.dealerHitsSoft17 && canDouble && tc >= 1.0) {
      return { recommendedAction: 'DOUBLE', isDeviation: true, reason: 'Illustrious 18 #9: Double 11 vs A at TC ≥ +1' };
    }
    if (pVal === 9 && upVal === 2 && canDouble && tc >= 1.0) {
      return { recommendedAction: 'DOUBLE', isDeviation: true, reason: 'Illustrious 18 #10: Double 9 vs 2 at TC ≥ +1' };
    }
    if (pVal === 9 && upVal === 7 && canDouble && tc >= 3.0) {
      return { recommendedAction: 'DOUBLE', isDeviation: true, reason: 'Illustrious 18 #12: Double 9 vs 7 at TC ≥ +3' };
    }
    if (pVal === 16 && upVal === 9) {
      if (tc >= 5.0) return { recommendedAction: 'STAND', isDeviation: true, reason: 'Illustrious 18 #13: Stand 16 vs 9 at TC ≥ +5' };
    }
  }

  // --- 4. SOFT TOTALS (BASIC STRATEGY) ---
  if (playerHand.isSoft && pVal <= 21) {
    if (pVal >= 20) return { recommendedAction: 'STAND', isDeviation: false, reason: 'Basic Strategy: Always stand on Soft 20+' };
    if (pVal === 19) {
      if (rules.dealerHitsSoft17 && upVal === 6 && canDouble) {
        return { recommendedAction: 'DOUBLE', isDeviation: false, reason: 'Basic Strategy: Double A,8 vs 6 under H17' };
      }
      return { recommendedAction: 'STAND', isDeviation: false, reason: 'Basic Strategy: Stand on Soft 19' };
    }
    if (pVal === 18) {
      if (canDouble && ((rules.dealerHitsSoft17 && upVal >= 2 && upVal <= 6) || (!rules.dealerHitsSoft17 && upVal >= 3 && upVal <= 6))) {
        return { recommendedAction: 'DOUBLE', isDeviation: false, reason: 'Basic Strategy: Double Soft 18 vs dealer bust cards' };
      }
      if (upVal >= 2 && upVal <= 8) {
        return { recommendedAction: 'STAND', isDeviation: false, reason: 'Basic Strategy: Stand on Soft 18 vs 2-8' };
      }
      return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit Soft 18 vs 9, 10, A' };
    }
    if (pVal === 17) {
      if (canDouble && upVal >= 3 && upVal <= 6) {
        return { recommendedAction: 'DOUBLE', isDeviation: false, reason: 'Basic Strategy: Double Soft 17 vs 3-6' };
      }
      return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit Soft 17' };
    }
    if (pVal === 15 || pVal === 16) {
      if (canDouble && upVal >= 4 && upVal <= 6) {
        return { recommendedAction: 'DOUBLE', isDeviation: false, reason: `Basic Strategy: Double Soft ${pVal} vs 4-6` };
      }
      return { recommendedAction: 'HIT', isDeviation: false, reason: `Basic Strategy: Hit Soft ${pVal}` };
    }
    if (pVal === 13 || pVal === 14) {
      if (canDouble && upVal >= 5 && upVal <= 6) {
        return { recommendedAction: 'DOUBLE', isDeviation: false, reason: `Basic Strategy: Double Soft ${pVal} vs 5-6` };
      }
      return { recommendedAction: 'HIT', isDeviation: false, reason: `Basic Strategy: Hit Soft ${pVal}` };
    }
  }

  // --- 5. HARD TOTALS (BASIC STRATEGY) ---
  if (pVal >= 17) {
    return { recommendedAction: 'STAND', isDeviation: false, reason: 'Basic Strategy: Stand on Hard 17+' };
  }
  if (pVal >= 13 && pVal <= 16) {
    if (upVal >= 2 && upVal <= 6) {
      return { recommendedAction: 'STAND', isDeviation: false, reason: `Basic Strategy: Stand on Hard ${pVal} vs dealer bust card (${upVal})` };
    }
    return { recommendedAction: 'HIT', isDeviation: false, reason: `Basic Strategy: Hit Hard ${pVal} vs high dealer upcard (${upVal})` };
  }
  if (pVal === 12) {
    if (upVal >= 4 && upVal <= 6) {
      return { recommendedAction: 'STAND', isDeviation: false, reason: 'Basic Strategy: Stand 12 vs 4-6' };
    }
    return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit 12 vs 2, 3, 7-A' };
  }
  if (pVal === 11) {
    if (canDouble && (rules.dealerHitsSoft17 || upVal <= 10)) {
      return { recommendedAction: 'DOUBLE', isDeviation: false, reason: 'Basic Strategy: Double on 11' };
    }
    return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit on 11' };
  }
  if (pVal === 10) {
    if (canDouble && upVal >= 2 && upVal <= 9) {
      return { recommendedAction: 'DOUBLE', isDeviation: false, reason: 'Basic Strategy: Double on 10 vs 2-9' };
    }
    return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit on 10' };
  }
  if (pVal === 9) {
    if (canDouble && upVal >= 3 && upVal <= 6) {
      return { recommendedAction: 'DOUBLE', isDeviation: false, reason: 'Basic Strategy: Double on 9 vs 3-6' };
    }
    return { recommendedAction: 'HIT', isDeviation: false, reason: 'Basic Strategy: Hit on 9' };
  }

  return { recommendedAction: 'HIT', isDeviation: false, reason: `Basic Strategy: Hit on ${pVal}` };
}
