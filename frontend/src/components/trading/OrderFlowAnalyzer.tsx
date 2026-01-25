'use client'

import { useState, useEffect } from 'react'
import { Activity, AlertTriangle, TrendingUp, TrendingDown, Eye } from 'lucide-react'

interface OrderFlowLevel {
    price: number
    bidVolume: number
    askVolume: number
    delta: number
    trades: number
}

interface OrderFlowAnalyzerProps {
    symbol: string
}

export default function OrderFlowAnalyzer({ symbol }: OrderFlowAnalyzerProps) {
    const [orderFlow, setOrderFlow] = useState<OrderFlowLevel[]>([])
    const [cvd, setCvd] = useState(0) // Cumulative Volume Delta
    const [spoofingAlerts, setSpoofingAlerts] = useState<string[]>([])
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchOrderFlow = async () => {
            try {
                setLoading(true)

                // Obtener Order Book de Binance
                const response = await fetch(`https://api.binance.com/api/v3/depth?symbol=${symbol}&limit=20`)
                const data = await response.json()

                // Procesar bids y asks
                const levels: OrderFlowLevel[] = []
                let cumulativeDelta = 0

                // Combinar bids y asks en niveles
                for (let i = 0; i < Math.min(data.bids.length, data.asks.length); i++) {
                    const bidPrice = parseFloat(data.bids[i][0])
                    const bidVolume = parseFloat(data.bids[i][1])
                    const askPrice = parseFloat(data.asks[i][0])
                    const askVolume = parseFloat(data.asks[i][1])

                    // Simular trades (en producción vendría del stream de trades)
                    const estimatedTrades = Math.floor((bidVolume + askVolume) * 0.1)

                    const level: OrderFlowLevel = {
                        price: (bidPrice + askPrice) / 2,
                        bidVolume,
                        askVolume,
                        delta: bidVolume - askVolume,
                        trades: estimatedTrades
                    }

                    levels.push(level)
                    cumulativeDelta += level.delta
                }

                setOrderFlow(levels)
                setCvd(cumulativeDelta)

                // Detectar Spoofing
                detectSpoofing(levels)

                setLoading(false)
            } catch (error) {
                console.error('Error fetching order flow:', error)
                setLoading(false)
            }
        }

        fetchOrderFlow()
        const interval = setInterval(fetchOrderFlow, 5000) // Actualizar cada 5s

        return () => clearInterval(interval)
    }, [symbol])

    const detectSpoofing = (levels: OrderFlowLevel[]) => {
        const alerts: string[] = []
        const avgVolume = levels.reduce((sum, l) => sum + l.bidVolume + l.askVolume, 0) / (levels.length * 2)

        levels.forEach(level => {
            // Detectar muros grandes con poco volumen de trades
            const volumeRatio = level.trades / (level.bidVolume + level.askVolume)

            if (level.bidVolume > avgVolume * 10 && volumeRatio < 0.05) {
                alerts.push(`⚠️ Posible BID spoofing en $${level.price.toFixed(2)}`)
            }

            if (level.askVolume > avgVolume * 10 && volumeRatio < 0.05) {
                alerts.push(`⚠️ Posible ASK spoofing en $${level.price.toFixed(2)}`)
            }
        })

        setSpoofingAlerts(alerts)
    }

    const maxVolume = Math.max(...orderFlow.map(l => Math.max(l.bidVolume, l.askVolume)), 1)

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-3 border-b border-white/10 shrink-0">
                <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-cyan-400" />
                    <span className="text-xs font-medium text-white">Order Flow</span>
                </div>
                <div className="flex items-center gap-3">
                    <div className={`text-xs font-mono ${cvd > 0 ? 'text-emerald-400' : cvd < 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                        CVD: {cvd > 0 ? '+' : ''}{cvd.toFixed(2)}
                    </div>
                    {loading && (
                        <div className="animate-spin h-3 w-3 border border-cyan-500 border-t-transparent rounded-full" />
                    )}
                </div>
            </div>

            {/* Spoofing Alerts */}
            {spoofingAlerts.length > 0 && (
                <div className="px-3 py-2 bg-rose-500/10 border-b border-rose-500/20 shrink-0">
                    {spoofingAlerts.slice(0, 2).map((alert, i) => (
                        <div key={i} className="flex items-center gap-2 text-xs text-rose-300">
                            <AlertTriangle className="h-3 w-3" />
                            <span>{alert}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* CVD Indicator */}
            <div className="px-3 py-2 border-b border-white/10 shrink-0">
                <div className="flex items-center justify-between text-xs mb-1">
                    <span className="text-slate-400">Presión de Mercado</span>
                    <span className={cvd > 0 ? 'text-emerald-400' : 'text-rose-400'}>
                        {cvd > 0 ? 'Alcista' : 'Bajista'}
                    </span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <div
                        className={`h-full transition-all ${cvd > 0 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                        style={{ width: `${Math.min(Math.abs(cvd) / maxVolume * 100, 100)}%` }}
                    />
                </div>
            </div>

            {/* Order Flow Heatmap */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                <div className="space-y-0.5 p-2">
                    {orderFlow.map((level, i) => {
                        const bidWidth = (level.bidVolume / maxVolume) * 100
                        const askWidth = (level.askVolume / maxVolume) * 100
                        const isBigWall = (level.bidVolume > maxVolume * 0.7) || (level.askVolume > maxVolume * 0.7)

                        return (
                            <div key={i} className="relative group">
                                {/* Price */}
                                <div className="text-center text-xs font-mono text-slate-400 mb-0.5">
                                    ${level.price.toFixed(2)}
                                </div>

                                {/* Volume Bars */}
                                <div className="flex items-center gap-1 h-5">
                                    {/* Bid (Green - Left) */}
                                    <div className="flex-1 flex justify-end">
                                        <div
                                            className={`h-full transition-all ${isBigWall ? 'bg-emerald-400' : 'bg-emerald-500/60'} rounded-l`}
                                            style={{ width: `${bidWidth}%` }}
                                        />
                                    </div>

                                    {/* Center Line */}
                                    <div className="w-px h-full bg-white/20" />

                                    {/* Ask (Red - Right) */}
                                    <div className="flex-1 flex justify-start">
                                        <div
                                            className={`h-full transition-all ${isBigWall ? 'bg-rose-400' : 'bg-rose-500/60'} rounded-r`}
                                            style={{ width: `${askWidth}%` }}
                                        />
                                    </div>
                                </div>

                                {/* Tooltip on Hover */}
                                <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-1 hidden group-hover:block z-10">
                                    <div className="bg-black/90 border border-white/20 rounded-lg px-2 py-1.5 text-xs whitespace-nowrap">
                                        <div className="text-emerald-400">Bid: {level.bidVolume.toFixed(4)}</div>
                                        <div className="text-rose-400">Ask: {level.askVolume.toFixed(4)}</div>
                                        <div className={level.delta > 0 ? 'text-emerald-300' : 'text-rose-300'}>
                                            Delta: {level.delta > 0 ? '+' : ''}{level.delta.toFixed(4)}
                                        </div>
                                        <div className="text-slate-400">Trades: {level.trades}</div>
                                    </div>
                                </div>

                                {/* Wall Indicator */}
                                {isBigWall && (
                                    <div className="absolute right-1 top-1/2 -translate-y-1/2">
                                        <Eye className="h-3 w-3 text-yellow-400" />
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* Legend */}
            <div className="p-2 border-t border-white/10 shrink-0 bg-white/[0.02]">
                <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 bg-emerald-500 rounded-sm" />
                        <span className="text-slate-400">Bids</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 bg-rose-500 rounded-sm" />
                        <span className="text-slate-400">Asks</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <Eye className="h-3 w-3 text-yellow-400" />
                        <span className="text-slate-400">Muros</span>
                    </div>
                </div>
            </div>
        </div>
    )
}
