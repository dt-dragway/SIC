'use client'

import { useState, useEffect } from 'react'
import { X, TrendingUp, TrendingDown, Target, Shield, DollarSign } from 'lucide-react'
import { toast } from 'sonner'
import { useAuth } from '@/hooks/useAuth'

interface SignalExecutionModalProps {
    isOpen: boolean
    onClose: () => void
    signal: {
        symbol: string
        type: string  // LONG or SHORT
        entry_price: number
        stop_loss: number
        take_profit: number
        confidence: number
    }
    accountBalance: number
    mode: 'practice' | 'real'
    onOrderSubmit?: () => void
}

export default function SignalExecutionModal({
    isOpen,
    onClose,
    signal,
    accountBalance,
    mode,
    onOrderSubmit
}: SignalExecutionModalProps) {
    // Dirección automática basada en la señal
    const side = signal.type === 'LONG' ? 'BUY' : 'SELL'
    const isLong = signal.type === 'LONG'

    // Estado para monto de inversión
    const [investmentAmount, setInvestmentAmount] = useState(5) // Mínimo $5 por defecto
    const [loading, setLoading] = useState(false)

    // Calcular cantidad basada en el monto
    const quantity = investmentAmount / signal.entry_price
    const fee = investmentAmount * 0.001 // 0.1% fee

    // Calcular riesgo y ganancia potencial
    const riskPerUnit = Math.abs(signal.entry_price - signal.stop_loss)
    const rewardPerUnit = Math.abs(signal.take_profit - signal.entry_price)
    const riskAmount = quantity * riskPerUnit
    const rewardAmount = quantity * rewardPerUnit
    const rrRatio = riskPerUnit > 0 ? rewardPerUnit / riskPerUnit : 0

    // Reset cuando cambia la señal
    useEffect(() => {
        setInvestmentAmount(5) // Reset a mínimo
    }, [signal.symbol])

    // Manejadores de porcentaje
    const handlePercentage = (percent: number) => {
        const amount = (accountBalance * percent) / 100
        setInvestmentAmount(Math.max(5, Math.round(amount * 100) / 100))
    }

    // Validaciones
    const isAmountValid = investmentAmount >= 5
    const hasEnoughBalance = investmentAmount <= accountBalance
    const canSubmit = isAmountValid && hasEnoughBalance && quantity > 0

    const { token, logout } = useAuth()

    const handleSubmit = async () => {
        if (!canSubmit) {
            if (!isAmountValid) toast.error('El monto mínimo es $5 USD')
            if (!hasEnoughBalance) toast.error('Saldo insuficiente')
            return
        }

        setLoading(true)

        try {
            const endpoint = mode === 'practice' ? '/api/v1/practice/order' : '/api/v1/trading/order'

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    symbol: signal.symbol,
                    side: side,
                    type: 'LIMIT',
                    quantity: quantity,
                    price: signal.entry_price,
                    stop_loss: signal.stop_loss,
                    take_profit: signal.take_profit
                })
            })

            const data = await response.json()

            if (response.ok) {
                toast.success(
                    isLong ? '🟢 Compra Ejecutada' : '🔴 Venta Ejecutada',
                    { description: `${quantity.toFixed(6)} ${signal.symbol.replace('USDT', '')} @ $${signal.entry_price.toFixed(2)}` }
                )
                if (onOrderSubmit) onOrderSubmit()
                onClose()
            } else {
                if (response.status === 401) {
                    toast.error('Sesión expirada. Redirigiendo al login...')
                    logout()
                    return
                }
                toast.error(data.detail || 'Error al ejecutar orden')
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

            {/* Modal */}
            <div className="relative w-full max-w-md bg-[#0a0a0f] border border-white/20 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                {/* Header con Dirección Automática */}
                <div className={`p-4 border-b border-white/10 ${isLong ? 'bg-emerald-500/10' : 'bg-rose-500/10'}`}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${isLong ? 'bg-emerald-500/20' : 'bg-rose-500/20'}`}>
                                {isLong ? (
                                    <TrendingUp className={`h-6 w-6 text-emerald-400`} />
                                ) : (
                                    <TrendingDown className={`h-6 w-6 text-rose-400`} />
                                )}
                            </div>
                            <div>
                                <h3 className="text-white font-bold text-lg flex items-center gap-2">
                                    {isLong ? 'COMPRAR' : 'VENDER'}
                                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${isLong ? 'bg-emerald-500/30 text-emerald-300' : 'bg-rose-500/30 text-rose-300'}`}>
                                        {signal.type}
                                    </span>
                                </h3>
                                <p className="text-slate-400 text-sm">{signal.symbol} • Confianza: {signal.confidence}%</p>
                            </div>
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                        >
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Información de la Señal */}
                <div className="p-4 space-y-3 border-b border-white/10">
                    <div className="grid grid-cols-3 gap-3 text-center">
                        <div className="p-3 bg-white/5 rounded-lg">
                            <p className="text-xs text-slate-500 mb-1">Entrada</p>
                            <p className="text-white font-mono font-bold">${signal.entry_price.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-rose-500/10 rounded-lg border border-rose-500/20">
                            <p className="text-xs text-rose-400 mb-1 flex items-center justify-center gap-1">
                                <Shield className="h-3 w-3" /> Stop Loss
                            </p>
                            <p className="text-rose-400 font-mono font-bold">${signal.stop_loss.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                            <p className="text-xs text-emerald-400 mb-1 flex items-center justify-center gap-1">
                                <Target className="h-3 w-3" /> Take Profit
                            </p>
                            <p className="text-emerald-400 font-mono font-bold">${signal.take_profit.toLocaleString()}</p>
                        </div>
                    </div>

                    {/* Ratio R:R */}
                    <div className="flex justify-between items-center px-2">
                        <span className="text-sm text-slate-400">Ratio Riesgo:Beneficio</span>
                        <span className={`font-mono font-bold ${rrRatio >= 2 ? 'text-emerald-400' : rrRatio >= 1 ? 'text-yellow-400' : 'text-rose-400'}`}>
                            1:{rrRatio.toFixed(2)}
                        </span>
                    </div>
                </div>

                {/* Monto de Inversión */}
                <div className="p-4 space-y-4">
                    <div>
                        <label className="block text-sm text-slate-400 mb-2 flex items-center gap-2">
                            <DollarSign className="h-4 w-4" />
                            Monto a Invertir (USD)
                        </label>

                        {/* Botones de Porcentaje */}
                        <div className="grid grid-cols-5 gap-2 mb-3">
                            {[10, 20, 30, 40, 50].map(percent => (
                                <button
                                    key={percent}
                                    onClick={() => handlePercentage(percent)}
                                    className="py-2 text-xs bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white rounded-lg transition-all border border-white/5 hover:border-white/20"
                                >
                                    {percent}%
                                </button>
                            ))}
                        </div>

                        {/* Campo de Monto */}
                        <div className="relative">
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">$</span>
                            <input
                                type="number"
                                value={investmentAmount}
                                onChange={(e) => setInvestmentAmount(Math.max(0, parseFloat(e.target.value) || 0))}
                                className="w-full bg-white/5 border border-white/10 rounded-lg pl-8 pr-4 py-3 text-white text-lg font-mono focus:outline-none focus:border-cyan-500/50"
                                placeholder="5.00"
                                min="5"
                                step="1"
                            />
                        </div>

                        {/* Información del Monto */}
                        <div className="flex justify-between text-xs text-slate-500 mt-2">
                            <span>Mínimo: $5.00</span>
                            <span>Disponible: ${accountBalance.toFixed(2)}</span>
                        </div>

                        {/* Errores */}
                        {!isAmountValid && investmentAmount > 0 && (
                            <p className="text-xs text-rose-400 mt-1">⚠️ El monto mínimo es $5 USD</p>
                        )}
                        {!hasEnoughBalance && (
                            <p className="text-xs text-rose-400 mt-1">⚠️ Saldo insuficiente</p>
                        )}
                    </div>

                    {/* Resumen */}
                    <div className="p-3 bg-white/5 rounded-lg space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-400">Cantidad</span>
                            <span className="text-white font-mono">{quantity.toFixed(6)} {signal.symbol.replace('USDT', '')}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-400">Fee (0.1%)</span>
                            <span className="text-slate-400 font-mono">${fee.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-sm border-t border-white/10 pt-2">
                            <span className="text-slate-400">Riesgo Máx.</span>
                            <span className="text-rose-400 font-mono">-${riskAmount.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-400">Ganancia Pot.</span>
                            <span className="text-emerald-400 font-mono">+${rewardAmount.toFixed(2)}</span>
                        </div>
                    </div>
                </div>

                {/* Footer - Botón de Ejecución */}
                <div className="p-4 border-t border-white/10">
                    <button
                        onClick={handleSubmit}
                        disabled={loading || !canSubmit}
                        className={`w-full py-4 rounded-xl font-bold text-white text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed ${isLong
                            ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 shadow-lg shadow-emerald-500/30'
                            : 'bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 shadow-lg shadow-rose-500/30'
                            }`}
                    >
                        {loading ? 'Procesando...' : (
                            <>
                                {isLong ? '🟢 Ejecutar COMPRA' : '🔴 Ejecutar VENTA'} • ${investmentAmount.toFixed(2)}
                            </>
                        )}
                    </button>

                    <p className="text-xs text-center text-slate-500 mt-2">
                        Modo: <span className={mode === 'practice' ? 'text-emerald-400' : 'text-rose-400'}>
                            {mode === 'practice' ? 'PRÁCTICA' : 'REAL'}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    )
}
