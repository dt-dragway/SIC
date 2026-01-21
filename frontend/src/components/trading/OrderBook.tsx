'use client'

import { useEffect, useState } from 'react'
import { ArrowUp, ArrowDown } from 'lucide-react'

interface OrderBookProps {
    symbol: string
}

interface OrderBookEntry {
    price: number
    quantity: number
    total: number
}

export default function OrderBook({ symbol }: OrderBookProps) {
    const [bids, setBids] = useState<OrderBookEntry[]>([])
    const [asks, setAsks] = useState<OrderBookEntry[]>([])
    const [loading, setLoading] = useState(true)

    const fetchOrderBook = async () => {
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const response = await fetch(`/api/v1/trading/depth/${symbol}?limit=15`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()

                // Process bids and asks
                const processedBids = data.bids.slice(0, 15).map((item: [string, string]) => ({
                    price: parseFloat(item[0]),
                    quantity: parseFloat(item[1]),
                    total: parseFloat(item[0]) * parseFloat(item[1])
                }))

                const processedAsks = data.asks.slice(0, 15).map((item: [string, string]) => ({
                    price: parseFloat(item[0]),
                    quantity: parseFloat(item[1]),
                    total: parseFloat(item[0]) * parseFloat(item[1])
                })).reverse()

                setBids(processedBids)
                setAsks(processedAsks)
                setLoading(false)
            }
        } catch (error) {
            console.error('Error fetching order book:', error)
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchOrderBook()
        const interval = setInterval(fetchOrderBook, 2000) // Update every 2 seconds
        return () => clearInterval(interval)
    }, [symbol])

    const spread = asks.length > 0 && bids.length > 0 ? asks[0].price - bids[0].price : 0
    const spreadPercent = spread > 0 && bids.length > 0 ? (spread / bids[0].price) * 100 : 0

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <div className="text-slate-500 text-sm">Cargando order book...</div>
            </div>
        )
    }

    return (
        <div className="h-full flex flex-col">
            {/* Header */}
            <div className="px-4 py-3 border-b border-white/10">
                <div className="grid grid-cols-3 text-xs text-slate-500 font-medium">
                    <div>Precio (USDT)</div>
                    <div className="text-right">Cantidad</div>
                    <div className="text-right">Total</div>
                </div>
            </div>

            {/* Asks (Sell Orders) - Red */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {asks.map((ask, index) => (
                    <div
                        key={`ask-${index}`}
                        className="grid grid-cols-3 px-4 py-1 hover:bg-rose-500/10 cursor-pointer text-xs group relative"
                    >
                        <div className="text-rose-400 font-mono">{ask.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                        <div className="text-slate-400 text-right font-mono">{ask.quantity.toFixed(6)}</div>
                        <div className="text-slate-500 text-right font-mono">{ask.total.toFixed(2)}</div>
                        {/* Depth Bar */}
                        <div className="absolute right-0 top-0 bottom-0 bg-rose-500/5" style={{ width: `${(ask.total / Math.max(...asks.map(a => a.total))) * 100}%` }}></div>
                    </div>
                ))}
            </div>

            {/* Spread */}
            <div className="px-4 py-2 bg-white/5 border-y border-white/10">
                <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-500">Spread</span>
                    <span className="text-white font-mono">
                        {spread.toFixed(2)} ({spreadPercent.toFixed(3)}%)
                    </span>
                </div>
            </div>

            {/* Bids (Buy Orders) - Green */}
            <div className="flex-1 overflow-y-auto custom-scrollbar">
                {bids.map((bid, index) => (
                    <div
                        key={`bid-${index}`}
                        className="grid grid-cols-3 px-4 py-1 hover:bg-emerald-500/10 cursor-pointer text-xs group relative"
                    >
                        <div className="text-emerald-400 font-mono">{bid.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                        <div className="text-slate-400 text-right font-mono">{bid.quantity.toFixed(6)}</div>
                        <div className="text-slate-500 text-right font-mono">{bid.total.toFixed(2)}</div>
                        {/* Depth Bar */}
                        <div className="absolute right-0 top-0 bottom-0 bg-emerald-500/5" style={{ width: `${(bid.total / Math.max(...bids.map(b => b.total))) * 100}%` }}></div>
                    </div>
                ))}
            </div>
        </div>
    )
}
