import React, { useState } from 'react';
import { Table, Sparkles, SlidersHorizontal, Info } from 'lucide-react';

interface StrategyMatrixProps {
  dealerHitsSoft17: boolean;
  doubleAfterSplit: boolean;
  lateSurrender: boolean;
}

export const StrategyMatrix: React.FC<StrategyMatrixProps> = ({
  dealerHitsSoft17,
  doubleAfterSplit,
  lateSurrender,
}) => {
  const [subTab, setSubTab] = useState<'hard' | 'soft' | 'pairs' | 'deviations'>('hard');

  const dealerHeaders = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A'];

  // Hard totals table
  const hardRows = [
    { total: '17-20', actions: ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'] },
    { total: '16', actions: ['S', 'S', 'S', 'S', 'S', 'H', 'H', lateSurrender ? 'Rh' : 'H', lateSurrender ? 'Rh' : 'H', lateSurrender ? 'Rh' : 'H'] },
    { total: '15', actions: ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', lateSurrender ? 'Rh' : 'H', lateSurrender && dealerHitsSoft17 ? 'Rh' : 'H'] },
    { total: '14', actions: ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'] },
    { total: '13', actions: ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'] },
    { total: '12', actions: ['H', 'H', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'] },
    { total: '11', actions: ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', dealerHitsSoft17 ? 'D' : 'H'] },
    { total: '10', actions: ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'] },
    { total: '9', actions: ['H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'] },
    { total: '5-8', actions: ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H'] },
  ];

  // Soft totals table
  const softRows = [
    { total: 'A,9 (20)', actions: ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'] },
    { total: 'A,8 (19)', actions: ['S', 'S', 'S', 'S', dealerHitsSoft17 ? 'Ds' : 'S', 'S', 'S', 'S', 'S', 'S'] },
    { total: 'A,7 (18)', actions: ['S', 'Ds', 'Ds', 'Ds', 'Ds', 'S', 'S', 'H', 'H', 'H'] },
    { total: 'A,6 (17)', actions: ['H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'] },
    { total: 'A,5 (16)', actions: ['H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'] },
    { total: 'A,4 (15)', actions: ['H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'] },
    { total: 'A,3 (14)', actions: ['H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'] },
    { total: 'A,2 (13)', actions: ['H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'] },
  ];

  // Pairs table
  const pairRows = [
    { total: 'A,A', actions: ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'] },
    { total: '10,10', actions: ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'] },
    { total: '9,9', actions: ['P', 'P', 'P', 'P', 'P', 'S', 'P', 'P', 'S', 'S'] },
    { total: '8,8', actions: ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'] },
    { total: '7,7', actions: ['P', 'P', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'] },
    { total: '6,6', actions: [doubleAfterSplit ? 'P' : 'H', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H', 'H'] },
    { total: '5,5', actions: ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'] },
    { total: '4,4', actions: ['H', 'H', 'H', doubleAfterSplit ? 'P' : 'H', doubleAfterSplit ? 'P' : 'H', 'H', 'H', 'H', 'H', 'H'] },
    { total: '3,3', actions: [doubleAfterSplit ? 'P' : 'H', doubleAfterSplit ? 'P' : 'H', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'] },
    { total: '2,2', actions: [doubleAfterSplit ? 'P' : 'H', doubleAfterSplit ? 'P' : 'H', 'P', 'P', 'P', 'P', 'H', 'H', 'H', 'H'] },
  ];

  // Illustrious 18 & Fab Four Table
  const illustrious18 = [
    { rank: '#1', play: 'Insurance', vs: "Dealer's Ace", index: '+3', normal: 'Decline', dev: 'Take Insurance' },
    { rank: '#2', play: '16 vs 10', vs: '10', index: '0', normal: 'Hit', dev: 'Stand if TC ≥ 0' },
    { rank: '#3', play: '15 vs 10', vs: '10', index: '+4', normal: 'Hit', dev: 'Stand if TC ≥ +4' },
    { rank: '#4', play: '10,10 vs 5', vs: '5', index: '+5', normal: 'Stand', dev: 'Split if TC ≥ +5' },
    { rank: '#5', play: '10,10 vs 6', vs: '6', index: '+4', normal: 'Stand', dev: 'Split if TC ≥ +4' },
    { rank: '#6', play: '10 vs 10', vs: '10', index: '+4', normal: 'Hit', dev: 'Double if TC ≥ +4' },
    { rank: '#7', play: '12 vs 3', vs: '3', index: '+2', normal: 'Hit', dev: 'Stand if TC ≥ +2' },
    { rank: '#8', play: '12 vs 2', vs: '2', index: '+3', normal: 'Hit', dev: 'Stand if TC ≥ +3' },
    { rank: '#9', play: '11 vs A (S17)', vs: 'Ace', index: '+1', normal: 'Hit', dev: 'Double if TC ≥ +1' },
    { rank: '#10', play: '9 vs 2', vs: '2', index: '+1', normal: 'Hit', dev: 'Double if TC ≥ +1' },
    { rank: '#11', play: '10 vs A', vs: 'Ace', index: '+4', normal: 'Hit', dev: 'Double if TC ≥ +4' },
    { rank: '#12', play: '9 vs 7', vs: '7', index: '+3', normal: 'Hit', dev: 'Double if TC ≥ +3' },
    { rank: '#13', play: '16 vs 9', vs: '9', index: '+5', normal: 'Hit', dev: 'Stand if TC ≥ +5' },
    { rank: '#14', play: '13 vs 2', vs: '2', index: '-1', normal: 'Stand', dev: 'Hit if TC < -1' },
    { rank: '#15', play: '12 vs 4', vs: '4', index: '0', normal: 'Stand', dev: 'Hit if TC < 0' },
    { rank: '#16', play: '12 vs 5', vs: '5', index: '-2', normal: 'Stand', dev: 'Hit if TC < -2' },
    { rank: '#17', play: '12 vs 6', vs: '6', index: '-1', normal: 'Stand', dev: 'Hit if TC < -1' },
    { rank: '#18', play: '13 vs 3', vs: '3', index: '-2', normal: 'Stand', dev: 'Hit if TC < -2' },
    { rank: 'FF #1', play: '14 vs 10', vs: '10', index: '+3', normal: 'Hit', dev: 'Surrender if TC ≥ +3' },
    { rank: 'FF #2', play: '15 vs 9', vs: '9', index: '+2', normal: 'Hit', dev: 'Surrender if TC ≥ +2' },
  ];

  const getCellBadge = (act: string) => {
    switch (act) {
      case 'H':
        return <span className="w-8 h-8 flex items-center justify-center rounded font-bold text-xs bg-emerald-900/80 text-emerald-200 border border-emerald-700/50">H</span>;
      case 'S':
        return <span className="w-8 h-8 flex items-center justify-center rounded font-bold text-xs bg-amber-950/80 text-amber-200 border border-amber-700/50">S</span>;
      case 'D':
        return <span className="w-8 h-8 flex items-center justify-center rounded font-bold text-xs bg-sky-900/80 text-sky-200 border border-sky-600/50">D</span>;
      case 'Ds':
        return <span className="w-8 h-8 flex items-center justify-center rounded font-bold text-xs bg-indigo-900/80 text-indigo-200 border border-indigo-600/50">Ds</span>;
      case 'P':
        return <span className="w-8 h-8 flex items-center justify-center rounded font-bold text-xs bg-purple-900/80 text-purple-200 border border-purple-600/50">P</span>;
      case 'Rh':
        return <span className="w-8 h-8 flex items-center justify-center rounded font-bold text-xs bg-rose-950/80 text-rose-300 border border-rose-700/50">Rh</span>;
      default:
        return <span className="w-8 h-8 flex items-center justify-center rounded font-bold text-xs bg-stone-800 text-stone-300">{act}</span>;
    }
  };

  return (
    <div id="strategy_matrix" className="space-y-6">
      {/* Top Banner & Tab Controls */}
      <div className="p-5 rounded-2xl bg-stone-900 border border-stone-800 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Table className="w-5 h-5 text-emerald-400" />
            Basic Strategy & Illustrious 18 Matrix
          </h2>
          <p className="text-xs text-stone-400 mt-1">
            Active configuration: {dealerHitsSoft17 ? 'H17 (Dealer hits Soft 17)' : 'S17 (Dealer stands on Soft 17)'} •{' '}
            {doubleAfterSplit ? 'DAS Enabled' : 'No DAS'} • {lateSurrender ? 'Late Surrender (LS)' : 'No Surrender'}
          </p>
        </div>

        {/* Sub-tab switcher */}
        <div className="flex rounded-xl bg-stone-950 p-1 border border-stone-800 text-xs">
          <button
            onClick={() => setSubTab('hard')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              subTab === 'hard' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            Hard Totals
          </button>
          <button
            onClick={() => setSubTab('soft')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              subTab === 'soft' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            Soft Totals
          </button>
          <button
            onClick={() => setSubTab('pairs')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              subTab === 'pairs' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            Pair Splitting
          </button>
          <button
            onClick={() => setSubTab('deviations')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              subTab === 'deviations' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            Illustrious 18 & Fab 4
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-3 text-xs bg-stone-950/60 p-3 rounded-xl border border-stone-800">
        <span className="text-stone-400 font-semibold text-[11px] uppercase tracking-wider">Legend:</span>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded bg-emerald-900/80 text-emerald-200 text-[11px] font-bold flex items-center justify-center border border-emerald-700">H</span>
          <span className="text-stone-300">Hit</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded bg-amber-950/80 text-amber-200 text-[11px] font-bold flex items-center justify-center border border-amber-700">S</span>
          <span className="text-stone-300">Stand</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded bg-sky-900/80 text-sky-200 text-[11px] font-bold flex items-center justify-center border border-sky-600">D</span>
          <span className="text-stone-300">Double (Hit if disallowed)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded bg-indigo-900/80 text-indigo-200 text-[11px] font-bold flex items-center justify-center border border-indigo-600">Ds</span>
          <span className="text-stone-300">Double (Stand if disallowed)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded bg-purple-900/80 text-purple-200 text-[11px] font-bold flex items-center justify-center border border-purple-600">P</span>
          <span className="text-stone-300">Split</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-5 h-5 rounded bg-rose-950/80 text-rose-300 text-[11px] font-bold flex items-center justify-center border border-rose-700">Rh</span>
          <span className="text-stone-300">Surrender (Hit if disallowed)</span>
        </div>
      </div>

      {/* Main Table Content */}
      <div className="p-6 rounded-2xl bg-stone-900 border border-stone-800 overflow-x-auto">
        {subTab === 'deviations' ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between border-b border-stone-800 pb-3">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                Illustrious 18 & Fab Four True Count Thresholds
              </h3>
              <span className="text-xs text-stone-400 font-mono">System: Hi-Lo</span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-stone-800 text-stone-400 font-mono">
                    <th className="py-2.5 px-3">Priority</th>
                    <th className="py-2.5 px-3">Player Hand</th>
                    <th className="py-2.5 px-3">Dealer Upcard</th>
                    <th className="py-2.5 px-3 text-center">TC Index</th>
                    <th className="py-2.5 px-3">Basic Play</th>
                    <th className="py-2.5 px-3">Counting Deviation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-800 font-mono">
                  {illustrious18.map((row, idx) => (
                    <tr key={idx} className="hover:bg-stone-800/40 transition">
                      <td className="py-2 px-3 text-emerald-400 font-bold">{row.rank}</td>
                      <td className="py-2 px-3 text-stone-200 font-sans font-semibold">{row.play}</td>
                      <td className="py-2 px-3 text-stone-300">{row.vs}</td>
                      <td className="py-2 px-3 text-center">
                        <span className="px-2 py-0.5 rounded bg-stone-800 text-amber-300 font-bold border border-stone-700">
                          {row.index}
                        </span>
                      </td>
                      <td className="py-2 px-3 text-stone-400">{row.normal}</td>
                      <td className="py-2 px-3 text-emerald-300 font-semibold">{row.dev}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b border-stone-800">
                <th className="text-left text-xs font-mono text-stone-400 pb-3 pr-4">
                  {subTab === 'hard' ? 'Player Total' : subTab === 'soft' ? 'Soft Hand' : 'Pair Rank'}
                </th>
                {dealerHeaders.map((dh) => (
                  <th key={dh} className="text-center text-xs font-mono text-emerald-400 pb-3 px-1.5">
                    {dh}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-800/60 font-mono">
              {(subTab === 'hard' ? hardRows : subTab === 'soft' ? softRows : pairRows).map((row, rIdx) => (
                <tr key={rIdx} className="hover:bg-stone-800/30 transition">
                  <td className="py-2 pr-4 text-xs font-semibold text-stone-300 whitespace-nowrap">
                    {row.total}
                  </td>
                  {row.actions.map((act, cIdx) => (
                    <td key={cIdx} className="py-1.5 px-1.5 text-center">
                      <div className="flex justify-center">{getCellBadge(act)}</div>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
