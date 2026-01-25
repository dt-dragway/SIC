'use client'

import { useState, useEffect } from 'react'
import { X, TrendingUp, TrendingDown, AlertTriangle, Target, Shield, DollarSign } from 'lucide-react'
import { toast } from 'sonner'
import RiskCalculator from './RiskCalculator'

interface OrderExecutionModalProps {
    isOpen: boolean
    onClose: () => void
    clickedPrice: number
    currentPrice: number
    symbol: string
    accountBalance: number
    mode: 'practice' | 'real'
    onOrderSubmit?: () => void
}

export default function OrderExecutionModal({
    isOpen,
    onClose,
    clickedPrice,
    currentPrice,
    symbol,
    accountBalance,
    mode,
    onOrderSubmit
}: OrderExecutionModalProps) {
    const [side, setSide] = useState<'BUY' | 'SELL'>('BUY')
    const [orderType, setOrderType] = useState<'MARKET' | 'LIMIT' | 'OCO'>('LIMIT')
    const [entryPrice, setEntryPrice] = useState(clickedPrice)
    const [stopLoss, setStopLoss] = useState(0)
    const [takeProfit, setTakeProfit] = useState(0)
    const [quantity, setQuantity] = useState(0)
    const [riskAmount, setRiskAmount] = useState(0)
    const [loading, setLoading] = useState(false)

    // ATR estimado (debería venir del backend en producción)
    const estimatedATR = currentPrice * 0.015 // 1.5% del precio

    // Auto-sugerir SL y TP cuando cambia el entry
    useEffect(() => {
        if (entryPrice > 0) {
            if (side === 'BUY') {
                // SL: Entry - (1.5 * ATR)
                setStopLoss(entryPrice - (estimatedATR * 1.5))
                // TP: Entry + (3 * riesgo) para R:R 3:1
                const risk = estimatedATR * 1.5
                setTakeProfit(entryPrice + (risk * 3))
            } else {
                // SELL: invertir
                setStopLoss(entryPrice + (estimatedATR * 1.5))
                const risk = estimatedATR * 1.5
                setTakeProfit(entryPrice - (risk * 3))
            }
        }
    }, [entryPrice, side, estimatedATR])

    // Reset cuando cambia el side
    useEffect(() => {
        setEntryPrice(clickedPrice)
    }, [side, clickedPrice])

    const handlePositionSizeCalculated = (size: number, risk: number) => {
        setQuantity(size)
        setRiskAmount(risk)
    }

    const handleSubmit = async () => {
        if (quantity <= 0) {
            toast.error('Cantidad inválida')
            return
        }

        setLoading(true)

        try {
            const token = localStorage.getItem('token')
            const endpoint = mode === 'practice' ? '/api/v1/practice/order' : '/api/v1/trading/order'

            const orderData = {
                symbol,
                side,
                type: orderType,
                quantity,
                price: orderType === 'LIMIT' ? entryPrice : null,
                stop_loss: orderType === 'OCO' ? stopLoss : null,
                take_profit: orderType === 'OCO' ? takeProfit : null,
                mode
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(orderData)
            })

            const data = await response.json()

            if (response.ok) {
                toast.success(
                    '✅ Orden Creada',
                    { description: `${orderType} ${side} en $${entryPrice.toFixed(2)}` }
                )
                if (onOrderSubmit) onOrderSubmit()
                onClose()
            } else {
                toast.error(data.detail || 'Error al crear orden')
            }
        } catch (error) {
            toast.error('Error de conexión')
            console.error(error)
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/70 backdrop-blur-sm"
                onClick={onClose}
            />

            {/* Modal Content */}
            <div className="relative w-full max-w-4xl bg-[#0a0a0f] border border-white/20 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-white/10 bg-white/[0.02] sticky top-0 z-10">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-cyan-500/20">
                            <Target className="h-5 w-5 text-cyan-400" />
                        </div>
                        <div>
                            <h3 className="text-white font-bold text-lg">Ejecución Profesional</h3>
                            <p className="text-slate-400 text-xs">
                                {symbol} • Precio marcado: ${clickedPrice.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                <div className="grid grid-cols-2 gap-4 p-4">
                    {/* Columna Izquierda - Configuración de Orden */}
                    <div className="space-y-4">
                        {/* Lado: BUY/SELL */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-2">Dirección</label>
                            <div className="grid grid-cols-2 gap-2">
                                <button
                                    onClick={() => setSide('BUY')}
                                    className={`py-3 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${side === 'BUY'
                                            ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20'
                                            : 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20'
                                        }`}
                                >
                                    <TrendingUp className="h-4 w-4" />
                                    COMPRAR
                                </button>
                                <button
                                    onClick={() => setSide('SELL')}
                                    className={`py-3 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2 ${side === 'SELL'
                                            ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                                            : 'bg-rose-500/10 text-rose-400 hover:bg-rose-500/20'
                                        }`}
                                >
                                    <TrendingDown className="h-4 w-4" />
                                    VENDER
                                </button>
                            </div>
                        </div>

                        {/* Tipo de Orden */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-2">Tipo de Orden</label>
                            <div className="grid grid-cols-3 gap-2">
                                {(['MARKET', 'LIMIT', 'OCO'] as const).map(type => (
                                    <button
                                        key={type}
                                        onClick={() => setOrderType(type)}
                                        className={`py-2 text-xs rounded-lg transition-all ${orderType === type
                                                ? 'bg-white/10 text-white border border-white/20'
                                                : 'text-slate-400 hover:text-white hover:bg-white/5'
                                            }`}
                                    >
                                        {type}
                                    </button>
                                ))}
                            </div>
                            <p className="text-xs text-slate-500 mt-2">
                                {orderType === 'MARKET' && '⚡ Ejecución inmediata al precio de mercado'}
                                {orderType === 'LIMIT' && '📊 Espera hasta alcanzar el precio límite'}
                                {orderType === 'OCO' && '🔄 Configura SL y TP automáticamente'}
                            </p>
                        </div>

                        {/* Precio de Entrada */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-2">
                                <DollarSign className="h-3 w-3" />
                                Precio de Entrada (USDT)
                            </label>
                            <input
                                type="number"
                                value={entryPrice}
                                onChange={(e) => setEntryPrice(parseFloat(e.target.value))}
                                disabled={orderType === 'MARKET'}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white text-lg font-mono focus:outline-none focus:border-cyan-500/50 disabled:opacity-50"
                                step="0.01"
                            />
                            <p className="text-xs text-slate-500 mt-1">
                                Precio actual: ${currentPrice.toLocaleString()} • Diferencia: {((entryPrice - currentPrice) / currentPrice * 100).toFixed(2)}%
                            </p>
                        </div>

                        {/* Stop Loss */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-2">
                                <Shield className="h-3 w-3 text-rose-400" />
                                Stop Loss (USDT)
                            </label>
                            <input
                                type="number"
                                value={stopLoss}
                                onChange={(e) => setStopLoss(parseFloat(e.target.value))}
                                className="w-full bg-white/5 border border-rose-500/20 rounded-lg px-4 py-3 text-white text-lg font-mono focus:outline-none focus:border-rose-500/50"
                                step="0.01"
                            />
                            <p className="text-xs text-rose-300 mt-1">
                                Riesgo: ${Math.abs(entryPrice - stopLoss).toFixed(2)} ({((Math.abs(entryPrice - stopLoss) / entryPrice) * 100).toFixed(2)}%)
                            </p>
                        </div>

                        {/* Take Profit */}
                        <div>
                            <label className="block text-xs text-slate-400 mb-2 flex items-center gap-2">
                                <Target className="h-3 w-3 text-emerald-400" />
                                Take Profit (USDT)
                            </label>
                            <input
                                type="number"
                                value={takeProfit}
                                onChange={(e) => setTakeProfit(parseFloat(e.target.value))}
                                className="w-full bg-white/5 border border-emerald-500/20 rounded-lg px-4 py-3 text-white text-lg font-mono focus:outline-none focus:border-emerald-500/50"
                                step="0.01"
                            />
                            <p className="text-xs text-emerald-300 mt-1">
                                Beneficio: ${Math.abs(takeProfit - entryPrice).toFixed(2)} ({((Math.abs(takeProfit - entryPrice) / entryPrice) * 100).toFixed(2)}%)
                            </p>
                        </div>
                    </div>

                    {/* Columna Derecha - Calculadora de Riesgo */}
                    <div>
                        <RiskCalculator
                            accountBalance={accountBalance}
                            entryPrice={entryPrice}
                            stopLoss={stopLoss}
                            takeProfit={takeProfit}
                            onPositionSizeCalculated={handlePositionSizeCalculated}
                        />
                    </div>
                </div>

                {/* Footer - Resumen y Botón */}
                <div className="p-4 border-t border-white/10 bg-white/[0.02]">
                    <div className="flex items-center justify-between mb-3">
                        <div className="text-sm text-slate-400">
                            Cantidad: <span className="text-white font-mono font-bold">{quantity.toFixed(6)}</span> {symbol.replace('USDT', '')}
                        </div>
                        <div className="text-sm text-slate-400">
                            Total: <span className="text-white font-mono font-bold">${(quantity * entryPrice).toFixed(2)}</span>
                        </div>
                    </div>

                    <button
                        onClick={handleSubmit}
                        disabled={loading || quantity <= 0}
                        className={`w-full py-4 rounded-lg font-bold text-white text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed ${side === 'BUY'
                                ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 shadow-lg shadow-emerald-500/30'
                                : 'bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 shadow-lg shadow-rose-500/30'
                            }`}
                    >
                        {loading ? 'Procesando...' : `${side === 'BUY' ? 'Ejecutar Compra' : 'Ejecutar Venta'} • ${orderType}`}
                    </button>

                    <p className="text-xs text-center text-slate-500 mt-2">
                        Modo: <span className={mode === 'practice' ? 'text-emerald-400' : 'text-rose-400'}>{mode === 'practice' ? 'PRÁCTICA' : 'REAL'}</span>
                    </p>
                </div>
            </div>
        </div>
    )
}
