/**
 * Hook personalizado para acceder a señales del Neural Engine
 * 
 * Proporciona acceso a señales de trading con explicaciones en español
 * y actualización automática cada 30 segundos.
 */

import { useState, useEffect, useCallback } from 'react'

export interface CandlestickPattern {
    name: string
    name_es: string
    direction: string
    strength: string
    confidence: number
    description_es: string
    icon: string
    color: string
}

export interface NeuralSignal {
    signal_id: string
    symbol: string
    direction: 'LONG' | 'SHORT' | 'HOLD'
    confidence: number
    strength: 'STRONG' | 'MODERATE' | 'WEAK'
    entry_price: number
    stop_loss: number
    take_profit: number
    risk_reward: number

    // Patrones y explicaciones
    candlestick_patterns: CandlestickPattern[]
    explanation_es: string
    execution_steps: string[]

    // Análisis técnico
    patterns_detected: string[]
    indicators_used: string[]
    top_trader_consensus: any
    timeframe_analysis: Record<string, string>
    reasoning: string[]

    // Metadata
    generated_at: string
    expires_at: string
}

export interface NeuralStatus {
    status: string
    total_trades_analyzed: number
    win_rate: number
    patterns_learned: number
    candlestick_analyzer_active: boolean
    supported_symbols: string[]
}

export function useNeuralSignal(symbol: string | null) {
    const [signal, setSignal] = useState<NeuralSignal | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const fetchSignal = useCallback(async () => {
        if (!symbol) return

        setLoading(true)
        setError(null)

        try {
            const token = localStorage.getItem('token')
            if (!token) {
                setError('No autenticado')
                return
            }

            const response = await fetch(`/api/v1/neural/neural-signal/${symbol}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (!response.ok) {
                throw new Error(`Error ${response.status}`)
            }

            const data = await response.json()
            setSignal(data)
        } catch (err: any) {
            setError(err.message)
            console.error('Error fetching neural signal:', err)
        } finally {
            setLoading(false)
        }
    }, [symbol])

    // Fetch inicial
    useEffect(() => {
        fetchSignal()
    }, [fetchSignal])

    // Auto-refresh cada 30 segundos
    useEffect(() => {
        if (!symbol) return

        const interval = setInterval(() => {
            fetchSignal()
        }, 30000) // 30 segundos

        return () => clearInterval(interval)
    }, [symbol, fetchSignal])

    return {
        signal,
        loading,
        error,
        refresh: fetchSignal
    }
}

export function useNeuralStatus() {
    const [status, setStatus] = useState<NeuralStatus | null>(null)
    const [loading, setLoading] = useState(false)

    const fetchStatus = useCallback(async () => {
        setLoading(true)

        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const response = await fetch('/api/v1/neural/neural-status', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (response.ok) {
                const data = await response.json()
                setStatus(data)
            }
        } catch (err) {
            console.error('Error fetching neural status:', err)
        } finally {
            setLoading(false)
        }
    }, [])

    useEffect(() => {
        fetchStatus()
    }, [fetchStatus])

    return { status, loading, refresh: fetchStatus }
}

export function useAllNeuralSignals(onlyStrong: boolean = false) {
    const [signals, setSignals] = useState<any[]>([])
    const [loading, setLoading] = useState(false)
    const [stats, setStats] = useState({
        bullish_count: 0,
        bearish_count: 0,
        neutral_count: 0
    })

    const fetchAll = useCallback(async () => {
        setLoading(true)

        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const response = await fetch(
                `/api/v1/neural/neural-signals/all?only_strong=${onlyStrong}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            )

            if (response.ok) {
                const data = await response.json()
                setSignals(data.signals)
                setStats({
                    bullish_count: data.bullish_count,
                    bearish_count: data.bearish_count,
                    neutral_count: data.neutral_count
                })
            }
        } catch (err) {
            console.error('Error fetching all signals:', err)
        } finally {
            setLoading(false)
        }
    }, [onlyStrong])

    useEffect(() => {
        fetchAll()

        // Auto-refresh cada minuto
        const interval = setInterval(fetchAll, 60000)
        return () => clearInterval(interval)
    }, [fetchAll])

    return { signals, stats, loading, refresh: fetchAll }
}
