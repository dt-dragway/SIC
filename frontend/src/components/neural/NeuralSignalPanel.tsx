'use client'

import { ArrowUp, ArrowDown, Minus, TrendingUp, Zap, AlertCircle, CheckCircle2, Clock } from 'lucide-react'
import { useNeuralSignal, type NeuralSignal } from '../../hooks/useNeuralSignals'
import LoadingSpinner from '../ui/LoadingSpinner'
import { use Effect, useState } from 'react'

interface NeuralSignalPanelProps {
    symbol: string
    onExecute?: (signal: NeuralSignal) => void
}

export default function NeuralSignalPanel({ symbol, onExecute }: NeuralSignalPanelProps) {
    const { signal, loading, error, refresh } = useNeuralSignal(symbol)
    const [timeRemaining, setTimeRemaining] = useState<string>('')

    // Calcular tiempo restante hasta que expire la señal
    useEffect(() => {
        if (!signal?.expires_at) return

        const updateTimer = () => {
            const now = new Date()
            const expires = new Date(signal.expires_at)
            const diff = expires.getTime() - now.getTime()

            if (diff <= 0) {
                setTimeRemaining('Expirada')
                return
            }

            const hours = Math.floor(diff / (1000 * 60 * 60))
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
            setTimeRemaining(`${hours}h ${minutes}m`)
        }

        updateTimer()
        const interval = setInterval(updateTimer, 60000) // Actualizar cada minuto

        return () => clearInterval(interval)
    }, [signal?.expires_at])

    if (loading && !signal) {
        return (
            <div className="bg-[#0a0a0f] rounded-lg border border-white/10 p-6">
                <div className="flex items-center justify-center py-12">
                    < LoadingSpinner />
                    <span className="ml-3 text-slate-400">Analizando {symbol}...</span>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="bg-[#0a0a0f] rounded-lg border border-white/10 p-6">
                <div className="flex items-center gap-3 text-rose-400">
                    <AlertCircle className="h-5 w-5" />
                    <span>Error: {error}</span>
                </div>
            </div>
        )
    }

    if (!signal) {
        return (
            <div className="bg-[#0a0a0f] rounded-lg border border-white/10 p-6">
                <div className="text-center py-12 text-slate-500">
                    No hay señal disponible
                </div>
            </div>
        )
    }

    // Colores según dirección
    const directionColors = {
        LONG: 'emerald',
        SHORT: 'rose',
        HOLD: 'slate'
    }

    const color = directionColors[signal.direction]

    // Icono según dirección
    const DirectionIcon = signal.direction === 'LONG' ? ArrowUp : signal.direction === 'SHORT' ? ArrowDown : Minus

    return (
        <div className="bg-[#0a0a0f] rounded-lg border border-white/10 overflow-hidden">
            {/* Header - Señal Principal */}
            <div className={`bg-${color}-500/10 border-b border-${color}-500/20 p-4`}>
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <Zap className={`h-5 w-5 text-${color}-400`} />
                        <h3 className="font-semibold text-white">Neural Engine</h3>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                        <Clock className="h-3 w-3" />
                        <span>Expira en: {timeRemaining}</span>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <DirectionIcon className={`h-8 w-8 text-${color}-400`} />
                    <div className="flex-1">
                        <div className={`text-2xl font-bold text-${color}-400`}>
                            SEÑAL {signal.direction}
                        </div>
                        <div className="flex items-center gap-2 mt-1">
                            <span className="text-sm text-slate-400">Confianza: {signal.confidence.toFixed(1)}%</span>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium bg-${color}-500/20 text-${color}-300`}>
                                {signal.strength === 'STRONG' ? 'FUERTE' : signal.strength === 'MODERATE' ? 'MODERADA' : 'DÉBIL'}
                            </span>
                        </div>
                    </div>
                </div>

                {/* Barra de confianza */}
                <div className="mt-3 h-2 bg-white/5 rounded-full overflow-hidden">
                    <div
                        className={`h-full bg-gradient-to-r from-${color}-500 to-${color}-400 transition-all`}
                        style={{ width: `${signal.confidence}%` }}
                    />
                </div>
            </div>

            {/* Body - Detalles */}
            <div className="p-4 space-y-4">
                {/* Patrones de Velas Detectados */}
                {signal.candlestick_patterns && signal.candlestick_patterns.length > 0 && (
                    <div>
                        <h4 className="text-xs font-medium text-slate-400 mb-2 flex items-center gap-2">
                            <TrendingUp className="h-3 w-3" />
                            Patrones de Velas Detectados
                        </h4>
                        <div className="space-y-1">
                            {signal.candlestick_patterns.slice(0, 3).map((pattern, i) => (
                                <div key={i} className="flex items-start gap-2 text-sm bg-white/5 rounded p-2">
                                    <span className="text-lg">{pattern.icon}</span>
                                    <div className="flex-1">
                                        <div className="font-medium text-white">{pattern.name_es}</div>
                                        <div className="text-xs text-slate-400">{pattern.description_es}</div>
                                    </div>
                                    <span className={`text-xs px-2 py-0.5 rounded bg-${pattern.color}-500/20 text-${pattern.color}-300`}>
                                        {pattern.confidence.toFixed(0)}%
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Explicación en Español */}
                <div>
                    <h4 className="text-xs font-medium text-slate-400 mb-2">💡 Explicación</h4>
                    <div className="text-sm text-slate-300 bg-white/5 rounded p-3 whitespace-pre-line">
                        {signal.explanation_es}
                    </div>
                </div>

                {/* Pasos de Ejecución */}
                <div>
                    <h4 className="text-xs font-medium text-slate-400 mb-2">📋 Cómo Ejecutar</h4>
                    <div className="space-y-2">
                        {signal.execution_steps.map((step, i) => (
                            <div key={i} className="flex items-start gap-2 text-sm text-slate-300">
                                <CheckCircle2 className="h-4 w-4 text-emerald-500 mt-0.5 shrink-0" />
                                <span>{step}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Niveles de Precio */}
                <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-cyan-500/10 border border-cyan-500/20 rounded p-2">
                        <div className="text-cyan-400 font-medium">Entrada</div>
                        <div className="text-white font-mono mt-1">${signal.entry_price.toLocaleString()}</div>
                    </div>
                    <div className="bg-rose-500/10 border border-rose-500/20 rounded p-2">
                        <div className="text-rose-400 font-medium">Stop Loss</div>
                        <div className="text-white font-mono mt-1">${signal.stop_loss.toLocaleString()}</div>
                    </div>
                    <div className="bg-emerald-500/10 border border-emerald-500/20 rounded p-2">
                        <div className="text-emerald-400 font-medium">Take Profit</div>
                        <div className="text-white font-mono mt-1">${signal.take_profit.toLocaleString()}</div>
                    </div>
                </div>

                {/* Botón de Ejecución */}
                {signal.direction !== 'HOLD' && onExecute && (
                    <button
                        onClick={() => onExecute(signal)}
                        className={`w-full py-3 rounded-lg font-medium transition-all bg-gradient-to-r from-${color}-600 to-${color}-500 hover:from-${color}-500 hover:to-${color}-400 text-white shadow-lg shadow-${color}-500/20`}
                    >
                        🚀 EJECUTAR SEÑAL {signal.direction}
                    </button>
                )}
            </div>
        </div>
    )
}
