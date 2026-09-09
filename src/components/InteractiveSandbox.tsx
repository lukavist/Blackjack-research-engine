import React, { useState } from 'react';
import { BankrollLedger } from './BankrollLedger';
import { CountingHUD } from './CountingHUD';
import { PlayArea } from './PlayArea';
import { RulesPanel } from './RulesPanel';
import { RoundTraceLog } from './RoundTraceLog';
import { adviseAction, getHiLoTag, calculateDecksRemaining, calculateTrueCount } from '../lib/strategyAdvisor';
import {
  CardData,
  HandData,
  PersistentBankrollData,
  DEFAULT_BANKROLL,
  loadPersistentBankroll,
  savePersistentBankroll,
  SUIT_SYMBOLS,
} from '../types';

interface InteractiveSandboxProps {
  bankrollData: PersistentBankrollData;
  setBankrollData: React.Dispatch<React.SetStateAction<PersistentBankrollData>>;
  totalProfitLoss: number;
  totalProfitLossPct: number;
}

export const InteractiveSandbox: React.FC<InteractiveSandboxProps> = ({
  bankrollData,
  setBankrollData,
  totalProfitLoss,
  totalProfitLossPct,
}) => {
  const [insuranceWagerLost, setInsuranceWagerLost] = useState<number>(0);

  // Table Configuration State
  const [numDecks, setNumDecks] = useState<number>(6);
  const [penetration, setPenetration] = useState<number>(0.75);
  const [dealerHitsSoft17, setDealerHitsSoft17] = useState<boolean>(false);
  const [doubleAfterSplit, setDoubleAfterSplit] = useState<boolean>(true);
  const [lateSurrender, setLateSurrender] = useState<boolean>(true);
  const [insuranceAllowed, setInsuranceAllowed] = useState<boolean>(true);
  const [wager, setWager] = useState<number>(25);

  const recordRoundSettlement = (roundProfit: number, roundWager: number) => {
    setBankrollData((prev) => {
      const newBankroll = Math.round((prev.bankroll + roundProfit) * 100) / 100;
      const newPeak = Math.max(prev.peakBankroll, newBankroll);
      const updated: PersistentBankrollData = {
        bankroll: newBankroll,
        initialBankroll: prev.initialBankroll,
        totalRounds: prev.totalRounds + 1,
        peakBankroll: newPeak,
        totalWagered: Math.round((prev.totalWagered + roundWager) * 100) / 100,
      };
      savePersistentBankroll(updated);
      return updated;
    });
  };

  const handleResetBankroll = (amount: number = DEFAULT_BANKROLL) => {
    const resetData: PersistentBankrollData = {
      bankroll: amount,
      initialBankroll: amount,
      totalRounds: 0,
      peakBankroll: amount,
      totalWagered: 0,
    };
    setBankrollData(resetData);
    savePersistentBankroll(resetData);
  };

  const handleReloadBankroll = (reloadAmount: number = 500) => {
    setBankrollData((prev) => {
      const newBankroll = Math.round((prev.bankroll + reloadAmount) * 100) / 100;
      const updated: PersistentBankrollData = {
        ...prev,
        bankroll: newBankroll,
        initialBankroll: prev.initialBankroll + reloadAmount,
        peakBankroll: Math.max(prev.peakBankroll, newBankroll),
      };
      savePersistentBankroll(updated);
      return updated;
    });
  };

  // Round Simulation State
  const [roundNumber, setRoundNumber] = useState<number>(1);
  const [gameState, setGameState] = useState<'idle' | 'in_progress' | 'insurance_offered' | 'completed'>('idle');
  const [playerHands, setPlayerHands] = useState<HandData[]>([]);
  const [currentHandIdx, setCurrentHandIdx] = useState<number>(0);
  const [dealerCards, setDealerCards] = useState<CardData[]>([]);
  const [dealerHoleHidden, setDealerHoleHidden] = useState<boolean>(true);
  const [logMessages, setLogMessages] = useState<string[]>([]);
  const [cardsDealt, setCardsDealt] = useState<number>(0);
  const [roundResultSummary, setRoundResultSummary] = useState<string | null>(null);
  const [netProfit, setNetProfit] = useState<number>(0);

  // Hi-Lo Card Counting State (observer pattern: no hole card leak)
  const [runningCount, setRunningCount] = useState<number>(0);
  const [cardsSeen, setCardsSeen] = useState<number>(0);

  const totalCardsInShoe = numDecks * 52;
  const cutCardThreshold = Math.floor(totalCardsInShoe * penetration);
  const decksRemaining = calculateDecksRemaining(totalCardsInShoe, cardsSeen);
  const trueCount = calculateTrueCount(runningCount, decksRemaining);

  const getSpreadAdvice = () => {
    const tcFloor = Math.floor(trueCount);
    if (tcFloor <= 1) return { units: 1, bet: wager, desc: `1 unit ($${wager}) - Standard Table Min` };
    if (tcFloor === 2) return { units: 2, bet: wager * 2, desc: `2 units ($${wager * 2}) - TC +2 Advantage` };
    if (tcFloor === 3) return { units: 4, bet: wager * 4, desc: `4 units ($${wager * 4}) - TC +3 High Advantage` };
    return { units: 8, bet: wager * 8, desc: `8 units ($${wager * 8}) - TC ≥ +4 Max Advantage` };
  };

  const calculateHandPoints = (cards: CardData[]) => {
    let total = cards.reduce((acc, c) => acc + c.value, 0);
    let aces = cards.filter((c) => c.rank === 'A').length;
    while (total > 21 && aces > 0) {
      total -= 10;
      aces -= 1;
    }
    return {
      value: total,
      isSoft: aces > 0 && cards.some((c) => c.rank === 'A'),
      isBust: total > 21,
      isBlackjack: cards.length === 2 && total === 21,
    };
  };

  const drawRandomCard = (): CardData => {
    const ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
    const suits = ['S', 'H', 'D', 'C'];
    const rank = ranks[Math.floor(Math.random() * ranks.length)];
    const suit = suits[Math.floor(Math.random() * suits.length)];
    let val = 0;
    if (['10', 'J', 'Q', 'K'].includes(rank)) val = 10;
    else if (rank === 'A') val = 11;
    else val = parseInt(rank, 10);
    return { rank, suit, value: val };
  };

  const resetShoeAndCount = () => {
    setCardsDealt(0);
    setCardsSeen(0);
    setRunningCount(0);
  };

  const startNewRound = () => {
    if (bankrollData.bankroll <= 0) {
      alert('Bankroll depleted! Please click "+$500 Reload" or "Reset to $1,000" to continue.');
      return;
    }

    const effectiveWager = Math.min(wager, bankrollData.bankroll);
    if (effectiveWager !== wager) {
      setWager(effectiveWager);
    }
    setInsuranceWagerLost(0);

    let currentCardsDealt = cardsDealt;
    let curRC = runningCount;
    let curSeen = cardsSeen;

    if (currentCardsDealt >= cutCardThreshold) {
      currentCardsDealt = 0;
      curRC = 0;
      curSeen = 0;
    }

    const p1 = drawRandomCard();
    const d1 = drawRandomCard();
    const p2 = drawRandomCard();
    const d2 = drawRandomCard();

    curRC += getHiLoTag(p1.rank) + getHiLoTag(p2.rank) + getHiLoTag(d1.rank);
    curSeen += 3;

    setRunningCount(curRC);
    setCardsSeen(curSeen);

    const initialPlayerCards = [p1, p2];
    const initialDealerCards = [d1, d2];
    const pPoints = calculateHandPoints(initialPlayerCards);
    const dPoints = calculateHandPoints(initialDealerCards);

    const initialPlayerHand: HandData = {
      cards: initialPlayerCards,
      bet: effectiveWager,
      status: 'ACTIVE',
      ...pPoints,
    };

    setCardsDealt(currentCardsDealt + 4);
    const newLogs = [
      `=== Round #${roundNumber} Started (Wager: $${effectiveWager}) ===`,
      `Visible deal: Player [${p1.rank}${SUIT_SYMBOLS[p1.suit].symbol}, ${p2.rank}${SUIT_SYMBOLS[p2.suit].symbol}] (${pPoints.value} ${pPoints.isSoft ? 'soft' : 'hard'}), Dealer upcard: [${d1.rank}${SUIT_SYMBOLS[d1.suit].symbol}]`,
      `Hi-Lo Count: RC ${curRC >= 0 ? '+' : ''}${curRC}, TC ${(curRC / Math.max((totalCardsInShoe - curSeen) / 52, 0.5)).toFixed(1)}`,
    ];

    setPlayerHands([initialPlayerHand]);
    setCurrentHandIdx(0);
    setDealerCards(initialDealerCards);
    setDealerHoleHidden(true);
    setRoundResultSummary(null);
    setNetProfit(0);

    if (insuranceAllowed && d1.rank === 'A') {
      newLogs.push('Dealer shows Ace. Insurance decision offered.');
      setGameState('insurance_offered');
      setLogMessages(newLogs);
      return;
    }

    if (d1.value === 10 || d1.rank === 'A') {
      if (dPoints.isBlackjack || pPoints.isBlackjack) {
        resolveImmediateBlackjack(pPoints.isBlackjack, dPoints.isBlackjack, initialPlayerHand, initialDealerCards, newLogs, curRC, curSeen);
        return;
      }
    } else if (pPoints.isBlackjack) {
      resolveImmediateBlackjack(true, false, initialPlayerHand, initialDealerCards, newLogs, curRC, curSeen);
      return;
    }

    setGameState('in_progress');
    setLogMessages(newLogs);
  };

  const resolveImmediateBlackjack = (
    pBJ: boolean,
    dBJ: boolean,
    playerHand: HandData,
    dealerHand: CardData[],
    currentLogs: string[],
    rc: number,
    seen: number
  ) => {
    setDealerHoleHidden(false);
    const updatedRC = rc + getHiLoTag(dealerHand[1].rank);
    setRunningCount(updatedRC);
    setCardsSeen(seen + 1);

    const logs = [...currentLogs, `Dealer reveals hole card: [${dealerHand[1].rank}${SUIT_SYMBOLS[dealerHand[1].suit].symbol}]`];
    let profit = 0;
    if (pBJ && dBJ) {
      logs.push('Outcome: PUSH (Both Player and Dealer hold natural Blackjack)');
      setRoundResultSummary('PUSH');
      setNetProfit(0);
    } else if (pBJ) {
      profit = playerHand.bet * 1.5;
      logs.push(`Outcome: BLACKJACK! Paid 3:2 (+${profit.toFixed(2)})`);
      setRoundResultSummary('BLACKJACK (+3:2)');
      setNetProfit(profit);
    } else if (dBJ) {
      profit = -playerHand.bet;
      logs.push(`Outcome: LOSS (Dealer natural Blackjack, -$${playerHand.bet.toFixed(2)})`);
      setRoundResultSummary('LOSS');
      setNetProfit(profit);
    }

    recordRoundSettlement(profit, playerHand.bet);
    const newBankroll = bankrollData.bankroll + profit;
    const newPL = totalProfitLoss + profit;
    logs.push(`[Ledger: Bankroll $${newBankroll.toFixed(2)} | Multi-Session P/L: ${newPL >= 0 ? '+' : ''}$${newPL.toFixed(2)}]`);

    setGameState('completed');
    setRoundNumber((r) => r + 1);
    setLogMessages(logs);
  };

  const handleInsuranceDecision = (takeInsurance: boolean) => {
    const logs = [...logMessages];
    const dPoints = calculateHandPoints(dealerCards);
    const pPoints = playerHands[0];
    const insBet = takeInsurance ? wager * 0.5 : 0;

    logs.push(takeInsurance ? `Player takes Insurance for $${insBet.toFixed(2)}` : 'Player declines Insurance');

    if (dPoints.isBlackjack) {
      setDealerHoleHidden(false);
      setRunningCount((rc) => rc + getHiLoTag(dealerCards[1].rank));
      setCardsSeen((cs) => cs + 1);

      logs.push(`Dealer reveals Blackjack with [${dealerCards[1].rank}${SUIT_SYMBOLS[dealerCards[1].suit].symbol}]!`);
      const insProfit = takeInsurance ? insBet * 2 : 0;
      const handProfit = pPoints.isBlackjack ? 0 : -wager;
      const total = insProfit + handProfit;

      logs.push(`Round settled. Total Net Profit: $${total.toFixed(2)}`);
      setRoundResultSummary(dPoints.isBlackjack && pPoints.isBlackjack ? 'PUSH' : 'LOSS');
      setNetProfit(total);

      recordRoundSettlement(total, wager + insBet);
      const newBankroll = bankrollData.bankroll + total;
      const newPL = totalProfitLoss + total;
      logs.push(`[Ledger: Bankroll $${newBankroll.toFixed(2)} | Multi-Session P/L: ${newPL >= 0 ? '+' : ''}$${newPL.toFixed(2)}]`);

      setGameState('completed');
      setRoundNumber((r) => r + 1);
    } else {
      if (takeInsurance) {
        logs.push(`Dealer does NOT have Blackjack. Insurance bet (-$${insBet.toFixed(2)}) is collected by dealer.`);
        setInsuranceWagerLost(insBet);
      }
      if (pPoints.isBlackjack) {
        resolveImmediateBlackjack(true, false, pPoints, dealerCards, logs, runningCount, cardsSeen);
        return;
      }
      setGameState('in_progress');
    }
    setLogMessages(logs);
  };

  const handleHit = () => {
    if (gameState !== 'in_progress') return;
    const newCard = drawRandomCard();
    setCardsDealt((c) => c + 1);
    setRunningCount((rc) => rc + getHiLoTag(newCard.rank));
    setCardsSeen((cs) => cs + 1);

    const activeHand = playerHands[currentHandIdx];
    const updatedCards = [...activeHand.cards, newCard];
    const pPoints = calculateHandPoints(updatedCards);

    const updatedHand: HandData = {
      ...activeHand,
      cards: updatedCards,
      ...pPoints,
      status: pPoints.isBust ? 'BUSTED' : pPoints.value === 21 ? 'STOOD' : 'ACTIVE',
    };

    const newPlayerHands = [...playerHands];
    newPlayerHands[currentHandIdx] = updatedHand;
    setPlayerHands(newPlayerHands);

    const logs = [
      ...logMessages,
      `Player hits: draws [${newCard.rank}${SUIT_SYMBOLS[newCard.suit].symbol}] -> Total: ${pPoints.value} (${pPoints.isSoft ? 'soft' : 'hard'})`,
    ];

    if (pPoints.isBust || pPoints.value === 21) {
      if (pPoints.isBust) logs.push(`Hand #${currentHandIdx + 1} BUSTS with ${pPoints.value}!`);
      else logs.push(`Hand #${currentHandIdx + 1} reached 21. Standing automatically.`);
      setLogMessages(logs);
      advanceOrDealerTurn(newPlayerHands, currentHandIdx, logs);
    } else {
      setLogMessages(logs);
    }
  };

  const handleStand = () => {
    if (gameState !== 'in_progress') return;
    const activeHand = playerHands[currentHandIdx];
    const newPlayerHands = [...playerHands];
    newPlayerHands[currentHandIdx] = { ...activeHand, status: 'STOOD' };
    setPlayerHands(newPlayerHands);

    const logs = [...logMessages, `Player stands on Hand #${currentHandIdx + 1} (${activeHand.value})`];
    setLogMessages(logs);
    advanceOrDealerTurn(newPlayerHands, currentHandIdx, logs);
  };

  const handleDouble = () => {
    if (gameState !== 'in_progress') return;
    const activeHand = playerHands[currentHandIdx];
    const newCard = drawRandomCard();
    setCardsDealt((c) => c + 1);
    setRunningCount((rc) => rc + getHiLoTag(newCard.rank));
    setCardsSeen((cs) => cs + 1);

    const updatedCards = [...activeHand.cards, newCard];
    const pPoints = calculateHandPoints(updatedCards);

    const updatedHand: HandData = {
      ...activeHand,
      bet: activeHand.bet * 2,
      cards: updatedCards,
      ...pPoints,
      status: pPoints.isBust ? 'BUSTED' : 'DOUBLED',
    };

    const newPlayerHands = [...playerHands];
    newPlayerHands[currentHandIdx] = updatedHand;
    setPlayerHands(newPlayerHands);

    const logs = [
      ...logMessages,
      `Player doubles to $${updatedHand.bet.toFixed(2)}: draws [${newCard.rank}${SUIT_SYMBOLS[newCard.suit].symbol}] -> Total: ${pPoints.value}`,
    ];
    if (pPoints.isBust) logs.push(`Hand #${currentHandIdx + 1} BUSTS on double!`);
    setLogMessages(logs);
    advanceOrDealerTurn(newPlayerHands, currentHandIdx, logs);
  };

  const handleSurrender = () => {
    if (gameState !== 'in_progress') return;
    const activeHand = playerHands[currentHandIdx];
    const newPlayerHands = [...playerHands];
    newPlayerHands[currentHandIdx] = { ...activeHand, status: 'SURRENDERED' };
    setPlayerHands(newPlayerHands);

    const logs = [...logMessages, `Player surrenders Hand #${currentHandIdx + 1}. Forfeits $${(activeHand.bet * 0.5).toFixed(2)}`];
    setLogMessages(logs);
    advanceOrDealerTurn(newPlayerHands, currentHandIdx, logs);
  };

  const handleSplit = () => {
    if (gameState !== 'in_progress') return;
    const activeHand = playerHands[currentHandIdx];
    if (activeHand.cards.length !== 2) return;

    const [card1, card2] = activeHand.cards;
    const newC1 = drawRandomCard();
    const newC2 = drawRandomCard();
    setCardsDealt((c) => c + 2);
    setRunningCount((rc) => rc + getHiLoTag(newC1.rank) + getHiLoTag(newC2.rank));
    setCardsSeen((cs) => cs + 2);

    const h1Cards = [card1, newC1];
    const h2Cards = [card2, newC2];
    const h1: HandData = { cards: h1Cards, bet: activeHand.bet, status: 'ACTIVE', ...calculateHandPoints(h1Cards) };
    const h2: HandData = { cards: h2Cards, bet: activeHand.bet, status: 'ACTIVE', ...calculateHandPoints(h2Cards) };

    const newHands = [...playerHands.slice(0, currentHandIdx), h1, h2, ...playerHands.slice(currentHandIdx + 1)];
    setPlayerHands(newHands);
    setLogMessages([...logMessages, `Player splits pair [${card1.rank}, ${card2.rank}]. Created 2 hands.`]);
  };

  const advanceOrDealerTurn = (hands: HandData[], currentIdx: number, currentLogs: string[]) => {
    const nextIdx = currentIdx + 1;
    if (nextIdx < hands.length) {
      setCurrentHandIdx(nextIdx);
    } else {
      executeDealerTurn(hands, currentLogs);
    }
  };

  const executeDealerTurn = (hands: HandData[], currentLogs: string[]) => {
    setDealerHoleHidden(false);
    let updatedRC = runningCount + getHiLoTag(dealerCards[1].rank);
    let updatedSeen = cardsSeen + 1;
    const logs = [...currentLogs, `Dealer reveals hole card: [${dealerCards[1].rank}${SUIT_SYMBOLS[dealerCards[1].suit].symbol}]`];

    const hasEligibleHands = hands.some((h) => h.status !== 'BUSTED' && h.status !== 'SURRENDERED');
    let currentDealerCards = [...dealerCards];
    let dPoints = calculateHandPoints(currentDealerCards);

    if (hasEligibleHands) {
      while (dPoints.value < 17 || (dPoints.value === 17 && dPoints.isSoft && dealerHitsSoft17)) {
        const nextCard = drawRandomCard();
        currentDealerCards = [...currentDealerCards, nextCard];
        dPoints = calculateHandPoints(currentDealerCards);
        updatedRC += getHiLoTag(nextCard.rank);
        updatedSeen += 1;
        logs.push(`Dealer hits: [${nextCard.rank}${SUIT_SYMBOLS[nextCard.suit].symbol}] -> Total: ${dPoints.value} (${dPoints.isSoft ? 'soft' : 'hard'})`);
      }
    }

    setRunningCount(updatedRC);
    setCardsSeen(updatedSeen);
    setDealerCards(currentDealerCards);
    logs.push(dPoints.isBust ? `Dealer BUSTS with ${dPoints.value}!` : `Dealer stands with ${dPoints.value}.`);

    let totalNet = 0;
    let totalWageredRound = 0;
    hands.forEach((hand, idx) => {
      let outcome = '';
      let profit = 0;
      if (hand.status === 'SURRENDERED') {
        outcome = 'SURRENDER';
        profit = -hand.bet * 0.5;
      } else if (hand.isBust) {
        outcome = 'LOSS';
        profit = -hand.bet;
      } else if (dPoints.isBust || hand.value > dPoints.value) {
        outcome = 'WIN';
        profit = hand.bet;
      } else if (hand.value < dPoints.value) {
        outcome = 'LOSS';
        profit = -hand.bet;
      } else {
        outcome = 'PUSH';
        profit = 0;
      }
      totalNet += profit;
      totalWageredRound += hand.bet;
      logs.push(`Hand #${idx + 1} Result: ${outcome} (Wager: $${hand.bet}, Profit: ${profit >= 0 ? '+' : ''}$${profit.toFixed(2)})`);
    });

    if (insuranceWagerLost > 0) {
      totalNet -= insuranceWagerLost;
      totalWageredRound += insuranceWagerLost;
      logs.push(`Insurance deduction: -$${insuranceWagerLost.toFixed(2)}`);
    }

    setNetProfit(totalNet);
    recordRoundSettlement(totalNet, totalWageredRound);
    const newBankroll = bankrollData.bankroll + totalNet;
    const newPL = totalProfitLoss + totalNet;
    logs.push(`[Ledger: Bankroll $${newBankroll.toFixed(2)} | Multi-Session P/L: ${newPL >= 0 ? '+' : ''}$${newPL.toFixed(2)}]`);

    setRoundResultSummary(totalNet > 0 ? 'WIN' : totalNet < 0 ? 'LOSS' : 'PUSH');
    setGameState('completed');
    setRoundNumber((r) => r + 1);
    setLogMessages(logs);
  };

  const activePlayerHand = playerHands[currentHandIdx];
  const canDouble = !!(activePlayerHand && activePlayerHand.cards.length === 2 && gameState === 'in_progress');
  const canSurrender = !!(activePlayerHand && activePlayerHand.cards.length === 2 && lateSurrender && gameState === 'in_progress');
  const canSplit = !!(
    activePlayerHand &&
    activePlayerHand.cards.length === 2 &&
    (activePlayerHand.cards[0].rank === activePlayerHand.cards[1].rank ||
      (activePlayerHand.cards[0].value === 10 && activePlayerHand.cards[1].value === 10)) &&
    gameState === 'in_progress'
  );

  const validActions = ['STAND', 'HIT'];
  if (canDouble) validActions.push('DOUBLE');
  if (canSplit) validActions.push('SPLIT');
  if (canSurrender) validActions.push('SURRENDER');

  const strategyAdvice = activePlayerHand && dealerCards.length > 0 && gameState === 'in_progress'
    ? adviseAction(activePlayerHand, dealerCards[0], validActions, { dealerHitsSoft17, doubleAfterSplit, lateSurrender }, trueCount)
    : null;

  const spreadAdvice = getSpreadAdvice();

  return (
    <div className="space-y-6">
      <BankrollLedger
        bankrollData={bankrollData}
        totalProfitLoss={totalProfitLoss}
        totalProfitLossPct={totalProfitLossPct}
        wager={wager}
        setWager={setWager}
        spreadAdvice={spreadAdvice}
        gameState={gameState}
        handleReloadBankroll={handleReloadBankroll}
        handleResetBankroll={handleResetBankroll}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <CountingHUD
            runningCount={runningCount}
            trueCount={trueCount}
            decksRemaining={decksRemaining}
            numDecks={numDecks}
            spreadAdvice={spreadAdvice}
            cardsDealt={cardsDealt}
            totalCardsInShoe={totalCardsInShoe}
            cutCardThreshold={cutCardThreshold}
            penetration={penetration}
            resetShoeAndCount={resetShoeAndCount}
          />

          <PlayArea
            dealerCards={dealerCards}
            dealerHoleHidden={dealerHoleHidden}
            calculateHandPoints={calculateHandPoints}
            gameState={gameState}
            trueCount={trueCount}
            wager={wager}
            handleInsuranceDecision={handleInsuranceDecision}
            playerHands={playerHands}
            currentHandIdx={currentHandIdx}
            strategyAdvice={strategyAdvice}
            startNewRound={startNewRound}
            handleHit={handleHit}
            handleStand={handleStand}
            handleDouble={handleDouble}
            handleSplit={handleSplit}
            handleSurrender={handleSurrender}
            canDouble={canDouble}
            canSplit={canSplit}
            canSurrender={canSurrender}
            lateSurrender={lateSurrender}
          />
        </div>

        <div className="space-y-6">
          <RulesPanel
            numDecks={numDecks}
            setNumDecks={setNumDecks}
            penetration={penetration}
            setPenetration={setPenetration}
            dealerHitsSoft17={dealerHitsSoft17}
            setDealerHitsSoft17={setDealerHitsSoft17}
            doubleAfterSplit={doubleAfterSplit}
            setDoubleAfterSplit={setDoubleAfterSplit}
            lateSurrender={lateSurrender}
            setLateSurrender={setLateSurrender}
            insuranceAllowed={insuranceAllowed}
            setInsuranceAllowed={setInsuranceAllowed}
            resetShoeAndCount={resetShoeAndCount}
          />

          <RoundTraceLog
            logMessages={logMessages}
            roundResultSummary={roundResultSummary}
            netProfit={netProfit}
          />
        </div>
      </div>
    </div>
  );
};
