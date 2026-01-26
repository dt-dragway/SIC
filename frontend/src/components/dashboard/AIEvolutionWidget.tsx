'use client';

import React, { useEffect, useState } from 'react';
import {
    Trophy,
    Star,
    Award,
    Zap,
    TrendingUp,
    Brain,
    ShieldCheck,
    RefreshCcw,
    AlertTriangle
} from 'lucide-react';

interface TradeStats {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    total_pnl: number;
    level: number;
    xp: number;
    next_level_xp: number;
    mastered_patterns: string[];
}

export default function AIEvolutionWidget() {
    const [stats, setStats] = useState<TradeStats | null>(null);
    const [loading, setLoading] = useState(true);
    const [showResetConfirm, setShowResetConfirm] = useState(false);
    const [resetting, setResetting] = useState(false);

    const fetchStats = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const response = await fetch('/api/v1/practice/stats', {
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                setStats(data);
            }
        } catch (error) {
            console.error('Error fetching evolution stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleReset = async () => {
        setResetting(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const response = await fetch('/api/v1/practice/reset', {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });

            if (response.ok) {
                // Recargar página para asegurar limpieza total de estados
                window.location.reload();
            }
        } catch (error) {
            console.error('Error resetting account:', error);
            setResetting(false);
        }
    };

    useEffect(() => {
        fetchStats();
        // Actualizar cada 10s
        const interval = setInterval(fetchStats, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading || !stats) {
        return (
            <div className="h-full w-full rounded-2xl bg-[#0a0a0f] border border-white/5 p-6 animate-pulse flex items-center justify-center">
                <div className="h-8 w-8 rounded-full border-2 border-violet-500 border-t-transparent animate-spin" />
            </div>
        );
    }

    const progressPercent = (stats.xp / stats.next_level_xp) * 100;

    return (
        <div className="relative group overflow-hidden rounded-3xl border border-white/10 bg-[#0a0a0f] shadow-2xl transition-all hover:border-violet-500/30">
            {/* Background Gradients */}
            <div className="absolute top-0 right-0 h-32 w-32 rounded-full bg-violet-600/10 blur-3xl pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 h-32 w-32 rounded-full bg-blue-600/10 blur-3xl pointer-events-none"></div>

            {/* Header */}
            <div className="border-b border-white/5 bg-white/[0.02] p-4 flex items-center justify-between backdrop-blur-md">
                <div className="flex items-center gap-3">
                    <div className="relative flex items-center justify-center h-10 w-10 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 shadow-lg shadow-violet-500/20">
                        <Trophy className="h-5 w-5 text-white" />
                        <div className="absolute -bottom-1 -right-1 bg-black rounded-full p-0.5 border border-white/10">
                            <div className="h-3 w-3 rounded-full bg-emerald-500 animate-pulse"></div>
                        </div>
                    </div>
                    <div>
                        <h3 className="font-bold text-white tracking-tight text-sm">Evolución Agente IA</h3>
                        <p className="text-[10px] text-slate-400 font-mono">
                            Nivel {stats.level} • {stats.xp}/{stats.next_level_xp} XP
                        </p>
                    </div>
                </div>

                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowResetConfirm(true)}
                        className="p-2 rounded-lg hover:bg-white/10 text-slate-500 hover:text-rose-400 transition-colors"
                        title="Resetear Cuenta de Práctica"
                    >
                        <RefreshCcw size={16} />
                    </button>
                    <div className="px-2 py-1 rounded-lg bg-violet-500/10 border border-violet-500/20 text-xs font-bold text-violet-400">
                        Lvl. {stats.level}
                    </div>
                </div>
            </div>

            {/* Main Stats */}
            <div className="p-5 space-y-6">

                {/* XP Progress Bar */}
                <div className="space-y-2">
                    <div className="flex justify-between text-[10px] font-mono text-slate-400 uppercase tracking-wider">
                        <span>Progreso Neuronal</span>
                        <span>{Math.round(progressPercent)}%</span>
                    </div>
                    <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-violet-500 to-fuchsia-500 rounded-full transition-all duration-1000 ease-out relative"
                            style={{ width: `${progressPercent}%` }}
                        >
                            <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                        </div>
                    </div>
                </div>

                {/* KPI Grid */}
                <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
                        <div className="flex items-center gap-2 text-slate-400 text-[10px] uppercase font-bold">
                            <Target size={12} className="text-emerald-400" />
                            Win Rate
                        </div>
                        <div className="text-xl font-bold text-white tracking-tight">
                            {stats.win_rate}%
                        </div>
                        <div className="text-[10px] text-slate-500">
                            {stats.winning_trades}W - {stats.losing_trades}L
                        </div>
                    </div>

                    <div className="p-3 rounded-xl bg-white/5 border border-white/5 space-y-1">
                        <div className="flex items-center gap-2 text-slate-400 text-[10px] uppercase font-bold">
                            <TrendingUp size={12} className={stats.total_pnl >= 0 ? "text-emerald-400" : "text-rose-400"} />
                            PnL Total
                        </div>
                        <div className={`text-xl font-bold tracking-tight ${stats.total_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                            {stats.total_pnl >= 0 ? '+' : ''}${stats.total_pnl.toLocaleString()}
                        </div>
                        <div className="text-[10px] text-slate-500">
                            {stats.total_trades} Trades
                        </div>
                    </div>
                </div>

                {/* Mastered Patterns */}
                <div className="space-y-3">
                    <h4 className="text-[10px] font-mono text-slate-500 uppercase tracking-wider flex items-center gap-2">
                        <Brain size={12} />
                        Patrones Dominados
                    </h4>

                    <div className="flex flex-wrap gap-2">
                        {stats.mastered_patterns && stats.mastered_patterns.length > 0 ? (
                            stats.mastered_patterns.map((pattern, i) => (
                                <span key={i} className="flex items-center gap-1 px-2 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-[10px] text-emerald-400 font-medium">
                                    <ShieldCheck size={10} />
                                    {pattern}
                                </span>
                            ))
                        ) : (
                            <span className="text-[10px] text-slate-600 italic px-2">
                                Realiza más trades ganadores para desbloquear patrones...
                            </span>
                        )}
                    </div>
                </div>
            </div>

            {/* Reset Confirmation Modal Overlay */}
            {showResetConfirm && (
                <div className="absolute inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6">
                    <div className="bg-[#0a0a0f] border border-rose-500/30 rounded-2xl p-6 max-w-sm w-full shadow-2xl shadow-rose-900/20 space-y-4">
                        <div className="flex items-center gap-3 text-rose-500">
                            <AlertTriangle size={24} />
                            <h3 className="font-bold text-lg">¿Resetear Cuenta?</h3>
                        </div>
                        <p className="text-sm text-slate-300 leading-relaxed">
                            Esto borrará todo tu historial de práctica, nivel, XP y devolverá tu balance a $100.
                            <br /><br />
                            <strong className="text-white">Esta acción no se puede deshacer.</strong>
                        </p>
                        <div className="flex gap-3 pt-2">
                            <button
                                onClick={() => setShowResetConfirm(false)}
                                className="flex-1 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-white font-medium transition-colors"
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleReset}
                                disabled={resetting}
                                className="flex-1 px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-700 text-white font-bold transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                            >
                                {resetting ? (
                                    <>
                                        <div className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Reset...
                                    </>
                                ) : (
                                    'Confirmar Reset'
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

// Icon helper
function Target({ size, className }: { size: number, className?: string }) {
    return (
        <svg
            xmlns="http://www.w3.org/2000/svg"
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className={className}
        >
            <circle cx="12" cy="12" r="10" />
            <circle cx="12" cy="12" r="6" />
            <circle cx="12" cy="12" r="2" />
        </svg>
    )
}
