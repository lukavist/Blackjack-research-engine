import React from 'react';
import { Eye, RotateCcw } from 'lucide-react';

interface CountingHUDProps {
  runningCount: number;
  trueCount: number;
  decksRemaining: number;
  numDecks: number;
  spreadAdvice: { units: number; bet: number };
  cardsDealt: number;
  totalCardsInShoe: number;
  cutCardThreshold: number;
  penetration: number;
  resetShoeAndCount: () => void;
}

export const CountingHUD: React.FC<CountingHUDProps> = ({
  runningCount,
  trueCount,
  decksRemaining,
  numDecks,
  spreadAdvice,
  cardsDealt,
  totalCardsInShoe,
  cutCardThreshold,
  penetration,
  resetShoeAndCount,
}) => {
  return (
    <div id="hilo_hud" className="p-4 rounded-2xl bg-stone-900 border border-stone-800 space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-stone-800 pb-2">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Hi-Lo Count HUD (Observer Pattern)
          </span>
        </div>
        <button
          onClick={resetShoeAndCount}
          className="text-[11px] font-mono text-stone-400 hover:text-emerald-400 flex items-center gap-1 transition"
        >
          <RotateCcw className="w-3 h-3" /> Reshuffle Shoe & Reset Count
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
        <div className="p-2.5 rounded-xl bg-stone-950 border border-stone-800">
          <span className="text-stone-500 text-[11px]">Running Count (RC)</span>
          <p
            className={`text-lg font-bold ${
              runningCount > 0 ? 'text-emerald-400' : runningCount < 0 ? 'text-red-400' : 'text-stone-200'
            }`}
          >
            {runningCount > 0 ? `+${runningCount}` : runningCount}
          </p>
        </div>

        <div className="p-2.5 rounded-xl bg-stone-950 border border-stone-800">
          <span className="text-stone-500 text-[11px]">True Count (TC)</span>
          <p
            className={`text-lg font-bold ${
              trueCount >= 1 ? 'text-emerald-400' : trueCount <= -1 ? 'text-red-400' : 'text-stone-200'
            }`}
          >
            {trueCount >= 0 ? `+${trueCount.toFixed(1)}` : trueCount.toFixed(1)}
          </p>
        </div>

        <div className="p-2.5 rounded-xl bg-stone-950 border border-stone-800">
          <span className="text-stone-500 text-[11px]">Decks Remaining</span>
          <p className="text-lg font-bold text-stone-200">
            {decksRemaining.toFixed(1)} / {numDecks}
          </p>
        </div>

        <div className="p-2.5 rounded-xl bg-stone-950 border border-stone-800">
          <span className="text-stone-500 text-[11px]">Recommended Bet</span>
          <p className="text-lg font-bold text-amber-300">
            {spreadAdvice.units}x (${spreadAdvice.bet})
          </p>
        </div>
      </div>

      {/* Penetration Progress */}
      <div className="space-y-1">
        <div className="flex justify-between text-[11px] text-stone-400 font-mono">
          <span>
            Shoe Penetration: {cardsDealt} / {totalCardsInShoe} cards
          </span>
          <span>
            Cut card: {cutCardThreshold} ({Math.round(penetration * 100)}%)
          </span>
        </div>
        <div className="w-full h-1.5 rounded-full bg-stone-950 overflow-hidden border border-stone-800">
          <div
            className={`h-full ${cardsDealt >= cutCardThreshold ? 'bg-amber-500' : 'bg-emerald-600'}`}
            style={{ width: `${Math.min((cardsDealt / cutCardThreshold) * 100, 100)}%` }}
          />
        </div>
      </div>
    </div>
  );
};
