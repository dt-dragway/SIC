'use client'

import { useState } from 'react'
import Header from '../../components/layout/Header'
import {
    Target,
    Activity,
    TrendingUp,
    TrendingDown,
    Calendar,
    Zap,
    ArrowUpRight,
    ArrowDownRight,
    BarChart3,
    AlertCircle,
    CheckCircle2,
    ChevronRight,
    Play
} from 'lucide-react'

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
        <main className="min-h-screen bg-[#0B0E14] text-slate-100 font-sans selection:bg-cyan-500/30">
            <Header />

            <div className="max-w-7xl mx-auto p-6">
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-rose-500 to-orange-600 flex items-center justify-center shadow-lg shadow-rose-500/20">
                            <Target className="text-white h-6 w-6" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-white">Señales <span className="text-rose-400">IA</span></h1>
                            <p className="text-slate-400 text-sm">Oportunidades detectoras por Inteligencia Artificial</p>
                        </div>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-blue-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Activity className="h-10 w-10" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Señales Activas</p>
                        <p className="text-3xl font-bold text-blue-400 tracking-tight">{signals.length}</p>
                    </div>
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-emerald-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <CheckCircle2 className="h-10 w-10" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Win Rate (7d)</p>
                        <p className="text-3xl font-bold text-emerald-400 tracking-tight">67%</p>
                    </div>
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-violet-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Calendar className="h-10 w-10" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Señales Hoy</p>
                        <p className="text-3xl font-bold text-violet-400 tracking-tight">5</p>
                    </div>
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-cyan-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Zap className="h-10 w-10" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Mejor Señal</p>
                        <p className="text-3xl font-bold text-cyan-400 tracking-tight">+12.5%</p>
                    </div>
                </div>

                {/* Signals Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {signals.map((signal, i) => (
                        <div
                            key={i}
                            className={`glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden transition-all hover:-translate-y-1 hover:shadow-2xl ${signal.type === 'LONG'
                                ? 'hover:shadow-emerald-500/10 hover:border-emerald-500/30'
                                : 'hover:shadow-rose-500/10 hover:border-rose-500/30'
                                }`}
                        >
                            {/* Background Glow */}
                            <div className={`absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl opacity-10 pointer-events-none ${signal.type === 'LONG' ? 'bg-emerald-500' : 'bg-rose-500'}`}></div>

                            {/* Header */}
                            <div className="flex justify-between items-center mb-6 relative z-10">
                                <div className="flex items-center gap-3">
                                    <div className="h-10 w-10 rounded-lg bg-white/5 flex items-center justify-center font-bold text-white border border-white/5">
                                        {signal.symbol.substring(0, 1)}
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-white leading-none">{signal.symbol.replace('USDT', '')}</h3>
                                        <span className="text-xs text-slate-500">USDT Perpetuos</span>
                                    </div>
                                </div>
                                <span className={`flex items-center gap-1 px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider ${signal.type === 'LONG'
                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                    }`}>
                                    {signal.type === 'LONG' ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                                    {signal.type}
                                </span>
                            </div>

                            {/* Confidence */}
                            <div className="mb-6 relative z-10">
                                <div className="flex justify-between text-xs mb-2">
                                    <span className="text-slate-400 font-medium uppercase tracking-wider flex items-center gap-1">
                                        <BarChart3 className="h-3 w-3" /> Confianza IA
                                    </span>
                                    <span className={`font-bold ${signal.confidence >= 80 ? 'text-emerald-400' : 'text-blue-400'}`}>{signal.confidence}%</span>
                                </div>
                                <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full ${signal.confidence >= 80 ? 'bg-gradient-to-r from-emerald-500 to-cyan-500' : 'bg-gradient-to-r from-blue-500 to-indigo-500'}`}
                                        style={{ width: `${signal.confidence}%` }}
                                    />
                                </div>
                            </div>

                            {/* Levels */}
                            <div className="grid grid-cols-2 gap-4 mb-6 relative z-10 bg-white/5 p-4 rounded-xl border border-white/5">
                                <div>
                                    <span className="text-xs text-slate-500 block mb-1">Entrada</span>
                                    <span className="font-mono text-white font-medium">${signal.entry_price.toLocaleString()}</span>
                                </div>
                                <div>
                                    <span className="text-xs text-slate-500 block mb-1">Ratio R:R</span>
                                    <span className="font-mono text-violet-400 font-bold">{signal.risk_reward}x</span>
                                </div>
                                <div>
                                    <span className="text-xs text-slate-500 block mb-1">Stop Loss</span>
                                    <span className="font-mono text-rose-400 font-medium">${signal.stop_loss.toLocaleString()}</span>
                                </div>
                                <div>
                                    <span className="text-xs text-slate-500 block mb-1">Take Profit</span>
                                    <span className="font-mono text-emerald-400 font-medium">${signal.take_profit.toLocaleString()}</span>
                                </div>
                            </div>

                            {/* Reasoning */}
                            <div className="mb-6 relative z-10">
                                <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2 flex items-center gap-1">
                                    <AlertCircle className="h-3 w-3" /> Análisis
                                </p>
                                <ul className="space-y-2">
                                    {signal.reasoning.map((r, j) => (
                                        <li key={j} className="text-xs text-slate-300 flex items-start gap-2">
                                            <ChevronRight className="h-3 w-3 text-cyan-500 mt-0.5" /> {r}
                                        </li>
                                    ))}
                                </ul>
                            </div>

                            {/* Action Button */}
                            <button className={`w-full py-3 rounded-xl font-bold text-sm transition-all shadow-lg active:scale-95 relative z-10 flex items-center justify-center gap-2 ${signal.type === 'LONG'
                                ? 'bg-emerald-500 text-black hover:bg-emerald-400 shadow-emerald-500/20'
                                : 'bg-rose-500 text-white hover:bg-rose-400 shadow-rose-500/20'
                                }`}>
                                <Play className="h-4 w-4 fill-current" />
                                Ejecutar Trade Automático
                            </button>
                        </div>
                    ))}
                </div>
            </div>
        </main>
    )
}
