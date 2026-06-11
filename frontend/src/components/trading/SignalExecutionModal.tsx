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
    accountBalance: number // Used for investment limit check (USD value)
    availableBalance: number // Actual available amount of the asset (e.g. 0.005 BTC)
    balanceAsset: string // "USDT", "BTC", etc.
    mode: 'practice' | 'real'
    onOrderSubmit?: () => void
}

export default function SignalExecutionModal({
    isOpen,
    onClose,
    signal,
    accountBalance,
    availableBalance,
    balanceAsset,
    mode,
    onOrderSubmit
}: SignalExecutionModalProps) {
    const [marketType, setMarketType] = useState<'spot' | 'futures'>('spot')
    const [leverage, setLeverage] = useState<number>(1)

    // Dirección automática basada en la señal
    const side = signal.type === 'LONG' ? 'BUY' : 'SELL'
    const isLong = signal.type === 'LONG'

    // Estado para monto de inversión
    const [investmentAmount, setInvestmentAmount] = useState(5) // Mínimo $5 por defecto
    const [loading, setLoading] = useState(false)

    // Calcular cantidad basada en el monto y apalancamiento
    const quantity = (investmentAmount * leverage) / signal.entry_price
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
        setMarketType('spot')
        setLeverage(1)
    }, [signal.symbol])

    // Manejadores de porcentaje
    const handlePercentage = (percent: number) => {
        const amount = (accountBalance * percent) / 100
        setInvestmentAmount(Math.max(5, Math.round(amount * 100) / 100))
    }

    // Validaciones
    const isAmountValid = investmentAmount >= 5
    // Validation:
    // In Spot BUY or Futures (both LONG/SHORT): we just check usdt balance >= margin/amount
    // In Spot SELL: we check cryptos available
    const hasEnoughBalance = (marketType === 'futures' || isLong)
        ? investmentAmount <= availableBalance
        : quantity <= availableBalance
    const canSubmit = isAmountValid && hasEnoughBalance && quantity > 0

    const { token: authToken } = useAuth()

    const handleSubmit = async () => {
        if (!canSubmit) {
            if (!isAmountValid) toast.error('El monto mínimo es $5 USD')
            if (!hasEnoughBalance) toast.error('Saldo insuficiente')
            return
        }

        setLoading(true)

        try {
            // Get token directly from storage to avoid useAuth hook initialization race condition
            const token = authToken || localStorage.getItem('token')

            if (!token) {
                toast.error('No hay sesión activa')
                setLoading(false)
                return
            }

            let endpoint = ''
            let bodyPayload = {}

            if (marketType === 'futures') {
                endpoint = mode === 'practice' ? '/api/v1/practice/futures/open' : '/api/v1/trading/futures/open'
                bodyPayload = {
                    symbol: signal.symbol,
                    side: signal.type, // LONG or SHORT
                    size: quantity,
                    leverage: leverage
                }
            } else {
                endpoint = mode === 'practice' ? '/api/v1/practice/order' : '/api/v1/trading/order'
                bodyPayload = {
                    symbol: signal.symbol,
                    side: side,
                    type: 'LIMIT',
                    quantity: quantity,
                    price: signal.entry_price,
                    stop_loss: signal.stop_loss,
                    take_profit: signal.take_profit
                }
            }

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(bodyPayload)
            })

            const data = await response.json()

            if (response.ok) {
                toast.success(
                    marketType === 'futures'
                        ? `🚀 Contrato ${signal.type} ${leverage}x Abierto`
                        : (isLong ? '🟢 Compra Spot Ejecutada' : '🔴 Venta Spot Ejecutada'),
                    { description: `${quantity.toFixed(6)} ${signal.symbol.replace('USDT', '')} @ $${signal.entry_price.toFixed(2)}` }
                )
                if (onOrderSubmit) onOrderSubmit()
                onClose()
            } else {
                if (response.status === 401) {
                    toast.error('Sesión expirada. Por favor, reingresa.')
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

                {/* Tipo de Mercado Selection */}
                <div className="px-4 py-3 border-b border-white/10">
                    <label className="block text-xs text-slate-500 uppercase tracking-wider mb-2 font-bold font-sans">Tipo de Mercado</label>
                    <div className="grid grid-cols-2 gap-2 bg-black/40 p-1 rounded-lg border border-white/5">
                        <button
                            type="button"
                            onClick={() => { setMarketType('spot'); setLeverage(1); }}
                            className={`py-2 text-xs font-bold rounded-md transition-all ${marketType === 'spot'
                                ? 'bg-white/10 text-white border border-white/10 shadow-sm'
                                : 'text-slate-400 hover:text-slate-200'
                            }`}
                        >
                            Spot (Al Contado)
                        </button>
                        <button
                            type="button"
                            onClick={() => setMarketType('futures')}
                            className={`py-2 text-xs font-bold rounded-md transition-all ${marketType === 'futures'
                                ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                                : 'text-slate-400 hover:text-slate-200'
                            }`}
                        >
                            🚀 Futuros IA
                        </button>
                    </div>
                </div>

                {/* Leverage Selector (Only for Futures) */}
                {marketType === 'futures' && (
                    <div className="px-4 py-3 border-b border-white/10 space-y-2 animate-in slide-in-from-top-2 duration-200">
                        <div className="flex justify-between items-center text-xs">
                            <span className="text-slate-400 font-sans">Apalancamiento</span>
                            <span className="text-cyan-400 font-bold font-mono text-sm">{leverage}x</span>
                        </div>
                        <div className="flex gap-2">
                            {[1, 2, 3, 5, 10, 20].map((l) => (
                                <button
                                    key={l}
                                    type="button"
                                    onClick={() => setLeverage(l)}
                                    className={`flex-1 py-1.5 rounded text-xs font-mono font-bold transition-all border ${leverage === l
                                        ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40'
                                        : 'bg-white/5 text-slate-400 border-transparent hover:bg-white/10'
                                    }`}
                                >
                                    {l === 1 ? '1x (Safe)' : `${l}x`}
                                </button>
                            ))}
                        </div>
                        {leverage > 5 && (
                            <p className="text-[10px] text-amber-400/80 italic font-medium">
                                ⚠️ Apalancamientos mayores a 5x amplifican proporcionalmente el riesgo de liquidación.
                            </p>
                        )}
                    </div>
                )}

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
                            <span>Mínimo: $5.00</span>
                            <span className="font-mono text-emerald-400">
                                Disp: {availableBalance.toLocaleString(undefined, { maximumFractionDigits: 6 })} {balanceAsset}
                            </span>
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
                            <span className="text-slate-400">
                                {marketType === 'futures' ? 'Tamaño Contrato (Size)' : 'Cantidad'}
                            </span>
                            <span className="text-white font-mono">{quantity.toFixed(6)} {signal.symbol.replace('USDT', '')}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-400">Fee (0.1%)</span>
                            <span className="text-slate-400 font-mono">${fee.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between text-sm border-t border-white/10 pt-2">
                            <span className="text-slate-400">
                                {marketType === 'futures' ? 'Margen (Colateral USDT)' : 'Riesgo Máx.'}
                            </span>
                            <span className={`${marketType === 'futures' ? 'text-cyan-400' : 'text-rose-400'} font-mono`}>
                                {marketType === 'futures' ? `$${investmentAmount.toFixed(2)}` : `-${riskAmount.toFixed(2)}`}
                            </span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-400">
                                {marketType === 'futures' ? 'Poder de Compra (Notional)' : 'Ganancia Pot.'}
                            </span>
                            <span className={`${marketType === 'futures' ? 'text-violet-400' : 'text-emerald-400'} font-mono`}>
                                {marketType === 'futures' ? `$${(investmentAmount * leverage).toFixed(2)}` : `+${rewardAmount.toFixed(2)}`}
                            </span>
                        </div>
                    </div>
                </div>
 
                {/* Footer - Botón de Ejecución */}
                <div className="p-4 border-t border-white/10">
                    <button
                        onClick={handleSubmit}
                        disabled={loading || !canSubmit}
                        className={`w-full py-4 rounded-xl font-bold text-white text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed ${marketType === 'futures'
                            ? 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 shadow-lg shadow-cyan-500/30'
                            : (isLong
                                ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 shadow-lg shadow-emerald-500/30'
                                : 'bg-gradient-to-r from-rose-500 to-rose-600 hover:from-rose-600 hover:to-rose-700 shadow-lg shadow-rose-500/30')
                            }`}
                    >
                        {loading ? 'Procesando...' : (
                            <>
                                {marketType === 'futures'
                                    ? `🚀 Ejecutar Contrato ${signal.type} ${leverage}x`
                                    : (isLong ? '🟢 Ejecutar COMPRA Spot' : '🔴 Ejecutar VENTA Spot')
                                } • ${investmentAmount.toFixed(2)}
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
