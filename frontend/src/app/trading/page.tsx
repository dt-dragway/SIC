'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { useAuth } from '../../hooks/useAuth'
import { useWallet } from '../../context/WalletContext'
import LoadingSpinner from '../../components/ui/LoadingSpinner'
import { GamepadIcon as Gamepad2, Swords, ArrowUp, ArrowDown, Clock, CheckCircle2 } from 'lucide-react'

// Professional trading components
import OrderBook from '../../components/trading/OrderBook'
import TradingPanel from '../../components/trading/TradingPanel'
import MarketList from '../../components/trading/MarketList'
import { InteractiveCandlestickChart } from '../../components/charts/InteractiveCandlestickChart'
import OrderExecutionModal from '../../components/trading/OrderExecutionModal'
import OrderFlowAnalyzer from '../../components/trading/OrderFlowAnalyzer'
import PendingOrdersPanel from '../../components/trading/PendingOrdersPanel'
import AIStatusBar from '../../components/trading/AIStatusBar'

interface Trade {
    id: string | number
    symbol: string
    side: 'BUY' | 'SELL'
    quantity: number
    price: number
    total?: number
    pnl?: number
    timestamp: string
    status?: string
}

export default function TradingPagePro() {
    const router = useRouter()
    const { isAuthenticated, loading: authLoading } = useAuth()
    const { mode, setMode, balances, refreshBalances } = useWallet()

    const [selectedSymbol, setSelectedSymbol] = useState('BTCUSDT')
    const [currentPrice, setCurrentPrice] = useState(0)
    const [priceChange24h, setPriceChange24h] = useState(0)
    const [trades, setTrades] = useState<Trade[]>([])
    const [tradesLoading, setTradesLoading] = useState(false)

    // Nuevo estado para trading profesional
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [clickedPrice, setClickedPrice] = useState(0)
    const [priceLines, setPriceLines] = useState<any[]>([])

    // Estado para tabs de órdenes
    const [orderTab, setOrderTab] = useState<'history' | 'pending'>('history')

    const usdtBalance = balances.find(b => b.asset === 'USDT')?.total || 0
    const totalBalance = balances.reduce((sum, b) => sum + (b.usd_value || 0), 0)

    // Fetch current price
    useEffect(() => {
        const fetchPrice = async () => {
            try {
                const response = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${selectedSymbol}`)
                const data = await response.json()

                if (data.lastPrice) {
                    setCurrentPrice(parseFloat(data.lastPrice))
                    setPriceChange24h(parseFloat(data.priceChangePercent))
                }
            } catch (error) {
                console.error('Error fetching price:', error)
            }
        }

        fetchPrice()
        const interval = setInterval(fetchPrice, 3000) // Update every 3 seconds
        return () => clearInterval(interval)
    }, [selectedSymbol])

    // Fetch trade history
    const fetchHistory = async () => {
        setTradesLoading(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const endpoint = mode === 'practice'
                ? '/api/v1/practice/orders'
                : '/api/v1/trading/orders'

            const response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                const tradesData = data.orders || []
                // Mapear datos al formato Trade
                const mappedTrades = tradesData.map((t: any) => ({
                    id: t.id,
                    symbol: t.symbol,
                    side: t.side,
                    quantity: t.quantity,
                    price: t.entry_price || t.price,
                    total: t.total,
                    pnl: t.pnl,
                    pnl_percent: t.pnl_percent,
                    timestamp: t.created_at,
                    status: t.status || 'FILLED'
                }))
                setTrades(mappedTrades.slice(0, 20)) // Last 20 trades
            }
        } catch (error) {
            console.error('Error fetching history:', error)
        } finally {
            setTradesLoading(false)
        }
    }

    useEffect(() => {
        if (isAuthenticated) {
            fetchHistory()
        }
    }, [mode, isAuthenticated])

    const handleOrderSuccess = () => {
        refreshBalances()
        fetchHistory()
    }

    const handleChartClick = (price: number) => {
        setClickedPrice(price)
        setIsModalOpen(true)
    }

    const handleModalSubmit = () => {
        handleOrderSuccess()
    }

    const formatDate = (dateString: string) => {
        const date = new Date(dateString)
        return date.toLocaleString('es-ES', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    if (authLoading || !isAuthenticated) {
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center h-96">
                    <LoadingSpinner />
                </div>
            </DashboardLayout>
        )
    }

    return (
        <DashboardLayout>
            <div className="h-[calc(100vh-80px)] flex flex-col overflow-hidden">
                {/* Top Bar - Symbol Info & Mode Toggle - COMPACT */}
                <div className="flex items-center justify-between py-2 px-1 border-b border-white/10 shrink-0">
                    {/* Symbol & Price */}
                    <div className="flex items-center gap-4">
                        <h1 className="text-xl font-bold text-white">
                            {selectedSymbol.replace('USDT', '')}<span className="text-slate-500 text-sm">/USDT</span>
                        </h1>
                        <span className="text-2xl font-mono text-white">
                            ${currentPrice.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                        <span className={`flex items-center text-sm font-medium ${priceChange24h >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {priceChange24h >= 0 ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
                            {Math.abs(priceChange24h).toFixed(2)}%
                        </span>
                    </div>

                    {/* AI Stats (only in practice mode) */}
                    {mode === 'practice' && (
                        <div className="hidden md:flex">
                            <AIStatusBar />
                        </div>
                    )}

                    {/* Mode Toggle - Compact */}
                    <div className="bg-white/5 p-1 rounded-lg border border-white/10 flex">
                        <button
                            onClick={() => setMode('practice')}
                            className={`flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium transition-all ${mode === 'practice' ? 'bg-emerald-500/20 text-emerald-400' : 'text-slate-400'}`}
                        >
                            <Gamepad2 className="h-3 w-3" />
                            Práctica
                        </button>
                        <button
                            onClick={() => setMode('real')}
                            className={`flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium transition-all ${mode === 'real' ? 'bg-rose-500/20 text-rose-400' : 'text-slate-400'}`}
                        >
                            <Swords className="h-3 w-3" />
                            Real
                        </button>
                    </div>
                </div>

                {/* Main Trading Area - Uses remaining space */}
                <div className="flex-1 grid grid-cols-12 gap-2 py-2 min-h-0">
                    {/* Left Column - Order Book */}
                    <div className="col-span-2 bg-[#0a0a0f] rounded-lg border border-white/10 flex flex-col overflow-hidden">
                        <OrderBook symbol={selectedSymbol} />
                    </div>

                    {/* Center Column - Interactive Chart */}
                    <div className="col-span-7 bg-[#0a0a0f] rounded-lg border border-white/10 overflow-hidden">
                        <InteractiveCandlestickChart
                            symbol={selectedSymbol}
                            onPriceClick={handleChartClick}
                            priceLines={priceLines}
                        />
                    </div>

                    {/* Right Column - Markets + Trading Panel */}
                    <div className="col-span-3 flex flex-col gap-2 overflow-hidden">
                        {/* Market List - Compact */}
                        <div className="bg-[#0a0a0f] rounded-lg border border-white/10 h-28 shrink-0 overflow-hidden">
                            <div className="px-3 py-1.5 border-b border-white/10 text-xs font-medium text-slate-400">Mercados</div>
                            <div className="overflow-y-auto h-[calc(100%-28px)]">
                                <MarketList currentSymbol={selectedSymbol} onSymbolChange={setSelectedSymbol} />
                            </div>
                        </div>

                        {/* Trading Panel - Takes remaining space */}
                        <div className="bg-[#0a0a0f] rounded-lg border border-white/10 flex-1 overflow-y-auto">
                            <TradingPanel
                                symbol={selectedSymbol}
                                currentPrice={currentPrice}
                                mode={mode}
                                usdtBalance={usdtBalance}
                                onOrderSuccess={handleOrderSuccess}
                            />
                        </div>
                    </div>
                </div>

                {/* Bottom - Orders Section - Fixed height */}
                <div className="h-48 shrink-0 bg-[#0a0a0f] rounded-lg border border-white/10 overflow-hidden flex flex-col">
                    {/* Tabs Header */}
                    <div className="px-4 border-b border-white/10 flex items-center gap-6 bg-white/[0.02]">
                        <button
                            onClick={() => setOrderTab('history')}
                            className={`py-2 text-xs font-medium border-b-2 transition-all ${orderTab === 'history'
                                ? 'text-white border-emerald-500'
                                : 'text-slate-500 border-transparent hover:text-slate-300'
                                }`}
                        >
                            Historial de Órdenes ({trades.length})
                        </button>
                        <button
                            onClick={() => setOrderTab('pending')}
                            className={`py-2 text-xs font-medium border-b-2 transition-all ${orderTab === 'pending'
                                ? 'text-white border-cyan-500'
                                : 'text-slate-500 border-transparent hover:text-slate-300'
                                }`}
                        >
                            Órdenes Pendientes
                        </button>
                    </div>

                    {/* Content Area */}
                    <div className="flex-1 overflow-y-auto relative">
                        {orderTab === 'history' ? (
                            <table className="w-full">
                                <thead className="sticky top-0 bg-[#0a0a0f] border-b border-white/10">
                                    <tr>
                                        <th className="text-left py-2 px-4 text-xs font-medium text-slate-500">Fecha</th>
                                        <th className="text-left py-2 px-4 text-xs font-medium text-slate-500">Par</th>
                                        <th className="text-left py-2 px-4 text-xs font-medium text-slate-500">Tipo</th>
                                        <th className="text-right py-2 px-4 text-xs font-medium text-slate-500">Precio</th>
                                        <th className="text-right py-2 px-4 text-xs font-medium text-slate-500">Cantidad</th>
                                        <th className="text-right py-2 px-4 text-xs font-medium text-slate-500">Total</th>
                                        <th className="text-center py-2 px-4 text-xs font-medium text-slate-500">Estado</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {tradesLoading ? (
                                        <tr><td colSpan={7} className="py-4 text-center text-slate-500 text-xs">Cargando...</td></tr>
                                    ) : trades.length === 0 ? (
                                        <tr><td colSpan={7} className="py-4 text-center text-slate-500 text-xs">Sin órdenes aún</td></tr>
                                    ) : (
                                        trades.map((trade, i) => (
                                            <tr key={i} className="hover:bg-white/5">
                                                <td className="py-2 px-4 text-xs text-slate-400 font-mono">{formatDate(trade.timestamp)}</td>
                                                <td className="py-2 px-4 text-xs text-white">{trade.symbol}</td>
                                                <td className="py-2 px-4">
                                                    <span className={`px-1.5 py-0.5 rounded text-xs ${trade.side === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                                                        {trade.side}
                                                    </span>
                                                </td>
                                                <td className="py-2 px-4 text-right font-mono text-xs text-slate-300">
                                                    ${trade.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
                                                </td>
                                                <td className="py-2 px-4 text-right font-mono text-xs text-slate-300">
                                                    {trade.quantity.toLocaleString(undefined, { maximumFractionDigits: 6 })}
                                                </td>
                                                <td className="py-2 px-4 text-right font-mono text-xs text-slate-300">
                                                    ${(trade.total || trade.price * trade.quantity).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                                </td>
                                                <td className="py-2 px-4 text-center">
                                                    <div className="flex items-center justify-center gap-1 text-emerald-400">
                                                        <CheckCircle2 className="h-3 w-3" />
                                                        <span className="text-[10px] font-medium">Completado</span>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        ) : (
                            <PendingOrdersPanel mode={mode} refreshTrigger={trades.length} />
                        )}
                    </div>
                </div>
            </div>

            {/* Modal de Ejecución Profesional */}
            <OrderExecutionModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                clickedPrice={clickedPrice}
                currentPrice={currentPrice}
                symbol={selectedSymbol}
                accountBalance={totalBalance}
                mode={mode}
                onOrderSubmit={handleModalSubmit}
            />
        </DashboardLayout>
    )
}

