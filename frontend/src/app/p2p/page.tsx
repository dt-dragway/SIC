'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
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
    orders_count?: number
}

export default function P2PPage() {
    const [activeTab, setActiveTab] = useState<'buy' | 'sell'>('buy')
    const [amount, setAmount] = useState('')
    const [loading, setLoading] = useState(false)
    const [offers, setOffers] = useState<P2POffer[]>([])

    // Filters
    const [selectedMethods, setSelectedMethods] = useState<string[]>([])

    // AI Analysis
    const [aiRecommendation, setAiRecommendation] = useState<any>(null)
    const [analyzing, setAnalyzing] = useState(false)

    const paymentMethods = ["Banesco", "Mercantil", "Pago Movil", "Provincial"]

    const toggleMethod = (method: string) => {
        if (selectedMethods.includes(method)) {
            setSelectedMethods(selectedMethods.filter(m => m !== method))
        } else {
            setSelectedMethods([...selectedMethods, method])
        }
    }

    const fetchOffers = async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const methodsParam = selectedMethods.length > 0 ? `&payment_methods=${selectedMethods.join(',')}` : ''
            const endpoint = `/api/v1/p2p/${activeTab}?limit=50${methodsParam}`

            const res = await fetch(endpoint, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const data = await res.json()
            setOffers(data.offers || [])

            // Trigger AI Analysis
            analyzeOffers(data.offers || [])

        } catch (e) {
            console.error("Error fetching P2P offers", e)
        } finally {
            setLoading(false)
        }
    }

    const analyzeOffers = async (offersList: P2POffer[]) => {
        if (offersList.length === 0) return
        setAnalyzing(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const res = await fetch('/api/v1/p2p/analyze', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(offersList.slice(0, 10)) // Analyze top 10
            })
            const data = await res.json()
            setAiRecommendation(data)
        } catch (e) {
            console.error("Error analyzing offers", e)
        } finally {
            setAnalyzing(false)
        }
    }

    // Initial load and filter change
    useEffect(() => {
        fetchOffers()
    }, [activeTab, selectedMethods])

    // Stats
    const bestBuy = offers.length > 0 ? Math.min(...offers.map(o => o.price)) : 0
    const bestSell = offers.length > 0 ? Math.max(...offers.map(o => o.price)) : 0
    // Note: Spread calculation usually needs both buy and sell markets, here we only show partial if only one loaded

    return (
        <DashboardLayout>

            <div className="max-w-7xl mx-auto p-6">
                <div className="flex items-center gap-3 mb-8">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                        <ArrowLeftRight className="text-white h-6 w-6" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-white">Mercado P2P <span className="text-indigo-400">VES - Real Time</span></h1>
                        <p className="text-slate-400 text-sm">Mostrando {offers.length} ofertas en tiempo real</p>
                    </div>
                </div>

                {/* AI Recommendation Card */}
                {aiRecommendation && (
                    <div className="mb-8 relative overflow-hidden rounded-2xl border border-indigo-500/30 bg-indigo-500/5 p-6">
                        <div className="absolute top-0 right-0 p-4 opacity-10">
                            <Wallet className="h-24 w-24 text-indigo-400" />
                        </div>
                        <div className="relative z-10">
                            <h3 className="text-lg font-bold text-indigo-300 flex items-center gap-2">
                                <span className="h-2 w-2 rounded-full bg-indigo-400 animate-pulse"></span>
                                Recomendación Inteligente
                            </h3>
                            <p className="text-white mt-2 text-lg">
                                {aiRecommendation.reason}
                            </p>
                            {aiRecommendation.best_offer && (
                                <div className="mt-4 flex items-center gap-4">
                                    <div className="px-3 py-1 bg-indigo-500/20 rounded border border-indigo-500/30 text-indigo-300 text-sm">
                                        @{aiRecommendation.best_offer.advertiser}
                                    </div>
                                    <div className="text-emerald-400 font-bold font-mono">
                                        {aiRecommendation.best_offer.price} Bs
                                    </div>
                                    <div className="text-slate-400 text-sm">
                                        {aiRecommendation.best_offer.completion_rate}% Completado
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Stats Cards (Simplified for now or need separate fetch for spread) */}

                {/* Filters */}
                <div className="mb-6 flex flex-wrap gap-2">
                    {paymentMethods.map(method => (
                        <button
                            key={method}
                            onClick={() => toggleMethod(method)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedMethods.includes(method)
                                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/20'
                                : 'bg-white/5 text-slate-400 hover:bg-white/10'
                                }`}
                        >
                            {method}
                        </button>
                    ))}
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
                    {loading ? (
                        <div className="p-8 text-center text-slate-500 animate-pulse">Cargando ofertas en tiempo real...</div>
                    ) : (
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
                                        <tr key={i} className={`hover:bg-white/[0.02] transition-colors ${aiRecommendation?.best_offer?.advertiser === offer.advertiser ? 'bg-indigo-500/10' : ''}`}>
                                            <td className="px-6 py-5">
                                                <div className="flex items-center gap-3">
                                                    <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-slate-700 to-slate-600 flex items-center justify-center text-xs font-bold text-white">
                                                        {offer.advertiser.charAt(0)}
                                                    </div>
                                                    <div>
                                                        <p className="font-medium text-white flex items-center gap-2">
                                                            {offer.advertiser}
                                                            {aiRecommendation?.best_offer?.advertiser === offer.advertiser && (
                                                                <span className="px-1.5 py-0.5 rounded bg-indigo-500 text-[10px] text-white">RECOMENDADO</span>
                                                            )}
                                                        </p>
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
                                            <td className="px-6 py-5 text-slate-300 font-mono">{Number(offer.available).toLocaleString()} <span className="text-slate-500 text-xs">USDT</span></td>
                                            <td className="px-6 py-5 text-sm text-slate-400">
                                                {Number(offer.min_amount).toLocaleString()} - {Number(offer.max_amount).toLocaleString()} USDT
                                            </td>
                                            <td className="px-6 py-5">
                                                <div className="flex flex-wrap gap-2">
                                                    {offer.payment_methods.slice(0, 3).map((m, j) => (
                                                        <span key={j} className="px-2 py-1 bg-white/5 border border-white/5 rounded text-[10px] text-slate-300 uppercase tracking-wide">
                                                            {m}
                                                        </span>
                                                    ))}
                                                    {offer.payment_methods.length > 3 && (
                                                        <span className="px-2 py-1 bg-white/5 border border-white/5 rounded text-[10px] text-slate-500 uppercase tracking-wide">
                                                            +{offer.payment_methods.length - 3}
                                                        </span>
                                                    )}
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
                    )}
                </div>
            </div>
        </DashboardLayout>
    )
}
