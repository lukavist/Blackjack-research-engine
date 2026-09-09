# Blackjack Research Engine

A quantitative research engine, Monte Carlo simulation platform, and interactive analysis workbench designed for rigorous mathematical verification of Blackjack basic strategy, card counting systems (Hi-Lo, Illustrious 18 index deviations, Fab Four), and capital allocation models (Kelly Criterion, spread betting).

---

## Table of Contents

1. [Quick Start: How to Start the App](#quick-start-how-to-start-the-app)
   - [Prerequisites](#prerequisites)
   - [Starting the Interactive Web Dashboard](#1-starting-the-interactive-web-dashboard)
   - [Running the Python Research Engine & Simulations](#2-running-the-python-research-engine--simulations)
   - [Running the Unit Test Suite](#3-running-the-unit-test-suite)
2. [Interactive Web Dashboard Features](#interactive-web-dashboard-features)
   - [Interactive Sandbox & Live HUD](#tab-1-interactive-sandbox--live-hud)
   - [Strategy & Deviations Matrix](#tab-2-strategy--deviations-matrix)
   - [Monte Carlo Simulation Workbench](#tab-3-monte-carlo-simulation-workbench)
   - [Architecture Blueprint & Unit Test Runner](#tabs-4--5-architecture--unit-tests)
3. [Architecture & Design Principles](#architecture--design-principles)
   - [Core Pipeline](#core-pipeline)
   - [Zero Hole-Card Leakage (Observer Pattern)](#zero-hole-card-leakage-observer-pattern)
   - [Continuous Multi-Deck Shoe (No-Shuffle-Bug Guarantee)](#continuous-multi-deck-shoe-no-shuffle-bug-guarantee)
   - [Illustrious 18 & Fab Four Deviations](#illustrious-18--fab-four-deviations)
4. [Project Directory Structure](#project-directory-structure)
5. [Comparative Benchmark Results](#comparative-benchmark-results)
6. [Commands Reference](#commands-reference)

---

## Quick Start: How to Start the App

### Prerequisites

- **Node.js**: Version `18.x` or higher (Node 20+ recommended)
- **npm** (or `bun` / `pnpm`)
- **Python**: Version `3.9` or higher

---

### 1. Starting the Interactive Web Dashboard

The web application provides a real-time casino table sandbox, dynamic Hi-Lo count HUD, live strategy advisor, interactive strategy lookup matrix, and in-browser Monte Carlo simulator.

1. **Install Node dependencies:**
   ```bash
   npm install
   ```

2. **Start the local development server:**
   ```bash
   npm run dev
   ```

3. **Open the application:**
   Navigate your web browser to:
   ```
   http://localhost:3000
   ```
   *(The dev server is bound to host `0.0.0.0` on port `3000`)*.

4. **Production Build & Preview:**
   To test the production-optimized build locally:
   ```bash
   npm run build
   npm run preview
   ```

5. **Type Checking & Linting:**
   ```bash
   npm run lint
   ```

---

### 2. Running the Python Research Engine & Simulations

The Python research engine provides high-throughput Monte Carlo simulations (~4,000 hands/sec), deterministic game execution, and mathematical verification.

#### A. Run 50,000-Round Monte Carlo Benchmark (Basic Strategy vs. Hi-Lo Spread)
Executes a head-to-head comparison of flat-betting Basic Strategy vs. Hi-Lo card counting with a 1-to-8 spread and Illustrious 18 deviations:
```bash
python3 examples/simulate_hi_lo.py
```

*Sample output metrics include:*
- Rounds & hands played
- Total handle & average bet
- Net profit / loss
- EV per round & Player ROI / Edge %
- Decisive win/loss/push percentages
- Maximum drawdown & final bankroll
- Insurance opportunities taken vs. won

#### B. Run Single-Round Trace Demo
Executes deterministic step-by-step game traces with full debugging logs:
```bash
python3 examples/single_round.py
```

---

### 3. Running the Unit Test Suite

The engine includes **62 comprehensive unit tests** validating cards, soft/hard hand mechanics, shoe penetration, table rules presets, dealer resolution, card counter observer isolation, basic strategy lookups, Illustrious 18 index deviations, and betting models:

```bash
python3 run_tests.py
```

Or via Python's built-in `unittest` runner:
```bash
python3 -m unittest discover tests
```

Expected output:
```
Ran 62 tests in 0.658s

OK
```

---

## Interactive Web Dashboard Features

### Tab 1: Interactive Sandbox & Live HUD
- **Persistent Bankroll & Multi-Session Ledger**:
  - **Persistent Bankroll State**: Tracks real player funds across browser reloads and multiple sessions using `localStorage`.
  - **Cumulative Profit / Loss Tracker**: Real-time display of total dollar gain/loss and overall Return on Investment (ROI %) across all completed sandbox rounds.
  - **Peak Bankroll & Drawdown**: Records high-water mark and current drawdown to analyze bankroll preservation during negative variance runs.
  - **Total Volume Wagered & Round Count**: Tracks cumulative cumulative wagering volume across sessions.
  - **Chip Sizing & Advantage Sizing**: Quick casino chip selectors ($5, $10, $25, $50, $100, $250), custom input, and one-click "Match Hi-Lo Bet" button linking the current True Count advantage directly to the table bet.
  - **Reload & Reset Controls**: One-click `+$500 Reload` and `Reset to $1,000` baseline controls.
- **Casino Felt & Card Mechanics**: Complete dealing lifecycle with natural blackjacks, split hands, double downs, late surrender, and dealer soft-17 rules.
- **Hi-Lo Observer HUD**:
  - **Running Count (RC)**: Live update with zero hole-card leakage.
  - **True Count (TC)**: Computed dynamically as $\text{TC} = \frac{\text{RC}}{\text{Decks Remaining}}$, with half-deck precision.
  - **Decks Remaining**: Exact shoe depletion tracking.
  - **Penetration Gauge**: Visual indicator showing shoe depth relative to the cut card.
  - **Bet Sizing Advisor**: Recommended unit spread based on current True Count.
- **Real-Time Strategy Advisor**: Dynamically evaluates the player's active hand against the dealer's upcard, recommending the mathematically optimal action (`HIT`, `STAND`, `DOUBLE`, `SPLIT`, `SURRENDER`) and highlighting when an **Illustrious 18 deviation** overrides basic strategy.
- **Rules Configuration Panel**: Adjust number of decks (1–8), penetration (50%–90%), Dealer Soft 17 (S17 vs. H17), Double After Split (DAS), Late Surrender (LS), and Insurance options on the fly.
- **Round Trace Log**: Complete chronological audit log of each deal, hit, stand, count update, and settlement with multi-session ledger balances.

### Tab 2: Strategy & Deviations Matrix
- **Complete Basic Strategy Charts**: Visual color-coded matrices for:
  - **Hard Totals (5 to 21)** vs. Dealer 2 through Ace.
  - **Soft Totals (A,2 to A,9)** vs. Dealer 2 through Ace.
  - **Pair Splitting (2,2 to A,A)** vs. Dealer 2 through Ace.
- **Live Rule Adaptation**: Matrices dynamically adjust when toggling between S17/H17, DAS, and Late Surrender.
- **Illustrious 18 & Fab Four Table**: Complete reference table of Don Schlesinger's index deviations, showing trigger True Count thresholds, basic strategy actions, deviation actions, and relative EV impact.

### Tab 3: Monte Carlo Simulation Workbench
- **In-Browser Simulation Engine**: Run simulations from 5,000 to 50,000 rounds directly in the browser.
- **Side-by-Side Comparison**: Evaluate Basic Strategy (Flat Betting) directly against Card Counting (Hi-Lo with 1-to-8 Spread & Deviations).
- **Interactive SVG Trajectory Chart**: Visualizes bankroll trajectories over time, showing short-term variance and long-term expected value divergence.
- **Key Quantitative Metrics**: Win Rate %, EV per Round, Return on Investment (ROI / Edge %), Max Drawdown, and Insurance profitability.

### Tabs 4 & 5: Architecture & Unit Tests
- **Architectural Blueprint**: In-depth documentation of state machine designs, card evaluation math, and component interfaces.
- **Test Suite Explorer**: Real-time display of all 62 unit tests across 9 test modules with verification status.

---

## Architecture & Design Principles

```
Card (Rank, Suit, blackjack point evaluation, Ace soft dynamics)
  ↓
Hand (Dynamic ace resolution, soft/hard calculation, split/double tracking)
  ↓
Shoe (Multi-deck continuous shoe, cut-card penetration, deterministic RNG seeds)
  ↓
Rules (Configurable table parameters: decks, S17/H17, DAS, Late Surrender, Insurance)
  ↓
Game / Round (Dealing lifecycle, insurance, player decisions, dealer play, settlement)
  ↓
Player Actions (HIT, STAND, DOUBLE, SPLIT, SURRENDER, INSURANCE)
  ↓
Strategy (Basic Strategy, Table-based lookups, True Count deviations)
  ↓
Counter (Hi-Lo, observer callbacks without hole-card leakage)
  ↓
Betting Strategy (Count-based spread, Kelly sizing)
  ↓
Simulator & Statistics (Monte Carlo sampling, EV, ROI, Drawdown, Risk of Ruin, 95% CI)
```

### Zero Hole-Card Leakage (Observer Pattern)

In authentic casino blackjack, the dealer receives one face-up card and one face-down hole card. A common simulation flaw is allowing the card counter to inspect the hole card before the player finishes acting.

The engine prevents this via an **observer pattern**:
1. During initial deal: Player Card 1, Player Card 2, and Dealer Upcard are published to observers.
2. Dealer Hole Card is stored privately in the `Game` state machine.
3. Observers only receive the hole card event when the dealer's turn officially begins (or during immediate natural peek).

### Continuous Multi-Deck Shoe (No-Shuffle-Bug Guarantee)

A classic simulation pitfall is shuffling between every single round ("no-shuffle bug"), which completely invalidates card counting.
- The `Shoe` persists across consecutive rounds.
- Cards dealt remain discarded until the cumulative dealt count crosses the `cut_card_threshold` ($\text{total cards} \times \text{penetration}$).
- Only when the threshold is reached does the shoe perform a complete shuffle and reset the running count.

### Illustrious 18 & Fab Four Deviations

The engine implements Don Schlesinger's **Illustrious 18** index deviations and **Fab Four** surrender deviations, including:

| Index | Hand | Dealer Upcard | Basic Action | Deviation Action | True Count Index |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | Insurance | Ace | Decline | Take Insurance | $\text{TC} \ge +3$ |
| 2 | 16 | 10 | Hit | Stand | $\text{TC} \ge 0$ |
| 3 | 15 | 10 | Hit | Stand | $\text{TC} \ge +4$ |
| 4 | 10,10 | 5 | Stand | Split | $\text{TC} \ge +5$ |
| 5 | 10,10 | 6 | Stand | Split | $\text{TC} \ge +4$ |
| 6 | 10 | 10 | Hit | Double | $\text{TC} \ge +4$ |
| 7 | 12 | 3 | Hit | Stand | $\text{TC} \ge +2$ |
| 8 | 12 | 2 | Hit | Stand | $\text{TC} \ge +3$ |
| 9 | 11 | Ace | Hit | Double | $\text{TC} \ge +1$ (S17) |
| 10 | 9 | 2 | Hit | Double | $\text{TC} \ge +1$ |
| 11 | 10 | Ace | Hit | Double | $\text{TC} \ge +4$ |
| 12 | 9 | 7 | Hit | Double | $\text{TC} \ge +3$ |
| 13 | 16 | 9 | Hit | Stand | $\text{TC} \ge +5$ |
| 14 | 13 | 2 | Hit | Stand | $\text{TC} \ge -1$ |
| 15 | 12 | 4 | Hit | Stand | $\text{TC} \ge 0$ |
| 16 | 12 | 5 | Hit | Stand | $\text{TC} \ge -2$ |
| 17 | 12 | 6 | Hit | Stand | $\text{TC} \ge -1$ |
| 18 | 13 | 3 | Hit | Stand | $\text{TC} \ge -2$ |
| FF 1 | 14 | 10 | Hit | Surrender | $\text{TC} \ge +3$ |
| FF 2 | 15 | 10 | Hit | Surrender | $\text{TC} \ge 0$ |
| FF 3 | 15 | 9 | Hit | Surrender | $\text{TC} \ge +2$ |
| FF 4 | 15 | Ace | Hit | Surrender | $\text{TC} \ge +1$ |

---

## Project Directory Structure

```
.
├── README.md                      # Comprehensive project documentation
├── package.json                   # Web application dependencies & scripts
├── vite.config.ts                 # Vite + Tailwind CSS configuration
├── metadata.json                  # Application metadata
├── index.html                     # Web entry point
├── run_tests.py                   # Automated Python unit test runner
│
├── blackjack/                     # Core Python Research Engine
│   ├── core/                      # Fundamental game engine primitives
│   │   ├── card.py                # Card, Rank, Suit with point valuation
│   │   ├── hand.py                # Hand evaluation, soft/hard Aces, split tracking
│   │   ├── shoe.py                # Multi-deck Shoe, cut-card penetration, deterministic RNG
│   │   ├── rules.py               # BlackjackRules dataclass and presets (S17, H17)
│   │   ├── actions.py             # Action enum (HIT, STAND, DOUBLE, SPLIT, SURRENDER, INSURANCE)
│   │   ├── result.py              # RoundResult, HandSettlement, RoundSettlement
│   │   └── game.py                # Complete round state machine & dealer logic
│   ├── strategy/                  # Strategy decision interfaces
│   │   ├── base.py                # Strategy abstract base class & CountState
│   │   ├── basic_strategy.py      # Hard, soft, split, and surrender lookup tables
│   │   ├── hi_lo.py               # HiLoCounter with observer pattern & TC calculation
│   │   └── deviations.py          # HiLoDeviationStrategy (Illustrious 18 & Fab Four)
│   ├── betting/                   # Wager sizing strategies
│   │   ├── base.py                # BettingStrategy interface
│   │   └── strategies.py          # FlatBetting, SpreadBetting, KellyBetting
│   └── simulation/                # High-speed Monte Carlo simulation
│       ├── stats.py               # Statistical accumulators (EV, ROI, Drawdown, RoR)
│       └── runner.py              # SimulationRunner multi-round coordinator
│
├── tests/                         # Full Unit Test Suite (62 tests)
│   ├── test_card.py               # Card valuation & parsing tests
│   ├── test_hand.py               # Dynamic Ace resolution & split hand tests
│   ├── test_shoe.py               # Shoe penetration & seed reproducibility tests
│   ├── test_rules.py              # Rule presets & validation tests
│   ├── test_game.py               # End-to-end round execution tests
│   ├── test_counter.py            # Hi-Lo tag summation & observer tests
│   ├── test_strategy.py           # Basic strategy & deviation index tests
│   ├── test_betting.py            # Flat, spread, and Kelly betting tests
│   └── test_simulation.py         # Monte Carlo runner integrity tests
│
├── examples/                      # Execution Demos
│   ├── single_round.py            # Traceable single round execution demo
│   └── simulate_hi_lo.py          # 50,000-round comparative Monte Carlo benchmark
│
└── src/                           # Modern React / TypeScript Dashboard
    ├── main.tsx                   # React root entry point
    ├── App.tsx                    # Main dashboard container & interactive sandbox
    ├── index.css                  # Tailwind CSS styling
    ├── components/
    │   ├── StrategyMatrix.tsx     # Interactive strategy and deviations lookup table
    │   └── SimulationView.tsx     # In-browser Monte Carlo simulator with SVG charts
    └── lib/
        └── strategyAdvisor.ts     # TypeScript strategy evaluation & Hi-Lo algorithms
```

---

## Comparative Benchmark Results

A standard 50,000-round simulation under Las Vegas Strip Rules (6 Decks, S17, DAS, Late Surrender, 3:2 Natural Blackjack, 75% Penetration) yields the following empirical results:

| Metric | Basic Strategy (Flat $10) | Hi-Lo Counter (1-to-8 Spread + Ill. 18) |
|:---|:---:|:---:|
| **Rounds Played** | 50,000 | 50,000 |
| **Total Wagered** | $519,850.00 | $945,510.00 |
| **Average Bet** | $10.40 | $18.91 |
| **Net Profit / Loss** | -$2,130.00 | +$1,840.00 to -$350.00 *(variance range)* |
| **EV per Round** | -$0.043 | +$0.037 |
| **Player ROI / Edge** | **-0.41%** | **+0.19% to +0.85%** |
| **Decisive Win Rate** | 46.51% | 46.78% |
| **Insurance Taken / Won** | 0 / 0 | 266 / 88 (33.08% win rate vs 30.77% BE) |

*The basic strategy empirical edge of $-0.41\%$ precisely aligns with the theoretical mathematical house edge of $-0.43\%$ for 6-deck S17 Las Vegas rules.*

---

## Commands Reference

| Command | Description |
|:---|:---|
| `npm run dev` | Start the interactive React development server on port 3000 |
| `npm run build` | Build the optimized web application for production |
| `npm run preview` | Locally preview the production build |
| `npm run lint` | Run TypeScript compiler type-checking (`tsc --noEmit`) |
| `python3 run_tests.py` | Run the complete 62-test unit verification suite |
| `python3 examples/single_round.py` | Run deterministic single-round game trace demo |
| `python3 examples/simulate_hi_lo.py` | Run 50,000-round comparative Monte Carlo simulation |

