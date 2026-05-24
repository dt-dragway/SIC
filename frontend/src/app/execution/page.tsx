'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import {
    Zap,
    Play,
    Pause,
    Settings,
    BarChart3,
    Clock,
    Target,
    AlertCircle,
    TrendingUp,
    CheckCircle2
} from 'lucide-react';

export default function ExecutionPage() {
    const [symbol, setSymbol] = useState('BTCUSDT');
    const [side, setSide] = useState('BUY');
    const [quantity, setQuantity] = useState('');
    const [duration, setDuration] = useState('10');
    const [algo, setAlgo] = useState('TWAP');
    const [loading, setLoading] = useState(false);
    const [activeOrders, setActiveOrders] = useState<any[]>([]);

    const startExecution = async () => {
        if (!quantity) return;
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/execution/execute', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol,
                    side,
                    total_quantity: parseFloat(quantity),
                    duration_minutes: parseInt(duration),
                    algorithm: algo
                })
            });

            if (res.ok) {
                const newOrder = {
                    id: Math.random().toString(36).substr(2, 9),
                    symbol,
                    side,
                    quantity,
                    duration,
                    algo,
                    status: 'RUNNING',
                    progress: 0,
                    start_time: new Date().toLocaleTimeString()
                };
                setActiveOrders([newOrder, ...activeOrders]);
                // Clear fields
                setQuantity('');
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Zap size={32} className="text-yellow-400" />
                        Smart Execution (TWAP/VWAP)
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Algoritmos institucionales para minimizar impacto de mercado y reducir slippage
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Execution Config */}
                    <div className="lg:col-span-1 glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h3 className="text-sm font-bold text-white mb-6 flex items-center gap-2">
                            <Settings size={18} className="text-slate-400" />
                            Nueva Orden Algorítmica
                        </h3>

                        <div className="space-y-4">
                            <div className="grid grid-cols-2 gap-2">
                                <button
                                    onClick={() => setSide('BUY')}
                                    className={`py-2 rounded-xl font-bold text-xs transition-all ${side === 'BUY' ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/20' : 'bg-white/5 text-slate-500'
                                        }`}
                                >
                                    BUY
                                </button>
                                <button
                                    onClick={() => setSide('SELL')}
                                    className={`py-2 rounded-xl font-bold text-xs transition-all ${side === 'SELL' ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20' : 'bg-white/5 text-slate-500'
                                        }`}
                                >
                                    SELL
                                </button>
                            </div>

                            <div>
                                <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Símbolo</label>
                                <select
                                    value={symbol}
                                    onChange={(e) => setSymbol(e.target.value)}
                                    className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-yellow-500/50 cursor-pointer"
                                >
                                    <option value="BTCUSDT" className="bg-[#12121a]">Bitcoin (BTC)</option>
                                    <option value="ETHUSDT" className="bg-[#12121a]">Ethereum (ETH)</option>
                                    <option value="SOLUSDT" className="bg-[#12121a]">Solana (SOL)</option>
                                    <option value="BNBUSDT" className="bg-[#12121a]">Binance Coin (BNB)</option>
                                </select>
                            </div>

                            <div>
                                <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Cantidad Total</label>
                                <input
                                    type="number"
                                    value={quantity}
                                    onChange={(e) => setQuantity(e.target.value)}
                                    placeholder="0.00"
                                    className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white font-mono focus:outline-none focus:border-yellow-500/50"
                                />
                            </div>

                            <div>
                                <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Algoritmo</label>
                                <select
                                    value={algo}
                                    onChange={(e) => setAlgo(e.target.value)}
                                    className="w-full bg-[#12121a] border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-yellow-500/50 cursor-pointer"
                                >
                                    <option value="TWAP" className="bg-[#12121a]">TWAP (Pesado en Tiempo)</option>
                                    <option value="VWAP" className="bg-[#12121a]">VWAP (Pesado en Volumen)</option>
                                    <option value="狙撃 (SNIPER)" className="bg-[#12121a]">狙撃 Sniper (Oculto)</option>
                                </select>
                            </div>

                            <div>
                                <label className="text-[10px] text-slate-500 uppercase font-bold mb-1 block">Duración ({duration}m)</label>
                                <input
                                    type="range"
                                    min="5"
                                    max="120"
                                    step="5"
                                    value={duration}
                                    onChange={(e) => setDuration(e.target.value)}
                                    className="w-full accent-yellow-500 bg-white/5 rounded-lg h-2"
                                />
                            </div>

                            <button
                                onClick={startExecution}
                                disabled={loading || !quantity}
                                className="w-full py-4 bg-gradient-to-r from-yellow-500 to-orange-600 text-white font-bold rounded-2xl hover:opacity-90 transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
                            >
                                <Play size={18} className="group-hover:translate-x-0.5 transition-transform" />
                                Lanzar Algoritmo
                            </button>
                        </div>
                    </div>

                    {/* Active Algorithmic Orders */}
                    <div className="lg:col-span-2 space-y-6">
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20 min-h-[400px]">
                            <h3 className="text-sm font-bold text-white mb-6 flex items-center gap-2">
                                <Target size={18} className="text-cyan-400" />
                                Órdenes Activas en el Mercado
                            </h3>

                            {activeOrders.length === 0 ? (
                                <div className="h-64 flex flex-col items-center justify-center text-slate-500 border-2 border-dashed border-white/5 rounded-2xl">
                                    <BarChart3 size={48} className="mb-4 opacity-20" />
                                    <p>No hay ejecuciones activas</p>
                                    <p className="text-xs">Usa el panel de la izquierda para lanzar una orden</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {activeOrders.map(order => (
                                        <div key={order.id} className="p-5 rounded-2xl bg-white/[0.03] border border-white/5">
                                            <div className="flex justify-between items-start mb-4">
                                                <div className="flex items-center gap-3">
                                                    <div className={`p-2 rounded-xl ${order.side === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'}`}>
                                                        <TrendingUp size={16} />
                                                    </div>
                                                    <div>
                                                        <h4 className="font-bold text-white flex items-center gap-2">
                                                            {order.symbol}
                                                            <span className="text-[10px] px-2 py-0.5 bg-white/10 rounded uppercase">{order.algo}</span>
                                                        </h4>
                                                        <p className="text-[10px] text-slate-500">Iniciado: {order.start_time}</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-[10px] font-bold text-cyan-400 animate-pulse flex items-center gap-1">
                                                        <Clock size={10} /> EJECUTANDO...
                                                    </span>
                                                    <button className="p-1 px-2 bg-rose-500/10 text-rose-500 rounded-lg hover:bg-rose-500/20 transition-all">
                                                        <Pause size={14} />
                                                    </button>
                                                </div>
                                            </div>

                                            {/* Progress Bar */}
                                            <div className="space-y-2">
                                                <div className="flex justify-between text-xs font-mono">
                                                    <span className="text-slate-400">Progreso de ejecución</span>
                                                    <span className="text-white">0%</span>
                                                </div>
                                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                                    <div className="h-full bg-gradient-to-r from-yellow-500 to-orange-500 w-1 transition-all"></div>
                                                </div>
                                                <div className="flex justify-between text-[10px] text-slate-500">
                                                    <span>0 / {order.quantity} {order.symbol.replace('USDT', '')}</span>
                                                    <span>⏳ {order.duration}m restantes</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Why use smart execution? */}
                        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-yellow-500/5 to-orange-500/5 flex items-start gap-4">
                            <div className="p-3 rounded-2xl bg-yellow-500/20 text-yellow-500">
                                <AlertCircle size={24} />
                            </div>
                            <div>
                                <h4 className="font-bold text-white">¿Por qué usar algoritmos?</h4>
                                <p className="text-xs text-slate-400 leading-relaxed mt-1">
                                    Los algoritmos de <strong>Smart Slicing</strong> evitan que el mercado detecte tu orden. Al dividir un cargo grande en micro-órdenes, evitas activar el detector de ballenas de otros traders y consigues un precio promedio mucho más cercano al precio de mercado real.
                                    <br /><br />
                                    <span className="text-emerald-400 flex items-center gap-1">
                                        <CheckCircle2 size={12} /> Slipagge reducido en un 80% estimado.
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>

                </div>

            </div>
        </DashboardLayout>
    );
}
