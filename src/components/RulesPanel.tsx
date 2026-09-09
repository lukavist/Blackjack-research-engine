import React from 'react';
import { Sliders } from 'lucide-react';

interface RulesPanelProps {
  numDecks: number;
  setNumDecks: (n: number) => void;
  penetration: number;
  setPenetration: (p: number) => void;
  dealerHitsSoft17: boolean;
  setDealerHitsSoft17: (h: boolean) => void;
  doubleAfterSplit: boolean;
  setDoubleAfterSplit: (d: boolean) => void;
  lateSurrender: boolean;
  setLateSurrender: (l: boolean) => void;
  insuranceAllowed: boolean;
  setInsuranceAllowed: (i: boolean) => void;
  resetShoeAndCount: () => void;
}

export const RulesPanel: React.FC<RulesPanelProps> = ({
  numDecks,
  setNumDecks,
  penetration,
  setPenetration,
  dealerHitsSoft17,
  setDealerHitsSoft17,
  doubleAfterSplit,
  setDoubleAfterSplit,
  lateSurrender,
  setLateSurrender,
  insuranceAllowed,
  setInsuranceAllowed,
  resetShoeAndCount,
}) => {
  return (
    <div id="rules_card" className="p-5 rounded-2xl bg-stone-900 border border-stone-800 space-y-4">
      <div className="flex items-center gap-2 text-white font-bold text-sm border-b border-stone-800 pb-2">
        <Sliders className="w-4 h-4 text-emerald-400" />
        Table Rules Configuration
      </div>

      <div className="space-y-3 text-xs">
        <div>
          <label className="text-stone-400 flex justify-between">
            <span>Decks in Shoe:</span>
            <span className="font-mono text-emerald-400 font-bold">{numDecks} Decks</span>
          </label>
          <input
            type="range"
            min={1}
            max={8}
            value={numDecks}
            onChange={(e) => {
              setNumDecks(Number(e.target.value));
              resetShoeAndCount();
            }}
            className="w-full accent-emerald-500"
          />
        </div>

        <div>
          <label className="text-stone-400 flex justify-between">
            <span>Cut-Card Penetration:</span>
            <span className="font-mono text-emerald-400 font-bold">{Math.round(penetration * 100)}%</span>
          </label>
          <input
            type="range"
            min={50}
            max={90}
            step={5}
            value={penetration * 100}
            onChange={(e) => setPenetration(Number(e.target.value) / 100)}
            className="w-full accent-emerald-500"
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-stone-400">Dealer Hits Soft 17 (H17)</span>
          <input
            type="checkbox"
            checked={dealerHitsSoft17}
            onChange={(e) => setDealerHitsSoft17(e.target.checked)}
            className="accent-emerald-500 rounded"
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-stone-400">Double After Split (DAS)</span>
          <input
            type="checkbox"
            checked={doubleAfterSplit}
            onChange={(e) => setDoubleAfterSplit(e.target.checked)}
            className="accent-emerald-500 rounded"
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-stone-400">Late Surrender (LS)</span>
          <input
            type="checkbox"
            checked={lateSurrender}
            onChange={(e) => setLateSurrender(e.target.checked)}
            className="accent-emerald-500 rounded"
          />
        </div>

        <div className="flex items-center justify-between">
          <span className="text-stone-400">Insurance Allowed</span>
          <input
            type="checkbox"
            checked={insuranceAllowed}
            onChange={(e) => setInsuranceAllowed(e.target.checked)}
            className="accent-emerald-500 rounded"
          />
        </div>
      </div>
    </div>
  );
};
