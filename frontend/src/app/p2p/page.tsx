'use client'

import { useState } from 'react'
import Header from '../../components/layout/Header'
import P2POpportunities from '../../components/dashboard/P2POpportunities'
import {
    Calculator,
    ArrowLeftRight,
    ArrowUpRight,
    ArrowDownRight,
    Wallet,
    Search,
    Filter,
    CheckCircle2,
    TrendingUp,
    DollarSign,
    Percent
} from 'lucide-react'

interface P2POffer {
    advertiser: string
    price: number
    available: number
    min_amount: number
    max_amount: number
    payment_methods: string[]
    completion_rate: number
}

export default function P2PPage() {
    const [activeTab, setActiveTab] = useState<'buy' | 'sell'>('buy')
    const [amount, setAmount] = useState('')

    // Demo data
    const buyOffers: P2POffer[] = [
        { advertiser: 'CryptoVzla', price: 36.50, available: 1500, min_amount: 10, max_amount: 500, payment_methods: ['Banesco', 'Mercantil'], completion_rate: 98.5 },
        { advertiser: 'BolívarEx', price: 36.45, available: 2000, min_amount: 50, max_amount: 1000, payment_methods: ['Provincial'], completion_rate: 99.1 },
        { advertiser: 'VESTrader', price: 36.55, available: 800, min_amount: 20, max_amount: 400, payment_methods: ['Pago Móvil'], completion_rate: 97.2 },
    ]

    const sellOffers: P2POffer[] = [
        { advertiser: 'VESMoney', price: 37.20, available: 1200, min_amount: 10, max_amount: 600, payment_methods: ['Banesco'], completion_rate: 99.0 },
        { advertiser: 'CryptoVzla', price: 37.15, available: 900, min_amount: 20, max_amount: 500, payment_methods: ['Mercantil', 'Banesco'], completion_rate: 98.5 },
    ]

    const offers = activeTab === 'buy' ? buyOffers : sellOffers
    const bestBuy = 36.45
    const bestSell = 37.20
    const spread = ((bestSell - bestBuy) / bestBuy * 100).toFixed(2)

    return (
        <main className="min-h-screen bg-[#0B0E14] text-slate-100 font-sans selection:bg-cyan-500/30">
            <Header />

            <div className="max-w-7xl mx-auto p-6">
                <div className="flex items-center gap-3 mb-8">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <ArrowLeftRight className="text-white h-6 w-6" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Mercado P2P <span className="text-indigo-400">VES</span></h1>
                        <p className="text-slate-400 text-sm">Arbitraje inteligente en tiempo real</p>
                    </div>
                </div>

                {/* AI Opportunities Panel */}
                <div className="mb-8">
                    <P2POpportunities />
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-emerald-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <TrendingUp className="h-10 w-10" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Mejor Compra</p>
                        <p className="text-3xl font-bold text-emerald-400 tracking-tight">{bestBuy} <span className="text-sm font-normal text-slate-500">Bs</span></p>
                    </div>
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-rose-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <TrendingUp className="h-10 w-10 transform rotate-180" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Mejor Venta</p>
                        <p className="text-3xl font-bold text-rose-400 tracking-tight">{bestSell} <span className="text-sm font-normal text-slate-500">Bs</span></p>
                    </div>
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-violet-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Percent className="h-10 w-10" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Spread Actual</p>
                        <p className="text-3xl font-bold text-violet-400 tracking-tight">{spread}%</p>
                    </div>
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl relative overflow-hidden group hover:border-cyan-500/30 transition-all">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <DollarSign className="h-10 w-10" />
                        </div>
                        <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">Ganancia /$100</p>
                        <p className="text-3xl font-bold text-cyan-400 tracking-tight">
                            {((parseFloat(spread) / 100) * 100 * bestBuy).toFixed(2)} <span className="text-sm font-normal text-slate-500">Bs</span>
                        </p>
                    </div>
                </div>

                {/* Calculator */}
                <div className="glass-card p-8 mb-8 border border-white/5 bg-white/[0.02] rounded-2xl">
                    <h2 className="text-lg font-semibold mb-6 text-white flex items-center gap-2">
                        <Calculator className="h-5 w-5 text-amber-400" />
                        Calculadora de Arbitraje
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
                        <div>
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">Cantidad USDT</label>
                            <div className="relative">
                                <span className="absolute left-4 top-3 text-slate-500">$</span>
                                <input
                                    type="number"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    placeholder="100"
                                    className="w-full bg-black/20 border border-white/10 rounded-xl pl-8 pr-4 py-3 text-white focus:outline-none focus:border-indigo-500/50 focus:bg-white/5 transition-all"
                                />
                            </div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                            <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Compras a</p>
                            <p className="text-xl font-bold text-white font-mono">{((parseFloat(amount || '0')) * bestBuy).toLocaleString()} <span className="text-xs text-slate-500">Bs</span></p>
                        </div>
                        <div className="bg-white/5 rounded-xl p-3 border border-white/5">
                            <p className="text-slate-400 text-xs uppercase tracking-wider mb-1">Vendes a</p>
                            <p className="text-xl font-bold text-white font-mono">{((parseFloat(amount || '0')) * bestSell).toLocaleString()} <span className="text-xs text-slate-500">Bs</span></p>
                        </div>
                        <div className="bg-emerald-500/10 rounded-xl p-3 border border-emerald-500/20 relative overflow-hidden">
                            <div className="absolute inset-0 bg-emerald-500/5 blur-xl"></div>
                            <p className="text-emerald-400 text-xs uppercase tracking-wider mb-1 relative z-10">Ganancia Neta</p>
                            <p className="text-xl font-bold text-emerald-400 font-mono relative z-10 flex items-center gap-1">
                                +{((parseFloat(amount || '0')) * (bestSell - bestBuy)).toFixed(2)} <span className="text-xs opacity-70">Bs</span>
                            </p>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-4 mb-6">
                    <button
                        onClick={() => setActiveTab('buy')}
                        className={`px-8 py-3 rounded-xl font-bold transition-all text-sm uppercase tracking-wide flex items-center gap-2 ${activeTab === 'buy'
                            ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20'
                            : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'
                            }`}
                    >
                        <ArrowDownRight className="h-4 w-4" />
                        Comprar USDT
                    </button>
                    <button
                        onClick={() => setActiveTab('sell')}
                        className={`px-8 py-3 rounded-xl font-bold transition-all text-sm uppercase tracking-wide flex items-center gap-2 ${activeTab === 'sell'
                            ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                            : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'
                            }`}
                    >
                        <ArrowUpRight className="h-4 w-4" />
                        Vender USDT
                    </button>
                </div>

                {/* Offers Table */}
                <div className="glass-card overflow-hidden border border-white/5 bg-white/[0.02] rounded-2xl">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-black/20 border-b border-white/5">
                                <tr>
                                    <th className="text-left px-6 py-5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Anunciante</th>
                                    <th className="text-left px-6 py-5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Precio</th>
                                    <th className="text-left px-6 py-5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Disponible</th>
                                    <th className="text-left px-6 py-5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Límites</th>
                                    <th className="text-left px-6 py-5 text-xs font-semibold text-slate-400 uppercase tracking-wider">Métodos</th>
                                    <th className="text-left px-6 py-5 text-xs font-semibold text-slate-400 uppercase tracking-wider"></th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {offers.map((offer, i) => (
                                    <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                                        <td className="px-6 py-5">
                                            <div className="flex items-center gap-3">
                                                <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-slate-700 to-slate-600 flex items-center justify-center text-xs font-bold text-white">
                                                    {offer.advertiser.charAt(0)}
                                                </div>
                                                <div>
                                                    <p className="font-medium text-white">{offer.advertiser}</p>
                                                    <p className="text-xs text-slate-500 flex items-center gap-1">
                                                        <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                                                        {offer.completion_rate}% completado
                                                    </p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-5">
                                            <p className={`text-xl font-bold font-mono ${activeTab === 'buy' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                {offer.price} <span className="text-xs text-slate-500 font-sans">Bs</span>
                                            </p>
                                        </td>
                                        <td className="px-6 py-5 text-slate-300 font-mono">{offer.available} <span className="text-slate-500 text-xs">USDT</span></td>
                                        <td className="px-6 py-5 text-sm text-slate-400">
                                            {offer.min_amount} - {offer.max_amount} USDT
                                        </td>
                                        <td className="px-6 py-5">
                                            <div className="flex flex-wrap gap-2">
                                                {offer.payment_methods.map((m, j) => (
                                                    <span key={j} className="px-2 py-1 bg-white/5 border border-white/5 rounded text-[10px] text-slate-300 uppercase tracking-wide">
                                                        {m}
                                                    </span>
                                                ))}
                                            </div>
                                        </td>
                                        <td className="px-6 py-5 text-right">
                                            <button className={`px-6 py-2 rounded-lg font-bold text-sm transition-all shadow-lg ${activeTab === 'buy'
                                                ? 'bg-emerald-500 text-black hover:bg-emerald-400 shadow-emerald-500/10'
                                                : 'bg-rose-500 text-white hover:bg-rose-400 shadow-rose-500/10'
                                                }`}>
                                                {activeTab === 'buy' ? 'Comprar' : 'Vender'}
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    )
}
