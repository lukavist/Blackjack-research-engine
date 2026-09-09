export interface CardData {
  rank: string;
  suit: string;
  value: number;
}

export interface HandData {
  cards: CardData[];
  bet: number;
  status: string;
  value: number;
  isSoft: boolean;
  isBust: boolean;
  isBlackjack: boolean;
}

export const DEFAULT_BANKROLL = 1000;

export interface PersistentBankrollData {
  bankroll: number;
  initialBankroll: number;
  totalRounds: number;
  peakBankroll: number;
  totalWagered: number;
}

export const loadPersistentBankroll = (): PersistentBankrollData => {
  try {
    const raw = localStorage.getItem('bj_sandbox_bankroll_v1');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (typeof parsed.bankroll === 'number' && !isNaN(parsed.bankroll)) {
        return {
          bankroll: Math.round(parsed.bankroll * 100) / 100,
          initialBankroll: typeof parsed.initialBankroll === 'number' ? parsed.initialBankroll : DEFAULT_BANKROLL,
          totalRounds: typeof parsed.totalRounds === 'number' ? parsed.totalRounds : 0,
          peakBankroll: typeof parsed.peakBankroll === 'number' ? parsed.peakBankroll : parsed.bankroll,
          totalWagered: typeof parsed.totalWagered === 'number' ? parsed.totalWagered : 0,
        };
      }
    }
  } catch (e) {
    console.error('Failed to load sandbox bankroll from localStorage:', e);
  }
  return {
    bankroll: DEFAULT_BANKROLL,
    initialBankroll: DEFAULT_BANKROLL,
    totalRounds: 0,
    peakBankroll: DEFAULT_BANKROLL,
    totalWagered: 0,
  };
};

export const savePersistentBankroll = (data: PersistentBankrollData): void => {
  try {
    localStorage.setItem('bj_sandbox_bankroll_v1', JSON.stringify(data));
  } catch (e) {
    console.error('Failed to save sandbox bankroll to localStorage:', e);
  }
};

export const SUIT_SYMBOLS: Record<string, { symbol: string; color: string }> = {
  S: { symbol: '♠', color: 'text-slate-900' },
  H: { symbol: '♥', color: 'text-red-600' },
  D: { symbol: '♦', color: 'text-red-600' },
  C: { symbol: '♣', color: 'text-slate-900' },
};
