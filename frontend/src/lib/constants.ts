
export interface CryptoSymbol {
    symbol: string;
    label: string;
    name: string;
    icon: string;
    color: string;
}

export const AVAILABLE_SYMBOLS: CryptoSymbol[] = [
    { symbol: 'BTCUSDT', label: 'BTC', name: 'Bitcoin', icon: '₿', color: 'text-orange-500' },
    { symbol: 'ETHUSDT', label: 'ETH', name: 'Ethereum', icon: 'Ξ', color: 'text-purple-500' },
    { symbol: 'BNBUSDT', label: 'BNB', name: 'Binance Coin', icon: 'BNB', color: 'text-yellow-500' },
    { symbol: 'SOLUSDT', label: 'SOL', name: 'Solana', icon: '◎', color: 'text-cyan-500' },
    { symbol: 'XRPUSDT', label: 'XRP', name: 'Ripple', icon: '✕', color: 'text-blue-500' },
    { symbol: 'ADAUSDT', label: 'ADA', name: 'Cardano', icon: '₳', color: 'text-blue-400' },
    { symbol: 'DOGEUSDT', label: 'DOGE', name: 'Dogecoin', icon: 'Ð', color: 'text-yellow-400' },
    { symbol: 'DOTUSDT', label: 'DOT', name: 'Polkadot', icon: '●', color: 'text-pink-500' },
    { symbol: 'MATICUSDT', label: 'MATIC', name: 'Polygon', icon: 'Ⓜ', color: 'text-violet-500' },
    { symbol: 'AVAXUSDT', label: 'AVAX', name: 'Avalanche', icon: '🔺', color: 'text-red-500' },
    { symbol: 'LINKUSDT', label: 'LINK', name: 'Chainlink', icon: '🔗', color: 'text-blue-600' },
    { symbol: 'LTCUSDT', label: 'LTC', name: 'Litecoin', icon: 'Ł', color: 'text-gray-400' },
    { symbol: 'TRXUSDT', label: 'TRX', name: 'Tron', icon: '♦', color: 'text-red-400' },
    { symbol: 'ATOMUSDT', label: 'ATOM', name: 'Cosmos', icon: '⚛', color: 'text-purple-400' },
    { symbol: 'UNIUSDT', label: 'UNI', name: 'Uniswap', icon: '🦄', color: 'text-pink-500' }
];

export const DEFAULT_SYMBOL = 'BTCUSDT';
