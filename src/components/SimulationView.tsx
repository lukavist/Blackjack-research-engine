import React, { useState, useRef } from 'react';
import { Play, RotateCcw, TrendingUp, BarChart3, ShieldCheck, Zap, Layers } from 'lucide-react';
import { adviseAction, getHiLoTag } from '../lib/strategyAdvisor';

interface SimulationResult {
  roundsPlayed: number;
  totalWagered: number;
  netProfit: number;
  evPerHand: number;
  roiPercent: number;
  winRate: number;
  maxDrawdown: number;
  finalBankroll: number;
  insuranceTaken: number;
  insuranceWon: number;
  elapsedSec: number;
  handsPerSec: number;
  trajectory: { round: number; bankroll: number }[];
}

export const SimulationView: React.FC<{
  numDecks: number;
  penetration: number;
  dealerHitsSoft17: boolean;
  doubleAfterSplit: boolean;
  lateSurrender: boolean;
}> = ({ numDecks, penetration, dealerHitsSoft17, doubleAfterSplit, lateSurrender }) => {
  const [numRounds, setNumRounds] = useState<number>(25000);
  const [spreadMaxUnits, setSpreadMaxUnits] = useState<number>(8);
  const [baseBet, setBaseBet] = useState<number>(10);
  const [startingBankroll, setStartingBankroll] = useState<number>(10000);

  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [progress, setProgress] = useState<number>(0);

  const [basicStats, setBasicStats] = useState<SimulationResult | null>(null);
  const [hiLoStats, setHiLoStats] = useState<SimulationResult | null>(null);

  const cancelRef = useRef<boolean>(false);

  // Fast client-side blackjack monte carlo simulation
  const runSimulation = async () => {
    setIsRunning(true);
    setProgress(0);
    cancelRef.current = false;

    const startT = performance.now();

    // Ranks and standard deck values
    const RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
    const RANK_VALUES: Record<string, number> = {
      '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
      '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11,
    };

    // Helper to generate and shuffle shoe
    const buildShoe = () => {
      const cards: { rank: string; value: number }[] = [];
      for (let d = 0; d < numDecks; d++) {
        for (let s = 0; s < 4; s++) {
          for (const r of RANKS) {
            cards.push({ rank: r, value: RANK_VALUES[r] });
          }
        }
      }
      // Fisher-Yates
      for (let i = cards.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        const temp = cards[i];
        cards[i] = cards[j];
        cards[j] = temp;
      }
      return cards;
    };

    // Evaluate hand value
    const evalHand = (cards: { rank: string; value: number }[]) => {
      let sum = cards.reduce((acc, c) => acc + c.value, 0);
      let aces = cards.filter((c) => c.rank === 'A').length;
      while (sum > 21 && aces > 0) {
        sum -= 10;
        aces--;
      }
      const isSoft = aces > 0;
      return { value: sum, isSoft, isBust: sum > 21, isBlackjack: cards.length === 2 && sum === 21 };
    };

    // Simulator for one system
    const simulateSystem = async (useHiLo: boolean): Promise<SimulationResult> => {
      let shoe = buildShoe();
      const cutThreshold = Math.floor(numDecks * 52 * penetration);

      let runningCount = 0;
      let cardsSeen = 0;

      let bankroll = startingBankroll;
      let peakBankroll = bankroll;
      let maxDrawdown = 0;

      let totalWagered = 0;
      let netProfit = 0;
      let wins = 0;
      let losses = 0;
      let decisive = 0;
      let insuranceTaken = 0;
      let insuranceWon = 0;

      const trajectory: { round: number; bankroll: number }[] = [{ round: 0, bankroll }];
      const sampleInterval = Math.max(Math.floor(numRounds / 100), 50);

      for (let r = 1; r <= numRounds; r++) {
        if (cancelRef.current) break;

        // Yield execution periodically to maintain responsive 60fps UI
        if (r % 1500 === 0) {
          setProgress(Math.floor(((useHiLo ? numRounds + r : r) / (numRounds * 2)) * 100));
          await new Promise((resolve) => setTimeout(resolve, 0));
        }

        // Reshuffle check
        if (shoe.length <= numDecks * 52 - cutThreshold) {
          shoe = buildShoe();
          runningCount = 0;
          cardsSeen = 0;
        }

        // 1. Bet sizing
        const decksRemaining = Math.max((numDecks * 52 - cardsSeen) / 52, 0.5);
        const trueCount = runningCount / decksRemaining;

        let bet = baseBet;
        if (useHiLo) {
          const tcFloor = Math.floor(trueCount);
          if (tcFloor <= 1) bet = baseBet;
          else if (tcFloor === 2) bet = baseBet * 2;
          else if (tcFloor === 3) bet = baseBet * 4;
          else bet = Math.min(baseBet * spreadMaxUnits, baseBet * 8);
        }
        totalWagered += bet;

        // 2. Deal
        const pCards = [shoe.pop()!, shoe.pop()!];
        const dCards = [shoe.pop()!, shoe.pop()!];

        // Track seen cards (player cards + dealer upcard)
        if (useHiLo) {
          runningCount += getHiLoTag(pCards[0].rank);
          runningCount += getHiLoTag(pCards[1].rank);
          runningCount += getHiLoTag(dCards[0].rank);
          cardsSeen += 3;
        }

        const dUpcard = dCards[0];
        const pEval = evalHand(pCards);
        const dEval = evalHand(dCards);

        // Insurance
        let insBet = 0;
        let insProfit = 0;
        if (dUpcard.rank === 'A') {
          if (useHiLo && trueCount >= 3.0) {
            insBet = bet * 0.5;
            insuranceTaken++;
            if (dEval.isBlackjack) {
              insProfit = insBet * 2.0;
              insuranceWon++;
            } else {
              insProfit = -insBet;
            }
          }
        }

        let roundProfit = insProfit;

        // Naturals
        if (dEval.isBlackjack || pEval.isBlackjack) {
          // Reveal hole card
          if (useHiLo) {
            runningCount += getHiLoTag(dCards[1].rank);
            cardsSeen += 1;
          }

          if (pEval.isBlackjack && dEval.isBlackjack) {
            roundProfit += 0; // Push
          } else if (pEval.isBlackjack) {
            roundProfit += bet * 1.5;
            wins++;
            decisive++;
          } else {
            roundProfit -= bet;
            losses++;
            decisive++;
          }
        } else {
          // Player decision loop
          let activeHandCards = [...pCards];
          let handBet = bet;
          let isSurrendered = false;

          while (true) {
            const curEval = evalHand(activeHandCards);
            if (curEval.isBust || curEval.value === 21) break;

            const valid = ['HIT', 'STAND'];
            if (activeHandCards.length === 2) {
              valid.push('DOUBLE');
              if (lateSurrender) valid.push('SURRENDER');
            }

            const adv = adviseAction(
              { cards: activeHandCards, isSoft: curEval.isSoft, value: curEval.value },
              dUpcard,
              valid,
              { dealerHitsSoft17, doubleAfterSplit, lateSurrender },
              useHiLo ? trueCount : 0
            );

            const action = adv ? adv.recommendedAction : 'STAND';

            if (action === 'SURRENDER') {
              isSurrendered = true;
              break;
            } else if (action === 'DOUBLE') {
              handBet *= 2;
              totalWagered += bet; // additional bet
              const card = shoe.pop()!;
              activeHandCards.push(card);
              if (useHiLo) {
                runningCount += getHiLoTag(card.rank);
                cardsSeen += 1;
              }
              break; // Stand after double
            } else if (action === 'HIT') {
              const card = shoe.pop()!;
              activeHandCards.push(card);
              if (useHiLo) {
                runningCount += getHiLoTag(card.rank);
                cardsSeen += 1;
              }
            } else {
              // Stand
              break;
            }
          }

          // Dealer plays
          if (useHiLo) {
            runningCount += getHiLoTag(dCards[1].rank);
            cardsSeen += 1;
          }

          if (isSurrendered) {
            roundProfit -= handBet * 0.5;
            losses++;
            decisive++;
          } else {
            const finalPEval = evalHand(activeHandCards);
            if (finalPEval.isBust) {
              roundProfit -= handBet;
              losses++;
              decisive++;
            } else {
              // Dealer draws to 17
              let finalDEval = evalHand(dCards);
              while (true) {
                if (finalDEval.value < 17 || (dealerHitsSoft17 && finalDEval.value === 17 && finalDEval.isSoft)) {
                  const card = shoe.pop()!;
                  dCards.push(card);
                  if (useHiLo) {
                    runningCount += getHiLoTag(card.rank);
                    cardsSeen += 1;
                  }
                  finalDEval = evalHand(dCards);
                } else {
                  break;
                }
              }

              // Outcome
              if (finalDEval.isBust || finalPEval.value > finalDEval.value) {
                roundProfit += handBet;
                wins++;
                decisive++;
              } else if (finalPEval.value < finalDEval.value) {
                roundProfit -= handBet;
                losses++;
                decisive++;
              } else {
                // Push
              }
            }
          }
        }

        bankroll += roundProfit;
        netProfit += roundProfit;

        if (bankroll > peakBankroll) peakBankroll = bankroll;
        const dd = peakBankroll - bankroll;
        if (dd > maxDrawdown) maxDrawdown = dd;

        if (r % sampleInterval === 0 || r === numRounds) {
          trajectory.push({ round: r, bankroll: Math.round(bankroll) });
        }
      }

      const elapsed = (performance.now() - startT) / 1000;
      return {
        roundsPlayed: numRounds,
        totalWagered,
        netProfit,
        evPerHand: netProfit / numRounds,
        roiPercent: (netProfit / totalWagered) * 100,
        winRate: decisive > 0 ? (wins / decisive) * 100 : 0,
        maxDrawdown,
        finalBankroll: bankroll,
        insuranceTaken,
        insuranceWon,
        elapsedSec: elapsed,
        handsPerSec: Math.round(numRounds / elapsed),
        trajectory,
      };
    };

    // Execute Basic Strategy first, then Hi-Lo
    const bsRes = await simulateSystem(false);
    setBasicStats(bsRes);

    const hiloRes = await simulateSystem(true);
    setHiLoStats(hiloRes);

    setProgress(100);
    setIsRunning(false);
  };

  return (
    <div id="simulation_view" className="space-y-6">
      {/* Simulation Controls Card */}
      <div className="p-6 rounded-2xl bg-stone-900 border border-stone-800 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-emerald-400" />
              Monte Carlo Strategy Simulator
            </h2>
            <p className="text-xs text-stone-400 mt-1">
              Simulates hundreds of thousands of hands in real-time comparing Basic Strategy vs. Hi-Lo Card Counting.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              id="run_simulation_btn"
              onClick={runSimulation}
              disabled={isRunning}
              className={`px-5 py-2.5 rounded-xl font-semibold text-xs flex items-center gap-2 transition ${
                isRunning
                  ? 'bg-stone-800 text-stone-500 cursor-not-allowed'
                  : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-950'
              }`}
            >
              <Play className="w-4 h-4 fill-white" />
              {isRunning ? `Simulating (${progress}%)...` : `Run ${numRounds.toLocaleString()} Rounds`}
            </button>
          </div>
        </div>

        {/* Config Inputs */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
            <label className="text-stone-400">Total Rounds</label>
            <select
              value={numRounds}
              onChange={(e) => setNumRounds(Number(e.target.value))}
              disabled={isRunning}
              className="w-full bg-stone-900 border border-stone-700 rounded-lg px-2.5 py-1.5 text-stone-200 font-mono"
            >
              <option value={5000}>5,000 Hands (~0.5s)</option>
              <option value={10000}>10,000 Hands (~1s)</option>
              <option value={25000}>25,000 Hands (~2.5s)</option>
              <option value={50000}>50,000 Hands (~5s)</option>
            </select>
          </div>

          <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
            <label className="text-stone-400">Hi-Lo Spread Max</label>
            <select
              value={spreadMaxUnits}
              onChange={(e) => setSpreadMaxUnits(Number(e.target.value))}
              disabled={isRunning}
              className="w-full bg-stone-900 border border-stone-700 rounded-lg px-2.5 py-1.5 text-stone-200 font-mono"
            >
              <option value={4}>1-to-4 Spread ($10 - $40)</option>
              <option value={8}>1-to-8 Spread ($10 - $80)</option>
              <option value={12}>1-to-12 Spread ($10 - $120)</option>
            </select>
          </div>

          <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
            <label className="text-stone-400">Base Unit Bet</label>
            <input
              type="number"
              min={5}
              max={100}
              value={baseBet}
              onChange={(e) => setBaseBet(Number(e.target.value))}
              disabled={isRunning}
              className="w-full bg-stone-900 border border-stone-700 rounded-lg px-2.5 py-1.5 text-stone-200 font-mono"
            />
          </div>

          <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
            <label className="text-stone-400">Starting Bankroll</label>
            <input
              type="number"
              min={1000}
              max={100000}
              step={1000}
              value={startingBankroll}
              onChange={(e) => setStartingBankroll(Number(e.target.value))}
              disabled={isRunning}
              className="w-full bg-stone-900 border border-stone-700 rounded-lg px-2.5 py-1.5 text-stone-200 font-mono"
            />
          </div>
        </div>

        {/* Progress Bar */}
        {isRunning && (
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs text-stone-400 font-mono">
              <span>Simulating game rounds across shoe deck states...</span>
              <span>{progress}%</span>
            </div>
            <div className="w-full h-2 rounded-full bg-stone-950 overflow-hidden border border-stone-800">
              <div
                className="h-full bg-emerald-500 transition-all duration-150"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Comparative Metrics Table */}
      {basicStats && hiLoStats && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Basic Strategy Card */}
            <div className="p-6 rounded-2xl bg-stone-900 border border-stone-800 space-y-4">
              <div className="flex items-center justify-between border-b border-stone-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-sky-400" />
                  <h3 className="font-bold text-white text-sm">Basic Strategy (Flat Bet)</h3>
                </div>
                <span className="text-xs font-mono text-stone-400">Fixed ${baseBet} / round</span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Net Profit</span>
                  <p className={`text-lg font-bold ${basicStats.netProfit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {basicStats.netProfit >= 0 ? '+' : ''}${basicStats.netProfit.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Player Edge / ROI</span>
                  <p className={`text-lg font-bold ${basicStats.roiPercent >= 0 ? 'text-emerald-400' : 'text-stone-300'}`}>
                    {basicStats.roiPercent.toFixed(2)}%
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">EV Per Round</span>
                  <p className="text-stone-200 font-bold text-sm">
                    {basicStats.evPerHand >= 0 ? '+' : ''}${basicStats.evPerHand.toFixed(3)}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Max Drawdown</span>
                  <p className="text-amber-400 font-bold text-sm">
                    ${basicStats.maxDrawdown.toLocaleString()}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Win Rate</span>
                  <p className="text-stone-200 font-bold text-sm">{basicStats.winRate.toFixed(2)}%</p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Total Wagered</span>
                  <p className="text-stone-200 font-bold text-sm">${basicStats.totalWagered.toLocaleString()}</p>
                </div>
              </div>
            </div>

            {/* Hi-Lo Spread Card */}
            <div className="p-6 rounded-2xl bg-stone-900 border border-emerald-900/40 space-y-4 shadow-xl shadow-emerald-950/20">
              <div className="flex items-center justify-between border-b border-stone-800 pb-3">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-emerald-400 shadow-sm shadow-emerald-400" />
                  <h3 className="font-bold text-white text-sm">Hi-Lo Counter (1-{spreadMaxUnits} Spread)</h3>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-700 text-[11px] font-mono font-bold">
                  Illustrious 18 Deviations
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs font-mono">
                <div className="p-3 rounded-xl bg-stone-950 border border-emerald-900/60 space-y-1">
                  <span className="text-stone-500">Net Profit</span>
                  <p className={`text-lg font-bold ${hiLoStats.netProfit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {hiLoStats.netProfit >= 0 ? '+' : ''}${hiLoStats.netProfit.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-emerald-900/60 space-y-1">
                  <span className="text-stone-500">Player Edge / ROI</span>
                  <p className={`text-lg font-bold ${hiLoStats.roiPercent >= 0 ? 'text-emerald-400' : 'text-stone-300'}`}>
                    {hiLoStats.roiPercent.toFixed(2)}%
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">EV Per Round</span>
                  <p className="text-emerald-300 font-bold text-sm">
                    {hiLoStats.evPerHand >= 0 ? '+' : ''}${hiLoStats.evPerHand.toFixed(3)}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Max Drawdown</span>
                  <p className="text-amber-400 font-bold text-sm">
                    ${hiLoStats.maxDrawdown.toLocaleString()}
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Insurance (+EV Plays)</span>
                  <p className="text-stone-200 font-bold text-sm">
                    {hiLoStats.insuranceWon} / {hiLoStats.insuranceTaken} won
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
                  <span className="text-stone-500">Total Wagered</span>
                  <p className="text-stone-200 font-bold text-sm">${hiLoStats.totalWagered.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Bankroll Trajectory Chart */}
          <div className="p-6 rounded-2xl bg-stone-900 border border-stone-800 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center gap-2 font-mono">
                <TrendingUp className="w-4 h-4 text-emerald-400" />
                Comparative Bankroll Trajectory Over Time
              </h3>
              <div className="flex items-center gap-4 text-xs font-mono">
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-0.5 bg-sky-400" />
                  <span className="text-stone-400">Basic Strategy</span>
                </div>
                <div className="flex items-center gap-1.5">
                  <div className="w-3 h-0.5 bg-emerald-400" />
                  <span className="text-stone-300">Hi-Lo (1-{spreadMaxUnits})</span>
                </div>
              </div>
            </div>

            {/* SVG Trajectory Chart */}
            <div className="bg-stone-950 p-4 rounded-xl border border-stone-800 h-64 flex flex-col justify-end">
              {(() => {
                const bsTraj = basicStats.trajectory;
                const hlTraj = hiLoStats.trajectory;
                const allVals = [...bsTraj.map((t) => t.bankroll), ...hlTraj.map((t) => t.bankroll)];
                const minVal = Math.min(...allVals, startingBankroll * 0.8);
                const maxVal = Math.max(...allVals, startingBankroll * 1.2);
                const range = maxVal - minVal || 1;

                const getSvgPoints = (traj: { round: number; bankroll: number }[]) => {
                  return traj
                    .map((pt, i) => {
                      const x = (i / (traj.length - 1)) * 100;
                      const y = 100 - ((pt.bankroll - minVal) / range) * 100;
                      return `${x},${y}`;
                    })
                    .join(' ');
                };

                const startY = 100 - ((startingBankroll - minVal) / range) * 100;

                return (
                  <div className="relative w-full h-full">
                    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full h-full overflow-visible">
                      {/* Baseline Starting Bankroll */}
                      <line
                        x1="0"
                        y1={startY}
                        x2="100"
                        y2={startY}
                        stroke="#57534e"
                        strokeDasharray="2 2"
                        strokeWidth="0.5"
                      />

                      {/* Basic Strategy Line */}
                      <polyline
                        fill="none"
                        stroke="#38bdf8"
                        strokeWidth="1.2"
                        points={getSvgPoints(bsTraj)}
                      />

                      {/* Hi-Lo Line */}
                      <polyline
                        fill="none"
                        stroke="#10b981"
                        strokeWidth="1.8"
                        points={getSvgPoints(hlTraj)}
                      />
                    </svg>

                    <div className="absolute top-1 left-1 text-[10px] font-mono text-stone-500">
                      High: ${Math.round(maxVal).toLocaleString()}
                    </div>
                    <div className="absolute bottom-1 left-1 text-[10px] font-mono text-stone-500">
                      Low: ${Math.round(minVal).toLocaleString()}
                    </div>
                    <div className="absolute right-1 text-[10px] font-mono text-stone-400" style={{ top: `${startY}%` }}>
                      Start: ${startingBankroll.toLocaleString()}
                    </div>
                  </div>
                );
              })()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
