import React from 'react';
import {
  Wallet,
  Save,
  Plus,
  RotateCcw,
  TrendingUp,
  TrendingDown,
  Coins,
  Sparkles,
} from 'lucide-react';
import { PersistentBankrollData } from '../types';

interface BankrollLedgerProps {
  bankrollData: PersistentBankrollData;
  totalProfitLoss: number;
  totalProfitLossPct: number;
  wager: number;
  setWager: (w: number) => void;
  spreadAdvice: { units: number; bet: number };
  gameState: 'idle' | 'in_progress' | 'insurance_offered' | 'completed';
  handleReloadBankroll: (amount?: number) => void;
  handleResetBankroll: (amount?: number) => void;
}

export const BankrollLedger: React.FC<BankrollLedgerProps> = ({
  bankrollData,
  totalProfitLoss,
  totalProfitLossPct,
  wager,
  setWager,
  spreadAdvice,
  gameState,
  handleReloadBankroll,
  handleResetBankroll,
}) => {
  return (
    <div id="bankroll_ledger_card" className="p-5 rounded-2xl bg-stone-900 border border-stone-800 space-y-4 shadow-xl">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-stone-800 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-950/80 border border-emerald-700/50 text-emerald-400">
            <Wallet className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-white font-mono tracking-wide flex items-center gap-2">
              PERSISTENT BANKROLL & MULTI-SESSION LEDGER
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-600/50 text-emerald-400 font-mono font-medium flex items-center gap-1">
                <Save className="w-2.5 h-2.5" /> Persistent Across Sessions
              </span>
            </h2>
            <p className="text-xs text-stone-400">
              Tracks real cumulative profits, losses, wagers, and drawdown across all sandbox sessions
            </p>
          </div>
        </div>

        {/* Quick Fund Controls */}
        <div className="flex items-center gap-2">
          <button
            id="btn_reload_bankroll"
            onClick={() => handleReloadBankroll(500)}
            className="px-3 py-1.5 rounded-lg bg-stone-800 hover:bg-stone-700 border border-stone-700 text-stone-200 text-xs font-mono font-medium flex items-center gap-1.5 transition"
            title="Add $500 reload to bankroll"
          >
            <Plus className="w-3.5 h-3.5 text-emerald-400" />
            +$500 Reload
          </button>
          <button
            id="btn_reset_bankroll"
            onClick={() => handleResetBankroll(1000)}
            className="px-3 py-1.5 rounded-lg bg-stone-800 hover:bg-stone-700 border border-stone-700 text-stone-300 hover:text-rose-300 text-xs font-mono font-medium flex items-center gap-1.5 transition"
            title="Reset bankroll and session history to $1,000 baseline"
          >
            <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
            Reset to $1,000
          </button>
        </div>
      </div>

      {/* 4-Stat Metric Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {/* 1. Current Bankroll */}
        <div id="stat_current_bankroll" className="p-3.5 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
          <span className="text-stone-400 text-[11px] font-mono uppercase tracking-wider block">
            Current Bankroll
          </span>
          <div className="text-xl font-bold font-mono text-white flex items-baseline gap-1">
            ${bankrollData.bankroll.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-stone-500">
            Baseline: ${bankrollData.initialBankroll.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        {/* 2. Total Multi-Session Profit / Loss */}
        <div
          id="stat_multisession_pl"
          className={`p-3.5 rounded-xl border space-y-1 ${
            totalProfitLoss > 0
              ? 'bg-emerald-950/20 border-emerald-900/50'
              : totalProfitLoss < 0
              ? 'bg-rose-950/20 border-rose-900/50'
              : 'bg-stone-950 border-stone-800'
          }`}
        >
          <span className="text-stone-400 text-[11px] font-mono uppercase tracking-wider flex items-center justify-between">
            <span>Total Multi-Session P/L</span>
            {totalProfitLoss !== 0 && (
              <span className={`flex items-center text-[10px] font-bold ${totalProfitLoss > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                {totalProfitLoss > 0 ? <TrendingUp className="w-3 h-3 mr-0.5" /> : <TrendingDown className="w-3 h-3 mr-0.5" />}
                {totalProfitLossPct >= 0 ? '+' : ''}{totalProfitLossPct.toFixed(1)}% ROI
              </span>
            )}
          </span>
          <div className={`text-xl font-bold font-mono flex items-baseline gap-1 ${
            totalProfitLoss > 0 ? 'text-emerald-400' : totalProfitLoss < 0 ? 'text-rose-400' : 'text-stone-300'
          }`}>
            {totalProfitLoss >= 0 ? '+' : ''}${totalProfitLoss.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-stone-500">
            Cumulative over {bankrollData.totalRounds} round{bankrollData.totalRounds === 1 ? '' : 's'}
          </div>
        </div>

        {/* 3. Peak Bankroll (High-Water Mark) */}
        <div id="stat_peak_bankroll" className="p-3.5 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
          <span className="text-stone-400 text-[11px] font-mono uppercase tracking-wider block">
            Peak (High-Water Mark)
          </span>
          <div className="text-xl font-bold font-mono text-stone-200">
            ${bankrollData.peakBankroll.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-stone-500">
            Drawdown: ${Math.max(0, bankrollData.peakBankroll - bankrollData.bankroll).toFixed(2)}
          </div>
        </div>

        {/* 4. Total Volume Wagered */}
        <div id="stat_total_wagered" className="p-3.5 rounded-xl bg-stone-950 border border-stone-800 space-y-1">
          <span className="text-stone-400 text-[11px] font-mono uppercase tracking-wider block">
            Total Volume Wagered
          </span>
          <div className="text-xl font-bold font-mono text-stone-200">
            ${bankrollData.totalWagered.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] font-mono text-stone-500">
            {bankrollData.totalRounds} completed rounds
          </div>
        </div>
      </div>

      {/* Interactive Wager Selector & Hi-Lo Bet Sizing Integration */}
      <div className="pt-2 border-t border-stone-800/80 flex flex-wrap items-center justify-between gap-3 text-xs font-mono">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="flex items-center gap-1.5 text-stone-300 font-semibold">
            <Coins className="w-4 h-4 text-amber-400" />
            <span>Table Wager:</span>
          </div>
          <div className="flex items-center gap-1.5 flex-wrap">
            {[5, 10, 25, 50, 100, 250].map((chipVal) => (
              <button
                key={chipVal}
                onClick={() => setWager(chipVal)}
                disabled={gameState === 'in_progress'}
                className={`px-2.5 py-1 rounded-lg border font-bold transition ${
                  wager === chipVal
                    ? 'bg-emerald-600 border-emerald-400 text-white shadow-md'
                    : 'bg-stone-950 border-stone-800 text-stone-400 hover:text-stone-200 hover:border-stone-700'
                } ${gameState === 'in_progress' ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                ${chipVal}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setWager(spreadAdvice.bet)}
            disabled={gameState === 'in_progress'}
            className="px-3 py-1 rounded-lg bg-amber-950/60 border border-amber-600/50 hover:bg-amber-900/60 text-amber-300 text-xs font-bold flex items-center gap-1.5 transition disabled:opacity-50"
            title="Set wager according to Hi-Lo count advantage"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Match Hi-Lo Bet (${spreadAdvice.bet})
          </button>
          <div className="flex items-center gap-1">
            <span className="text-stone-500">Custom:</span>
            <input
              type="number"
              min={1}
              max={Math.max(1, bankrollData.bankroll)}
              value={wager}
              onChange={(e) => setWager(Math.max(1, Number(e.target.value)))}
              disabled={gameState === 'in_progress'}
              className="w-20 px-2 py-0.5 rounded bg-stone-950 border border-stone-800 text-white text-center font-bold focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>
      </div>
    </div>
  );
};
