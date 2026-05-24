'use client';

import React from 'react';
import { useAIContext } from '@/context/AIContext';
import { Target, X, Terminal, Sparkles, Brain, Activity } from 'lucide-react';

export default function GlobalBrainModal() {
    const { isBrainOpen, toggleBrain, analysis, status } = useAIContext();

    if (!isBrainOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
                onClick={toggleBrain}
            />

            {/* Modal Content */}
            <div className="relative w-full max-w-2xl bg-[#0a0a0f] border border-white/10 rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-200">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-white/5 bg-white/[0.02]">
                    <div className="flex items-center gap-3">
                        <div className="relative flex items-center justify-center h-8 w-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 shadow-lg shadow-violet-500/20">
                            <Brain className="h-4 w-4 text-white" />
                            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
                                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${status?.available ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 ${status?.available ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
                            </span>
                        </div>
                        <div>
                            <h3 className="text-white font-bold text-sm">Neural Engine Core</h3>
                            <p className="text-slate-400 text-xs font-mono">Global Market Analysis</p>
                        </div>
                    </div>
                    <button
                        onClick={toggleBrain}
                        className="p-2 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
                    >
                        <X size={20} />
                    </button>
                </div>

                {/* Body */}
                <div className="p-6 space-y-6">
                    {/* Status Banner */}
                    <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-violet-500/10 border border-violet-500/20">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-violet-500/20 text-violet-300">
                                <Sparkles size={18} />
                            </div>
                            <div>
                                <h4 className="text-white text-sm font-medium">Análisis Activo</h4>
                                <p className="text-violet-200/60 text-xs">El motor está procesando señales en tiempo real.</p>
                            </div>
                        </div>
                        {analysis && (
                            <div className={`px-3 py-1 rounded text-xs font-bold uppercase tracking-wider ${analysis.signal === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' :
                                analysis.signal === 'SELL' ? 'bg-rose-500/20 text-rose-400' :
                                    'bg-slate-500/20 text-slate-400'
                                }`}>
                                {analysis.signal} ({analysis.confidence}%)
                            </div>
                        )}
                    </div>

                    {/* Agent Logic Core (Terminal Style) */}
                    <div className="bg-black/50 rounded-xl border border-white/10 overflow-hidden">
                        <div className="bg-white/5 px-4 py-2 flex items-center gap-2 border-b border-white/5">
                            <Terminal size={14} className="text-slate-400" />
                            <span className="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Live Inference Logs</span>
                        </div>
                        <div className="p-4 space-y-4 font-mono text-xs max-h-[300px] overflow-y-auto custom-scrollbar">
                            {analysis ? (
                                analysis.reasoning.map((line, i) => (
                                    <div key={i} className="flex gap-3 text-slate-300 animate-in slide-in-from-left-2 duration-300" style={{ animationDelay: `${i * 100}ms` }}>
                                        <span className="text-slate-600 select-none">{(i + 1).toString().padStart(2, '0')}</span>
                                        <p className="leading-relaxed">
                                            <span className="text-violet-500 mr-2">➜</span>
                                            {line}
                                        </p>
                                    </div>
                                ))
                            ) : (
                                <div className="flex flex-col items-center justify-center py-12 text-slate-600 gap-2">
                                    <Activity size={24} className="animate-pulse" />
                                    <p>Esperando datos...</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="px-6 py-4 bg-white/[0.02] border-t border-white/5 flex justify-between items-center text-xs text-slate-500 font-mono">
                    <span>Model: {status?.model || 'Unknown'}</span>
                    <span className="flex items-center gap-2">
                        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                        Thinking
                    </span>
                </div>
            </div>
        </div>
    );
}
