'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import dynamic from 'next/dynamic'
import DashboardLayout from '../components/layout/DashboardLayout'
import AIWidget from '../components/dashboard/AIWidget'
import { useAuth } from '../hooks/useAuth'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import { useWallet } from '../context/WalletContext' // Import Context
import InstitutionalAssistant from '../components/ai/InstitutionalAssistant'
import AINeuroEngine from '../components/ai/AINeuroEngine'

const CandlestickChart = dynamic(
    () => import('../components/charts/CandlestickChart').then(mod => mod.CandlestickChart),
    { ssr: false }
)

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
    const router = useRouter()
    const { isAuthenticated, loading: authLoading, token } = useAuth()
    const { mode, setMode, totalUsd, balances, isLoading: walletLoading } = useWallet() // Use Global Wallet

    const [signals, setSignals] = useState<Signal[]>([])
    const [dataLoading, setDataLoading] = useState(true)

    // Auth Guard
    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push('/login')
        }
    }, [authLoading, isAuthenticated, router])

    // Data Fetching
    useEffect(() => {
        if (authLoading || !isAuthenticated || !token) return;

        const fetchData = async () => {
            try {
                setDataLoading(true);

                // === REAL AI ANALYSIS ===
                // Connect to trading agent for real market analysis
                const signalsRes = await fetch('/api/v1/signals/scan', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });

                if (signalsRes.ok) {
                    const data = await signalsRes.json();
                    // Only show top 5 signals in dashboard
                    const topSignals = data.signals ? data.signals.slice(0, 5) : [];
                    setSignals(topSignals);
                } else {
                    // Fallback to empty if API fails
                    console.warn('Signals API failed, showing empty state');
                    setSignals([]);
                }

                // Market Status (Optional global stats)
                // const marketRes = await fetch('/api/v1/market/status');
            } catch (error) {
                console.error("Error fetching dashboard data", error);
                setSignals([]); // Clear signals on error
            } finally {
                setDataLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 120000); // Update every 2 minutes

        return () => clearInterval(interval);
    }, [authLoading, isAuthenticated, token]);

    if (authLoading || (walletLoading && isAuthenticated)) {
        return <LoadingSpinner />
    }

    if (!isAuthenticated) {
        return null;
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto px-6 py-6 pb-6">
                {/* Header with Mode Switcher */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Dashboard
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">Visión general de tu portafolio y señales de trading</p>
                    </div>

                    {/* Mode Switcher */}
                    <div className="flex items-center gap-2 bg-white/5 p-1 rounded-lg border border-white/10">
                        <button
                            onClick={() => setMode('practice')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${mode === 'practice'
                                ? 'bg-emerald-500/20 text-emerald-400 shadow-sm ring-1 ring-emerald-500/50'
                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            Modo Práctica
                        </button>
                        <button
                            onClick={() => setMode('real')}
                            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${mode === 'real'
                                ? 'bg-blue-500/20 text-blue-400 shadow-sm ring-1 ring-blue-500/50'
                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            Modo Real
                        </button>
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    {/* Balance Card */}
                    <div className="relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-sm hover:border-white/10 transition-all group">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 group-hover:bg-emerald-500/20 transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 12V8H6a2 2 0 0 1-2-2c0-1.1.9-2 2-2h12v4" /><path d="M4 6v12a2 2 0 0 0 2-2h14v-4" /><path d="M18 12a2 2 0 0 0-2 2c0 1.1.9 2 2 2h4v-4h-4z" /></svg>
                            </div>
                            <p className="text-slate-400 text-sm font-medium">Balance Total</p>
                        </div>
                        <p className="text-3xl font-bold text-white tracking-tight">
                            ${totalUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}
                        </p>
                        <div className="mt-3 flex items-center gap-2">
                            <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-0.5 rounded-full ${mode === 'practice' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-cyan-500/10 text-cyan-400'
                                }`}>
                                {mode === 'practice' ? 'USD VIRTUAL' : 'BINANCE SPOT'}
                            </span>
                        </div>
                    </div>

                    {/* P&L Card */}
                    <div className="relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-sm hover:border-white/10 transition-all group">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 group-hover:bg-cyan-500/20 transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10" /><line x1="18" y1="20" x2="18" y2="4" /><line x1="6" y1="20" x2="6" y2="16" /></svg>
                            </div>
                            <p className="text-slate-400 text-sm font-medium">P&L 24h</p>
                        </div>
                        <p className="text-3xl font-bold text-emerald-400 tracking-tight">
                            +$0.00
                        </p>
                        <p className="text-xs text-emerald-500/80 mt-1 font-mono">+0.00%</p>
                    </div>

                    {/* Signals Card */}
                    <div className="relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-sm hover:border-white/10 transition-all group">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-violet-500/10 text-violet-400 group-hover:bg-violet-500/20 transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="22" y1="12" x2="18" y2="12" /><line x1="6" y1="12" x2="2" y2="12" /><line x1="12" y1="6" x2="12" y2="2" /><line x1="12" y1="22" x2="12" y2="18" /></svg>
                            </div>
                            <p className="text-slate-400 text-sm font-medium">Señales Activas</p>
                        </div>
                        <p className="text-3xl font-bold text-violet-400 tracking-tight">
                            {signals.length}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">Actualizado: Ahora</p>
                    </div>

                    {/* Win Rate Card */}
                    <div className="relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-sm hover:border-white/10 transition-all group">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 group-hover:bg-amber-500/20 transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" /><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" /><path d="M4 22h16" /><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" /><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" /><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" /></svg>
                            </div>
                            <p className="text-slate-400 text-sm font-medium">Tasa de Acierto</p>
                        </div>
                        <p className="text-3xl font-bold text-amber-400 tracking-tight">
                            --%
                        </p>
                        <p className="text-xs text-slate-500 mt-1">Sin operaciones</p>
                    </div>
                </div>

                {/* AI Neural Engine Widget */}
                <div className="mb-8">
                    <AIWidget symbol="BTCUSDT" />
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Chart Section */}
                    <div className="lg:col-span-2 glass-card p-6 border border-white/5 bg-white/[0.02]">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                <span className="text-orange-500">₿</span> BTCUSDT
                            </h2>
                            <div className="flex gap-2">
                                {['1h', '4h', '1d'].map(tf => (
                                    <button
                                        key={tf}
                                        className="px-3 py-1 text-sm rounded bg-white/5 hover:bg-sic-green hover:text-black transition-all border border-white/5"
                                    >
                                        {tf}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="bg-black/40 rounded-lg min-h-[400px] h-[400px] border border-white/5 overflow-hidden">
                            <CandlestickChart symbol="BTCUSDT" />
                        </div>
                    </div>

                    {/* Signals Panel */}
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02]">
                        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                            <span>🎯</span> Señales IA
                        </h2>

                        {signals.length > 0 ? (
                            <div className="space-y-4">
                                {signals.map((signal, i) => (
                                    <div
                                        key={i}
                                        className={`p-4 rounded-lg border ${signal.type === 'LONG'
                                            ? 'border-emerald-500/30 bg-emerald-500/5'
                                            : 'border-rose-500/30 bg-rose-500/5'
                                            } hover:border-opacity-50 transition-all`}
                                    >
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="font-bold tracking-tight">{signal.symbol}</span>
                                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${signal.type === 'LONG'
                                                ? 'bg-emerald-500/20 text-emerald-400'
                                                : 'bg-rose-500/20 text-rose-400'
                                                }`}>
                                                {signal.type}
                                            </span>
                                        </div>

                                        <div className="text-sm space-y-1.5 text-slate-400">
                                            <div className="flex justify-between">
                                                <span>Confianza</span>
                                                <span className="text-white font-mono">{signal.confidence}%</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Entrada</span>
                                                <span className="text-white font-mono">${signal.entry_price.toLocaleString()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Stop Loss</span>
                                                <span className="text-rose-400 font-mono">${signal.stop_loss.toLocaleString()}</span>
                                            </div>
                                            <div className="flex justify-between">
                                                <span>Take Profit</span>
                                                <span className="text-emerald-400 font-mono">${signal.take_profit.toLocaleString()}</span>
                                            </div>
                                        </div>

                                        <button className="w-full mt-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm font-medium transition-all">
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
                    <Link href="/trading" className="glass-card p-4 text-center hover:border-emerald-500/30 transition-all group bg-white/[0.02]">
                        <span className="text-2xl grayscale group-hover:grayscale-0 transition-all">📈</span>
                        <p className="mt-2 font-medium text-slate-300 group-hover:text-white">Trading</p>
                    </Link>
                    <Link href="/p2p" className="glass-card p-4 text-center hover:border-emerald-500/30 transition-all group bg-white/[0.02]">
                        <span className="text-2xl grayscale group-hover:grayscale-0 transition-all">💱</span>
                        <p className="mt-2 font-medium text-slate-300 group-hover:text-white">P2P VES</p>
                    </Link>
                    <Link href="/signals" className="glass-card p-4 text-center hover:border-emerald-500/30 transition-all group bg-white/[0.02]">
                        <span className="text-2xl grayscale group-hover:grayscale-0 transition-all">🎯</span>
                        <p className="mt-2 font-medium text-slate-300 group-hover:text-white">Señales</p>
                    </Link>
                    <Link href="/wallet" className="glass-card p-4 text-center hover:border-emerald-500/30 transition-all group bg-white/[0.02]">
                        <span className="text-2xl grayscale group-hover:grayscale-0 transition-all">💰</span>
                        <p className="mt-2 font-medium text-slate-300 group-hover:text-white">Billetera</p>
                    </Link>
                </div>
            </div>
        </DashboardLayout>
    )
}
