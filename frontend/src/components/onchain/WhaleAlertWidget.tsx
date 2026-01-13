'use client';

import { useState, useEffect } from 'react';
import { Waves, TrendingUp, TrendingDown, ArrowUpCircle, ArrowDownCircle, Users } from 'lucide-react';

interface WhaleAlert {
    id: number;
    blockchain: string;
    amount: number;
    amount_usd: number;
    from_label: string | null;
    to_label: string | null;
    flow_type: string;
    sentiment: string;
    timestamp: string;
}

interface WhaleSummary {
    total_alerts: number;
    total_volume_usd: number;
    exchange_inflows: number;
    exchange_outflows: number;
    whale_to_whale: number;
    bullish_signals: number;
    bearish_signals: number;
}

export default function WhaleAlertWidget({ blockchain = "BTC" }: { blockchain?: string }) {
    const [alerts, setAlerts] = useState<WhaleAlert[]>([]);
    const [summary, setSummary] = useState<WhaleSummary | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchWhaleData();
        const interval = setInterval(fetchWhaleData, 30000); // 30s refresh
        return () => clearInterval(interval);
    }, [blockchain]);

    const fetchWhaleData = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const headers = { 'Authorization': `Bearer ${token}` };

            const [feedRes, summaryRes] = await Promise.all([
                fetch(`/api/v1/onchain/whale-feed?blockchain=${blockchain}&limit=10`, { headers }),
                fetch(`/api/v1/onchain/whale-summary?blockchain=${blockchain}`, { headers })
            ]);

            if (feedRes.ok) setAlerts(await feedRes.json());
            if (summaryRes.ok) setSummary(await summaryRes.json());

        } catch (error) {
            console.error("Error fetching whale data:", error);
        } finally {
            setLoading(false);
        }
    };

    const getFlowIcon = (flowType: string) => {
        if (flowType === "exchange_inflow") return <ArrowDownCircle className="text-rose-400" size={16} />;
        if (flowType === "exchange_outflow") return <ArrowUpCircle className="text-emerald-400" size={16} />;
        return <Users className="text-slate-400" size={16} />;
    };

    const getFlowLabel = (flowType: string) => {
        if (flowType === "exchange_inflow") return "Exchange Inflow";
        if (flowType === "exchange_outflow") return "Exchange Outflow";
        return "Whale → Whale";
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = Math.floor((now.getTime() - date.getTime()) / 1000 / 60); // minutes

        if (diff < 1) return "Ahora";
        if (diff < 60) return `${diff}m`;
        if (diff < 1440) return `${Math.floor(diff / 60)}h`;
        return `${Math.floor(diff / 1440)}d`;
    };

    return (
        <div className="space-y-4">
            {/* Summary Stats */}
            {summary && (
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="glass-card p-3 rounded-xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex items-center gap-2 mb-1">
                            <Waves size={14} className="text-cyan-400" />
                            <span className="text-[10px] text-slate-500 uppercase font-bold">Alerts 24h</span>
                        </div>
                        <p className="text-lg font-bold text-white font-mono">{summary.total_alerts}</p>
                    </div>

                    <div className="glass-card p-3 rounded-xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex items-center gap-2 mb-1">
                            <ArrowDownCircle size={14} className="text-rose-400" />
                            <span className="text-[10px] text-slate-500 uppercase font-bold">Inflows</span>
                        </div>
                        <p className="text-lg font-bold text-rose-400 font-mono">{summary.exchange_inflows}</p>
                    </div>

                    <div className="glass-card p-3 rounded-xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex items-center gap-2 mb-1">
                            <ArrowUpCircle size={14} className="text-emerald-400" />
                            <span className="text-[10px] text-slate-500 uppercase font-bold">Outflows</span>
                        </div>
                        <p className="text-lg font-bold text-emerald-400 font-mono">{summary.exchange_outflows}</p>
                    </div>

                    <div className="glass-card p-3 rounded-xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex items-center gap-2 mb-1">
                            <TrendingUp size={14} className="text-amber-400" />
                            <span className="text-[10px] text-slate-500 uppercase font-bold">Sentiment</span>
                        </div>
                        <p className={`text-lg font-bold font-mono ${summary.bullish_signals > summary.bearish_signals ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {summary.bullish_signals > summary.bearish_signals ? '↑ Bull' : '↓ Bear'}
                        </p>
                    </div>
                </div>
            )}

            {/* Alert Feed */}
            <div className="glass-card p-4 rounded-2xl border border-white/5 bg-black/20 max-h-96 overflow-y-auto">
                <h3 className="text-sm font-bold text-slate-300 mb-3 flex items-center gap-2">
                    <Waves size={16} className="text-cyan-400" /> Live Whale Feed
                </h3>

                {loading ? (
                    <div className="py-8 text-center">
                        <div className="h-6 w-6 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                        <p className="text-xs text-slate-500 mt-2">Escaneando blockchain...</p>
                    </div>
                ) : alerts.length === 0 ? (
                    <p className="text-slate-600 text-center py-8 text-sm">No hay movimientos grandes recientes</p>
                ) : (
                    <div className="space-y-2">
                        {alerts.map(alert => (
                            <div
                                key={alert.id}
                                className={`p-3 rounded-lg border ${alert.sentiment === 'bullish'
                                    ? 'bg-emerald-500/5 border-emerald-500/20'
                                    : alert.sentiment === 'bearish'
                                        ? 'bg-rose-500/5 border-rose-500/20'
                                        : 'bg-white/5 border-white/5'
                                    } hover:bg-white/10 transition-all`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <div className="flex items-center gap-2">
                                        {getFlowIcon(alert.flow_type)}
                                        <span className="text-xs font-bold text-white">${(alert.amount_usd / 1_000_000).toFixed(2)}M</span>
                                    </div>
                                    <span className="text-[10px] text-slate-500 font-mono">{formatTime(alert.timestamp)}</span>
                                </div>

                                <div className="text-[11px] space-y-1">
                                    <div className="flex justify-between text-slate-400">
                                        <span>Tipo:</span>
                                        <span className="text-white font-medium">{getFlowLabel(alert.flow_type)}</span>
                                    </div>
                                    <div className="flex justify-between text-slate-400">
                                        <span>From:</span>
                                        <span className="text-slate-300 truncate max-w-[120px]">{alert.from_label || "Unknown"}</span>
                                    </div>
                                    <div className="flex justify-between text-slate-400">
                                        <span>To:</span>
                                        <span className="text-slate-300 truncate max-w-[120px]">{alert.to_label || "Unknown"}</span>
                                    </div>
                                </div>

                                {alert.sentiment !== 'neutral' && (
                                    <div className="mt-2 pt-2 border-t border-white/5">
                                        <span className={`text-[10px] px-2 py-0.5 rounded uppercase font-bold ${alert.sentiment === 'bullish'
                                                ? 'bg-emerald-500/20 text-emerald-400'
                                                : 'bg-rose-500/20 text-rose-400'
                                            }`}>
                                            {alert.sentiment === 'bullish' ? '↑ Bullish Signal' : '↓ Bearish Signal'}
                                        </span>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
