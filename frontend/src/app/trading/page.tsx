'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import {
    TrendingUp,
    TrendingDown,
    Clock,
    BarChart2,
    Zap,
    Wallet,
    ArrowUpRight,
    ArrowDownRight,
    Search,
    ChevronDown,
    Gamepad2,
    Swords,
    Target,
    Activity,
    Calendar,
    CheckCircle2,
    ChevronRight,
    Play,
    History,
    ArrowRightLeft,
    Users,
    AlertCircle,


} from 'lucide-react'
import { toast } from 'sonner'
import { CandlestickChart } from '../../components/charts/CandlestickChart'

const SYMBOLS = [
    { symbol: 'BTCUSDT', name: 'Bitcoin', icon: 'BTC' },
    { symbol: 'ETHUSDT', name: 'Ethereum', icon: 'ETH' },
    { symbol: 'BNBUSDT', name: 'BNB', icon: 'BNB' },
    { symbol: 'SOLUSDT', name: 'Solana', icon: 'SOL' },
    { symbol: 'XRPUSDT', name: 'XRP', icon: 'XRP' },
    { symbol: 'ADAUSDT', name: 'Cardano', icon: 'ADA' },
]

interface OrderForm {
    side: 'BUY' | 'SELL'
    quantity: string
    usdtAmount: string
    price: string
}

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

interface Trade {
    id: string | number
    symbol: string
    side: 'BUY' | 'SELL'
    quantity: number
    price: number
    total?: number
    pnl?: number
    timestamp: string
    status?: string | number
    type?: string
    advertiser?: string
    fiat?: string
}

interface Stats {
    total_trades: number
    win_rate: number
    total_pnl: number
    volume: number
}

import { useRouter } from 'next/navigation'
import { useAuth } from '../../hooks/useAuth'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import { useWallet } from '../../context/WalletContext'

