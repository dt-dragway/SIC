'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Balance {
    asset: string
    total: number
    usd_value: number
}

interface Signal {
    symbol: string
    type: string
    confidence: number
    entry_price: number
    stop_loss: number
    take_profit: number
    strength: string
}

export default function Home() {
    const [mode, setMode] = useState<'practice' | 'real'>('practice')
    const [wallet, setWallet] = useState<{ total_usd: number; balances: Balance[] } | null>(null)
    const [signals, setSignals] = useState<Signal[]>([])
    const [loading, setLoading] = useState(true)

    // Simulated data for demo (will connect to API)
    useEffect(() => {
        // Demo data
        setWallet({
            total_usd: 100.00,
            balances: [
                { asset: 'USDT', total: 100.00, usd_value: 100.00 }
            ]
        })

        setSignals([
            {
                symbol: 'BTCUSDT',
                type: 'LONG',
                confidence: 87.5,
                entry_price: 45000,
                stop_loss: 44200,
                take_profit: 47500,
                strength: 'STRONG'
            }
        ])

        setLoading(false)
    }, [])

    return (
        <main className="min-h-screen bg-sic-dark">
            {/* Header */}
            <header className="border-b border-sic-border px-6 py-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <span className="text-2xl">🪙</span>
                        <h1 className="text-xl font-bold text-white">SIC Ultra</h1>
                    </div>

                    {/* Mode Toggle */}
                    <div className="flex items-center gap-4">
                        <div className="glass-card flex p-1">
                            <button
                                onClick={() => setMode('practice')}
                                className={`px-4 py-2 rounded-lg transition-all ${mode === 'practice'
                                        ? 'bg-sic-green text-black font-semibold'
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                🎮 Práctica
                            </button>
                            <button
                                onClick={() => setMode('real')}
                                className={`px-4 py-2 rounded-lg transition-all ${mode === 'real'
                                        ? 'bg-sic-red text-white font-semibold'
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                ⚔️ Real
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto p-6">
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    {/* Balance Card */}
                    <div className="glass-card p-6">
                        <p className="text-gray-400 text-sm mb-1">Balance Total</p>
                        <p className="text-3xl font-bold text-sic-green">
                            ${wallet?.total_usd.toFixed(2) || '0.00'}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                            {mode === 'practice' ? 'Dinero virtual' : 'Wallet Binance'}
                        </p>
                    </div>

                    {/* P&L Card */}
                    <div className="glass-card p-6">
                        <p className="text-gray-400 text-sm mb-1">P&L Hoy</p>
                        <p className="text-3xl font-bold text-sic-green">
                            +$0.00
                        </p>
                        <p className="text-xs text-sic-green mt-1">+0.00%</p>
                    </div>

                    {/* Signals Card */}
                    <div className="glass-card p-6">
                        <p className="text-gray-400 text-sm mb-1">Señales Activas</p>
                        <p className="text-3xl font-bold text-sic-blue">
                            {signals.length}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Última: hace 5min</p>
                    </div>

                    {/* Win Rate Card */}
                    <div className="glass-card p-6">
                        <p className="text-gray-400 text-sm mb-1">Win Rate</p>
                        <p className="text-3xl font-bold text-sic-purple">
                            --%
                        </p>
                        <p className="text-xs text-gray-500 mt-1">Sin trades aún</p>
                    </div>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Chart Section */}
                    <div className="lg:col-span-2 glass-card p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">📈 BTCUSDT</h2>
                            <div className="flex gap-2">
                                {['1h', '4h', '1d'].map(tf => (
                                    <button
                                        key={tf}
                                        className="px-3 py-1 text-sm rounded bg-sic-border hover:bg-sic-green hover:text-black transition-all"
                                    >
                                        {tf}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="bg-sic-dark rounded-lg h-[400px] flex items-center justify-center">
                            <p className="text-gray-500">📊 Gráfico TradingView aquí</p>
                        </div>
                    </div>

                    {/* Signals Panel */}
                    <div className="glass-card p-6">
                        <h2 className="text-lg font-semibold mb-4">🎯 Señales IA</h2>

                        {signals.length > 0 ? (
                            <div className="space-y-4">
                                {signals.map((signal, i) => (
                                    <div
                                        key={i}
                                        className={`p-4 rounded-lg border ${signal.type === 'LONG'
                                                ? 'border-sic-green bg-sic-green/10'
                                                : 'border-sic-red bg-sic-red/10'
                                            } ${signal.strength === 'STRONG' ? 'signal-strong' : ''}`}
                                    >
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="font-bold">{signal.symbol}</span>
                                            <span className={`px-2 py-1 rounded text-xs font-bold ${signal.type === 'LONG'
                                                    ? 'bg-sic-green text-black'
                                                    : 'bg-sic-red text-white'
                                                }`}>
                                                {signal.type}
                                            </span>
                                        </div>

                                        <div className="text-sm space-y-1 text-gray-300">
                                            <p>Confianza: <span className="text-white font-semibold">{signal.confidence}%</span></p>
                                            <p>Entry: <span className="text-white">${signal.entry_price.toLocaleString()}</span></p>
                                            <p>SL: <span className="text-sic-red">${signal.stop_loss.toLocaleString()}</span></p>
                                            <p>TP: <span className="text-sic-green">${signal.take_profit.toLocaleString()}</span></p>
                                        </div>

                                        <button className="w-full mt-3 btn-primary text-sm">
                                            Ejecutar Trade
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500 text-center py-8">
                                No hay señales activas
                            </p>
                        )}
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
                    <Link href="/trading" className="glass-card p-4 text-center hover:border-sic-green transition-all">
                        <span className="text-2xl">📈</span>
                        <p className="mt-2 font-medium">Trading</p>
                    </Link>
                    <Link href="/p2p" className="glass-card p-4 text-center hover:border-sic-green transition-all">
                        <span className="text-2xl">💱</span>
                        <p className="mt-2 font-medium">P2P VES</p>
                    </Link>
                    <Link href="/signals" className="glass-card p-4 text-center hover:border-sic-green transition-all">
                        <span className="text-2xl">🎯</span>
                        <p className="mt-2 font-medium">Señales</p>
                    </Link>
                    <Link href="/wallet" className="glass-card p-4 text-center hover:border-sic-green transition-all">
                        <span className="text-2xl">💰</span>
                        <p className="mt-2 font-medium">Wallet</p>
                    </Link>
                </div>
            </div>
        </main>
    )
}
