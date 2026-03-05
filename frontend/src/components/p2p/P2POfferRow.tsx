'use client'

import React from 'react'
import { CheckCircle2, ShieldCheck, Clock, ThumbsUp } from 'lucide-react'

interface P2POffer {
    advertiser: string
    price: number
    available: number
    min_amount: number
    max_amount: number
    payment_methods: string[]
    completion_rate: number
    orders_count?: number
    is_verified?: boolean
}

interface P2POfferRowProps {
    offer: P2POffer
    activeTab: 'buy' | 'sell'
    isRecommended?: boolean
}

export default function P2POfferRow({ offer, activeTab, isRecommended }: P2POfferRowProps) {
    return (
        <tr className={`group transition-all duration-300 border-b border-white/[0.03] hover:bg-white/[0.02] ${isRecommended ? 'bg-indigo-500/[0.03]' : ''}`}>
            {/* Anunciante */}
            <td className="px-6 py-5">
                <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                        <span className="font-bold text-indigo-400 hover:text-indigo-300 cursor-pointer transition-colors text-base">
                            {offer.advertiser}
                        </span>
                        {offer.is_verified && (
                            <ShieldCheck className="h-4 w-4 text-amber-400" fill="currentColor" fillOpacity={0.2} />
                        )}
                        {isRecommended && (
                            <span className="px-1.5 py-0.5 rounded-sm bg-indigo-500/20 text-indigo-400 text-[10px] font-bold tracking-tighter uppercase border border-indigo-500/30">
                                Best Choice
                            </span>
                        )}
                    </div>
                    <div className="flex items-center gap-3 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                            <ThumbsUp className="h-3 w-3" />
                            {offer.orders_count || 1200} órdenes
                        </span>
                        <span className="w-1 h-1 rounded-full bg-slate-700"></span>
                        <span className="text-slate-400 font-medium">{offer.completion_rate}% completado</span>
                    </div>
                </div>
            </td>

            {/* Precio */}
            <td className="px-6 py-5">
                <div className="flex flex-col">
                    <div className="flex items-baseline gap-1">
                        <span className="text-xl font-black text-white font-mono">
                            {offer.price.toLocaleString('es-VE', { minimumFractionDigits: 2 })}
                        </span>
                        <span className="text-xs font-bold text-slate-500">VES</span>
                    </div>
                </div>
            </td>

            {/* Disponibilidad y Límites */}
            <td className="px-6 py-5">
                <div className="space-y-1.5">
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500 font-medium w-16 uppercase tracking-tighter">Disponible</span>
                        <span className="text-sm text-slate-300 font-mono font-bold">
                            {offer.available.toLocaleString()} <span className="text-[10px] text-slate-500">USDT</span>
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="text-xs text-slate-500 font-medium w-16 uppercase tracking-tighter">Límite</span>
                        <span className="text-sm text-slate-400 font-mono">
                            {offer.min_amount.toLocaleString()} - {offer.max_amount.toLocaleString()} <span className="text-[10px] text-slate-600">VES</span>
                        </span>
                    </div>
                </div>
            </td>

            {/* Métodos de Pago */}
            <td className="px-6 py-5">
                <div className="flex flex-wrap gap-1.5 max-w-[200px]">
                    {offer.payment_methods.map((method, idx) => (
                        <div
                            key={idx}
                            className="flex items-center gap-1.5 px-2 py-1 rounded bg-white/[0.03] border border-white/[0.05] group-hover:border-white/[0.1] transition-colors"
                        >
                            <div className={`w-1 h-3 rounded-full ${method.toLowerCase().includes('banesco') ? 'bg-emerald-500' :
                                    method.toLowerCase().includes('mercantil') ? 'bg-blue-500' :
                                        method.toLowerCase().includes('pago movil') ? 'bg-orange-500' : 'bg-slate-500'
                                }`} />
                            <span className="text-[10px] font-bold text-slate-300 uppercase letter tracking-tight">
                                {method}
                            </span>
                        </div>
                    ))}
                </div>
            </td>

            {/* Acción */}
            <td className="px-6 py-5 text-right">
                <button
                    className={`relative overflow-hidden group/btn px-8 py-2.5 rounded-lg font-black text-sm uppercase tracking-wider transition-all duration-300 ${activeTab === 'buy'
                            ? 'bg-emerald-500 text-black hover:bg-emerald-400 hover:shadow-[0_0_20px_rgba(16,185,129,0.3)]'
                            : 'bg-rose-500 text-white hover:bg-rose-400 hover:shadow-[0_0_20px_rgba(244,63,94,0.3)]'
                        }`}
                >
                    <span className="relative z-10">
                        {activeTab === 'buy' ? 'Comprar USDT' : 'Vender USDT'}
                    </span>
                    <div className="absolute inset-0 bg-white/20 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300" />
                </button>
            </td>
        </tr>
    )
}
