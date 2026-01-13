'use client';

import { useState } from 'react';
import DashboardLayout from '@/components/layout/DashboardLayout';
import { Bot, Play, TrendingUp, TrendingDown, Award, AlertTriangle } from 'lucide-react';

interface Trade {
    timestamp: string;
    type: string;
    price: number;
    pnl: number | null;
}

interface BacktestResult {
    symbol: string;
    strategy: string;
    total_trades: number;
    win_rate: number;
    total_pnl: number;
    sharpe_ratio: number;
    max_drawdown: number;
    trades: Trade[];
}

export default function AutomationPage() {
    const [symbol, setSymbol] = useState('BTCUSDT');
    const [strategy, setStrategy] = useState('SIMPLE_MA_CROSS');
    const [fastMA, setFastMA] = useState('9');
    const [slowMA, setSlowMA] = useState('21');
    const [rsiPeriod, setRsiPeriod] = useState('14');
    const [oversold, setOversold] = useState('30');
    const [overbought, setOverbought] = useState('70');
    const [startDate, setStartDate] = useState('2024-01-01');
    const [endDate, setEndDate] = useState('2024-12-31');
    const [result, setResult] = useState<BacktestResult | null>(null);
    const [loading, setLoading] = useState(false);

    const runBacktest = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');

            const parameters = strategy === 'SIMPLE_MA_CROSS'
                ? { fast_ma: parseFloat(fastMA), slow_ma: parseFloat(slowMA) }
                : { rsi_period: parseFloat(rsiPeriod), oversold: parseFloat(oversold), overbought: parseFloat(overbought) };

            const res = await fetch('/api/v1/automation/backtest', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    symbol,
                    strategy,
                    parameters,
                    start_date: startDate,
                    end_date: endDate
                })
            });

            if (res.ok) setResult(await res.json());
        } catch (error) {
            console.error("Error running backtest:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-fuchsia-500 bg-clip-text text-transparent flex items-center gap-3">
                        <Bot size={32} className="text-violet-400" />
                        Automation & Backtesting
                    </h1>
                    <p className="text-slate-400 text-sm mt-1">
                        Prueba estrategias con datos históricos reales
                    </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                    {/* Strategy Builder */}
                    <div className="lg:col-span-1 glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                        <h2 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Play size={18} className="text-emerald-400" />
                            Configuración
                        </h2>

                        <div className="space-y-3">
                            <div>
                                <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Símbolo</label>
                                <select
                                    value={symbol}
                                    onChange={(e) => setSymbol(e.target.value)}
                                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm"
                                >
                                    <option value="BTCUSDT">BTC/USDT</option>
                                    <option value="ETHUSDT">ETH/USDT</option>
                                    <option value="SOLUSDT">SOL/USDT</option>
                                </select>
                            </div>

                            <div>
                                <label className="text-xs text-slate-500 uppercase font-bold mb-1 block">Estrategia</label>
                                <select
                                    value={strategy}
                                    onChange={(e) => setStrategy(e.target.value)}
                                    className="w-full px-3 py-2 rounded-lg bg-white/5 border border-white/10 text-white text-sm"
                                >
                                    <option value="SIMPLE_MA_CROSS">MA Cross</option>
                                    <option value="RSI_MEAN_REVERSION">RSI Mean Reversion</option>
                                </select>
                            </div>

                            {strategy === 'SIMPLE_MA_CROSS' && (
                                <div className="grid grid-cols-2 gap-2">
                                    <div>
                                        <label className="text-xs text-slate-500 mb-1 block">Fast MA</label>
                                        <input
                                            type="number"
                                            value={fastMA}
                                            onChange={(e) => setFastMA(e.target.value)}
                                            className="w-full px-2 py-1 rounded bg-white/5 border border-white/10 text-white text-sm font-mono"
                                        />
                                    </div>
                                    <div>
                                        <label className="text-xs text-slate-500 mb-1 block">Slow MA</label>
                                        <input
                                            type="number"
                                            value={slowMA}
                                            onChange={(e) => setSlowMA(e.target.value)}
                                            className="w-full px-2 py-1 rounded bg-white/5 border border-white/10 text-white text-sm font-mono"
                                        />
                                    </div>
                                </div>
                            )}

                            {strategy === 'RSI_MEAN_REVERSION' && (
                                <div className="space-y-2">
                                    <div>
                                        <label className="text-xs text-slate-500 mb-1 block">RSI Period</label>
                                        <input
                                            type="number"
                                            value={rsiPeriod}
                                            onChange={(e) => setRsiPeriod(e.target.value)}
                                            className="w-full px-2 py-1 rounded bg-white/5 border border-white/10 text-white text-sm font-mono"
                                        />
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                        <div>
                                            <label className="text-xs text-slate-500 mb-1 block">Oversold</label>
                                            <input
                                                type="number"
                                                value={oversold}
                                                onChange={(e) => setOversold(e.target.value)}
                                                className="w-full px-2 py-1 rounded bg-white/5 border border-white/10 text-white text-sm font-mono"
                                            />
                                        </div>
                                        <div>
                                            <label className="text-xs text-slate-500 mb-1 block">Overbought</label>
                                            <input
                                                type="number"
                                                value={overbought}
                                                onChange={(e) => setOverbought(e.target.value)}
                                                className="w-full px-2 py-1 rounded bg-white/5 border border-white/10 text-white text-sm font-mono"
                                            />
                                        </div>
                                    </div>
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-2">
                                <div>
                                    <label className="text-xs text-slate-500 mb-1 block">Desde</label>
                                    <input
                                        type="date"
                                        value={startDate}
                                        onChange={(e) => setStartDate(e.target.value)}
                                        className="w-full px-2 py-1 rounded bg-white/5 border border-white/10 text-white text-xs"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs text-slate-500 mb-1 block">Hasta</label>
                                    <input
                                        type="date"
                                        value={endDate}
                                        onChange={(e) => setEndDate(e.target.value)}
                                        className="w-full px-2 py-1 rounded bg-white/5 border border-white/10 text-white text-xs"
                                    />
                                </div>
                            </div>

                            <button
                                onClick={runBacktest}
                                disabled={loading}
                                className="w-full mt-4 px-6 py-3 rounded-lg bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white font-bold hover:opacity-90 transition-all disabled:opacity-50"
                            >
                                {loading ? 'Ejecutando...' : 'Ejecutar Backtest'}
                            </button>
                        </div>
                    </div>

                    {/* Results Dashboard */}
                    <div className="lg:col-span-2 space-y-6">

                        {result && (
                            <>
                                {/* Metrics */}
                                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                    <div className="glass-card p-4 rounded-xl border border-white/5">
                                        <div className="flex items-center gap-2 mb-1">
                                            <Award size={14} className="text-emerald-400" />
                                            <span className="text-[10px] text-slate-500 uppercase font-bold">Win Rate</span>
                                        </div>
                                        <p className="text-xl font-bold text-emerald-400 font-mono">{result.win_rate.toFixed(1)}%</p>
                                    </div>

                                    <div className="glass-card p-4 rounded-xl border border-white/5">
                                        <div className="flex items-center gap-2 mb-1">
                                            <TrendingUp size={14} className="text-cyan-400" />
                                            <span className="text-[10px] text-slate-500 uppercase font-bold">Total PnL</span>
                                        </div>
                                        <p className={`text-xl font-bold font-mono ${result.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                            ${result.total_pnl.toFixed(2)}
                                        </p>
                                    </div>

                                    <div className="glass-card p-4 rounded-xl border border-white/5">
                                        <div className="flex items-center gap-2 mb-1">
                                            <Bot size={14} className="text-violet-400" />
                                            <span className="text-[10px] text-slate-500 uppercase font-bold">Sharpe</span>
                                        </div>
                                        <p className="text-xl font-bold text-white font-mono">{result.sharpe_ratio.toFixed(2)}</p>
                                    </div>

                                    <div className="glass-card p-4 rounded-xl border border-white/5">
                                        <div className="flex items-center gap-2 mb-1">
                                            <AlertTriangle size={14} className="text-rose-400" />
                                            <span className="text-[10px] text-slate-500 uppercase font-bold">Max DD</span>
                                        </div>
                                        <p className="text-xl font-bold text-rose-400 font-mono">-${result.max_drawdown.toFixed(2)}</p>
                                    </div>
                                </div>

                                {/* Trade History */}
                                <div className="glass-card p-6 rounded-3xl border border-white/5 bg-black/20">
                                    <h3 className="text-sm font-bold text-white mb-4">Historial de Trades ({result.total_trades} total)</h3>

                                    <div className="max-h-96 overflow-y-auto space-y-2">
                                        {result.trades.map((trade, i) => (
                                            <div key={i} className={`p-3 rounded-lg border ${trade.type === 'BUY'
                                                    ? 'bg-emerald-500/10 border-emerald-500/30'
                                                    : 'bg-rose-500/10 border-rose-500/30'
                                                }`}>
                                                <div className="flex justify-between items-center mb-1">
                                                    <span className={`text-xs font-bold uppercase ${trade.type === 'BUY' ? 'text-emerald-400' : 'text-rose-400'
                                                        }`}>
                                                        {trade.type}
                                                    </span>
                                                    <span className="text-[10px] text-slate-500 font-mono">
                                                        {new Date(trade.timestamp).toLocaleDateString()}
                                                    </span>
                                                </div>
                                                <div className="flex justify-between text-sm">
                                                    <span className="text-slate-400">Precio:</span>
                                                    <span className="text-white font-mono">${trade.price.toFixed(2)}</span>
                                                </div>
                                                {trade.pnl !== null && (
                                                    <div className="flex justify-between text-sm mt-1 pt-1 border-t border-white/10">
                                                        <span className="text-slate-400">PnL:</span>
                                                        <span className={`font-mono font-bold ${trade.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'
                                                            }`}>
                                                            {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                                                        </span>
                                                    </div>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </>
                        )}

                        {!result && !loading && (
                            <div className="glass-card p-12 rounded-3xl border border-white/5 border-dashed flex flex-col items-center justify-center text-center">
                                <Bot size={48} className="text-slate-600 mb-4" />
                                <p className="text-slate-400">Configura y ejecuta un backtest para ver resultados</p>
                            </div>
                        )}

                        {loading && (
                            <div className="glass-card p-12 rounded-3xl border border-white/5 flex flex-col items-center justify-center">
                                <div className="h-12 w-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                                <p className="text-white font-medium">Ejecutando backtest...</p>
                                <p className="text-xs text-slate-500 mt-1">Analizando datos históricos</p>
                            </div>
                        )}
                    </div>

                </div>

            </div>
        </DashboardLayout>
    );
}
