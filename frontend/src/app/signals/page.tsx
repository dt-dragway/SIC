'use client'

import { useState } from 'react'
import Link from 'next/link'

interface Signal {
    symbol: string
    type: 'LONG' | 'SHORT'
    strength: 'STRONG' | 'MODERATE' | 'WEAK'
    confidence: number
    entry_price: number
    stop_loss: number
    take_profit: number
    risk_reward: number
    reasoning: string[]
    indicators: {
        rsi: number
        trend: string
    }
}

export default function SignalsPage() {
    // Demo signals
    const signals: Signal[] = [
        {
            symbol: 'BTCUSDT',
            type: 'LONG',
            strength: 'STRONG',
            confidence: 87.5,
            entry_price: 45000,
            stop_loss: 44200,
            take_profit: 47500,
            risk_reward: 3.12,
            reasoning: ['RSI sobreventa', 'MACD cruce alcista', 'Precio en banda inferior'],
            indicators: { rsi: 28, trend: 'BULLISH' }
        },
        {
            symbol: 'ETHUSDT',
            type: 'LONG',
            strength: 'MODERATE',
            confidence: 65.0,
            entry_price: 2500,
            stop_loss: 2420,
            take_profit: 2680,
            risk_reward: 2.25,
            reasoning: ['RSI neutral', 'Tendencia alcista'],
            indicators: { rsi: 45, trend: 'BULLISH' }
        }
    ]

    return (
        <main className="min-h-screen bg-sic-dark">
            {/* Header */}
            <header className="border-b border-sic-border px-6 py-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="text-2xl">🪙</Link>
                        <h1 className="text-xl font-bold">🎯 Señales IA</h1>
                    </div>
                    <button className="btn-primary">
                        🔄 Escanear Mercado
                    </button>
                </div>
            </header>

            <div className="max-w-7xl mx-auto p-6">
                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Señales Activas</p>
                        <p className="text-2xl font-bold text-sic-blue">{signals.length}</p>
                    </div>
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Win Rate (7d)</p>
                        <p className="text-2xl font-bold text-sic-green">67%</p>
                    </div>
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Señales Hoy</p>
                        <p className="text-2xl font-bold text-sic-purple">5</p>
                    </div>
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Mejor Señal</p>
                        <p className="text-2xl font-bold text-sic-green">+12.5%</p>
                    </div>
                </div>

                {/* Signals Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {signals.map((signal, i) => (
                        <div
                            key={i}
                            className={`glass-card p-6 ${signal.strength === 'STRONG' ? 'signal-strong' : ''
                                } ${signal.type === 'LONG'
                                    ? 'border-l-4 border-l-sic-green'
                                    : 'border-l-4 border-l-sic-red'
                                }`}
                        >
                            {/* Header */}
                            <div className="flex justify-between items-center mb-4">
                                <div className="flex items-center gap-2">
                                    <span className="text-2xl font-bold">{signal.symbol.replace('USDT', '')}</span>
                                    <span className={`px-2 py-1 rounded text-xs font-bold ${signal.type === 'LONG'
                                            ? 'bg-sic-green text-black'
                                            : 'bg-sic-red text-white'
                                        }`}>
                                        {signal.type}
                                    </span>
                                </div>
                                <span className={`px-2 py-1 rounded text-xs ${signal.strength === 'STRONG' ? 'bg-sic-purple text-white' :
                                        signal.strength === 'MODERATE' ? 'bg-sic-blue text-white' :
                                            'bg-gray-600 text-white'
                                    }`}>
                                    {signal.strength}
                                </span>
                            </div>

                            {/* Confidence */}
                            <div className="mb-4">
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-gray-400">Confianza</span>
                                    <span className="font-bold">{signal.confidence}%</span>
                                </div>
                                <div className="w-full h-2 bg-sic-border rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${signal.confidence >= 70 ? 'bg-sic-green' : signal.confidence >= 50 ? 'bg-sic-blue' : 'bg-sic-red'}`}
                                        style={{ width: `${signal.confidence}%` }}
                                    />
                                </div>
                            </div>

                            {/* Levels */}
                            <div className="space-y-2 mb-4">
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Entry</span>
                                    <span className="font-mono">${signal.entry_price.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Stop Loss</span>
                                    <span className="font-mono text-sic-red">${signal.stop_loss.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">Take Profit</span>
                                    <span className="font-mono text-sic-green">${signal.take_profit.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-gray-400">R:R</span>
                                    <span className="font-bold text-sic-purple">{signal.risk_reward}x</span>
                                </div>
                            </div>

                            {/* Indicators */}
                            <div className="flex gap-2 mb-4">
                                <span className={`px-2 py-1 rounded text-xs ${signal.indicators.rsi < 30 ? 'bg-sic-green/20 text-sic-green' :
                                        signal.indicators.rsi > 70 ? 'bg-sic-red/20 text-sic-red' :
                                            'bg-sic-border text-gray-300'
                                    }`}>
                                    RSI: {signal.indicators.rsi}
                                </span>
                                <span className={`px-2 py-1 rounded text-xs ${signal.indicators.trend === 'BULLISH' ? 'bg-sic-green/20 text-sic-green' : 'bg-sic-red/20 text-sic-red'
                                    }`}>
                                    {signal.indicators.trend === 'BULLISH' ? '📈' : '📉'} {signal.indicators.trend}
                                </span>
                            </div>

                            {/* Reasoning */}
                            <div className="mb-4">
                                <p className="text-gray-400 text-xs mb-1">Razonamiento:</p>
                                <ul className="text-sm text-gray-300 space-y-1">
                                    {signal.reasoning.map((r, j) => (
                                        <li key={j}>• {r}</li>
                                    ))}
                                </ul>
                            </div>

                            {/* Action Button */}
                            <button className={`w-full py-3 rounded-lg font-bold ${signal.type === 'LONG'
                                    ? 'bg-sic-green text-black'
                                    : 'bg-sic-red text-white'
                                }`}>
                                Ejecutar Trade
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </main>
    )
}
