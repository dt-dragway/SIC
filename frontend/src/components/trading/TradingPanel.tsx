import { useState } from 'react'
import { TrendingUp, TrendingDown, Wallet } from 'lucide-react'
import { toast } from 'sonner'

interface TradingPanelProps {
    symbol: string
    currentPrice: number
    mode: 'practice' | 'real'
    usdtBalance: number
    assetBalance: number // New prop
    onOrderSuccess?: () => void
}

export default function TradingPanel({ symbol, currentPrice, mode, usdtBalance, assetBalance, onOrderSuccess }: TradingPanelProps) {
    const [side, setSide] = useState<'BUY' | 'SELL'>('BUY')
    const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT'>('MARKET')
    const [quantity, setQuantity] = useState('')
    const [price, setPrice] = useState(currentPrice.toString())
    const [loading, setLoading] = useState(false)

    const asset = symbol.replace('USDT', '')

    // Update price when currentPrice changes
    if (orderType === 'MARKET' && parseFloat(price) !== currentPrice) {
        setPrice(currentPrice.toString())
    }

    const total = parseFloat(quantity || '0') * (orderType === 'MARKET' ? currentPrice : parseFloat(price || '0'))
    const fee = total * 0.001 // 0.1% fee
    const totalWithFee = total + fee

    const handlePercentage = (percent: number) => {
        if (side === 'BUY') {
            // For Buy, use USDT balance
            const availableBalance = usdtBalance
            const targetAmount = (availableBalance * percent) / 100
            const qty = targetAmount / (orderType === 'MARKET' ? currentPrice : parseFloat(price || currentPrice.toString()))
            setQuantity(qty.toFixed(6))
        } else {
            // For Sell, use Asset balance
            const targetQty = (assetBalance * percent) / 100
            setQuantity(targetQty.toFixed(6))
        }
    }

    const handleSubmit = async () => {
        if (!quantity || parseFloat(quantity) <= 0) {
            toast.error('Ingresa una cantidad válida')
            return
        }

        if (total < 2) {
            toast.error('El monto mínimo de inversión es $2 USD')
            return
        }

        if (side === 'BUY' && totalWithFee > usdtBalance) {
            toast.error(`Saldo insuficiente. Necesitas $${totalWithFee.toFixed(2)} USDT`)
            return
        }

        if (side === 'SELL' && parseFloat(quantity) > assetBalance) {
            toast.error(`Saldo insuficiente. Tienes ${assetBalance} ${asset}`)
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
                    className={`py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all ${side === 'BUY'
                        ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20'
                        : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'
                        }`}
                >
                    Comprar
                </button>
                <button
                    onClick={() => setSide('SELL')}
                    className={`py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all ${side === 'SELL'
                        ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                        : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'
                        }`}
                >
                    Vender
                </button>
            </div>

            {/* Balances Display */}
            <div className="flex justify-between items-center mb-4 px-1 text-[10px] font-medium text-slate-400">
                <div className="flex items-center gap-1.5">
                    <Wallet className="h-3 w-3" />
                    <span>USDT: <span className="text-white font-mono">${usdtBalance.toFixed(2)}</span></span>
                </div>
                <div className="flex items-center gap-1.5">
                    <Wallet className="h-3 w-3" />
                    <span>{asset}: <span className="text-white font-mono">{assetBalance.toFixed(6)}</span></span>
                </div>
            </div>

            {/* Order Type */}
            <div className="flex gap-2 mb-3 bg-white/5 p-1 rounded-lg">
                <button
                    onClick={() => setOrderType('MARKET')}
                    className={`flex-1 py-1.5 text-xs font-medium rounded transition-all ${orderType === 'MARKET'
                        ? 'bg-white/10 text-white shadow-sm'
                        : 'text-slate-500 hover:text-slate-300'
                        }`}
                >
                    Market
                </button>
                <button
                    onClick={() => setOrderType('LIMIT')}
                    className={`flex-1 py-1.5 text-xs font-medium rounded transition-all ${orderType === 'LIMIT'
                        ? 'bg-white/10 text-white shadow-sm'
                        : 'text-slate-500 hover:text-slate-300'
                        }`}
                >
                    Limit
                </button>
            </div>

            {/* Price (only for Limit) */}
            {orderType === 'LIMIT' && (
                <div className="mb-4">
                    <div className="flex justify-between text-xs text-slate-500 mb-1.5 px-1">
                        <span>Precio</span>
                        <span>USDT</span>
                    </div>
                    <div className="relative">
                        <input
                            type="number"
                            value={price}
                            onChange={(e) => setPrice(e.target.value)}
                            className="w-full bg-[#0B0E14] border border-white/10 rounded-lg px-3 py-2.5 text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50 transition-all placeholder:text-slate-700"
                            placeholder="0.00"
                        />
                        <span className="absolute right-3 top-2.5 text-xs text-slate-500 font-bold">USDT</span>
                    </div>
                </div>
            )}

            {/* Amount */}
            <div className="mb-3">
                <div className="flex justify-between text-xs text-slate-500 mb-1.5 px-1">
                    <span>Cantidad</span>
                    <span>{asset}</span>
                </div>
                <div className="relative">
                    <input
                        type="number"
                        value={quantity}
                        onChange={(e) => setQuantity(e.target.value)}
                        className="w-full bg-[#0B0E14] border border-white/10 rounded-lg px-3 py-2.5 text-white text-sm font-mono focus:outline-none focus:border-cyan-500/50 transition-all placeholder:text-slate-700"
                        placeholder="0.00"
                    />
                    <span className="absolute right-3 top-2.5 text-xs text-slate-500 font-bold">{asset}</span>
                </div>
            </div>

            {/* Percentage Buttons */}
            <div className="grid grid-cols-4 gap-2 mb-4">
                {[25, 50, 75, 100].map(percent => (
                    <button
                        key={percent}
                        onClick={() => handlePercentage(percent)}
                        className="py-1 text-[10px] font-bold bg-white/5 hover:bg-white/10 text-slate-500 hover:text-white rounded border border-white/5 hover:border-white/10 transition-all"
                    >
                        {percent}%
                    </button>
                ))}
            </div>

            {/* Total */}
            <div className="mb-4 p-3 bg-white/[0.02] border border-white/5 rounded-xl space-y-1.5">
                <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Valor Estimado</span>
                    <span className="text-white font-mono">${total.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs">
                    <span className="text-slate-500">Comisión (0.1%)</span>
                    <span className="text-slate-500 font-mono">${fee.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-xs pt-2 border-t border-white/5">
                    <span className="text-slate-400 font-medium">Total a Pagar</span>
                    <span className="text-emerald-400 font-mono font-bold">${totalWithFee.toFixed(2)}</span>
                </div>
            </div>

            {/* Submit Button */}
            <button
                onClick={handleSubmit}
                disabled={loading || !quantity}
                className={`w-full py-3.5 rounded-xl font-black text-sm uppercase tracking-wider transition-all disabled:opacity-50 disabled:cursor-not-allowed ${side === 'BUY'
                    ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-400 hover:to-emerald-500 text-black shadow-lg shadow-emerald-500/20'
                    : 'bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-400 hover:to-rose-500 text-white shadow-lg shadow-rose-500/20'
                    }`}
            >
                {loading ? 'Procesando...' : (
                    side === 'BUY' ? `Comprar ${asset}` : `Vender ${asset}`
                )}
            </button>
        </div>
    )
}
