'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Activity, Brain, Target, Sparkles, TrendingUp, Award, AlertCircle } from 'lucide-react';

interface LearningProgress {
    experience: {
        level: number;
        trades_completed: number;
        target_trades: number;
        percentage: number;
        status: string;
    };
    win_rate: {
        current: number;
        target: number;
        winning_trades: number;
        losing_trades: number;
        status: string;
        color: string;
    };
    patterns: {
        learned: number;
        target: number;
        percentage: number;
        list: string[];
        status: string;
    };
    confidence: {
        average: number;
        target: number;
        percentage: number;
        status: string;
    };
    mastery: {
        level: number;
        title: string;
        next_level: number;
        progress_to_next: number;
    };
    evolution: {
        history: Array<{
            timestamp: string;
            win_rate: number;
            pnl: number;
        }>;
        trend: string;
        recent_winrate: number;
    };
    stats: {
        total_pnl: number;
        best_trade: number;
        worst_trade: number;
    };
}

export default function AgentIAPage() {
    const [progress, setProgress] = useState<LearningProgress | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchProgress();
        const interval = setInterval(fetchProgress, 10000); // Actualizar cada 10s
        return () => clearInterval(interval);
    }, []);

    const fetchProgress = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) {
                setError('No estás autenticado');
                setLoading(false);
                return;
            }

            const response = await fetch('/api/v1/signals/learning-progress', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error('Error al cargar datos');
            }

            const data = await response.json();
            setProgress(data);
            setError('');
        } catch (err) {
            setError('Error al conectar con el servidor');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const getColorClass = (color: string) => {
        switch (color) {
            case 'red': return 'bg-rose-500';
            case 'yellow': return 'bg-amber-500';
            case 'green': return 'bg-emerald-500';
            default: return 'bg-blue-500';
        }
    };

    const getTrendEmoji = (trend: string) => {
        switch (trend) {
            case 'improving': return '📈';
            case 'declining': return '📉';
            default: return '➡️';
        }
    };

    if (loading) {
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center">
                        <div className="h-16 w-16 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                        <p className="mt-4 text-slate-400">Cargando métricas de la IA...</p>
                    </div>
                </div>
            </DashboardLayout>
        );
    }

    if (error) {
        return (
            <DashboardLayout>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <div className="text-center">
                        <AlertCircle className="w-16 h-16 text-rose-400 mx-auto mb-4" />
                        <p className="text-xl text-rose-400 mb-4">{error}</p>
                        <button
                            onClick={fetchProgress}
                            className="px-6 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white rounded-lg font-bold hover:opacity-90 transition-all"
                        >
                            Reintentar
                        </button>
                    </div>
                </div>
            </DashboardLayout>
        );
    }

    if (!progress) return null;

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-purple-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Brain className="text-violet-400" size={32} />
                        Evolución del Agente IA
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Sistema de aprendizaje neuronal en tiempo real
                    </p>
                </div>

                {/* Nivel de Maestría Principal */}
                <div className="glass-card rounded-3xl border border-white/5 bg-gradient-to-br from-violet-500/10 to-purple-500/5 p-8">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-3xl font-bold text-white">{progress.mastery.title}</h2>
                        <Award className="w-12 h-12 text-amber-400" />
                    </div>
                    <div className="relative">
                        <div className="h-6 bg-black/30 rounded-full overflow-hidden border border-white/10">
                            <div
                                className="h-full bg-gradient-to-r from-violet-500 to-purple-600 transition-all duration-1000 ease-out rounded-full relative overflow-hidden"
                                style={{ width: `${progress.mastery.level}%` }}
                            >
                                <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                            </div>
                        </div>
                        <p className="mt-3 text-sm text-slate-400 text-center">
                            Nivel {progress.mastery.level.toFixed(1)}/100
                            {progress.mastery.level < 100 && ` • Próximo nivel: ${progress.mastery.next_level}`}
                        </p>
                    </div>
                </div>

                {/* Métricas Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {/* Experiencia */}
                    <div className="glass-card rounded-2xl border border-white/5 bg-black/20 p-6 hover:bg-white/5 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2 uppercase">
                                <Activity className="w-4 h-4 text-blue-400" />
                                Experiencia
                            </h3>
                            <span className="text-2xl font-bold text-blue-400">
                                {progress.experience.percentage.toFixed(0)}%
                            </span>
                        </div>
                        <div className="relative h-2 bg-black/30 rounded-full overflow-hidden border border-white/10">
                            <div
                                className="h-full bg-blue-500 transition-all duration-500"
                                style={{ width: `${progress.experience.percentage}%` }}
                            ></div>
                        </div>
                        <p className="mt-3 text-xs text-slate-500">
                            {progress.experience.trades_completed} / {progress.experience.target_trades} trades
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-blue-500/20 text-blue-400 text-[10px] rounded-full font-bold uppercase">
                            {progress.experience.status}
                        </span>
                    </div>

                    {/* Win Rate */}
                    <div className="glass-card rounded-2xl border border-white/5 bg-black/20 p-6 hover:bg-white/5 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2 uppercase">
                                <Target className="w-4 h-4 text-emerald-400" />
                                Tasa de Éxito
                            </h3>
                            <span className="text-2xl font-bold text-emerald-400">
                                {progress.win_rate.current.toFixed(1)}%
                            </span>
                        </div>
                        <div className="relative h-2 bg-black/30 rounded-full overflow-hidden border border-white/10">
                            <div
                                className={`h-full ${getColorClass(progress.win_rate.color)} transition-all duration-500`}
                                style={{ width: `${progress.win_rate.current}%` }}
                            ></div>
                        </div>
                        <p className="mt-3 text-xs text-slate-500">
                            {progress.win_rate.winning_trades} ganados • {progress.win_rate.losing_trades} perdidos
                        </p>
                        <span className={`inline-block mt-2 px-2 py-1 text-[10px] rounded-full font-bold uppercase ${progress.win_rate.color === 'green' ? 'bg-emerald-500/20 text-emerald-400' :
                                progress.win_rate.color === 'yellow' ? 'bg-amber-500/20 text-amber-400' :
                                    'bg-rose-500/20 text-rose-400'
                            }`}>
                            {progress.win_rate.status}
                        </span>
                    </div>

                    {/* Patrones */}
                    <div className="glass-card rounded-2xl border border-white/5 bg-black/20 p-6 hover:bg-white/5 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2 uppercase">
                                <Sparkles className="w-4 h-4 text-purple-400" />
                                Patrones
                            </h3>
                            <span className="text-2xl font-bold text-purple-400">
                                {progress.patterns.learned}
                            </span>
                        </div>
                        <div className="relative h-2 bg-black/30 rounded-full overflow-hidden border border-white/10">
                            <div
                                className="h-full bg-purple-500 transition-all duration-500"
                                style={{ width: `${progress.patterns.percentage}%` }}
                            ></div>
                        </div>
                        <p className="mt-3 text-xs text-slate-500">
                            {progress.patterns.learned} / {progress.patterns.target} dominados
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-purple-500/20 text-purple-400 text-[10px] rounded-full font-bold uppercase">
                            {progress.patterns.status}
                        </span>
                    </div>

                    {/* Confianza */}
                    <div className="glass-card rounded-2xl border border-white/5 bg-black/20 p-6 hover:bg-white/5 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2 uppercase">
                                <TrendingUp className="w-4 h-4 text-orange-400" />
                                Confianza
                            </h3>
                            <span className="text-2xl font-bold text-orange-400">
                                {progress.confidence.average.toFixed(1)}%
                            </span>
                        </div>
                        <div className="relative h-2 bg-black/30 rounded-full overflow-hidden border border-white/10">
                            <div
                                className="h-full bg-orange-500 transition-all duration-500"
                                style={{ width: `${progress.confidence.percentage}%` }}
                            ></div>
                        </div>
                        <p className="mt-3 text-xs text-slate-500">
                            Meta: {progress.confidence.target}%
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-orange-500/20 text-orange-400 text-[10px] rounded-full font-bold uppercase">
                            {progress.confidence.status}
                        </span>
                    </div>

                    {/* Tendencia */}
                    <div className="glass-card rounded-2xl border border-white/5 bg-black/20 p-6 hover:bg-white/5 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-slate-300 flex items-center gap-2 uppercase">
                                <TrendingUp className="w-4 h-4 text-cyan-400" />
                                Tendencia
                            </h3>
                            <span className="text-2xl">
                                {getTrendEmoji(progress.evolution.trend)}
                            </span>
                        </div>
                        <div className="relative h-2 bg-black/30 rounded-full overflow-hidden border border-white/10">
                            <div
                                className="h-full bg-cyan-500 transition-all duration-500"
                                style={{ width: `${progress.evolution.recent_winrate}%` }}
                            ></div>
                        </div>
                        <p className="mt-3 text-xs text-slate-500">
                            Win rate reciente: {progress.evolution.recent_winrate.toFixed(1)}%
                        </p>
                        <span className="inline-block mt-2 px-2 py-1 bg-cyan-500/20 text-cyan-400 text-[10px] rounded-full font-bold uppercase">
                            {progress.evolution.trend}
                        </span>
                    </div>

                    {/* PnL Total */}
                    <div className="glass-card rounded-2xl border border-white/5 bg-black/20 p-6 hover:bg-white/5 transition-all">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-bold text-slate-300 uppercase">PnL Total</h3>
                            <span className={`text-2xl font-bold ${progress.stats.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                ${progress.stats.total_pnl.toFixed(2)}
                            </span>
                        </div>
                        <div className="space-y-2 mt-4">
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-500">Mejor:</span>
                                <span className="font-bold text-emerald-400">+${progress.stats.best_trade.toFixed(2)}</span>
                            </div>
                            <div className="flex justify-between text-xs">
                                <span className="text-slate-500">Peor:</span>
                                <span className="font-bold text-rose-400">${progress.stats.worst_trade.toFixed(2)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Patrones Aprendidos */}
                {progress.patterns.list.length > 0 && (
                    <div className="glass-card rounded-3xl border border-white/5 bg-black/20 p-6">
                        <h3 className="text-lg font-bold text-white mb-4">Patrones Dominados</h3>
                        <div className="flex flex-wrap gap-2">
                            {progress.patterns.list.map((pattern, index) => (
                                <span
                                    key={index}
                                    className="px-3 py-1.5 bg-purple-500/20 text-purple-300 rounded-full text-xs font-medium border border-purple-500/30"
                                >
                                    {pattern}
                                </span>
                            ))}
                        </div>
                    </div>
                )}

                {/* Footer */}
                <div className="text-center text-xs text-slate-600">
                    Actualizado: {new Date().toLocaleTimeString()} • Auto-refresh cada 10s
                </div>
            </div>
        </DashboardLayout>
    );
}
