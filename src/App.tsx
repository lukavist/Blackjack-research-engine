import React, { useState } from 'react';
import {
  ShieldCheck,
  TrendingUp,
  TrendingDown,
  Layers,
  Activity,
  Cpu,
  BarChart3,
  Terminal,
  Wallet,
} from 'lucide-react';
import { StrategyMatrix } from './components/StrategyMatrix';
import { SimulationView } from './components/SimulationView';
import { InteractiveSandbox } from './components/InteractiveSandbox';
import { ArchitectureView } from './components/ArchitectureView';
import { UnitTestsView } from './components/UnitTestsView';
import {
  PersistentBankrollData,
  loadPersistentBankroll,
} from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState<'interactive' | 'matrix' | 'simulation' | 'architecture' | 'tests'>('interactive');

  // Persistent Bankroll State across sessions
  const [bankrollData, setBankrollData] = useState<PersistentBankrollData>(loadPersistentBankroll);

  // Profit / Loss calculation across multiple sessions
  const totalProfitLoss = Math.round((bankrollData.bankroll - bankrollData.initialBankroll) * 100) / 100;
  const totalProfitLossPct = bankrollData.initialBankroll > 0
    ? (totalProfitLoss / bankrollData.initialBankroll) * 100
    : 0;

  return (
    <div id="app_root" className="min-h-screen bg-stone-950 text-stone-100 flex flex-col font-sans">
      {/* Header Bar */}
      <header id="main_header" className="border-b border-stone-800 bg-stone-900/80 backdrop-blur px-6 py-4 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-emerald-950 border border-emerald-700/50 text-emerald-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white font-mono tracking-tight flex items-center gap-2">
              BLACKJACK RESEARCH ENGINE
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-950 border border-emerald-600 text-emerald-400 font-mono font-medium">
                v1.0 • Hi-Lo & Illustrious 18
              </span>
            </h1>
            <p className="text-xs text-stone-400">
              Deterministic Simulation, Observer-Pattern Hi-Lo Counting, and Index Deviations
            </p>
          </div>
        </div>

        {/* Header Persistent Bankroll Pill */}
        <div id="header_bankroll_badge" className="flex items-center gap-3 bg-stone-950/80 px-3.5 py-1.5 rounded-xl border border-stone-800 text-xs font-mono">
          <div className="flex items-center gap-1.5 text-stone-400">
            <Wallet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Bankroll:</span>
            <span className="font-bold text-white">${bankrollData.bankroll.toFixed(2)}</span>
          </div>
          <span className="text-stone-700">|</span>
          <div className="flex items-center gap-1.5">
            <span className="text-stone-400">Total P/L:</span>
            <span className={`font-bold flex items-center ${totalProfitLoss > 0 ? 'text-emerald-400' : totalProfitLoss < 0 ? 'text-rose-400' : 'text-stone-300'}`}>
              {totalProfitLoss > 0 ? <TrendingUp className="w-3 h-3 mr-0.5" /> : totalProfitLoss < 0 ? <TrendingDown className="w-3 h-3 mr-0.5" /> : null}
              {totalProfitLoss >= 0 ? '+' : ''}${totalProfitLoss.toFixed(2)}
            </span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav id="nav_tabs" className="flex items-center gap-1 bg-stone-950/60 p-1 rounded-lg border border-stone-800 text-xs">
          <button
            id="tab_interactive"
            onClick={() => setActiveTab('interactive')}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition ${
              activeTab === 'interactive' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            <Activity className="w-3.5 h-3.5" />
            Interactive Sandbox
          </button>
          <button
            id="tab_matrix"
            onClick={() => setActiveTab('matrix')}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition ${
              activeTab === 'matrix' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            Strategy & Deviations
          </button>
          <button
            id="tab_simulation"
            onClick={() => setActiveTab('simulation')}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition ${
              activeTab === 'simulation' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            <Cpu className="w-3.5 h-3.5" />
            Monte Carlo Engine
          </button>
          <button
            id="tab_architecture"
            onClick={() => setActiveTab('architecture')}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition ${
              activeTab === 'architecture' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Architecture
          </button>
          <button
            id="tab_tests"
            onClick={() => setActiveTab('tests')}
            className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 font-medium transition ${
              activeTab === 'tests' ? 'bg-emerald-600 text-white shadow' : 'text-stone-400 hover:text-stone-200'
            }`}
          >
            <Terminal className="w-3.5 h-3.5" />
            Unit Tests (62/62)
          </button>
        </nav>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {activeTab === 'interactive' && (
          <InteractiveSandbox
            bankrollData={bankrollData}
            setBankrollData={setBankrollData}
            totalProfitLoss={totalProfitLoss}
            totalProfitLossPct={totalProfitLossPct}
          />
        )}

        {activeTab === 'matrix' && (
          <StrategyMatrix
            dealerHitsSoft17={false}
            doubleAfterSplit={true}
            lateSurrender={true}
          />
        )}

        {activeTab === 'simulation' && (
          <SimulationView
            numDecks={6}
            penetration={0.75}
            dealerHitsSoft17={false}
            doubleAfterSplit={true}
            lateSurrender={true}
          />
        )}

        {activeTab === 'architecture' && <ArchitectureView />}

        {activeTab === 'tests' && <UnitTestsView />}
      </main>
    </div>
  );
}
