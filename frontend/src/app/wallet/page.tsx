'use client'

import { useState } from 'react'
import Link from 'next/link'

interface Balance {
    asset: string
    free: number
    locked: number
    total: number
    usd_value: number
}

export default function WalletPage() {
    const [mode, setMode] = useState<'practice' | 'real'>('practice')

    // Demo balances
    const practiceBalances: Balance[] = [
        { asset: 'USDT', free: 85.50, locked: 0, total: 85.50, usd_value: 85.50 },
        { asset: 'BTC', free: 0.00032, locked: 0, total: 0.00032, usd_value: 14.50 },
    ]

    const realBalances: Balance[] = [
        { asset: 'USDT', free: 500.00, locked: 0, total: 500.00, usd_value: 500.00 },
        { asset: 'BTC', free: 0.015, locked: 0, total: 0.015, usd_value: 675.00 },
        { asset: 'ETH', free: 0.25, locked: 0, total: 0.25, usd_value: 625.00 },
        { asset: 'BNB', free: 2.5, locked: 0, total: 2.5, usd_value: 800.00 },
    ]

    const balances = mode === 'practice' ? practiceBalances : realBalances
    const totalUsd = balances.reduce((sum, b) => sum + b.usd_value, 0)

    return (
        <main className="min-h-screen bg-sic-dark">
            {/* Header */}
            <header className="border-b border-sic-border px-6 py-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="text-2xl">🪙</Link>
                        <h1 className="text-xl font-bold">💰 Wallet</h1>
                    </div>

                    {/* Mode Toggle */}
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
            </header>

            <div className="max-w-7xl mx-auto p-6">
                {/* Total Balance */}
                <div className="glass-card p-8 mb-6 text-center">
                    <p className="text-gray-400 mb-2">
                        {mode === 'practice' ? '🎮 Balance Virtual' : '💰 Balance Real (Binance)'}
                    </p>
                    <p className="text-5xl font-bold text-white mb-2">
                        ${totalUsd.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                    {mode === 'practice' && (
                        <p className="text-sm text-gray-500">Iniciaste con $100.00</p>
                    )}

                    {mode === 'practice' && (
                        <div className="mt-4">
                            <button className="btn-secondary">
                                🔄 Resetear a $100
                            </button>
                        </div>
                    )}
                </div>

                {/* Balances Table */}
                <div className="glass-card overflow-hidden">
                    <div className="p-4 border-b border-sic-border">
                        <h2 className="text-lg font-semibold">Activos</h2>
                    </div>
                    <table className="w-full">
                        <thead className="bg-sic-dark">
                            <tr>
                                <th className="text-left px-6 py-4 text-gray-400 font-medium">Activo</th>
                                <th className="text-right px-6 py-4 text-gray-400 font-medium">Disponible</th>
                                <th className="text-right px-6 py-4 text-gray-400 font-medium">En Órdenes</th>
                                <th className="text-right px-6 py-4 text-gray-400 font-medium">Total</th>
                                <th className="text-right px-6 py-4 text-gray-400 font-medium">Valor USD</th>
                            </tr>
                        </thead>
                        <tbody>
                            {balances.map((balance, i) => (
                                <tr key={i} className="border-t border-sic-border hover:bg-sic-dark/50">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-3">
                                            <span className="text-2xl">
                                                {balance.asset === 'BTC' ? '₿' :
                                                    balance.asset === 'ETH' ? 'Ξ' :
                                                        balance.asset === 'BNB' ? '⬡' :
                                                            balance.asset === 'USDT' ? '💵' : '🪙'}
                                            </span>
                                            <span className="font-medium">{balance.asset}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono">
                                        {balance.free.toFixed(balance.asset === 'USDT' ? 2 : 8)}
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono text-gray-400">
                                        {balance.locked.toFixed(balance.asset === 'USDT' ? 2 : 8)}
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono font-medium">
                                        {balance.total.toFixed(balance.asset === 'USDT' ? 2 : 8)}
                                    </td>
                                    <td className="px-6 py-4 text-right font-mono text-sic-green font-medium">
                                        ${balance.usd_value.toFixed(2)}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
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
                    <button className="glass-card p-4 text-center hover:border-sic-green transition-all">
                        <span className="text-2xl">📊</span>
                        <p className="mt-2 font-medium">Historial</p>
                    </button>
                </div>
            </div>
        </main>
    )
}
