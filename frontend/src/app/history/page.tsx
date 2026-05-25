'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { useWallet } from '@/context/WalletContext';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import {
    History,
    TrendingUp,
    Clock,
    CheckCircle2,
    ArrowUpRight,
    ArrowDownRight,
    ArrowRightLeft,
    Users,
    Brain,
    User,
    ChevronLeft,
    ChevronRight
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
    strategy?: string;
    market_type?: string;
}

interface Stats {
    total_trades: number;
    win_rate: number;
    total_pnl: number;
    volume: number;
}


export default function HistoryPage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const { mode } = useWallet();
    const [activeTab, setActiveTab] = useState<'TRADING' | 'P2P'>('TRADING');
    const [trades, setTrades] = useState<Trade[]>([]);
    const [stats, setStats] = useState<Stats>({ total_trades: 0, win_rate: 0, total_pnl: 0, volume: 0 });
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('ALL');
    const [timeRange, setTimeRange] = useState('ALL'); // Nuevo sistema de rango: ALL, 24H, 7D, 30D

    // Estado de Paginación Premium
    const [currentPage, setCurrentPage] = useState(1);
    const itemsPerPage = 15;

    useEffect(() => {
        if (isAuthenticated) {
            fetchHistory();
        }
    }, [mode, activeTab, isAuthenticated]);

    useEffect(() => {
        setCurrentPage(1);
    }, [filter, activeTab, timeRange]);

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const headers = { 'Authorization': `Bearer ${token}` };

            if (activeTab === 'TRADING') {
                const endpoint = mode === 'practice' ? '/api/v1/practice/trades' : '/api/v1/trading/orders?limit=100';
                const res = await fetch(endpoint, { headers });
                
                if (res.ok) {
                    const data = await res.json();
                    let adaptedTrades = [];
                    
                    if (mode === 'practice') {
                        adaptedTrades = data;
                    } else {
                        adaptedTrades = (data.orders || []).map((o: any) => ({
                            id: o.orderId,
                            symbol: o.symbol,
                            side: o.side,
                            quantity: parseFloat(o.origQty),
                            price: parseFloat(o.price || o.cummulativeQuoteQty / o.executedQty || 0),
                            total: parseFloat(o.cummulativeQuoteQty),
                            timestamp: new Date(o.time).toISOString(),
                            status: o.status,
                            type: o.type,
                            strategy: o.strategy || 'MANUAL'
                        }));
                    }
                    
                    setTrades(adaptedTrades);
                    
                    // Fetch Stats for practice
                    if (mode === 'practice') {
                        const statsRes = await fetch('/api/v1/practice/stats', { headers });
                        if (statsRes.ok) {
                            const statsData = await statsRes.json();
                            setStats({
                                total_trades: statsData.total_trades,
                                win_rate: statsData.win_rate,
                                total_pnl: statsData.total_pnl,
                                volume: adaptedTrades.reduce((acc: number, t: any) => acc + (t.total || 0), 0)
                            });
                        }
                    } else {
                        setStats({
                            total_trades: adaptedTrades.length,
                            win_rate: 0,
                            total_pnl: 0,
                            volume: adaptedTrades.reduce((acc: number, t: any) => acc + (t.total || 0), 0)
                        });
                    }
                }
            } else {
                // P2P Data
                const res = await fetch('/api/v1/p2p/history', { headers });
                if (res.ok) {
                    const data = await res.json();
                    const adaptedTrades = (data.trades || []).map((t: any) => ({
                        id: t.orderNumber,
                        symbol: t.asset,
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
                        volume: adaptedTrades.reduce((acc: number, t: any) => acc + (t.quantity || 0), 0)
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
        try {
            return new Date(dateString).toLocaleString('es-ES', {
                month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });
        } catch (e) {
            return 'Fecha inválida';
        }
    };

    // Lógica de filtrado mejorada
    const filteredTrades = trades.filter(t => {
        const tradeDate = new Date(t.timestamp).getTime();
        const now = new Date().getTime();
        
        // Filtro de tipo (BUY/SELL)
        const matchSide = filter === 'ALL' || t.side === filter;
        
        // Filtro de rango de tiempo
        let matchTime = true;
        if (timeRange === '24H') {
            matchTime = (now - tradeDate) <= (24 * 60 * 60 * 1000);
        } else if (timeRange === '7D') {
            matchTime = (now - tradeDate) <= (7 * 24 * 60 * 60 * 1000);
        } else if (timeRange === '30D') {
            matchTime = (now - tradeDate) <= (30 * 24 * 60 * 60 * 1000);
        }
        
        return matchSide && matchTime;
    });

    // Calcular elementos paginados
    const totalPages = Math.ceil(filteredTrades.length / itemsPerPage);
    const paginatedTrades = filteredTrades.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage);

    // Calcular estadísticas dinámicas en base al historial filtrado actual
    const displayVolume = filteredTrades.reduce((acc: number, t: any) => {
        if (activeTab === 'TRADING') {
            return acc + (t.total || 0);
        } else {
            // Para P2P sumamos la cantidad de USDT (dólares reales) para consistencia en $
            return acc + (t.quantity || 0);
        }
    }, 0);

    const displayTotalTrades = filteredTrades.length;

    // Calcular PNL acumulado dinámicamente si aplica
    const displayPnL = filteredTrades.reduce((acc: number, t: any) => acc + (t.pnl || 0), 0);

    if (authLoading || !isAuthenticated) return <LoadingSpinner />;

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

                    <div className="flex flex-wrap items-center gap-4">
                        {/* Selector de Tipo (ALL, BUY, SELL) */}
                        <div className="flex gap-2 bg-white/[0.02] border border-white/5 p-1 rounded-xl">
                            {['ALL', 'BUY', 'SELL'].map(f => (
                                <button
                                    key={f}
                                    onClick={() => setFilter(f)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${filter === f
                                        ? 'bg-white/10 text-white border-white/20'
                                        : 'bg-transparent text-slate-500 border-transparent hover:bg-white/5'}`}
                                >
                                    {f === 'ALL' ? 'Todos' : f === 'BUY' ? 'Compras' : 'Ventas'}
                                </button>
                            ))}
                        </div>

                        {/* Selector de Rango de Tiempo (Nuevo Sistema) */}
                        <div className="flex items-center gap-2 bg-white/[0.02] border border-white/5 p-1 rounded-xl">
                            {[
                                { val: 'ALL', label: 'Todo' },
                                { val: '24H', label: 'Últimas 24h' },
                                { val: '7D', label: '7 Días' },
                                { val: '30D', label: '30 Días' }
                            ].map(r => (
                                <button
                                    key={r.val}
                                    onClick={() => setTimeRange(r.val)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${timeRange === r.val
                                        ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                                        : 'bg-transparent text-slate-500 border-transparent hover:bg-white/5'}`}
                                >
                                    {r.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {activeTab === 'P2P' && mode === 'practice' && (
                    <div className="glass-card p-5 rounded-3xl border border-amber-500/20 bg-gradient-to-r from-amber-500/5 to-transparent flex items-start gap-4 text-amber-300/80 text-xs leading-relaxed max-w-4xl animate-in fade-in duration-300">
                        <Users size={18} className="text-amber-400 shrink-0 mt-0.5" />
                        <div>
                            <span className="font-bold text-white block mb-1 text-sm">Historial de Consulta Informativa (P2P Binance Real)</span>
                            Estás operando en **Modo Práctica (Simulador)**, pero la pestaña de Mercado P2P muestra en tiempo real tu historial real de transacciones C2C de Binance con fines de visualización y consulta. Las operaciones de práctica del robot de trading IA o el Sentinel CIO están completamente aisladas de esta vista.
                        </div>
                    </div>
                )}

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
                            ${displayVolume.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                        </p>
                    </div>

                    <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                        <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 rounded-lg bg-violet-500/10 text-violet-400">
                                <Clock size={18} />
                            </div>
                            <span className="text-xs font-bold text-slate-500 uppercase">Operaciones</span>
                        </div>
                        <p className="text-2xl font-mono text-white font-bold">{displayTotalTrades}</p>
                    </div>

                    {/* Conditional Stat */}
                    {activeTab === 'TRADING' && mode === 'practice' && (
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-white/[0.02] to-transparent">
                            <div className="flex items-center gap-3 mb-2">
                                <div className={`p-2 rounded-lg ${displayPnL >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                    {displayPnL >= 0 ? <ArrowUpRight size={18} /> : <ArrowDownRight size={18} />}
                                </div>
                                <span className="text-xs font-bold text-slate-500 uppercase">PNL Acumulado</span>
                            </div>
                            <p className={`text-2xl font-mono font-bold ${displayPnL >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {displayPnL >= 0 ? '+' : ''}{displayPnL.toFixed(2)} USD
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
                                    <th className="text-left py-5 px-6 text-[10px] font-bold text-slate-500 uppercase tracking-widest">Ejecución</th>
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
                                        <td colSpan={activeTab === 'P2P' ? 9 : 8} className="py-20 text-center">
                                            <div className="flex flex-col items-center gap-4">
                                                <div className="h-8 w-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
                                                <span className="text-slate-500 font-mono text-xs">Sincronizando con Blockchain...</span>
                                            </div>
                                        </td>
                                    </tr>
                                ) : filteredTrades.length === 0 ? (
                                    <tr>
                                        <td colSpan={activeTab === 'P2P' ? 9 : 8} className="py-20 text-center text-slate-600">
                                            <div className="flex flex-col items-center gap-4">
                                                <History size={48} className="opacity-20" />
                                                <p>No se encontraron registros en {activeTab}</p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : (
                                    paginatedTrades.map((trade, i) => (
                                        <tr key={i} className="group hover:bg-white/[0.03] transition-colors">
                                            <td className="py-4 px-6 text-xs text-slate-400 font-mono">
                                                {formatDate(trade.timestamp)}
                                            </td>
                                            <td className="py-4 px-6">
                                                <div className="flex items-center gap-2">
                                                    <span className="font-bold text-white text-sm">{trade.symbol}</span>
                                                    {activeTab === 'TRADING' && (
                                                        <span className={`px-1.5 py-0.5 rounded text-[8px] font-bold tracking-wider uppercase ${
                                                            trade.market_type === 'FUTURES'
                                                                ? 'bg-violet-500/15 text-violet-400 border border-violet-500/25'
                                                                : 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/25'
                                                        }`}>
                                                            {trade.market_type === 'FUTURES' ? 'FUTUROS' : 'SPOT'}
                                                        </span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="py-4 px-6">
                                                <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider ${trade.side === 'BUY'
                                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                                    : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                                    }`}>
                                                    {trade.side === 'BUY' ? 'Compra' : 'Venta'}
                                                </span>
                                            </td>
                                            <td className="py-4 px-6">
                                                {activeTab === 'P2P' ? (
                                                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider bg-violet-500/10 text-violet-400 border border-violet-500/20">
                                                        <Users size={12} /> P2P Escaneado
                                                    </span>
                                                ) : (trade.strategy === 'AI_SIGNAL' || trade.strategy === 'AI_AUTO' || trade.strategy === 'AI' || trade.strategy === 'SENTINEL_CIO') ? (
                                                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse">
                                                        <Brain size={12} /> Cerebro IA (Auto)
                                                    </span>
                                                ) : (
                                                    <span className="inline-flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-500/10 text-slate-400 border border-slate-500/20">
                                                        <User size={12} /> Manual (Usuario)
                                                    </span>
                                                )}
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
                    
                    {/* Paginación Premium */}
                    {totalPages > 1 && (
                        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 px-6 py-4 border-t border-white/5 bg-white/[0.01]">
                            <div className="text-xs text-slate-500 font-mono">
                                Mostrando <span className="text-slate-300 font-bold">{Math.min(filteredTrades.length, (currentPage - 1) * itemsPerPage + 1)}–{Math.min(filteredTrades.length, currentPage * itemsPerPage)}</span> de <span className="text-white font-bold">{filteredTrades.length}</span> operaciones
                            </div>
                            
                            <div className="flex items-center gap-1">
                                <button
                                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                    disabled={currentPage === 1}
                                    className="p-2 rounded-lg bg-white/5 border border-white/5 text-slate-400 hover:text-white hover:bg-white/10 disabled:opacity-40 disabled:hover:text-slate-400 disabled:hover:bg-white/5 transition-all"
                                >
                                    <ChevronLeft size={16} />
                                </button>
                                
                                {Array.from({ length: totalPages }, (_, idx) => {
                                    const pageNum = idx + 1;
                                    if (totalPages > 5 && Math.abs(currentPage - pageNum) > 1 && pageNum !== 1 && pageNum !== totalPages) {
                                        if (pageNum === 2 || pageNum === totalPages - 1) {
                                            return <span key={pageNum} className="px-2 text-slate-600 font-mono">...</span>;
                                        }
                                        return null;
                                    }
                                    return (
                                        <button
                                            key={pageNum}
                                            onClick={() => setCurrentPage(pageNum)}
                                            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all border ${
                                                currentPage === pageNum
                                                    ? 'bg-amber-500/25 text-amber-400 border-amber-500/40 shadow-sm shadow-amber-500/10'
                                                    : 'bg-transparent text-slate-400 border-transparent hover:bg-white/5 hover:text-white'
                                            }`}
                                        >
                                            {pageNum}
                                        </button>
                                    );
                                })}
                                
                                <button
                                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                                    disabled={currentPage === totalPages}
                                    className="p-2 rounded-lg bg-white/5 border border-white/5 text-slate-400 hover:text-white hover:bg-white/10 disabled:opacity-40 disabled:hover:text-slate-400 disabled:hover:bg-white/5 transition-all"
                                >
                                    <ChevronRight size={16} />
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    );
}
