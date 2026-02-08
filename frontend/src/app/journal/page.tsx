'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import {
    BookOpen,
    Plus,
    BarChart3,
    TrendingUp,
    TrendingDown,
    Target,
    Star,
    Brain,
    Calendar,
    Award,
    Activity,
    Info
} from 'lucide-react';

interface JournalEntry {
    id: number;
    symbol: string;
    side: string;
    entry_price: number;
    exit_price: number;
    pnl: number;
    mood: string;
    strategy: string;
    notes: string;
    lessons: string;
    rating: number;
    created_at: string;
}

interface Metrics {
    total_trades: number;
    win_rate: number;
    profit_factor: number;
    expectancy: number;
    avg_win: number;
    avg_loss: number;
    total_pnl: number;
}

export default function JournalPage() {
    const [entries, setEntries] = useState<JournalEntry[]>([]);
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);

    // Form state
    const [symbol, setSymbol] = useState('BTCUSDT');
    const [side, setSide] = useState('BUY');
    const [entryPrice, setEntryPrice] = useState('');
    const [exitPrice, setExitPrice] = useState('');
    const [pnl, setPnl] = useState('');
    const [mood, setMood] = useState('CALM');
    const [strategy, setStrategy] = useState('PRICE_ACTION');
    const [notes, setNotes] = useState('');
    const [rating, setRating] = useState(3);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const token = localStorage.getItem('token');
            const [entriesRes, metricsRes] = await Promise.all([
                fetch('/api/v1/journal/entries', { headers: { 'Authorization': `Bearer ${token}` } }),
                fetch('/api/v1/journal/metrics', { headers: { 'Authorization': `Bearer ${token}` } })
            ]);

            if (entriesRes.ok) setEntries(await entriesRes.json());
            if (metricsRes.ok) setMetrics(await metricsRes.json());
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    const handleCreateEntry = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/journal/entries', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol, side, entry_price: parseFloat(entryPrice),
                    exit_price: parseFloat(exitPrice), pnl: parseFloat(pnl),
                    mood, strategy, notes, rating
                })
            });

            if (res.ok) {
                setShowModal(false);
                fetchData();
            }
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div className="flex justify-between items-end">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-indigo-500 bg-clip-text text-transparent flex items-center gap-3">
                            <BookOpen size={32} className="text-violet-400" />
                            Trading Journal Pro
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">
                            Auditoría de performance y psicología del trader
                        </p>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="px-6 py-3 bg-gradient-to-r from-violet-600 to-indigo-700 text-white font-bold rounded-2xl flex items-center gap-2 hover:opacity-90 transition-all shadow-lg shadow-violet-500/20"
                    >
                        <Plus size={20} />
                        Registrar Trade
                    </button>
                </div>

                {/* KPI Cards */}
                {metrics && (
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                            <p className="text-xs text-slate-500 uppercase font-bold mb-2 flex items-center gap-2">
                                <Award size={14} className="text-violet-400" />
                                Profit Factor
                            </p>
                            <p className={`text-2xl font-black font-mono ${metrics.profit_factor >= 1.5 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {metrics.profit_factor.toFixed(2)}
                            </p>
                        </div>
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                            <p className="text-xs text-slate-500 uppercase font-bold mb-2 flex items-center gap-2">
                                <Target size={14} className="text-cyan-400" />
                                Win Rate
                            </p>
                            <p className="text-2xl font-black font-mono text-white">
                                {metrics.win_rate}%
                            </p>
                        </div>
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                            <p className="text-xs text-slate-500 uppercase font-bold mb-2 flex items-center gap-2">
                                <Activity size={14} className="text-amber-400" />
                                Expectancy
                            </p>
                            <p className={`text-2xl font-black font-mono ${metrics.expectancy > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                ${metrics.expectancy.toFixed(2)}
                            </p>
                        </div>
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                            <p className="text-xs text-slate-500 uppercase font-bold mb-2 flex items-center gap-2">
                                <Award size={14} className="text-emerald-400" />
                                Total PnL
                            </p>
                            <p className={`text-2xl font-black font-mono ${metrics.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                ${metrics.total_pnl.toFixed(2)}
                            </p>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">

                    {/* Trade History */}
                    <div className="lg:col-span-3">
                        <div className="glass-card rounded-3xl border border-white/5 bg-black/20 overflow-hidden">
                            <div className="p-6 border-b border-white/5 flex justify-between items-center">
                                <h3 className="font-bold text-white flex items-center gap-2">
                                    <Calendar size={18} className="text-slate-400" />
                                    Historial de Ejecuciones
                                </h3>
                            </div>

                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead className="text-[10px] text-slate-500 uppercase font-bold bg-white/[0.02]">
                                        <tr>
                                            <th className="px-6 py-4">Fecha</th>
                                            <th className="px-6 py-4">Activo</th>
                                            <th className="px-6 py-4">Lado</th>
                                            <th className="px-6 py-4">PnL ($)</th>
                                            <th className="px-6 py-4">Estrategia</th>
                                            <th className="px-6 py-4">Mood</th>
                                            <th className="px-6 py-4">Rating</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-white/5">
                                        {entries.map((entry) => (
                                            <tr key={entry.id} className="hover:bg-white/[0.02] transition-colors group">
                                                <td className="px-6 py-4 text-xs text-slate-400">{new Date(entry.created_at).toLocaleDateString()}</td>
                                                <td className="px-6 py-4 font-bold text-white">{entry.symbol}</td>
                                                <td className="px-6 py-4">
                                                    <span className={`px-2 py-1 rounded-lg text-[10px] font-bold ${entry.side === 'BUY' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                                                        }`}>
                                                        {entry.side}
                                                    </span>
                                                </td>
                                                <td className={`px-6 py-4 font-mono font-bold ${entry.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                    {entry.pnl > 0 ? '+' : ''}{entry.pnl.toFixed(2)}
                                                </td>
                                                <td className="px-6 py-4 text-xs text-slate-300">{entry.strategy}</td>
                                                <td className="px-6 py-4">
                                                    <span className="text-[10px] bg-white/5 px-2 py-1 rounded text-slate-400">
                                                        {entry.mood}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <div className="flex gap-0.5">
                                                        {[...Array(5)].map((_, i) => (
                                                            <Star key={i} size={10} className={i < entry.rating ? 'fill-amber-400 text-amber-400' : 'text-slate-700'} />
                                                        ))}
                                                    </div>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>

                    {/* Stats Radar/Info */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                                <Brain size={16} className="text-violet-400" />
                                Brain Journal Insights
                            </h3>
                            <div className="space-y-4">
                                <div className="p-4 rounded-2xl bg-violet-500/5 border border-violet-500/10">
                                    <p className="text-xs text-slate-400 mb-2">Tu mejor desempeño:</p>
                                    <p className="text-sm font-bold text-white">Price Action en BTCUSDT</p>
                                    <p className="text-[10px] text-emerald-400 mt-1">75% Win Rate</p>
                                </div>
                                <div className="p-4 rounded-2xl bg-rose-500/5 border border-rose-500/10">
                                    <p className="text-xs text-slate-400 mb-2">Punto de fricción:</p>
                                    <p className="text-sm font-bold text-white">Mood: ANXIOUS</p>
                                    <p className="text-[10px] text-rose-400 mt-1">-12% Performance hit</p>
                                </div>
                            </div>
                        </div>

                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-indigo-500/10 to-transparent">
                            <h4 className="text-xs font-bold text-indigo-400 uppercase mb-3 flex items-center gap-2">
                                <Info size={14} /> ¿Sabías qué?
                            </h4>
                            <p className="text-xs text-slate-400 leading-relaxed">
                                Los traders que llevan un diario profesional tienen un 40% más de probabilidad de ser rentables. El autoconocimiento es la ventaja competitiva definitiva.
                            </p>
                        </div>
                    </div>

                </div>

            </div>

            {/* Modal para Registro */}
            {showModal && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className="bg-[#0B0E14] border border-white/10 rounded-3xl w-full max-w-2xl overflow-hidden shadow-2xl">
                        <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                <Plus size={20} className="text-violet-400" />
                                Registrar Nueva Operación
                            </h2>
                            <button onClick={() => setShowModal(false)} className="text-slate-500 hover:text-white transition-colors">
                                Cerar
                            </button>
                        </div>

                        <form onSubmit={handleCreateEntry} className="p-8 space-y-6">
                            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                                <div>
                                    <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Símbolo</label>
                                    <input value={symbol} onChange={e => setSymbol(e.target.value)} className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50" />
                                </div>
                                <div>
                                    <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Lado</label>
                                    <select value={side} onChange={e => setSide(e.target.value)} className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50 cursor-pointer">
                                        <option value="BUY" className="bg-[#12121a]">BUY</option>
                                        <option value="SELL" className="bg-[#12121a]">SELL</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Entrada ($)</label>
                                    <input type="number" value={entryPrice} onChange={e => setEntryPrice(e.target.value)} className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white font-mono focus:outline-none focus:border-violet-500/50" />
                                </div>
                                <div>
                                    <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">PnL ($)</label>
                                    <input type="number" value={pnl} onChange={e => setPnl(e.target.value)} className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white font-mono focus:outline-none focus:border-violet-500/50" />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Estado de Ánimo</label>
                                    <select value={mood} onChange={e => setMood(e.target.value)} className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50 cursor-pointer">
                                        <option value="CALM" className="bg-[#12121a]">Calma</option>
                                        <option value="ANXIOUS" className="bg-[#12121a]">Ansiedad</option>
                                        <option value="GREEDY" className="bg-[#12121a]">Codicia</option>
                                        <option value="FRUSTRATED" className="bg-[#12121a]">Frustración</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Calidad Setup (1-5)</label>
                                    <input type="range" min="1" max="5" value={rating} onChange={e => setRating(parseInt(e.target.value))} className="w-full accent-violet-500" />
                                </div>
                            </div>

                            <div>
                                <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Notas y Lecciones</label>
                                <textarea
                                    value={notes}
                                    onChange={e => setNotes(e.target.value)}
                                    className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-3 text-sm text-white h-24 focus:outline-none focus:border-violet-500/50"
                                    placeholder="¿Por qué entraste? ¿Qué aprendiste?"
                                ></textarea>
                            </div>

                            <button type="submit" className="w-full py-4 bg-gradient-to-r from-violet-600 to-indigo-700 text-white font-bold rounded-2xl hover:opacity-90 transition-all">
                                Guardar en Diario
                            </button>
                        </form>
                    </div>
                </div>
            )}
        </DashboardLayout>
    );
}
