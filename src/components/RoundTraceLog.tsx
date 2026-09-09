import React from 'react';
import { Terminal } from 'lucide-react';

interface RoundTraceLogProps {
  logMessages: string[];
  roundResultSummary: string;
  netProfit: number;
}

export const RoundTraceLog: React.FC<RoundTraceLogProps> = ({
  logMessages,
  roundResultSummary,
  netProfit,
}) => {
  return (
    <div id="trace_log" className="p-4 rounded-xl bg-stone-900 border border-stone-800 space-y-2 text-xs">
      <div className="flex items-center justify-between pb-1 border-b border-stone-800">
        <h3 className="font-semibold text-stone-200 flex items-center gap-1.5 font-mono">
          <Terminal className="w-3.5 h-3.5 text-emerald-400" />
          Round Trace Log
        </h3>
        {roundResultSummary && (
          <span
            className={`text-[11px] font-mono px-2 py-0.5 rounded font-bold ${
              netProfit > 0
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-600'
                : netProfit < 0
                ? 'bg-red-950 text-red-300 border border-red-600'
                : 'bg-stone-800 text-stone-300'
            }`}
          >
            {roundResultSummary} ({netProfit >= 0 ? '+' : ''}${netProfit.toFixed(2)})
          </span>
        )}
      </div>

      <div className="bg-stone-950 rounded-lg p-3 h-56 overflow-y-auto font-mono text-[11px] space-y-1 text-stone-300">
        {logMessages.length === 0 ? (
          <span className="text-stone-600 italic">No actions logged yet. Press Deal Round.</span>
        ) : (
          logMessages.map((msg, idx) => (
            <div
              key={idx}
              className={
                msg.startsWith('===')
                  ? 'text-emerald-400 font-bold border-b border-stone-800 pb-0.5 pt-1'
                  : msg.includes('Result:') || msg.includes('Outcome:')
                  ? 'text-amber-300 font-semibold'
                  : msg.includes('BUST')
                  ? 'text-red-400'
                  : 'text-stone-300'
              }
            >
              {msg}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
