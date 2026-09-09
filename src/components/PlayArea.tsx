import React from 'react';
import { Play, Sparkles } from 'lucide-react';
import { CardData, HandData, SUIT_SYMBOLS } from '../types';
import { AdvisorResult } from '../lib/strategyAdvisor';

interface PlayAreaProps {
  dealerCards: CardData[];
  dealerHoleHidden: boolean;
  calculateHandPoints: (cards: CardData[]) => { value: number; isSoft: boolean; isBust: boolean; isBlackjack: boolean };
  gameState: 'idle' | 'in_progress' | 'insurance_offered' | 'completed';
  trueCount: number;
  wager: number;
  handleInsuranceDecision: (take: boolean) => void;
  playerHands: HandData[];
  currentHandIdx: number;
  strategyAdvice: AdvisorResult | null;
  startNewRound: () => void;
  handleHit: () => void;
  handleStand: () => void;
  handleDouble: () => void;
  handleSplit: () => void;
  handleSurrender: () => void;
  canDouble: boolean;
  canSplit: boolean;
  canSurrender: boolean;
  lateSurrender: boolean;
}

export const PlayArea: React.FC<PlayAreaProps> = ({
  dealerCards,
  dealerHoleHidden,
  calculateHandPoints,
  gameState,
  trueCount,
  wager,
  handleInsuranceDecision,
  playerHands,
  currentHandIdx,
  strategyAdvice,
  startNewRound,
  handleHit,
  handleStand,
  handleDouble,
  handleSplit,
  handleSurrender,
  canDouble,
  canSplit,
  canSurrender,
  lateSurrender,
}) => {
  return (
    <div id="table_felt" className="rounded-2xl border border-emerald-900/60 bg-gradient-to-b from-emerald-950 to-stone-950 p-6 shadow-2xl relative overflow-hidden space-y-8">
      {/* Dealer Section */}
      <div id="dealer_section" className="space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-emerald-300/80 border-b border-emerald-900/40 pb-2">
          <span className="font-semibold uppercase tracking-wider">Dealer Hand</span>
          <span>
            {dealerCards.length > 0 && !dealerHoleHidden
              ? `Value: ${calculateHandPoints(dealerCards).value}`
              : dealerCards.length > 0
              ? `Showing: ${dealerCards[0].value}`
              : 'Awaiting Deal'}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-3 min-h-[96px]">
          {dealerCards.length === 0 ? (
            <div className="w-16 h-24 rounded-lg border border-dashed border-emerald-800/40 flex items-center justify-center text-emerald-700/50 text-xs">
              Empty
            </div>
          ) : (
            dealerCards.map((card, idx) => {
              const isHole = idx === 1 && dealerHoleHidden;
              return (
                <div
                  key={idx}
                  className={`w-16 h-24 rounded-xl border flex flex-col justify-between p-2 shadow-lg select-none transition-all ${
                    isHole
                      ? 'bg-gradient-to-br from-red-900 to-red-950 border-red-800 text-red-200'
                      : 'bg-stone-50 border-stone-200 text-stone-900'
                  }`}
                >
                  {isHole ? (
                    <div className="h-full flex items-center justify-center font-mono font-bold text-xs text-red-400/80">
                      HOLE
                    </div>
                  ) : (
                    <>
                      <div className="text-xs font-bold leading-none font-mono">
                        {card.rank}
                      </div>
                      <div className={`text-2xl text-center leading-none ${SUIT_SYMBOLS[card.suit].color}`}>
                        {SUIT_SYMBOLS[card.suit].symbol}
                      </div>
                      <div className="text-xs font-bold leading-none self-end rotate-180 font-mono">
                        {card.rank}
                      </div>
                    </>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Center Divider / Insurance Notice */}
      {gameState === 'insurance_offered' && (
        <div className="p-4 rounded-xl bg-amber-950/80 border border-amber-600/50 text-amber-200 text-xs space-y-3 shadow-lg">
          <div className="flex items-center justify-between">
            <span className="font-bold font-mono">Insurance Offered (Dealer shows Ace)</span>
            <span className="text-[11px] font-mono text-amber-300">
              {trueCount >= 3.0 ? '✓ Hi-Lo Advice: TAKE INSURANCE (TC ≥ +3)' : '✗ Hi-Lo Advice: DECLINE (TC < +3)'}
            </span>
          </div>
          <p className="text-stone-300 text-[11px]">
            Insurance costs half your wager (${(wager * 0.5).toFixed(2)}) and pays 2:1 if dealer holds Blackjack.
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => handleInsuranceDecision(true)}
              className={`px-4 py-2 rounded-lg font-bold text-xs shadow transition ${
                trueCount >= 3.0 ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-amber-700 hover:bg-amber-600 text-white'
              }`}
            >
              Take Insurance (${(wager * 0.5).toFixed(2)})
            </button>
            <button
              onClick={() => handleInsuranceDecision(false)}
              className={`px-4 py-2 rounded-lg font-bold text-xs shadow transition ${
                trueCount < 3.0 ? 'bg-emerald-600 hover:bg-emerald-500 text-white' : 'bg-stone-800 hover:bg-stone-700 text-stone-300'
              }`}
            >
              Decline Insurance
            </button>
          </div>
        </div>
      )}

      {/* Player Section */}
      <div id="player_section" className="space-y-3">
        <div className="flex items-center justify-between text-xs font-mono text-emerald-300/80 border-b border-emerald-900/40 pb-2">
          <span className="font-semibold uppercase tracking-wider">
            Player Hands ({playerHands.length})
          </span>
          <span>Wager: ${wager}</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {playerHands.length === 0 ? (
            <div className="w-16 h-24 rounded-lg border border-dashed border-emerald-800/40 flex items-center justify-center text-emerald-700/50 text-xs">
              Empty
            </div>
          ) : (
            playerHands.map((hand, hIdx) => {
              const isCurrent = hIdx === currentHandIdx && gameState === 'in_progress';
              return (
                <div
                  key={hIdx}
                  className={`p-3 rounded-xl border transition-all ${
                    isCurrent
                      ? 'bg-emerald-900/40 border-emerald-500 ring-1 ring-emerald-400 shadow-md'
                      : 'bg-stone-950/60 border-stone-800'
                  }`}
                >
                  <div className="flex justify-between items-center text-xs font-mono text-stone-300 mb-2">
                    <span className="font-bold">Hand #{hIdx + 1}</span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        hand.status === 'BUSTED'
                          ? 'bg-red-950 text-red-300 border border-red-800'
                          : hand.status === 'DOUBLED'
                          ? 'bg-sky-950 text-sky-300 border border-sky-800'
                          : hand.status === 'SURRENDERED'
                          ? 'bg-stone-800 text-stone-400'
                          : 'bg-emerald-950 text-emerald-300'
                      }`}
                    >
                      {hand.status} ({hand.value} {hand.isSoft ? 'soft' : 'hard'})
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {hand.cards.map((card, cIdx) => (
                      <div
                        key={cIdx}
                        className="w-14 h-20 rounded-lg bg-stone-50 border border-stone-200 text-stone-900 flex flex-col justify-between p-1.5 shadow select-none"
                      >
                        <div className="text-xs font-bold leading-none font-mono">
                          {card.rank}
                        </div>
                        <div className={`text-xl text-center leading-none ${SUIT_SYMBOLS[card.suit].color}`}>
                          {SUIT_SYMBOLS[card.suit].symbol}
                        </div>
                        <div className="text-xs font-bold leading-none self-end rotate-180 font-mono">
                          {card.rank}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Live Strategy Advisor Banner */}
      {strategyAdvice && (
        <div className="p-3.5 rounded-xl bg-stone-900/90 border border-emerald-600/50 flex flex-wrap items-center justify-between gap-3 shadow-lg">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-4 h-4 text-emerald-400 shrink-0" />
            <div>
              <div className="text-xs font-bold text-white flex items-center gap-2">
                <span>Strategy Advisor Recommendation:</span>
                <span
                  className={`px-2 py-0.5 rounded font-mono text-xs font-bold ${
                    strategyAdvice.recommendedAction === 'HIT'
                      ? 'bg-emerald-950 text-emerald-300 border border-emerald-700'
                      : strategyAdvice.recommendedAction === 'STAND'
                      ? 'bg-amber-950 text-amber-300 border border-amber-700'
                      : strategyAdvice.recommendedAction === 'DOUBLE'
                      ? 'bg-sky-950 text-sky-300 border border-sky-600'
                      : strategyAdvice.recommendedAction === 'SPLIT'
                      ? 'bg-purple-950 text-purple-300 border border-purple-600'
                      : 'bg-rose-950 text-rose-300 border border-rose-700'
                  }`}
                >
                  {strategyAdvice.recommendedAction}
                </span>
                {strategyAdvice.isDeviation && (
                  <span className="px-1.5 py-0.5 rounded bg-amber-950 text-amber-300 border border-amber-700 text-[10px] font-mono">
                    Hi-Lo Deviation
                  </span>
                )}
              </div>
              <p className="text-[11px] text-stone-400 mt-0.5">{strategyAdvice.reason}</p>
            </div>
          </div>
        </div>
      )}

      {/* Player Action Buttons */}
      <div id="player_actions" className="flex flex-wrap items-center gap-2 pt-2 border-t border-emerald-900/40">
        <button
          id="btn_deal"
          onClick={startNewRound}
          disabled={gameState === 'in_progress' || gameState === 'insurance_offered'}
          className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition ${
            gameState === 'in_progress' || gameState === 'insurance_offered'
              ? 'bg-stone-800 text-stone-500 cursor-not-allowed'
              : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-950'
          }`}
        >
          <Play className="w-3.5 h-3.5 fill-white" />
          Deal Round (${wager})
        </button>

        <button
          id="btn_hit"
          onClick={handleHit}
          disabled={gameState !== 'in_progress'}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
            gameState !== 'in_progress'
              ? 'bg-stone-800 text-stone-500 cursor-not-allowed'
              : strategyAdvice?.recommendedAction === 'HIT'
              ? 'bg-emerald-600 hover:bg-emerald-500 text-white ring-2 ring-emerald-400'
              : 'bg-stone-800 hover:bg-stone-700 text-stone-200'
          }`}
        >
          Hit
        </button>

        <button
          id="btn_stand"
          onClick={handleStand}
          disabled={gameState !== 'in_progress'}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
            gameState !== 'in_progress'
              ? 'bg-stone-800 text-stone-500 cursor-not-allowed'
              : strategyAdvice?.recommendedAction === 'STAND'
              ? 'bg-amber-600 hover:bg-amber-500 text-white ring-2 ring-amber-400'
              : 'bg-stone-800 hover:bg-stone-700 text-stone-200'
          }`}
        >
          Stand
        </button>

        <button
          id="btn_double"
          onClick={handleDouble}
          disabled={!canDouble}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
            !canDouble
              ? 'bg-stone-800 text-stone-500 cursor-not-allowed'
              : strategyAdvice?.recommendedAction === 'DOUBLE'
              ? 'bg-sky-600 hover:bg-sky-500 text-white ring-2 ring-sky-400'
              : 'bg-stone-800 hover:bg-stone-700 text-stone-200'
          }`}
        >
          Double
        </button>

        <button
          id="btn_split"
          onClick={handleSplit}
          disabled={!canSplit}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
            !canSplit
              ? 'bg-stone-800 text-stone-500 cursor-not-allowed'
              : strategyAdvice?.recommendedAction === 'SPLIT'
              ? 'bg-purple-600 hover:bg-purple-500 text-white ring-2 ring-purple-400'
              : 'bg-stone-800 hover:bg-stone-700 text-stone-200'
          }`}
        >
          Split
        </button>

        {lateSurrender && (
          <button
            id="btn_surrender"
            onClick={handleSurrender}
            disabled={!canSurrender}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
              !canSurrender
                ? 'bg-stone-800 text-stone-500 cursor-not-allowed'
                : strategyAdvice?.recommendedAction === 'SURRENDER'
                ? 'bg-rose-600 hover:bg-rose-500 text-white ring-2 ring-rose-400'
                : 'bg-stone-800 hover:bg-stone-700 text-stone-200'
            }`}
          >
            Surrender
          </button>
        )}
      </div>
    </div>
  );
};
