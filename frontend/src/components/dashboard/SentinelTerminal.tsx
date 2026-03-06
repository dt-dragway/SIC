'use client';

import React, { useEffect, useState } from 'react';
import { Terminal, Cpu, Zap, Activity } from 'lucide-react';

interface SentinelLog {
    id: number;
    symbol: string;
    side: string;
    price: number;
    quantity: number;
    reason: string;
    timestamp: string;
}

export default function SentinelTerminal() {
    const [logs, setLogs] = useState<SentinelLog[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchLogs = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch('/api/v1/practice/sentinel-logs', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                setLogs(data);
            }
        } catch (error) {
            console.error('Error fetching sentinel logs:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 10000); // Check every 10s
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="bg-black/40 rounded-3xl border border-white/5 overflow-hidden flex flex-col h-full shadow-2xl">
            {/* Header */}
            <div className="bg-white/[0.03] border-b border-white/5 py-3 px-5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-1.5 rounded-lg bg-blue-500/20 text-blue-400">
                        <Cpu size={14} />
                    </div>
                    <div>
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider">Centinela CIO</h3>
                        <p className="text-[10px] text-slate-500 font-mono">Justificación Cuantitativa Live</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="flex h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                    <span className="text-[9px] font-mono text-emerald-400/80 uppercase">Sentinel Active</span>
                </div>
            </div>

            {/* Terminal Body */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar font-mono text-[11px]">
                {loading && logs.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-2 opacity-50">
                        <Activity size={24} className="animate-spin" />
                        <p>Sincronizando con Sentinel Engine...</p>
                    </div>
                ) : logs.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-slate-600 italic py-10">
                        <p>No se han detectado operaciones tácticas en el ciclo actual.</p>
                        <p className="text-[10px] mt-1">Esperando desequilibrío en Order Flow...</p>
                    </div>
                ) : (
                    logs.map((log, i) => (
                        <div key={log.id} className="border-l-2 border-blue-500/30 pl-3 py-1 animate-in slide-in-from-left-2 duration-300" style={{ animationDelay: `${i * 50}ms` }}>
                            <div className="flex items-center justify-between mb-1">
                                <span className={`font-bold ${log.side === 'BUY' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    [{log.side} {log.symbol}]
                                </span>
                                <span className="text-[9px] text-slate-500">
                                    {new Date(log.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                            <div className="text-slate-300 leading-relaxed">
                                <span className="text-blue-400 mr-2">LOG:</span>
                                {log.reason}
                            </div>
                            <div className="mt-1 text-slate-500 text-[10px] flex gap-3">
                                <span>PX: ${log.price.toLocaleString()}</span>
                                <span>QTY: {log.quantity.toFixed(4)}</span>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Footer */}
            <div className="bg-black/20 p-2 px-5 border-t border-white/5">
                <div className="flex items-center gap-2 text-[9px] text-slate-500 italic">
                    <Zap size={10} className="text-amber-500" />
                    Protocolo Centinela Omnipresente v2.0 - Vigilancia 24/7 Activa
                </div>
            </div>
        </div>
    );
}
