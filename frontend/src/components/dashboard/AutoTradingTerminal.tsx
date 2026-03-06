'use client';

import React, { useEffect, useState } from 'react';
import { Terminal, Cpu, Zap, Activity, CheckCircle, XCircle } from 'lucide-react';

interface TradeLog {
    symbol: string;
    signal: {
        action?: string;
        type?: string;
        confidence?: number;
        reasoning?: string[];
    };
    executed_at: string;
    success: boolean;
    order_id?: string;
}

interface PendingSignal {
    symbol: string;
    signal: {
        action?: string;
        type?: string;
        confidence?: number;
        reasoning?: string[];
    };
    added_at: string;
}

export default function AutoTradingTerminal({ isRunning }: { isRunning: boolean }) {
    const [history, setHistory] = useState<TradeLog[]>([]);
    const [pending, setPending] = useState<PendingSignal[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchQueue = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch('/api/v1/automated-trading/queue', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                setHistory(data.execution_history || []);
                setPending(data.pending_signals || []);
            }
        } catch (error) {
            console.error('Error fetching automated trading logs:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchQueue();
        const interval = setInterval(fetchQueue, 5000); // Check every 5s
        return () => clearInterval(interval);
    }, []);

    // Combine and sort logs for the terminal view: Put pending signals first, then reverse chronological history
    const terminalLogs = [
        ...pending.map(p => ({ ...p, isPending: true })),
        ...[...history].reverse().map(h => ({ ...h, isPending: false }))
    ];

    return (
        <div className="bg-black/80 rounded-xl border border-white/10 overflow-hidden flex flex-col h-[500px] shadow-2xl mt-8">
            {/* Header */}
            <div className="bg-white/[0.05] border-b border-white/10 py-3 px-5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className={`p-1.5 rounded-lg ${isRunning ? 'bg-green-500/20 text-green-400' : 'bg-slate-500/20 text-slate-400'}`}>
                        <Terminal size={16} />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white tracking-wide">Terminal de Ejecución</h3>
                        <p className="text-[10px] text-slate-400 font-mono">Motor Auto-Execution Live Logs</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className={`flex h-2 w-2 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-slate-600'}`}></span>
                    <span className={`text-[10px] font-mono uppercase ${isRunning ? 'text-green-400' : 'text-slate-500'}`}>
                        {isRunning ? 'System Active' : 'System Paused'}
                    </span>
                </div>
            </div>

            {/* Terminal Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 custom-scrollbar font-mono text-xs">
                {loading && terminalLogs.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-2">
                        <Activity size={24} className="animate-spin" />
                        <p>Iniciando interfaz de terminal...</p>
                    </div>
                ) : terminalLogs.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-600 italic py-10 opacity-70">
                        <Terminal size={32} className="mb-2 opacity-50" />
                        <p>No hay actividad registrada en la memoria reciente.</p>
                        <p className="text-[10px] mt-2 text-slate-500">
                            {isRunning ? 'Escaneando mercados en busca de oportunidades...' : 'Inicia la automatización para ver logs.'}
                        </p>
                    </div>
                ) : (
                    terminalLogs.map((log: any, i) => {
                        const isPending = log.isPending;
                        const action = log.signal?.action || log.signal?.type || 'UNKNOWN';
                        const sideColor = action === 'BUY' || action === 'LONG' ? 'text-green-400' : 'text-red-400';
                        const timeStr = isPending
                            ? new Date(log.added_at).toLocaleTimeString()
                            : new Date(log.executed_at).toLocaleTimeString();

                        return (
                            <div
                                key={isPending ? `pending-${log.symbol}-${log.added_at}` : `exec-${log.symbol}-${log.executed_at}`}
                                className={`border-l-2 pl-3 py-1 animate-in slide-in-from-left-2 duration-300 ${isPending ? 'border-yellow-500/50' :
                                        (log.success ? 'border-green-500/50' : 'border-red-500/50')
                                    }`}
                            >
                                <div className="flex items-center justify-between mb-1.5 opacity-90">
                                    <div className="flex items-center gap-2">
                                        <span className="text-slate-500">[{timeStr}]</span>
                                        {isPending ? (
                                            <span className="bg-yellow-500/10 text-yellow-400 px-1.5 py-0.5 rounded text-[10px] uppercase font-bold tracking-wider">
                                                En Cola (Validando)
                                            </span>
                                        ) : log.success ? (
                                            <span className="bg-green-500/10 text-green-400 px-1.5 py-0.5 rounded flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider">
                                                <CheckCircle size={10} /> Completado
                                            </span>
                                        ) : (
                                            <span className="bg-red-500/10 text-red-400 px-1.5 py-0.5 rounded flex items-center gap-1 text-[10px] uppercase font-bold tracking-wider">
                                                <XCircle size={10} /> Fallido
                                            </span>
                                        )}
                                        <span className={`font-bold ml-1 ${sideColor}`}>
                                            {action} {log.symbol}
                                        </span>
                                    </div>
                                    <span className="text-[10px] text-slate-500 hidden sm:inline-block">
                                        Confianza: {log.signal?.confidence || 0}%
                                    </span>
                                </div>
                                <div className="text-slate-300 leading-relaxed text-[11px]">
                                    {log.signal?.reasoning && log.signal.reasoning.length > 0 ? (
                                        <div className="flex items-start gap-2">
                                            <span className="text-blue-400 opacity-70 mt-0.5">❯</span>
                                            <span className="opacity-90">{log.signal.reasoning[0]}</span>
                                        </div>
                                    ) : (
                                        <div className="flex items-start gap-2 text-slate-500">
                                            <span className="opacity-50 mt-0.5">❯</span>
                                            <span>Procesando parámetros algorítmicos...</span>
                                        </div>
                                    )}
                                </div>
                                {!isPending && log.order_id && (
                                    <div className="mt-1.5 text-slate-600 text-[9px] flex gap-3 opacity-60">
                                        <span>OrdID: {log.order_id}</span>
                                    </div>
                                )}
                            </div>
                        );
                    })
                )}
                {/* Auto-scroll target */}
                <div className="h-2"></div>
            </div>

            {/* Footer */}
            <div className="bg-white/[0.02] p-2.5 px-5 border-t border-white/5 shadow-inner">
                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <div className="flex items-center gap-2">
                        <Cpu size={12} className="text-blue-500/70" />
                        <span>Execution Engine conectada al canal de señales primario</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
