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
import SignalExecutionModal from '../components/trading/SignalExecutionModal' // Import Modal
import SentinelTerminal from '../components/dashboard/SentinelTerminal'
import { AVAILABLE_SYMBOLS, DEFAULT_SYMBOL } from '../lib/constants'
import { X, TrendingUp, TrendingDown, Trash2, ShieldAlert } from 'lucide-react'
import { toast } from 'sonner'

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
    type: 'LONG' | 'SHORT'
    entry_price: number
    stop_loss: number
    take_profit: number
    confidence: number
    reasoning?: string[]
}

export default function Home() {
    const router = useRouter()
    const { isAuthenticated, token, loading: authLoading } = useAuth()
    const { mode, setMode, totalUsd, isLoading: walletLoading, balances, refreshBalances } = useWallet() // Use Context

    const [selectedSymbol, setSelectedSymbol] = useState(DEFAULT_SYMBOL)
    const [signals, setSignals] = useState<Signal[]>([])
    const [stats, setStats] = useState({
        total_trades: 0,
        winning_trades: 0,
        losing_trades: 0,
        win_rate: 0,
        total_pnl: 0,
        roi_percent: 0
    })
    const [loading, setLoading] = useState(true)
    const [futuresPositions, setFuturesPositions] = useState<any[]>([])

    // Modal signal execution state
    const [isOrderModalOpen, setIsOrderModalOpen] = useState(false)
    const [selectedSignal, setSelectedSignal] = useState<Signal | null>(null)

    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push('/login')
        }
    }, [authLoading, isAuthenticated, router])

    useEffect(() => {
        const handleBinanceError = (e: Event) => {
            const detail = (e as CustomEvent).detail
            toast.error("⚠️ Error de Conexión a Binance", {
                description: `${detail}. Por favor, verifica que tus API Keys de Binance sean correctas y estén bien escritas en el archivo .env.`,
                duration: 10000
            })
        }
        window.addEventListener('sic_binance_error', handleBinanceError)
        return () => window.removeEventListener('sic_binance_error', handleBinanceError)
    }, [])

    useEffect(() => {
        if (!isAuthenticated) return

        fetchInitialData()
    }, [isAuthenticated, mode])

    // Polling en tiempo real silencioso para estadísticas y posiciones de futuros
    useEffect(() => {
        if (!isAuthenticated) return

        const intervalTime = mode === 'practice' ? 5000 : 30000
        const interval = setInterval(() => {
            fetchInitialData(true)
        }, intervalTime)

        return () => clearInterval(interval)
    }, [isAuthenticated, mode])

    const fetchInitialData = async (silent: boolean = false) => {
        if (!silent) setLoading(true)
        try {
            const authHeaders = { 'Authorization': `Bearer ${token}` }

            const [signalsRes, statsRes, positionsRes] = await Promise.all([
                fetch('/api/v1/trading/signals/dashboard', { headers: authHeaders }),
                fetch(mode === 'practice' ? '/api/v1/practice/stats' : '/api/v1/trading/stats', { headers: authHeaders }),
                fetch(mode === 'practice' ? '/api/v1/practice/futures/positions' : '/api/v1/trading/futures/positions', { headers: authHeaders }).catch(() => null)
            ])

            if (signalsRes.ok) {
                const signalsData = await signalsRes.json()
                setSignals(signalsData)
            }

            if (statsRes.ok) {
                const statsData = await statsRes.json()
                setStats({
                    total_trades: statsData.total_trades || 0,
                    winning_trades: statsData.winning_trades || 0,
                    losing_trades: statsData.losing_trades || 0,
                    win_rate: statsData.win_rate || 0,
                    total_pnl: statsData.total_pnl || 0,
                    roi_percent: statsData.roi_percent || 0
                })
            }

            if (positionsRes && positionsRes.ok) {
                setFuturesPositions(await positionsRes.json())
            } else {
                setFuturesPositions([])
            }

        } catch (error) {
            console.error('Error fetching dashboard data:', error)
        } finally {
            if (!silent) setLoading(false)
        }
    }

    const handleClosePosition = async (id: number, symbol: string) => {
        try {
            const authHeaders = { 'Authorization': `Bearer ${token}` }
            const endpoint = mode === 'practice'
                ? `/api/v1/practice/futures/close/${id}`
                : `/api/v1/trading/futures/close/${id}`

            const res = await fetch(endpoint, {
                method: 'POST',
                headers: authHeaders
            })

            if (res.ok) {
                const data = await res.json()
                const pnl = data.realized_pnl
                toast.success(`🚀 Contrato ${symbol} Cerrado`, {
                    description: `Posición liquidada con éxito. PNL Realizado: ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)} USD`
                })
                fetchInitialData(true)
                refreshBalances()
            } else {
                toast.error("Error al cerrar el contrato de futuros")
            }
        } catch (error) {
            console.error("Error closing position:", error)
            toast.error("Error de conexión al servidor")
        }
    }

    const handleRefresh = async () => {
        setLoading(true)
        await Promise.all([
            fetchInitialData(),
            refreshBalances()
        ])
        setLoading(false)
    }


    const handleExecuteSignal = (signal: Signal) => {
        setSelectedSignal(signal)
        setIsOrderModalOpen(true)
    }

    const handleDismissSignal = (index: number) => {
        const newSignals = [...signals]
        newSignals.splice(index, 1)
        setSignals(newSignals)
    }

    if (authLoading || !isAuthenticated) {
        return <LoadingSpinner />
    }

    const currentSymbolData = AVAILABLE_SYMBOLS.find(s => s.symbol === selectedSymbol) || AVAILABLE_SYMBOLS[0]

    return (
        <DashboardLayout>
            <div className="max-w-[1600px] mx-auto">
                {/* Dashboard Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                    <div>
                        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Dashboard</h1>
                        <p className="text-slate-500 mt-1 font-medium">Bienvenido, {mode === 'practice' ? 'Modo Simulación Activo' : 'Entorno Real (Mainnet)'}</p>
                    </div>

                    <div className="flex bg-white/5 p-1 rounded-lg border border-white/10 backdrop-blur-sm">
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
                        <p className="text-3xl font-bold text-white tracking-tight" suppressHydrationWarning>
                            ${totalUsd > 0 && totalUsd < 1
                                ? totalUsd.toLocaleString('en-US', { minimumFractionDigits: 5, maximumFractionDigits: 5 })
                                : totalUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
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
                            <div className={`p-2 rounded-lg ${stats.total_pnl >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'} group-hover:opacity-80 transition-colors`}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="20" x2="12" y2="10" /><line x1="18" y1="20" x2="18" y2="4" /><line x1="6" y1="20" x2="6" y2="16" /></svg>
                            </div>
                            <p className="text-slate-400 text-sm font-medium">P&L Total</p>
                        </div>
                        <p className={`text-3xl font-bold tracking-tight ${stats.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {stats.total_pnl >= 0 ? '+' : ''}${stats.total_pnl.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                        </p>
                        <p className={`text-xs mt-1 font-mono ${stats.roi_percent >= 0 ? 'text-emerald-500/80' : 'text-rose-500/80'}`}>
                            ROI: {stats.roi_percent >= 0 ? '+' : ''}{stats.roi_percent.toFixed(2)}%
                        </p>
                    </div>

                    {/* Signals Card */}
                    <div className="relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-sm hover:border-white/10 transition-all group">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-violet-500/10 text-violet-400 group-hover:bg-violet-500/20 transition-colors">
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><line x1="22" y1="12" x2="18" y2="12" /><line x1="6" y1="12" x2="2" y2="12" /><line x1="12" y1="6" x2="12" y2="2" /><line x1="12" y1="22" x2="12" y2="18" /></svg>
                            </div>
                            <p className="text-slate-400 text-sm font-medium">Operaciones</p>
                        </div>
                        <p className="text-3xl font-bold text-violet-400 tracking-tight">
                            {stats.total_trades}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">{signals.length} señales activas</p>
                    </div>

                    {/* Win Rate Card */}
                    <div className="relative overflow-hidden rounded-xl border border-white/5 bg-white/[0.02] p-6 backdrop-blur-sm hover:border-white/10 transition-all group">
                        <div className="flex items-center gap-3 mb-2">
                            <div className={`p-2 rounded-lg ${stats.win_rate >= 50 ? 'bg-amber-500/10 text-amber-400' : 'bg-slate-500/10 text-slate-400'} group-hover:opacity-80 transition-colors`}>
                                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" /><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" /><path d="M4 22h16" /><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" /><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" /><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" /></svg>
                            </div>
                            <p className="text-slate-400 text-sm font-medium">Tasa de Acierto</p>
                        </div>
                        <p className={`text-3xl font-bold tracking-tight ${stats.win_rate >= 50 ? 'text-amber-400' : 'text-slate-400'}`}>
                            {stats.total_trades > 0 ? `${stats.win_rate.toFixed(1)}%` : '--%'}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                            {stats.winning_trades}W / {stats.losing_trades}L
                        </p>
                    </div>
                </div>


                <div className="mb-8">
                    <AIWidget symbol={selectedSymbol} />
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Chart Section */}
                    <div className="lg:col-span-2 glass-card p-6 border border-white/5 bg-white/[0.02]">
                        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4">
                            <div className="flex items-center gap-4">
                                <h2 className="text-lg font-semibold flex items-center gap-2">
                                    <span className={currentSymbolData.color}>{currentSymbolData.icon}</span>
                                    {selectedSymbol}
                                </h2>

                                {/* Symbol Selector */}
                                <div className="flex gap-1 bg-black/40 p-1 rounded-lg border border-white/5 overflow-x-auto whitespace-nowrap scrollbar-hide max-w-[200px] sm:max-w-md">
                                    {AVAILABLE_SYMBOLS.map(sym => (
                                        <button
                                            key={sym.symbol}
                                            onClick={() => setSelectedSymbol(sym.symbol)}
                                            className={`px-3 py-1 text-xs rounded-md font-medium transition-all ${selectedSymbol === sym.symbol
                                                ? 'bg-white/10 text-white shadow-sm border border-white/10'
                                                : 'text-slate-500 hover:text-slate-300 hover:bg-white/5'
                                                }`}
                                        >
                                            {sym.label}
                                        </button>
                                    ))}
                                </div>
                            </div>

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
                            <CandlestickChart
                                symbol={selectedSymbol}
                                activeSignal={signals.find(s => s.symbol === selectedSymbol)}
                            />
                        </div>
                    </div>

                    {/* Signals Panel */}
                    <div className="mate-card p-6 border border-white/5 bg-white/[0.02]">
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
                                            <div className="flex items-center gap-2">
                                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold tracking-wider ${signal.type === 'LONG'
                                                    ? 'bg-emerald-500/20 text-emerald-400'
                                                    : 'bg-rose-500/20 text-rose-400'
                                                    }`}>
                                                    {signal.type === 'LONG' ? 'COMPRAR (LONG)' : 'VENDER (SHORT)'}
                                                </span>
                                                <button
                                                    onClick={(e) => {
                                                        e.stopPropagation()
                                                        handleDismissSignal(i)
                                                    }}
                                                    className="p-1 text-slate-500 hover:text-white hover:bg-white/10 rounded-full transition-all"
                                                    title="Descartar señal"
                                                >
                                                    <X size={14} />
                                                </button>
                                            </div>
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

                                        <button
                                            onClick={() => handleExecuteSignal(signal)}
                                            className="w-full mt-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm font-medium transition-all"
                                        >
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

                {/* Posiciones de Futuros Activas */}
                <div className="mt-8 glass-card overflow-hidden rounded-3xl border border-white/5 bg-white/[0.01] backdrop-blur-md">
                    <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                        <div className="flex items-center gap-2">
                            <span className="text-xl">📊</span>
                            <h2 className="font-bold text-lg text-white">Posiciones de Futuros Tácticos</h2>
                            <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-mono">
                                {futuresPositions.length} Abierta{futuresPositions.length > 1 ? 's' : ''}
                            </span>
                        </div>
                    </div>

                    {futuresPositions.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-black/40">
                                    <tr>
                                        <th className="text-left py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">Par</th>
                                        <th className="text-center py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">Dirección / Lever</th>
                                        <th className="text-right py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">Tamaño (Contrato)</th>
                                        <th className="text-right py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">Precio Entrada</th>
                                        <th className="text-right py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">Precio Liquidación</th>
                                        <th className="text-right py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">Margen</th>
                                        <th className="text-right py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">PNL No Realizado (uPNL)</th>
                                        <th className="text-center py-4 px-6 text-xs font-semibold text-slate-400 uppercase tracking-wider">Acción</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5 bg-black/10">
                                    {futuresPositions.map((pos) => {
                                        const isLong = pos.side === 'LONG';
                                        const pnlIsPositive = pos.unrealized_pnl >= 0;
                                        return (
                                            <tr key={pos.id} className="hover:bg-white/[0.02] transition-colors group">
                                                <td className="py-4 px-6 font-bold text-white tracking-tight">
                                                    {pos.symbol}
                                                </td>
                                                <td className="py-4 px-6 text-center">
                                                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${
                                                        isLong 
                                                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                                                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                                    }`}>
                                                        {isLong ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                                                        {pos.side} {pos.leverage}x
                                                    </span>
                                                </td>
                                                <td className="py-4 px-6 text-right font-mono text-slate-200">
                                                    {pos.size.toLocaleString('en-US', { minimumFractionDigits: 4, maximumFractionDigits: 6 })} {pos.symbol.replace('USDT', '')}
                                                    <div className="text-[10px] text-slate-500 mt-0.5">
                                                        Notional: ${(pos.size * pos.entry_price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USDT
                                                    </div>
                                                </td>
                                                <td className="py-4 px-6 text-right font-mono text-slate-300">
                                                    ${pos.entry_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 })}
                                                </td>
                                                <td className="py-4 px-6 text-right font-mono text-amber-500 font-medium">
                                                    ${pos.liquidation_price > 0.01 
                                                        ? pos.liquidation_price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 }) 
                                                        : '0.00'
                                                    }
                                                </td>
                                                <td className="py-4 px-6 text-right font-mono text-slate-400">
                                                    ${pos.margin.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USDT
                                                </td>
                                                <td className="py-4 px-6 text-right font-mono">
                                                    <div className={`font-bold flex items-center justify-end gap-1 ${pnlIsPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                        {pnlIsPositive ? '+' : ''}${pos.unrealized_pnl.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                                    </div>
                                                    <div className={`text-xs ${pnlIsPositive ? 'text-emerald-500/80' : 'text-rose-500/80'}`}>
                                                        {pnlIsPositive ? '+' : ''}{pos.pnl_percent.toFixed(2)}%
                                                    </div>
                                                </td>
                                                <td className="py-4 px-6 text-center">
                                                    <button
                                                        onClick={() => handleClosePosition(pos.id, pos.symbol)}
                                                        className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 hover:text-rose-300 font-medium text-xs transition-all border border-rose-500/20 hover:border-rose-500/40 flex items-center justify-center gap-1 mx-auto"
                                                        title="Cerrar Posición"
                                                    >
                                                        <Trash2 size={12} />
                                                        Cerrar
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="p-8 text-center flex flex-col items-center justify-center space-y-3">
                            <div className="h-12 w-12 rounded-2xl bg-white/5 flex items-center justify-center text-slate-400 border border-white/5">
                                📊
                            </div>
                            <div>
                                <h3 className="text-white font-bold text-sm">Sin Posiciones Activas</h3>
                                <p className="text-slate-500 text-xs mt-1 max-w-sm mx-auto leading-relaxed">
                                    No tienes contratos de futuros tácticos abiertos en este momento. Selecciona una señal de trading de la terminal de arriba y opera en LONG o SHORT para abrir una posición con apalancamiento.
                                </p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Sentinel CIO Activity Log */}
                <div className="mt-8 min-h-[400px]">
                    <SentinelTerminal />
                </div>
            </div>

            {/* Modal de Ejecución de Señales */}
            {selectedSignal && (
                <SignalExecutionModal
                    isOpen={isOrderModalOpen}
                    onClose={() => setIsOrderModalOpen(false)}
                    signal={selectedSignal}
                    accountBalance={mode === 'practice' ? totalUsd : (balances.find(b => b.asset === 'USDT')?.total || 0)}
                    availableBalance={(() => {
                        if (selectedSignal.type === 'LONG') {
                            return (balances.find(b => b.asset === 'USDT')?.total || 0)
                        } else {
                            const baseAsset = selectedSignal.symbol.replace('USDT', '')
                            return balances.find(b => b.asset === baseAsset)?.total || 0
                        }
                    })()}
                    balanceAsset={(() => {
                        if (selectedSignal.type === 'LONG') return 'USDT'
                        return selectedSignal.symbol.replace('USDT', '')
                    })()}
                    mode={mode === 'practice' ? 'practice' : 'real'}
                    onOrderSubmit={async () => {
                        if (selectedSignal) {
                            setSignals(prev => prev.filter(s => s.symbol !== selectedSignal.symbol))
                        }
                        setIsOrderModalOpen(false)
                        await handleRefresh()
                    }}
                />
            )}
        </DashboardLayout>
    )
}
