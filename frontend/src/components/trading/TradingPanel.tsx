'use client'

import { useState } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { toast } from 'sonner'

interface TradingPanelProps {
    symbol: string
    currentPrice: number
    mode: 'practice' | 'real'
    usdtBalance: number
    onOrderSuccess?: () => void
}

export default function TradingPanel({ symbol, currentPrice, mode, usdtBalance, onOrderSuccess }: TradingPanelProps) {
    const [side, setSide] = useState<'BUY' | 'SELL'>('BUY')
    const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET')
    const [quantity, setQuantity] = useState('')
    const [price, setPrice] = useState(currentPrice.toString())
    const [loading, setLoading] = useState(false)

    // Update price when currentPrice changes
    if (orderType === 'MARKET' && parseFloat(price) !== currentPrice) {
        setPrice(currentPrice.toString())
    }

    const total = parseFloat(quantity || '0') * (orderType === 'MARKET' ? currentPrice : parseFloat(price || '0'))
    const fee = total * 0.001 // 0.1% fee
    const totalWithFee = total + fee

    const handlePercentage = (percent: number) => {
        const availableBalance = usdtBalance
        const targetAmount = (availableBalance * percent) / 100
        const qty = targetAmount / (orderType === 'MARKET' ? currentPrice : parseFloat(price || currentPrice.toString()))
        setQuantity(qty.toFixed(6))
    }

    const handleSubmit = async () => {
        if (!quantity || parseFloat(quantity) <= 0) {
            toast.error('Ingresa una cantidad válida')
            return
        }

        if (side === 'BUY' && totalWithFee > usdtBalance) {
            toast.error(`Saldo insuficiente. Necesitas $${totalWithFee.toFixed(2)} USDT`)
            return
        }

        setLoading(true)

        try {
            const token = localStorage.getItem('token')
            const endpoint = mode === 'practice' ? '/api/v1/practice/order' : '/api/v1/trading/order'

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    symbol: symbol,
                    side: side,
                    type: orderType,
                    quantity: parseFloat(quantity),
                    price: orderType === 'LIMIT' ? parseFloat(price) : null,
                    mode: mode
                })
            })

            const data = await response.json()

            if (response.ok && (data.success || data.message)) {
                toast.success(
                    mode === 'practice' ? 'Orden de Práctica Ejecutada' : 'Orden Real Enviada',
                    { description: data.message || `${side} ${quantity} ${symbol}` }
                )
                setQuantity('')
                if (onOrderSuccess) onOrderSuccess()
            } else {
                toast.error(data.detail || data.error || 'Error al ejecutar orden')
            }
        } catch (error) {
            toast.error('Error de conexión')
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="p-3">
            {/* Buy/Sell Tabs */}
            <div className="grid grid-cols-2 gap-2 mb-3">
                <button
                    onClick={() => setSide('BUY')}
                    className={`py-2.5 rounded-lg text-sm font-medium transition-all ${side === 'BUY'
                        ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                        : 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'
                        }`}
                >
                    Comprar
                </button>
                <button
                    onClick={() => setSide('SELL')}
                    className={`py-2.5 rounded-lg text-sm font-medium transition-all ${side === 'SELL'
                        ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                        : 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20'
                        }`}
                >
                    Vender
                </button>
            </div>

            {/* Order Type */}
            <div className="flex gap-2 mb-3">
                <button
                    onClick={() => setOrderType('MARKET')}
                    className={`flex-1 py-2 text-xs rounded-lg transition-all ${orderType === 'MARKET'
                        ? 'bg-white/10 text-white border border-white/20'
                        : 'text-slate-400 hover:text-white'
                        }`}
                >
                    Market
                </button>
                <button
                    onClick={() => setOrderType('LIMIT')}
                    className={`flex-1 py-2 text-xs rounded-lg transition-all ${orderType === 'LIMIT'
                        ? 'bg-white/10 text-white border border-white/20'
                        : 'text-slate-400 hover:text-white'
                        }`}
                >
                    Limit
                </button>
            </div>

            {/* Price (only for Limit) */}
            {orderType === 'LIMIT' && (
                <div className="mb-4">
                    <label className="block text-xs text-slate-500 mb-2">Precio (USDT)</label>
                    <input
                        type="number"
                        value={price}
                        onChange={(e) => setPrice(e.target.value)}
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                        placeholder="0.00"
                    />
                </div>
            )}

            {/* Amount */}
            <div className="mb-3">
                <label className="block text-xs text-slate-500 mb-2">Cantidad ({symbol.replace('USDT', '')})</label>
                <input
                    type="number"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                    placeholder="0.00"
                />
            </div>

            {/* Percentage Buttons */}
            <div className="grid grid-cols-4 gap-1 mb-3">
                {[25, 50, 75, 100].map(percent => (
                    <button
                        key={percent}
                        onClick={() => handlePercentage(percent)}
                        className="py-1.5 text-xs bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white rounded-lg transition-all"
                    >
                        {percent}%
                    </button>
                ))}
            </div>

            {/* Total */}
            <div className="mb-3 p-2 bg-white/5 rounded-lg space-y-1">
                <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Total</span>
                    <span className="text-white font-mono">${total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Fee (0.1%)</span>
                    <span className="text-slate-400 font-mono">${fee.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs pt-1 border-t border-white/10">
                    <span className="text-slate-500">Total + Fee</span>
                    <span className="text-white font-mono font-medium">${totalWithFee.toFixed(2)}</span>
                </div>
            </div>

            {/* Available Balance */}
            <div className="mb-3 text-xs text-slate-500">
                Disponible: <span className="text-white font-mono">${usdtBalance.toFixed(2)} USDT</span>
            </div>

            {/* Submit Button */}
            <button
                onClick={handleSubmit}
                disabled={loading || !quantity}
                className={`w-full py-3 rounded-lg font-medium text-white transition-all ${side === 'BUY'
                    ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 shadow-lg shadow-emerald-500/20'
                    : 'bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 shadow-lg shadow-rose-500/20'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
                {loading ? 'Procesando...' : `${side === 'BUY' ? 'Comprar' : 'Vender'} ${symbol.replace('USDT', '')}`}
            </button>
        </div>
    )
}
