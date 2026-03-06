import { useEffect, useState, memo, useCallback } from 'react'
import { ArrowUp, ArrowDown } from 'lucide-react'

interface OrderBookProps {
    symbol: string
}

interface OrderBookEntry {
    price: number
    quantity: number
    total: number
}

const OrderBook = memo(({ symbol }: OrderBookProps) => {
    const [bids, setBids] = useState<OrderBookEntry[]>([])
    const [asks, setAsks] = useState<OrderBookEntry[]>([])
    const [loading, setLoading] = useState(true)

    const fetchOrderBook = useCallback(async () => {
        // Optimización: Detener fetch si el usuario no está viendo la pestaña
        if (typeof document !== 'undefined' && document.hidden) return;

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
    }, [symbol])

    useEffect(() => {
        fetchOrderBook()
        const interval = setInterval(fetchOrderBook, 2000)
        return () => clearInterval(interval)
    }, [fetchOrderBook])

    const spread = asks.length > 0 && bids.length > 0 ? asks[0].price - bids[0].price : 0
    const spreadPercent = spread > 0 && bids.length > 0 ? (spread / bids[0].price) * 100 : 0

    if (loading) {
        return (
            <div className="h-full flex items-center justify-center mate-card bg-slate-900/50">
                <div className="text-slate-500 text-sm">Cargando order book...</div>
            </div>
        )
    }

    return (
        <div className="h-full flex flex-col mate-card overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-white/5 bg-slate-900/60">
                <div className="grid grid-cols-3 text-[10px] text-slate-500 font-bold uppercase tracking-wider">
                    <div>Precio (USDT)</div>
                    <div className="text-right">Cantidad</div>
                    <div className="text-right">Total</div>
                </div>
            </div>

            {/* Asks (Sell Orders) - Red */}
            <div className="flex-1 overflow-y-auto custom-scrollbar bg-black/20">
                {asks.map((ask, index) => (
                    <div
                        key={`ask-${index}`}
                        className="grid grid-cols-3 px-4 py-0.5 hover:bg-rose-500/5 cursor-pointer text-[11px] group relative"
                    >
                        <div className="text-rose-400 font-mono z-10">{ask.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                        <div className="text-slate-400 text-right font-mono z-10">{ask.quantity.toFixed(6)}</div>
                        <div className="text-slate-500 text-right font-mono z-10">{ask.total.toFixed(2)}</div>
                        {/* Static Depth Bar (No animation/blur) */}
                        <div className="absolute right-0 top-0 bottom-0 bg-rose-500/10" style={{ width: `${(ask.total / Math.max(...asks.map(a => a.total))) * 100}%` }}></div>
                    </div>
                ))}
            </div>

            {/* Spread */}
            <div className="px-4 py-1.5 bg-slate-900/80 border-y border-white/5">
                <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-500 font-medium">Spread</span>
                    <span className="text-white font-mono font-bold">
                        {spread.toFixed(2)} <span className="text-slate-400 font-normal">({spreadPercent.toFixed(3)}%)</span>
                    </span>
                </div>
            </div>

            {/* Bids (Buy Orders) - Green */}
            <div className="flex-1 overflow-y-auto custom-scrollbar bg-black/20">
                {bids.map((bid, index) => (
                    <div
                        key={`bid-${index}`}
                        className="grid grid-cols-3 px-4 py-0.5 hover:bg-emerald-500/5 cursor-pointer text-[11px] group relative"
                    >
                        <div className="text-emerald-400 font-mono z-10">{bid.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                        <div className="text-slate-400 text-right font-mono z-10">{bid.quantity.toFixed(6)}</div>
                        <div className="text-slate-500 text-right font-mono z-10">{bid.total.toFixed(2)}</div>
                        {/* Static Depth Bar (No animation/blur) */}
                        <div className="absolute right-0 top-0 bottom-0 bg-emerald-500/10" style={{ width: `${(bid.total / Math.max(...bids.map(b => b.total))) * 100}%` }}></div>
                    </div>
                ))}
            </div>
        </div>
    )
})

OrderBook.displayName = 'OrderBook';

export default OrderBook;
