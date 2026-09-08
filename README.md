# Blackjack Research Engine

A quantitative research engine and Monte Carlo simulation platform designed for rigorous mathematical analysis of Blackjack basic strategy, card counting systems (Hi-Lo, deviations, Illustrious 18), and betting systems (Kelly Criterion, spread betting).

---

## Architecture Overview

The system strictly adheres to the principle: **Correctness → Architecture → Performance**.

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

---

## Directory Structure

```
blackjack/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── card.py          # Card, Rank, Suit with blackjack point values
│   ├── hand.py          # Hand with soft/hard Ace logic, status, actions
│   ├── shoe.py          # Multi-deck Shoe, cut-card penetration, seed
│   ├── rules.py         # BlackjackRules dataclass and presets (S17, H17)
│   ├── actions.py       # Action enum (HIT, STAND, DOUBLE, SPLIT, SURRENDER, INSURANCE)
│   ├── result.py        # RoundResult, HandSettlement, RoundSettlement
│   └── game.py          # Complete round state machine & dealer logic
│
tests/
├── __init__.py
├── test_card.py         # Rank and Card unit tests
├── test_hand.py         # Soft/hard Ace dynamics, blackjack, bust tests
├── test_shoe.py         # Penetration, deterministic seeds, no-shuffle tests
├── test_rules.py        # Rules validation and presets
└── test_game.py         # Deterministic end-to-end game round tests
│
examples/
└── single_round.py      # Traceable single round execution demo
run_tests.py             # Automated test discovery runner
```

---

## Running the Unit Tests

Execute the test suite with verbose reporting:

```bash
python3 run_tests.py
```

Or via standard `unittest`:

```bash
python3 -m unittest discover tests
```

---

## Running Single-Round Interactive Demo

```bash
python3 examples/single_round.py
```

---

## Completed: Phase 1 — Core Engine

1. **Card**: Ranks 2-10, J, Q, K, A. Numerical valuation, suits, parsing, immutability.
2. **Hand**: Ace point evaluation (A=11 or A=1 reduction), strict `is_soft` definition, natural blackjack, splits, busts.
3. **Shoe**: Multi-deck (1 to 8+ decks), cut-card penetration threshold, deterministic random seeds, persistent shoe across consecutive rounds (no-shuffle bug prevention).
4. **Rules**: `BlackjackRules` dataclass with S17/H17 options, DAS, late surrender, insurance, and deck configurations.
5. **Game**: Deal order, natural blackjacks, insurance handling, player actions (HIT, STAND, DOUBLE, SPLIT, SURRENDER), dealer playout, separated `result` and `profit` settlement, observer callbacks for card counters without hole-card leaks.
6. **Tests**: 39 comprehensive unit tests covering all core mechanics.
