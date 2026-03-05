'use client'

import React from 'react'
import { Brain, Cpu, Sparkles, Wand2 } from 'lucide-react'

interface AIAnalysisCardProps {
    recommendation: {
        reason: string
        best_offer?: {
            advertiser: string
            price: number
            completion_rate: number
        }
    } | null
    isAnalyzing: boolean
}

export default function AIAnalysisCard({ recommendation, isAnalyzing }: AIAnalysisCardProps) {
    if (!recommendation && !isAnalyzing) return null

    return (
        <div className="relative group mb-8">
            {/* Animated Glow Effect */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl blur opacity-10 group-hover:opacity-25 transition duration-1000 group-hover:duration-200 animate-gradient-xy"></div>

            <div className="relative glass-card bg-[#0d0d15]/90 border-white/[0.05] p-6 overflow-hidden">
                {/* Background Pattern */}
                <div className="absolute top-0 right-0 p-8 opacity-[0.03] pointer-events-none">
                    <Brain className="h-48 w-48 text-white rotate-12" />
                </div>

                <div className="flex flex-col md:flex-row gap-6 items-center">
                    {/* Left: AI Avatar/Icon */}
                    <div className="relative">
                        <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-indigo-600 to-violet-700 flex items-center justify-center shadow-2xl shadow-indigo-500/40">
                            {isAnalyzing ? (
                                <Cpu className="h-8 w-8 text-white animate-spin-slow" />
                            ) : (
                                <Sparkles className="h-8 w-8 text-white animate-pulse" />
                            )}
                        </div>
                        {!isAnalyzing && (
                            <div className="absolute -top-2 -right-2 h-6 w-6 rounded-full bg-emerald-500 border-4 border-[#0d0d15] flex items-center justify-center">
                                <div className="h-1.5 w-1.5 rounded-full bg-white animate-ping" />
                            </div>
                        )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 text-center md:text-left">
                        <div className="flex items-center justify-center md:justify-start gap-2 mb-2">
                            <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 text-[10px] font-black uppercase tracking-[0.2em] border border-indigo-500/20">
                                SIC ENGINE v4.0
                            </span>
                            <span className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">Neural Analysis</span>
                        </div>

                        {isAnalyzing ? (
                            <div className="space-y-2">
                                <div className="h-6 w-3/4 bg-white/5 rounded animate-pulse" />
                                <div className="h-4 w-1/2 bg-white/5 rounded animate-pulse" />
                            </div>
                        ) : (
                            <>
                                <h3 className="text-xl font-bold text-white mb-2 leading-tight">
                                    {recommendation?.reason}
                                </h3>
                                {recommendation?.best_offer && (
                                    <div className="flex flex-wrap items-center justify-center md:justify-start gap-4">
                                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/5 border border-emerald-500/10">
                                            <span className="text-xs font-medium text-slate-400">Comericiante:</span>
                                            <span className="text-sm font-black text-emerald-400">@{recommendation.best_offer.advertiser}</span>
                                        </div>
                                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-500/5 border border-indigo-500/10">
                                            <span className="text-xs font-medium text-slate-400">Precio Sugerido:</span>
                                            <span className="text-sm font-black text-white font-mono">{recommendation.best_offer.price} VES</span>
                                        </div>
                                    </div>
                                )}
                            </>
                        )}
                    </div>

                    {/* Right: Call to Action */}
                    {!isAnalyzing && (
                        <button className="flex items-center gap-2 px-6 py-3 rounded-xl bg-white text-black font-black text-sm hover:bg-slate-200 transition-all shadow-xl shadow-white/5">
                            <Wand2 className="h-4 w-4" />
                            APLICAR ESTRATEGIA
                        </button>
                    )}
                </div>
            </div>
        </div>
    )
}
