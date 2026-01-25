'use client'

import { useState, useEffect } from 'react'
import { Calculator, AlertTriangle, CheckCircle2, Info } from 'lucide-react'

interface RiskCalculatorProps {
    accountBalance: number
    entryPrice: number
    stopLoss: number
    takeProfit: number
    winRate?: number  // % histórico de trades ganadores (0-1)
    avgWinLossRatio?: number  // Ratio promedio Win/Loss
    onPositionSizeCalculated?: (size: number, riskAmount: number) => void
}

export default function RiskCalculator({
    accountBalance,
    entryPrice,
    stopLoss,
    takeProfit,
    winRate = 0.55,  // Default 55% win rate
    avgWinLossRatio = 1.5,  // Default 1.5:1
    onPositionSizeCalculated
}: RiskCalculatorProps) {
    const [maxRiskPercent, setMaxRiskPercent] = useState(1.0) // 1% por defecto
    const [kellyFraction, setKellyFraction] = useState(0.25) // 1/4 de Kelly

    // Cálculos
    const riskPerUnit = Math.abs(entryPrice - stopLoss)
    const rewardPerUnit = Math.abs(takeProfit - entryPrice)
    const rrRatio = riskPerUnit > 0 ? rewardPerUnit / riskPerUnit : 0

    // Kelly Criterion Fraccionado
    const kellyPercent = winRate > 0 && avgWinLossRatio > 0
        ? (winRate - (1 - winRate) / avgWinLossRatio) * kellyFraction
        : 0

    // Tamaño de posición basado en riesgo máximo
    const maxRiskAmount = accountBalance * (maxRiskPercent / 100)
    const positionSize = riskPerUnit > 0 ? maxRiskAmount / riskPerUnit : 0

    // Tamaño sugerido por Kelly
    const kellySuggestedSize = accountBalance * kellyPercent / 100

    // Validaciones
    const isRRValid = rrRatio >= 2.0
    const isRiskValid = maxRiskPercent <= 2.0
    const isTradeValid = isRRValid && isRiskValid && riskPerUnit > 0

    // Calcular dólares en riesgo
    const dollarRisk = positionSize * riskPerUnit
    const potentialProfit = positionSize * rewardPerUnit

    useEffect(() => {
        if (isTradeValid && onPositionSizeCalculated) {
            onPositionSizeCalculated(positionSize, dollarRisk)
        }
    }, [positionSize, dollarRisk, isTradeValid])

    return (
        <div className="bg-[#0a0a0f] rounded-lg border border-white/10 p-4 space-y-4">
            {/* Header */}
            <div className="flex items-center gap-2 pb-3 border-b border-white/10">
                <Calculator className="h-5 w-5 text-cyan-400" />
                <h3 className="text-white font-semibold text-sm">Calculadora de Riesgo Profesional</h3>
            </div>

            {/* Parámetros de Usuario */}
            <div className="space-y-3">
                <div>
                    <label className="block text-xs text-slate-400 mb-1.5">Riesgo Máximo por Trade (%)</label>
                    <input
                        type="number"
                        value={maxRiskPercent}
                        onChange={(e) => setMaxRiskPercent(parseFloat(e.target.value) || 1)}
                        step="0.1"
                        min="0.1"
                        max="5"
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                    />
                    {maxRiskPercent > 2 && (
                        <p className="text-rose-400 text-xs mt-1 flex items-center gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            ¡Riesgo excesivo! Máximo recomendado: 2%
                        </p>
                    )}
                </div>

                <div>
                    <label className="block text-xs text-slate-400 mb-1.5 flex items-center gap-1">
                        Win Rate Histórico (%)
                        <Info className="h-3 w-3 text-slate-500" />
                    </label>
                    <input
                        type="number"
                        value={(winRate * 100).toFixed(0)}
                        onChange={(e) => setMaxRiskPercent(parseFloat(e.target.value) / 100 || 0.55)}
                        step="1"
                        min="0"
                        max="100"
                        className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-cyan-500/50"
                        disabled
                    />
                    <p className="text-xs text-slate-500 mt-1">Calculado automáticamente del historial</p>
                </div>
            </div>

            {/* Resultados - Ratios */}
            <div className="space-y-2 pt-2 border-t border-white/10">
                <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">Ratio Riesgo:Beneficio</span>
                    <span className={`text-sm font-mono font-bold ${isRRValid ? 'text-emerald-400' : 'text-rose-400'}`}>
                        1:{rrRatio.toFixed(2)} {isRRValid ? '✓' : '✗'}
                    </span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">Distancia a SL</span>
                    <span className="text-sm font-mono text-white">
                        ${riskPerUnit.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">Distancia a TP</span>
                    <span className="text-sm font-mono text-white">
                        ${rewardPerUnit.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                </div>
            </div>

            {/* Resultados - Tamaño de Posición */}
            <div className="space-y-2 pt-2 border-t border-white/10">
                <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">Tamaño de Posición</span>
                    <span className="text-sm font-mono font-bold text-cyan-400">
                        {positionSize.toFixed(6)}
                    </span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">$ en Riesgo</span>
                    <span className="text-sm font-mono text-rose-400">
                        -${dollarRisk.toFixed(2)}
                    </span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">$ Potencial (si TP)</span>
                    <span className="text-sm font-mono text-emerald-400">
                        +${potentialProfit.toFixed(2)}
                    </span>
                </div>

                <div className="flex justify-between items-center">
                    <span className="text-xs text-slate-400">% del Balance en Riesgo</span>
                    <span className={`text-sm font-mono ${maxRiskPercent <= 2 ? 'text-white' : 'text-rose-400'}`}>
                        {maxRiskPercent.toFixed(2)}%
                    </span>
                </div>
            </div>

            {/* Kelly Suggestion */}
            <div className="bg-violet-500/10 border border-violet-500/20 rounded-lg p-3">
                <div className="flex items-start gap-2">
                    <Info className="h-4 w-4 text-violet-400 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-xs text-violet-300 font-medium mb-1">Kelly Criterion</p>
                        <p className="text-xs text-slate-300">
                            Basado en tu win rate de {(winRate * 100).toFixed(0)}% y ratio {avgWinLossRatio.toFixed(1)}:1,
                            Kelly sugiere <span className="text-white font-mono">{(kellyPercent * 100).toFixed(2)}%</span> del balance.
                        </p>
                    </div>
                </div>
            </div>

            {/* Validación Final */}
            <div className={`rounded-lg p-3 border ${isTradeValid ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-rose-500/10 border-rose-500/20'}`}>
                <div className="flex items-center gap-2">
                    {isTradeValid ? (
                        <>
                            <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                            <span className="text-sm text-emerald-300 font-medium">Trade Válido - Cumple Criterios</span>
                        </>
                    ) : (
                        <>
                            <AlertTriangle className="h-5 w-5 text-rose-400" />
                            <div className="flex-1">
                                <span className="text-sm text-rose-300 font-medium block">Trade Rechazado</span>
                                <ul className="text-xs text-rose-200 mt-1 space-y-0.5">
                                    {!isRRValid && <li>• R:R debe ser ≥ 2:1</li>}
                                    {!isRiskValid && <li>• Riesgo máximo 2% por trade</li>}
                                    {riskPerUnit <= 0 && <li>• SL debe estar por debajo de Entry (BUY)</li>}
                                </ul>
                            </div>
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}
