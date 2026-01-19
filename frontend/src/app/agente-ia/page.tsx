'use client'

import { useState, useEffect } from 'react'
import { Activity, Brain, Target, Sparkles, TrendingUp, Award } from 'lucide-react'

interface LearningProgress {
    experience: {
        level: number
        trades_completed: number
        target_trades: number
        percentage: number
        status: string
    }
    win_rate: {
        current: number
        target: number
        winning_trades: number
        losing_trades: number
        status: string
        color: string
    }
    patterns: {
        learned: number
        target: number
        percentage: number
        list: string[]
        status: string
    }
    confidence: {
        average: number
        target: number
        percentage: number
        status: string
    }
    mastery: {
        level: number
        title: string
        next_level: number
        progress_to_next: number
    }
    evolution: {
        history: Array<{
            timestamp: string
            win_rate: number
            pnl: number
        }>
        trend: string
        recent_winrate: number
    }
    stats: {
        total_pnl: number
        best_trade: number
        worst_trade: number
    }
}

export default function AgentIAPage() {
    const [progress, setProgress] = useState<LearningProgress | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    useEffect(() => {
        fetchProgress()
        const interval = setInterval(fetchProgress, 10000) // Actualizar cada 10s
        return () => clearInterval(interval)
    }, [])

    const fetchProgress = async () => {
        try {
            const token = localStorage.getItem('token')
            if (!token) {
                setError('No estás autenticado')
                setLoading(false)
                return
            }

            const response = await fetch('http://localhost:8000/api/v1/signals/learning-progress', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })

            if (!response.ok) {
                throw new Error('Error al cargar datos')
            }

            const data = await response.json()
            setProgress(data)
            setError('')
        } catch (err) {
            setError('Error al conectar con el servidor')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const getColorClass = (color: string) => {
        switch (color) {
            case 'red': return 'bg-red-500'
            case 'yellow': return 'bg-yellow-500'
            case 'green': return 'bg-green-500'
            default: return 'bg-blue-500'
        }
    }

    const getTrendEmoji = (trend: string) => {
        switch (trend) {
            case 'improving': return '📈'
            case 'declining': return '📉'
            default: return '➡️'
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="mt-4 text-gray-600">Cargando métricas de la IA...</p>
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center text-red-600">
                    <p className="text-xl">{error}</p>
                    <button
                        onClick={fetchProgress}
                        className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                        Reintentar
                    </button>
                </div>
            </div>
        )
    }

    if (!progress) return null

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                        <Brain className="w-10 h-10 text-blue-600" />
                        Evolución del Agente IA
                    </h1>
                    <p className="text-gray-600">Sistema de aprendizaje neuronal en tiempo real</p>
                </div>

                {/* Nivel de Maestría Principal */}
                <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border-2 border-blue-100">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-3xl font-bold text-gray-900">{progress.mastery.title}</h2>
                        <Award className="w-12 h-12 text-yellow-500" />
                    </div>
                    <div className="relative">
                        <div className="h-6 bg-gray-200 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-1000 ease-out rounded-full"
                                style={{ width: `${progress.mastery.level}%` }}
                            >
                                <div className="h-full w-full bg-white/20 animate-pulse"></div>
                            </div>
                        </div>
                        <p className="mt-3 text-sm text-gray-600 text-center">
                            Nivel {progress.mastery.level.toFixed(1)}/100
                            {progress.mastery.level < 100 && ` • Próximo nivel: ${progress.mastery.next_level}`}
                        </p>
                    </div>
                </div>

                {/* Métricas Individuales */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {/* Experiencia */}
                    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                <Activity className="w-5 h-5 text-blue-600" />
                                Experiencia
                            </h3>
                            <span className="text-2xl font-bold text-blue-600">
                                {progress.experience.percentage.toFixed(0)}%
                            </span>
                        </div>
                        <div className="relative">
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-blue-500 transition-all duration-500"
                                    style={{ width: `${progress.experience.percentage}%` }}
                                ></div>
                            </div>
                        </div>
                        <p className="mt-3 text-sm text-gray-600">
                            {progress.experience.trades_completed} / {progress.experience.target_trades} trades completados
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            {progress.experience.status}
                        </span>
                    </div>

                    {/* Win Rate */}
                    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                <Target className="w-5 h-5 text-green-600" />
                                Tasa de Éxito
                            </h3>
                            <span className="text-2xl font-bold text-green-600">
                                {progress.win_rate.current.toFixed(1)}%
                            </span>
                        </div>
                        <div className="relative">
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${getColorClass(progress.win_rate.color)} transition-all duration-500`}
                                    style={{ width: `${progress.win_rate.current}%` }}
                                ></div>
                            </div>
                        </div>
                        <p className="mt-3 text-sm text-gray-600">
                            {progress.win_rate.winning_trades} ganados • {progress.win_rate.losing_trades} perdidos
                        </p>
                        <span className={`inline-block mt-2 px-2 py-1 text-xs rounded-full ${progress.win_rate.color === 'green' ? 'bg-green-100 text-green-800' :
                                progress.win_rate.color === 'yellow' ? 'bg-yellow-100 text-yellow-800' :
                                    'bg-red-100 text-red-800'
                            }`}>
                            {progress.win_rate.status}
                        </span>
                    </div>

                    {/* Patrones Aprendidos */}
                    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                <Sparkles className="w-5 h-5 text-purple-600" />
                                Patrones
                            </h3>
                            <span className="text-2xl font-bold text-purple-600">
                                {progress.patterns.learned}
                            </span>
                        </div>
                        <div className="relative">
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-purple-500 transition-all duration-500"
                                    style={{ width: `${progress.patterns.percentage}%` }}
                                ></div>
                            </div>
                        </div>
                        <p className="mt-3 text-sm text-gray-600">
                            {progress.patterns.learned} / {progress.patterns.target} patrones dominados
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full">
                            {progress.patterns.status}
                        </span>
                    </div>

                    {/* Confianza */}
                    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-orange-600" />
                                Confianza
                            </h3>
                            <span className="text-2xl font-bold text-orange-600">
                                {progress.confidence.average.toFixed(1)}%
                            </span>
                        </div>
                        <div className="relative">
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-orange-500 transition-all duration-500"
                                    style={{ width: `${progress.confidence.percentage}%` }}
                                ></div>
                            </div>
                        </div>
                        <p className="mt-3 text-sm text-gray-600">
                            Meta: {progress.confidence.target}%
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">
                            {progress.confidence.status}
                        </span>
                    </div>

                    {/* Evolución */}
                    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900  flex items-center gap-2">
                                <TrendingUp className="w-5 h-5 text-indigo-600" />
                                Tendencia
                            </h3>
                            <span className="text-2xl">
                                {getTrendEmoji(progress.evolution.trend)}
                            </span>
                        </div>
                        <div className="relative">
                            <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-indigo-500 transition-all duration-500"
                                    style={{ width: `${progress.evolution.recent_winrate}%` }}
                                ></div>
                            </div>
                        </div>
                        <p className="mt-3 text-sm text-gray-600">
                            Win rate reciente: {progress.evolution.recent_winrate.toFixed(1)}%
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded-full capitalize">
                            {progress.evolution.trend}
                        </span>
                    </div>

                    {/* PnL Total */}
                    <div className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-gray-900">PnL Total</h3>
                            <span className={`text-2xl font-bold ${progress.stats.total_pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                ${progress.stats.total_pnl.toFixed(2)}
                            </span>
                        </div>
                        <div className="space-y-2 mt-4">
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Mejor trade:</span>
                                <span className="font-semibold text-green-600">+${progress.stats.best_trade.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Peor trade:</span>
                                <span className="font-semibold text-red-600">${progress.stats.worst_trade.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Patrones Aprendidos - Lista */}
                {progress.patterns.list.length > 0 && (
                    <div className="bg-white rounded-xl shadow-md p-6">
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">Patrones Dominados</h3>
                        <div className="flex flex-wrap gap-2">
                            {progress.patterns.list.map((pattern, index) => (
                                <span
                                    key={index}
                                    className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium"
                                >
                                    {pattern}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Footer */}
                <div className="mt-8 text-center text-sm text-gray-500">
                    Actualizado hace {new Date().toLocaleTimeString()} • Auto-refresh cada 10s
                </div>
            </div>
        </div>
    )
}
