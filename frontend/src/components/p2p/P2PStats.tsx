'use client'

import React from 'react'
import { TrendingUp, TrendingDown, RefreshCw, Zap, Star } from 'lucide-react'

interface P2PStatsProps {
    bestBuy: number
    bestSell: number
    spread: number
    isLoading: boolean
    onRefresh: () => void
}

export default function P2PStats({ bestBuy, bestSell, spread, isLoading, onRefresh }: P2PStatsProps) {
    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            {/* Mejor Compra */}
            <div className="glass-card p-5 bg-gradient-to-br from-white/[0.03] to-white/[0.01] border-emerald-500/10 hover:border-emerald-500/30 transition-all group">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                        <Star className="h-3 w-3 text-amber-500" fill="currentColor" />
                        MEJOR PRECIO COMPRA
                    </span>
                    <div className="p-1.5 bg-emerald-500/10 rounded-lg">
                        <TrendingDown className="h-4 w-4 text-emerald-400" />
                    </div>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-black text-white font-mono tracking-tighter">
                        {bestBuy > 0 ? bestBuy.toLocaleString('es-VE', { minimumFractionDigits: 2 }) : '---'}
                    </span>
                    <span className="text-xs font-bold text-emerald-400">VES</span>
                </div>
                <div className="mt-2 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-emerald-500/30 w-1/3 group-hover:w-1/2 transition-all duration-700" />
                </div>
            </div>

            {/* Mejor Venta */}
            <div className="glass-card p-5 bg-gradient-to-br from-white/[0.03] to-white/[0.01] border-rose-500/10 hover:border-rose-500/30 transition-all group">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                        <Zap className="h-3 w-3 text-rose-500" fill="currentColor" />
                        MEJOR PRECIO VENTA
                    </span>
                    <div className="p-1.5 bg-rose-500/10 rounded-lg">
                        <TrendingUp className="h-4 w-4 text-rose-400" />
                    </div>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-black text-white font-mono tracking-tighter">
                        {bestSell > 0 ? bestSell.toLocaleString('es-VE', { minimumFractionDigits: 2 }) : '---'}
                    </span>
                    <span className="text-xs font-bold text-rose-400">VES</span>
                </div>
                <div className="mt-2 h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                    <div className="h-full bg-rose-500/30 w-1/3 group-hover:w-1/2 transition-all duration-700" />
                </div>
            </div>

            {/* Spread Comercial */}
            <div className="glass-card p-5 bg-gradient-to-br from-white/[0.03] to-white/[0.01] border-indigo-500/10 hover:border-indigo-500/30 transition-all group">
                <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">SPREAD COMERCIAL</span>
                    <div className="p-1.5 bg-indigo-500/10 rounded-lg">
                        <RefreshCw className={`h-4 w-4 text-indigo-400 ${isLoading ? 'animate-spin' : ''}`} />
                    </div>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-black text-indigo-300 font-mono tracking-tighter">
                        {spread > 0 ? spread.toFixed(2) : '0.00'}
                    </span>
                    <span className="text-xs font-bold text-indigo-500">%</span>
                </div>
                <p className="text-[10px] text-slate-500 mt-2 font-medium italic">Margen de rentabilidad bruta</p>
            </div>

            {/* Control Panel */}
            <div className="glass-card p-5 bg-indigo-600/10 border-indigo-500/20 flex flex-col justify-between">
                <div className="text-[10px] font-bold text-indigo-300 uppercase tracking-widest mb-1">MOTOR DE DATOS</div>
                <button
                    onClick={onRefresh}
                    disabled={isLoading}
                    className="flex items-center justify-center gap-2 w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg font-bold text-sm transition-all shadow-lg shadow-indigo-600/20"
                >
                    <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                    {isLoading ? 'ACTUALIZANDO...' : 'REFRESCAR MERCADO'}
                </button>
                <div className="mt-2 flex items-center justify-center gap-2">
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                    <span className="text-[10px] font-bold text-slate-400 uppercase">Live Feed Active</span>
                </div>
            </div>
        </div>
    )
}
