'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useWallet } from '@/context/WalletContext';
import {
    History,
    TrendingUp,
    Clock,
    CheckCircle2,
    ArrowUpRight,
    ArrowDownRight,
    ArrowRightLeft,
    Users
} from 'lucide-react';

interface Trade {
    id: string | number;
    symbol: string; // Or asset for P2P
    side: 'BUY' | 'SELL';
    quantity: number; // crypto amount
    price: number;
    total?: number; // fiat amount
    pnl?: number;
    timestamp: string;
    status?: string | number;
    type?: string;
    advertiser?: string; // P2P specific
    fiat?: string; // P2P specific
}

interface Stats {
    total_trades: number;
    win_rate: number;
    total_pnl: number;
    volume: number;
}


export default function HistoryPage() {
    const { mode } = useWallet();
    const [activeTab, setActiveTab] = useState<'TRADING' | 'P2P'>('TRADING');
    const [trades, setTrades] = useState<Trade[]>([]);
    const [stats, setStats] = useState<Stats>({ total_trades: 0, win_rate: 0, total_pnl: 0, volume: 0 });
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL');

    useEffect(() => {
        fetchHistory();
    }, [mode, activeTab]);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const headers = { 'Authorization': `Bearer ${token}` };

            if (activeTab === 'TRADING') {
                if (mode === 'practice') {
                    // Practice Data
                    const [tradesRes, statsRes] = await Promise.all([
                        fetch('/api/v1/practice/trades', { headers }),
                        fetch('/api/v1/practice/stats', { headers })
                    ]);

                    if (tradesRes.ok && statsRes.ok) {
                        const tradesData = await tradesRes.json();
                        const statsData = await statsRes.json();
                        setTrades(tradesData);
                        setStats({
                            total_trades: statsData.total_trades,
                            win_rate: statsData.win_rate,
                            total_pnl: statsData.total_pnl,
                            volume: tradesData.reduce((acc: number, t: any) => acc + (t.total || 0), 0)
                        });
                    }
                } else {
                    // Real Spot Data
                    const res = await fetch('/api/v1/trading/orders?limit=50', { headers });
                    if (res.ok) {
                        const data = await res.json();
                        const adaptedTrades = data.orders.map((o: any) => ({
                            id: o.orderId,
                            symbol: o.symbol,
                            side: o.side,
                            quantity: parseFloat(o.origQty),
                            price: parseFloat(o.price || o.cummulativeQuoteQty / o.executedQty || 0),
                            total: parseFloat(o.cummulativeQuoteQty),
                            timestamp: new Date(o.time).toISOString(),
                            status: o.status,
                            type: o.type
                        }));
                        setTrades(adaptedTrades);
                        setStats({
                            total_trades: adaptedTrades.length,
                            win_rate: 0,
                            total_pnl: 0,
                            volume: adaptedTrades.reduce((acc: number, t: any) => acc + (t.total || 0), 0)
                        });
                    }
                }
            } else {
                // P2P Data (Always Real)
                const res = await fetch('/api/v1/p2p/history', { headers });
                if (res.ok) {
                    const data = await res.json();
                    const adaptedTrades = data.trades.map((t: any) => ({
                        id: t.orderNumber,
                        symbol: t.asset, // Use asset as symbol
                        side: t.type,
                        quantity: t.amount,
                        price: t.price,
                        total: t.fiat_amount,
                        fiat: t.fiat,
                        timestamp: t.timestamp,
                        status: t.status,
                        advertiser: t.advertiser
                    }));
                    setTrades(adaptedTrades);
                    setStats({
                        total_trades: adaptedTrades.length,
                        win_rate: 0,
                        total_pnl: 0,
                        volume: adaptedTrades.reduce((acc: number, t: any) => acc + (t.total || 0), 0)
                    });
                }
            }
        } catch (error) {
            console.error("Error fetching history:", error);
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleString('es-ES', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };

    const filteredTrades = trades.filter(t => filter === 'ALL' || t.side === filter);

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header & Tabs */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-200 to-yellow-500 bg-clip-text text-transparent flex items-center gap-3">
                            <History className="text-amber-400" size={32} />
                            Historial Global
                        </h1>
                        <div className="flex items-center gap-2 mt-2">
                            <button
                                onClick={() => setActiveTab('TRADING')}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${activeTab === 'TRADING' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/50' : 'text-slate-500 hover:bg-white/5'}`}
                            >
                                <TrendingUp size={14} /> Trading Spot
                            </button>
                            <button
                                onClick={() => setActiveTab('P2P')}
                                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-2 ${activeTab === 'P2P' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'text-slate-500 hover:bg-white/5'}`}
                            >
                                <Users size={14} /> Mercado P2P
                            </button>
                        </div>
                    </div>

                    <div className="flex gap-2">
                        {['ALL', 'BUY', 'SELL'].map(f => (
                            <button
                                key={f}
                                onClick={() => setFilter(f)}
                                className={`px-4 py-2 rounded-lg text-xs font-bold transition-all border ${filter === f
                                    ? 'bg-white/10 text-white border-white/20'
                                    : 'bg-transparent text-slate-500 border-transparent hover:bg-white/5'}`}
                            >
                                {f === 'ALL' ? 'Todos' : f === 'BUY' ? 'Compras' : 'Ventas'}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                                <ArrowRightLeft size={18} />
                            </div>
                            <span className="text-xs font-bold text-slate-500 uppercase">Volumen Movido</span>
                        </div>
                        <p className="text-2xl font-mono text-white font-bold">
                            ${stats.volume.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                        </p>
                    </div>

                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-violet-500/10 text-violet-400">
                                <Clock size={18} />
                            </div>
                            <span className="text-xs font-bold text-slate-500 uppercase">Operaciones</span>
                        </div>
                        <p className="text-2xl font-mono text-white font-bold">{stats.total_trades}</p>
                    </div>

                    {/* Conditional Stat */}
                    {activeTab === 'TRADING' && mode === 'practice' && (
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                            <div className="flex items-center gap-3 mb-2">
                                <div className={`p-2 rounded-lg ${stats.total_pnl >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                    {stats.total_pnl >= 0 ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                                </div>
                                <span className="text-xs font-bold text-slate-500 uppercase">PNL Acumulado</span>
                            </div>
                            <p className={`text-2xl font-mono font-bold ${stats.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {stats.total_pnl >= 0 ? '+' : ''}{stats.total_pnl.toFixed(2)} USD
                            </p>
                        </div>
                    )}
                </div>

                {/* Trades Table */}
                <div className="glass-card overflow-hidden rounded-3xl border border-white/5 bg-gradient-to-b from-black/20 to-transparent">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-white/[0.02] border-b border-white/5">
                                <tr>
                                    <th className="text-left py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Fecha</th>
                                    <th className="text-left py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                                        {activeTab === 'TRADING' ? 'Par' : 'Activo'}
                                    </th>
                                    <th className="text-left py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Tipo</th>
                                    <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Precio</th>
                                    <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Cantidad</th>
                                    <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Total</th>
                                    {activeTab === 'P2P' && <th className="text-right py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Contraparte</th>}
                                    <th className="text-center py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Estado</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {loading ? (
                                    <tr>
                                        <td colSpan={activeTab === 'P2P' ? 8 : 7} className="py-20 text-center">
                                            <div className="flex flex-col items-center gap-4">
                                                <div className="h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                                                <span className="text-slate-500 font-mono text-xs">Sincronizando con Blockchain...</span>
                                            </div>
                                        </td>
                                    </tr>
                                ) : filteredTrades.length === 0 ? (
                                    <tr>
                                        <td colSpan={activeTab === 'P2P' ? 8 : 7} className="py-20 text-center text-slate-600">
                                            <div className="flex flex-col items-center gap-4">
                                                <History size={48} className="opacity-20" />
                                                <p>No se encontraron registros en {activeTab}</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : (
                                    filteredTrades.map((trade, i) => (
                                        <tr key={i} className="group hover:bg-white/[0.03] transition-colors">
                                            <td className="py-4 px-6 text-xs text-slate-400 font-mono">
                                                {formatDate(trade.timestamp)}
                                            </td>
                                            <td className="py-4 px-6">
                                                <span className="font-bold text-white text-sm">{trade.symbol}</span>
                                            </td>
                                            <td className="py-4 px-6">
                                                <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${trade.side === 'BUY'
                                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                                    }`}>
                                                    {trade.side === 'BUY' ? 'Compra' : 'Venta'}
                                                </span>
                                            </td>
                                            <td className="py-4 px-6 text-right font-mono text-sm text-slate-300">
                                                {trade.price.toLocaleString()} {activeTab === 'P2P' ? (trade.fiat || 'VES') : 'USDT'}
                                            </td>
                                            <td className="py-4 px-6 text-right font-mono text-sm text-slate-300">
                                                {trade.quantity}
                                            </td>
                                            <td className="py-4 px-6 text-right font-mono text-sm text-slate-300">
                                                {trade.total ? trade.total.toLocaleString() : (trade.price * trade.quantity).toLocaleString()} {activeTab === 'P2P' ? (trade.fiat || 'VES') : 'USDT'}
                                            </td>
                                            {activeTab === 'P2P' && (
                                                <td className="py-4 px-6 text-right font-mono text-xs text-cyan-400">
                                                    {trade.advertiser || 'Anon'}
                                                </td>
                                            )}
                                            <td className="py-4 px-6 text-center">
                                                {(!trade.status || trade.status === 'FILLED' || trade.status === 4) ? (
                                                    <CheckCircle2 size={16} className="text-emerald-500 mx-auto" />
                                                ) : (
                                                    <span className="text-[10px] text-amber-500 uppercase">{trade.status}</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
