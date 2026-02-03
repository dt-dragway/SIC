'use client'

import { useState } from 'react'



import { AVAILABLE_SYMBOLS } from '../../lib/constants'

// Adapter to match existing component logic directly


interface MarketListProps {
    currentSymbol: string
    onSymbolChange: (symbol: string) => void
}

export default function MarketList({ currentSymbol, onSymbolChange }: MarketListProps) {
    return (
        <div className="grid grid-cols-2 gap-1 px-1 py-1">
            {AVAILABLE_SYMBOLS.map(sym => (
                <button
                    key={sym.symbol}
                    onClick={() => onSymbolChange(sym.symbol)}
                    className={`text-left px-2 py-1.5 rounded text-xs transition-all flex items-center justify-between group ${currentSymbol === sym.symbol
                        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_10px_rgba(6,182,212,0.1)]'
                        : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'
                        }`}
                >
                    <div className="flex flex-col">
                        <span className="font-bold text-[10px] leading-tight">{sym.symbol.replace('USDT', '')}</span>
                        <span className="text-[9px] text-slate-600 group-hover:text-slate-500">USDT</span>
                    </div>
                </button>
            ))}
        </div>
    )
}