export default function TradingPage() {
    const router = useRouter()
    const { isAuthenticated, loading: authLoading } = useAuth()
    const { mode, setMode, balances } = useWallet()

    // Tab state
    const [activeTab, setActiveTab] = useState<'CHART' | 'SIGNALS' | 'HISTORY'>('CHART')

    // Chart tab states
    const [selectedSymbol, setSelectedSymbol] = useState(SYMBOLS[0])
    const [currentPrice, setCurrentPrice] = useState(45000)
    const [change24h, setChange24h] = useState(2.5)
    const [order, setOrder] = useState<OrderForm>({ side: 'BUY', quantity: '', usdtAmount: '', price: '' })

    // Signals tab states
    const [signals, setSignals] = useState<Signal[]>([])

    // History tab states
    const [historySubTab, setHistorySubTab] = useState<'TRADING' | 'P2P'>('TRADING')
    const [trades, setTrades] = useState<Trade[]>([])
    const [stats, setStats] = useState<Stats>({ total_trades: 0, win_rate: 0, total_pnl: 0, volume: 0 })
    const [historyLoading, setHistoryLoading] = useState(false)
    const [filter, setFilter] = useState('ALL')

    const usdtBalance = balances.find(b => b.asset === 'USDT')?.total || 0

    // Market Data Fetching
    useEffect(() => {
        if (authLoading || !isAuthenticated) return

        const fetchMarketData = async () => {
            try {
                const priceRes = await fetch(`https://api.binance.com/api/v3/ticker/price?symbol=${selectedSymbol.symbol}`)
                const priceData = await priceRes.json()
                if (priceData.price) {
                    setCurrentPrice(parseFloat(priceData.price))
                }

                const statsRes = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${selectedSymbol.symbol}`)
                const statsData = await statsRes.json()
                if (statsData.priceChangePercent) {
                    setChange24h(parseFloat(statsData.priceChangePercent))
                }
            } catch (error) {
                console.error('Error fetching Binance data', error)
            }
        }

        fetchMarketData()
        const interval = setInterval(fetchMarketData, 5000)

        return () => clearInterval(interval)
    }, [selectedSymbol, authLoading, isAuthenticated])

    // Signals Fetching
    useEffect(() => {
        if (activeTab === 'SIGNALS' && isAuthenticated) {
            fetchSignals()
        }
    }, [activeTab, isAuthenticated])

    const fetchSignals = async () => {
        // Demo signals for now
        setSignals([
            {
                symbol: 'BTCUSDT',
                type: 'LONG',
                strength: 'STRONG',
                confidence: 87.5,
                entry_price: 45000,
                stop_loss: 44200,
                take_profit: 47500,
                risk_reward: 3.12,
                reasoning: ['RSI sobreventa', 'MACD cruce alcista', 'Tendencia alcista confirmada'],
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
                reasoning: ['RSI neutral', 'Patrón de acumulación'],
                indicators: { rsi: 45, trend: 'BULLISH' }
            }
        ])
    }

    // History Fetching
    useEffect(() => {
        if (activeTab === 'HISTORY' && isAuthenticated) {
            fetchHistory()
        }
    }, [activeTab, mode, historySubTab, isAuthenticated])

    const fetchHistory = async () => {
        setHistoryLoading(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const headers = { 'Authorization': `Bearer ${token}` }

            if (historySubTab === 'TRADING') {
                if (mode === 'practice') {
                    const [tradesRes, statsRes] = await Promise.all([
                        fetch('/api/v1/practice/trades', { headers }),
                        fetch('/api/v1/practice/stats', { headers })
                    ])

                    if (tradesRes.ok && statsRes.ok) {
                        const tradesData = await tradesRes.json()
                        const statsData = await statsRes.json()
                        setTrades(tradesData)
                        setStats({
                            total_trades: statsData.total_trades,
                            win_rate: statsData.win_rate,
                            total_pnl: statsData.total_pnl,
                            volume: tradesData.reduce((acc: number, t: any) => acc + (t.total || 0), 0)
                        })
                    }
                } else {
                    const res = await fetch('/api/v1/trading/orders?limit=50', { headers })
                    if (res.ok) {
                        const data = await res.json()
                        const adaptedTrades = data.orders.map((o: any) => ({
                            id: o.orderId,
                            symbol: o.symbol,
                            side: o.side,
                            quantity: parseFloat(o.origQty),
                            price: parseFloat(o.price || o.cummulativeQuoteQty / o.executedQty || 0),
                            total: parseFloat(o.cummulativeQuoteQty),
                            timestamp: new Date(o.time).toISOString(),
                            status: o.status,
                            type: o.type
                        }))
                        setTrades(adaptedTrades)
                        setStats({
                            total_trades: adaptedTrades.length,
                            win_rate: 0,
                            total_pnl: 0,
                            volume: adaptedTrades.reduce((acc: number, t: any) => acc + (t.total || 0), 0)
                        })
                    }
                }
            }
        } catch (error) {
            console.error('Error fetching history:', error)
        } finally {
            setHistoryLoading(false)
        }
    }

    // Auth Guard
    useEffect(() => {
        if (!authLoading && !isAuthenticated) {
            router.push('/login')
        }
    }, [authLoading, isAuthenticated, router])

    if (authLoading) return <LoadingSpinner />
    if (!isAuthenticated) return null

    const handleOrder = () => {
        if (!order.quantity) {
            toast.error('Por favor ingresa una cantidad válida')
            return
        }

        const qty = parseFloat(order.quantity)
        const total = qty * currentPrice

        if (order.side === 'BUY' && total > usdtBalance) {
            toast.error('Saldo USDT insuficiente para esta operación')
            return
        }

        const message = `${order.side === 'BUY' ? 'Compra' : 'Venta'} de ${qty} ${selectedSymbol.symbol.replace('USDT', '')} ejecutada correctamente`

        if (mode === 'practice') {
            toast.success('Orden de Práctica Exitosa', { description: message })
        } else {
            toast.success('Orden Real Enviada', { description: 'Tu orden ha sido enviada al mercado' })
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('es-ES', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        })
    }

    const filteredTrades = trades.filter(t => filter === 'ALL' || t.side === filter)

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header with Tabs and Mode Toggle */}
                <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
                    {/* Tabs */}
                    <div className="flex items-center gap-2 bg-white/5 p-1 rounded-xl border border-white/10">
                        <button
                            onClick={() => setActiveTab('CHART')}
                            className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'CHART'
                                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/30'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <BarChart2 className="h-4 w-4" />
                            Gráfico
                        </button>
                        <button
                            onClick={() => setActiveTab('SIGNALS')}
                            className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'SIGNALS'
                                    ? 'bg-gradient-to-r from-violet-500/20 to-purple-500/20 text-violet-400 border border-violet-500/30'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <Target className="h-4 w-4" />
                            Señales IA
                        </button>
                        <button
                            onClick={() => setActiveTab('HISTORY')}
                            className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'HISTORY'
                                    ? 'bg-gradient-to-r from-amber-500/20 to-orange-500/20 text-amber-400 border border-amber-500/30'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                }`}
                        >
                            <History className="h-4 w-4" />
                            Historial
                        </button>
                    </div>

                    {/* Mode Toggle (only show on Chart and History tabs) */}
                    {(activeTab === 'CHART' || activeTab === 'HISTORY') && (
                        <div className="bg-white/5 p-1 rounded-lg border border-white/10 flex relative">
                            <div className={`absolute top-1 bottom-1 w-[calc(50%-4px)] bg-gradient-to-r transition-all duration-300 rounded-md shadow-sm ${mode === 'practice'
                                ? 'left-1 from-emerald-500/20 to-emerald-600/20 border border-emerald-500/30'
                                : 'left-[50%] from-rose-500/20 to-rose-600/20 border border-rose-500/30'
                                }`}></div>

                            <button
                                onClick={() => setMode('practice')}
                                className={`relative z-10 flex items-center gap-2 px-6 py-2 rounded-md text-sm font-medium transition-all ${mode === 'practice' ? 'text-emerald-400' : 'text-slate-400 hover:text-slate-200'
                                    }`}
                            >
                                <Gamepad2 className="h-4 w-4" />
                                Práctica
                            </button>
                            <button
                                onClick={() => setMode('real')}
                                className={`relative z-10 flex items-center gap-2 px-6 py-2 rounded-md text-sm font-medium transition-all ${mode === 'real' ? 'text-rose-400' : 'text-slate-400 hover:text-slate-200'
                                    }`}
                            >
                                <Swords className="h-4 w-4" />
                                Real
                            </button>
                        </div>
                    )}
                </div>

                {/* TAB 1: CHART & EXECUTION */}
                {activeTab === 'CHART' && (
                    <>
                        <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
                            <div className="flex items-center gap-6">
                                {/* Symbol Selector */}
                                <div className="relative group">
                                    <select
                                        value={selectedSymbol.symbol}
                                        onChange={(e) => setSelectedSymbol(SYMBOLS.find(s => s.symbol === e.target.value) || SYMBOLS[0])}
                                        className="appearance-none bg-white/5 border border-white/10 hover:border-cyan-500/50 rounded-xl pl-5 pr-12 py-3 text-white font-medium focus:outline-none transition-all cursor-pointer min-w-[180px]"
                                    >
                                        {SYMBOLS.map(s => (
                                            <option key={s.symbol} value={s.symbol} className="bg-slate-900 text-white">
                                                {s.symbol}
                                            </option>
                                        ))}
                                    </select>
                                    <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-hover:text-cyan-400 transition-colors">
                                        <ChevronDown className="h-4 w-4" />
                                    </div>
                                </div>

                                {/* Price Info */}
                                <div>
                                    <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">{selectedSymbol.name}</p>
                                    <div className="flex items-baseline gap-3">
                                        <p className="text-3xl font-bold text-white tracking-tight">
                                            ${currentPrice.toLocaleString()}
                                        </p>
                                        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-bold ${change24h >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                            {change24h >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                                            {change24h}%
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Chart */}
                            <div className="lg:col-span-2 glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl md:min-h-[600px] flex flex-col">
                                <div className="flex justify-between items-center mb-6">
                                    <h2 className="text-lg font-semibold flex items-center gap-2 text-white">
                                        <BarChart2 className="h-5 w-5 text-cyan-400" />
                                        Gráfico de Mercado
                                    </h2>
                                    <div className="flex bg-white/5 p-1 rounded-lg gap-1">
                                        {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
                                            <button
                                                key={tf}
                                                className="px-3 py-1 text-xs rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-all font-medium"
                                            >
                                                {tf}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <div className="flex-1 bg-black/40 rounded-xl border border-white/5 overflow-hidden relative min-h-[500px]">
                                    <CandlestickChart symbol={selectedSymbol.symbol} />
                                </div>
                            </div>

                            {/* Order Form */}
                            <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl h-fit">
                                <h2 className="text-lg font-semibold mb-6 text-white flex items-center gap-2">
                                    <Zap className="h-5 w-5 text-violet-400" />
                                    Ejecución Rápida
                                </h2>

                                {/* Balance */}
                                <div className="bg-white/5 rounded-xl p-4 mb-6 border border-white/5 flex items-center justify-between">
                                    <div>
                                        <p className="text-slate-400 text-xs uppercase tracking-wider font-medium mb-1">Balance Disponible</p>
                                        <p className="text-xl font-bold text-emerald-400 tracking-tight">${usdtBalance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 })}</p>
                                    </div>
                                    <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                                        <Wallet className="h-5 w-5 text-emerald-400" />
                                    </div>
                                </div>

                                {/* Side Toggle */}
                                <div className="grid grid-cols-2 gap-2 mb-6 bg-white/5 p-1 rounded-xl">
                                    <button
                                        onClick={() => setOrder({ ...order, side: 'BUY' })}
                                        className={`py-3 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 ${order.side === 'BUY'
                                            ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20'
                                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                                            }`}
                                    >
                                        <TrendingUp className="h-4 w-4" />
                                        Comprar
                                    </button>
                                    <button
                                        onClick={() => setOrder({ ...order, side: 'SELL' })}
                                        className={`py-3 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 ${order.side === 'SELL'
                                            ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                                            : 'text-slate-400 hover:text-white hover:bg-white/5'
                                            }`}
                                    >
                                        <TrendingDown className="h-4 w-4" />
                                        Vender
                                    </button>
                                </div>

                                {/* Quantity Input - BTC */}
                                <div className="mb-4">
                                    <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">Cantidad</label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            value={order.quantity}
                                            onChange={(e) => {
                                                const qty = e.target.value
                                                const usdt = qty ? (parseFloat(qty) * currentPrice).toFixed(2) : ''
                                                setOrder({ ...order, quantity: qty, usdtAmount: usdt })
                                            }}
                                            placeholder="0.001"
                                            step="0.00001"
                                            className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500/50 focus:bg-white/5 transition-all font-mono text-lg"
                                        />
                                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 text-sm font-medium">{selectedSymbol.symbol.replace('USDT', '')}</span>
                                    </div>
                                </div>

                                {/* USDT Amount Input */}
                                <div className="mb-4">
                                    <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">Monto en USDT</label>
                                    <div className="relative">
                                        <input
                                            type="number"
                                            value={order.usdtAmount}
                                            onChange={(e) => {
                                                const usdt = e.target.value
                                                const qty = usdt && currentPrice ? (parseFloat(usdt) / currentPrice).toFixed(8) : ''
                                                setOrder({ ...order, usdtAmount: usdt, quantity: qty })
                                            }}
                                            placeholder="100.00"
                                            step="0.01"
                                            className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-emerald-500/50 focus:bg-white/5 transition-all font-mono text-lg"
                                        />
                                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 text-sm font-medium">USDT</span>
                                    </div>
                                </div>

                                {/* Price Display */}
                                <div className="mb-4">
                                    <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">Precio de Mercado</label>
                                    <div className="w-full bg-white/5 border border-white/5 rounded-xl px-4 py-3 text-slate-300 font-mono flex justify-between items-center cursor-not-allowed">
                                        <span>${currentPrice.toLocaleString()}</span>
                                        <span className="text-xs text-slate-500">USDT</span>
                                    </div>
                                </div>

                                {/* Total */}
                                <div className="mb-8">
                                    <div className="flex justify-between items-center mb-2">
                                        <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Estimado</label>
                                    </div>
                                    <div className="w-full bg-gradient-to-r from-white/5 to-white/[0.02] border border-white/10 rounded-xl px-4 py-4 text-white font-bold font-mono text-xl flex justify-between items-center">
                                        <span>${(parseFloat(order.quantity || '0') * currentPrice).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 6 })}</span>
                                        <span className="text-sm text-slate-500 font-sans">USDT</span>
                                    </div>
                                </div>

                                {/* Submit Button */}
                                <button
                                    onClick={handleOrder}
                                    className={`w-full py-4 rounded-xl font-bold text-lg transition-all active:scale-95 shadow-lg flex items-center justify-center gap-2 ${order.side === 'BUY'
                                        ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-black hover:from-emerald-400 hover:to-emerald-500 shadow-emerald-500/20'
                                        : 'bg-gradient-to-r from-rose-500 to-rose-600 text-white hover:from-rose-400 hover:to-rose-500 shadow-rose-500/20'
                                        }`}
                                >
                                    {order.side === 'BUY' ? 'Comprar Ahora' : 'Vender Ahora'}
                                </button>

                                {mode === 'practice' && (
                                    <div className="mt-4 flex items-center justify-center gap-2 text-xs text-emerald-400/80 bg-emerald-500/5 py-2 rounded-lg border border-emerald-500/10">
                                        <Gamepad2 className="h-4 w-4" />
                                        Modo Simulación Activo
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                )}

                {/* TAB 2: SIGNALS */}
                {activeTab === 'SIGNALS' && (
                    <div>
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
                                                <BarChart2 className="h-3 w-3" /> Confianza IA
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
                )}

                {/* TAB 3: HISTORY */}
                {activeTab === 'HISTORY' && (
                    <div className="space-y-8">
                        {/* Header & Tabs */}
                        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                            <div>
                                <h2 className="text-2xl font-bold text-white flex items-center gap-3">
                                    <History className="text-amber-400" size={28} />
                                    Historial de Operaciones
                                </h2>
                                <div className="flex items-center gap-2 mt-2">
                                    <button
                                        onClick={() => setHistorySubTab('TRADING')}
                                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${historySubTab === 'TRADING' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50' : 'text-slate-500 hover:bg-white/5'}`}
                                    >
                                        <TrendingUp size={14} /> Trading Spot
                                    </button>
                                    <button
                                        onClick={() => setHistorySubTab('P2P')}
                                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${historySubTab === 'P2P' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'text-slate-500 hover:bg-white/5'}`}
                                    >
                                        <Users size={14} /> Mercado P2P
                                    </button>
                                </div>
                            </div>

                            <div className="flex gap-2">
                                {['ALL', 'BUY', 'SELL'].map(f => (
                                    <button
                                        key={f}
                                        onClick={() => setFilter(f)}
                                        className={`px-4 py-2 rounded-lg text-xs font-bold transition-all border ${filter === f
                                            ? 'bg-white/10 text-white border-white/20'
                                            : 'bg-transparent text-slate-500 border-transparent hover:bg-white/5'}`}
                                    >
                                        {f === 'ALL' ? 'Todos' : f === 'BUY' ? 'Compras' : 'Ventas'}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Stats Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                                        <ArrowRightLeft size={18} />
                                    </div>
                                    <span className="text-xs font-bold text-slate-500 uppercase">Volumen Movido</span>
                                </div>
                                <p className="text-2xl font-mono text-white font-bold">
                                    ${stats.volume.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                                </p>
                            </div>

                            <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="p-2 rounded-lg bg-violet-500/10 text-violet-400">
                                        <Clock size={18} />
                                    </div>
                                    <span className="text-xs font-bold text-slate-500 uppercase">Operaciones</span>
                                </div>
                                <p className="text-2xl font-mono text-white font-bold">{stats.total_trades}</p>
                            </div>

                            {historySubTab === 'TRADING' && mode === 'practice' && (
                                <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                                    <div className="flex items-center gap-3 mb-2">
                                        <div className={`p-2 rounded-lg ${stats.total_pnl >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                            {stats.total_pnl >= 0 ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                                        </div>
                                        <span className="text-xs font-bold text-slate-500 uppercase">PNL Acumulado</span>
                                    </div>
                                    <p className={`text-2xl font-mono font-bold ${stats.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {stats.total_pnl >= 0 ? '+' : ''}{stats.total_pnl.toFixed(2)} USD
                                    </p>
                                </div>
                            )}
                        </div>

                        {/* Trades Table */}
                        <div className="glass-card overflow-hidden rounded-3xl border border-white/5 bg-gradient-to-b from-black/20 to-transparent">
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-white/[0.02] border-b border-white/5">
                                        <tr>
                                            <th className="text-left py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Fecha</th>
                                            <th className="text-left py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                                                {historySubTab === 'TRADING' ? 'Par' : 'Activo'}
                                            </th>
                                            <th className="text-left py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Tipo</th>
                                            <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Precio</th>
                                            <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Cantidad</th>
                                            <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Total</th>
                                            {historySubTab === 'P2P' && <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Contraparte</th>}
                                            <th className="text-center py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Estado</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5">
                                        {historyLoading ? (
                                            <tr>
                                                <td colSpan={historySubTab === 'P2P' ? 8 : 7} className="py-20 text-center">
                                                    <div className="flex flex-col items-center gap-4">
                                                        <div className="h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                                                        <span className="text-slate-500 font-mono text-xs">Sincronizando con Blockchain...</span>
                                                    </div>
                                                </td>
                                            </tr>
                                        ) : filteredTrades.length === 0 ? (
                                            <tr>
                                                <td colSpan={historySubTab === 'P2P' ? 8 : 7} className="py-20 text-center text-slate-600">
                                                    <div className="flex flex-col items-center gap-4">
                                                        <History size={48} className="opacity-20" />
                                                        <p>No se encontraron registros en {historySubTab}</p>
                                                    </div>
                                                </td>
                                            </tr>
                                        ) : (
                                            filteredTrades.map((trade, i) => (
                                                <tr key={i} className="group hover:bg-white/[0.03] transition-colors">
                                                    <td className="py-4 px-6 text-xs text-slate-400 font-mono">
                                                        {formatDate(trade.timestamp)}
                                                    </td>
                                                    <td className="py-4 px-6">
                                                        <span className="font-bold text-white text-sm">{trade.symbol}</span>
                                                    </td>
                                                    <td className="py-4 px-6">
                                                        <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${trade.side === 'BUY'
                                                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                                            }`}>
                                                            {trade.side === 'BUY' ? 'Compra' : 'Venta'}
                                                        </span>
                                                    </td>
                                                    <td className="py-4 px-6 text-right font-mono text-sm text-slate-300">
                                                        {trade.price.toLocaleString()} {historySubTab === 'P2P' ? (trade.fiat || 'VES') : 'USDT'}
                                                    </td>
                                                    <td className="py-4 px-6 text-right font-mono text-sm text-slate-300">
                                                        {trade.quantity}
                                                    </td>
                                                    <td className="py-4 px-6 text-right font-mono text-sm text-slate-300">
                                                        {trade.total ? trade.total.toLocaleString() : (trade.price * trade.quantity).toLocaleString()} {historySubTab === 'P2P' ? (trade.fiat || 'VES') : 'USDT'}
                                                    </td>
                                                    {historySubTab === 'P2P' && (
                                                        <td className="py-4 px-6 text-right font-mono text-xs text-cyan-400">
                                                            {trade.advertiser || 'Anon'}
                                                        </td>
                                                    )}
                                                    <td className="py-4 px-6 text-center">
                                                        {(!trade.status || trade.status === 'FILLED' || trade.status === 4) ? (
                                                            <CheckCircle2 size={16} className="text-emerald-500 mx-auto" />
                                                        ) : (
                                                            <span className="text-[10px] text-amber-500 uppercase">{trade.status}</span>
                                                        )}
                                                    </td>
                                                </tr>
                                            ))
                                        )}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </DashboardLayout>
    )
}
