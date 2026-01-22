'use client'

import { useState } from 'react'

interface Symbol {
    symbol: string
    name: string
}

const SYMBOLS: Symbol[] = [
    { symbol: 'BTCUSDT', name: 'Bitcoin' },
    { symbol: 'ETHUSDT', name: 'Ethereum' },
    { symbol: 'BNBUSDT', name: 'BNB' },
    { symbol: 'SOLUSDT', name: 'Solana' },
    { symbol: 'XRPUSDT', name: 'XRP' },
    { symbol: 'ADAUSDT', name: 'Cardano' },
    { symbol: 'DOGEUSDT', name: 'Dogecoin' },
    { symbol: 'DOTUSDT', name: 'Polkadot' },
    { symbol: 'MATICUSDT', name: 'Polygon' },
    { symbol: 'AVAXUSDT', name: 'Avalanche' },
    { symbol: 'LINKUSDT', name: 'Chainlink' },
    { symbol: 'LTCUSDT', name: 'Litecoin' },
    { symbol: 'TRXUSDT', name: 'Tron' },
    { symbol: 'ATOMUSDT', name: 'Cosmos' },
]

interface MarketListProps {
    currentSymbol: string
    onSymbolChange: (symbol: string) => void
}

export default function MarketList({ currentSymbol, onSymbolChange }: MarketListProps) {
    return (
        <div className="bg-[#0a0a0f] rounded-xl border border-white/10 p-4 h-full">
            <h3 className="text-sm font-medium text-slate-400 mb-3">Mercados</h3>
            <div className="space-y-1">
                {SYMBOLS.map(sym => (
                    <button
                        key={sym.symbol}
                        onClick={() => onSymbolChange(sym.symbol)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all ${currentSymbol === sym.symbol
                            ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                            : 'text-slate-400 hover:bg-white/5 hover:text-white'
                            }`}
                    >
                        <div className="flex items-center justify-between">
                            <span className="font-mono">{sym.symbol.replace('USDT', '')}</span>
                            <span className="text-xs text-slate-500">/USDT</span>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    )
}
