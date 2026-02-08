'use client'

import { useState, useEffect, useCallback } from 'react'
import DashboardLayout from '../../components/layout/DashboardLayout'
import P2POfferRow from '../../components/p2p/P2POfferRow'
import P2PStats from '../../components/p2p/P2PStats'
import AIAnalysisCard from '../../components/p2p/AIAnalysisCard'
import {
    ArrowLeftRight,
    ArrowUpRight,
    ArrowDownRight,
    Search,
    Filter,
    ChevronDown,
    Info,
    LayoutGrid,
    List,
    ShieldCheck
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
    is_verified?: boolean
}

export default function P2PPage() {
    const [activeTab, setActiveTab] = useState<'buy' | 'sell'>('buy')
    const [loading, setLoading] = useState(false)
    const [offers, setOffers] = useState<P2POffer[]>([])
    const [selectedMethods, setSelectedMethods] = useState<string[]>([])
    const [aiRecommendation, setAiRecommendation] = useState<any>(null)
    const [isAnalyzing, setIsAnalyzing] = useState(false)
    const [cryptoType, setCryptoType] = useState('USDT')
    const [fiatType, setFiatType] = useState('VES')
    const [amount, setAmount] = useState<string>('')

    const paymentMethods = ["Banesco", "Mercantil", "Pago Movil", "Provincial", "BNC", "Bancaribe"]
    const cryptos = ["USDT", "BTC", "ETH", "BNB", "FDUSD"]

    const fetchOffers = useCallback(async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const methodsParam = selectedMethods.length > 0 ? `&payment_methods=${selectedMethods.join(',')}` : ''
            const amountParam = amount ? `&amount=${amount}` : ''
            const endpoint = `/api/v1/p2p/${activeTab}?limit=50&crypto=${cryptoType}&fiat=${fiatType}${methodsParam}${amountParam}`

            const res = await fetch(endpoint, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const data = await res.json()
            const offersList = data.offers || []
            setOffers(offersList)

            // Trigger AI Analysis
            if (offersList.length > 0) {
                analyzeOffers(offersList)
            }

        } catch (e) {
            console.error("Error fetching P2P offers", e)
        } finally {
            setLoading(false)
        }
    }, [activeTab, selectedMethods, cryptoType, fiatType, amount])

    const analyzeOffers = async (offersList: P2POffer[]) => {
        setIsAnalyzing(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const res = await fetch('/api/v1/p2p/analyze', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(offersList.slice(0, 10))
            })
            const data = await res.json()
            setAiRecommendation(data)
        } catch (e) {
            console.error("Error analyzing offers", e)
        } finally {
            setIsAnalyzing(false)
        }
    }

    const toggleMethod = (method: string) => {
        setSelectedMethods(prev =>
            prev.includes(method) ? prev.filter(m => m !== method) : [...prev, method]
        )
    }

    useEffect(() => {
        fetchOffers()
    }, [fetchOffers])

    // Calc Stats
    const bestBuy = offers.length > 0 ? Math.min(...offers.map(o => o.price)) : 0
    const bestSell = offers.length > 0 ? Math.max(...offers.map(o => o.price)) : 0
    // Hypothetical spread calculation (in real world needs both sides concurrently)
    const spread = bestBuy > 0 && bestSell > 0 ? ((bestSell - bestBuy) / bestBuy) * 100 : 0

    return (
        <DashboardLayout>
            <div className="max-w-[1400px] mx-auto p-4 md:p-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-10">
                    <div className="space-y-2">
                        <div className="flex items-center gap-2">
                            <div className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-500 text-[10px] font-black uppercase tracking-widest border border-amber-500/20">
                                Institutional Grade
                            </div>
                            <div className="flex items-center gap-1 text-slate-500 text-xs font-bold">
                                <ShieldCheck className="h-3 w-3" />
                                Mercado Verificado
                            </div>
                        </div>
                        <h1 className="text-4xl font-black text-white tracking-tight flex items-center gap-4">
                            P2P Marketplace
                            <span className="text-indigo-500 font-light font-mono text-2xl">/ {fiatType}</span>
                        </h1>
                        <p className="text-slate-500 font-medium max-w-xl">
                            Opera de persona a persona con seguridad institucional. Precios actualizados cada 30 segundos mediante IA.
                        </p>
                    </div>

                    <div className="flex items-center gap-2 bg-white/[0.03] p-1.5 rounded-xl border border-white/5">
                        <button className="p-2 text-slate-400 hover:text-white transition-colors">
                            <LayoutGrid className="h-4 w-4" />
                        </button>
                        <button className="p-2 bg-white/10 text-white rounded-lg transition-colors">
                            <List className="h-4 w-4" />
                        </button>
                    </div>
                </div>

                {/* AI & Stats Grid */}
                <AIAnalysisCard recommendation={aiRecommendation} isAnalyzing={isAnalyzing} />
                <P2PStats
                    bestBuy={bestBuy}
                    bestSell={bestSell}
                    spread={spread}
                    isLoading={loading}
                    onRefresh={fetchOffers}
                />

                {/* Trading Controls & Filters */}
                <div className="mb-8 space-y-4">
                    {/* Primary Controls */}
                    <div className="flex flex-col lg:flex-row gap-4 justify-between items-start lg:items-center">
                        <div className="flex items-center gap-2 bg-white/5 p-1 rounded-2xl border border-white/5">
                            <button
                                onClick={() => setActiveTab('buy')}
                                className={`px-8 py-3 rounded-xl font-black text-sm uppercase tracking-wider transition-all duration-300 flex items-center gap-2 ${activeTab === 'buy'
                                    ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20 scale-[1.02]'
                                    : 'text-slate-500 hover:text-white'
                                    }`}
                            >
                                <ArrowDownRight className="h-4 w-4" />
                                Comprar
                            </button>
                            <button
                                onClick={() => setActiveTab('sell')}
                                className={`px-8 py-3 rounded-xl font-black text-sm uppercase tracking-wider transition-all duration-300 flex items-center gap-2 ${activeTab === 'sell'
                                    ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20 scale-[1.02]'
                                    : 'text-slate-500 hover:text-white'
                                    }`}
                            >
                                <ArrowUpRight className="h-4 w-4" />
                                Vender
                            </button>
                        </div>

                        <div className="flex flex-wrap items-center gap-3">
                            <div className="flex items-center gap-1 bg-white/5 rounded-xl p-1 border border-white/5">
                                {cryptos.map(crypto => (
                                    <button
                                        key={crypto}
                                        onClick={() => setCryptoType(crypto)}
                                        className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${cryptoType === crypto ? 'bg-white/10 text-white' : 'text-slate-500 hover:text-slate-300'}`}
                                    >
                                        {crypto}
                                    </button>
                                ))}
                            </div>

                            <div className="relative group">
                                <div className="absolute inset-y-0 left-3 flex items-center pointer-events-none">
                                    <Search className="h-4 w-4 text-slate-500" />
                                </div>
                                <input
                                    type="text"
                                    placeholder="Buscar monto..."
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && fetchOffers()}
                                    onBlur={() => fetchOffers()}
                                    className="bg-[#12121a] border border-white/10 rounded-xl py-2.5 pl-10 pr-4 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:border-indigo-500/50 transition-all w-48 shadow-inner"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Secondary Filters (Payment Methods) */}
                    <div className="flex items-center gap-4 py-4 border-t border-white/[0.03]">
                        <div className="flex items-center gap-2 text-slate-500">
                            <Filter className="h-4 w-4" />
                            <span className="text-[10px] font-black uppercase tracking-tighter">Métodos:</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {paymentMethods.map(method => (
                                <button
                                    key={method}
                                    onClick={() => toggleMethod(method)}
                                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${selectedMethods.includes(method)
                                        ? 'bg-indigo-500/20 border-indigo-500/40 text-indigo-300'
                                        : 'bg-white/5 border-transparent text-slate-500 hover:bg-white/10'
                                        }`}
                                >
                                    {method}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Main Market Table */}
                <div className="relative glass-card overflow-hidden bg-white/[0.015] border-white/5 rounded-3xl">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-white/[0.03] border-b border-white/5">
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Anunciante</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Precio Unitario</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Disponibilidad / Límite</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest">Métodos de Pago</th>
                                    <th className="px-6 py-4 text-[10px] font-black text-slate-500 uppercase tracking-widest text-right">Ejecución</th>
                                </tr>
                            </thead>
                            <tbody>
                                {loading ? (
                                    <tr>
                                        <td colSpan={5} className="py-20 text-center">
                                            <div className="flex flex-col items-center gap-4">
                                                <div className="h-10 w-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
                                                <p className="text-slate-400 font-bold text-sm uppercase tracking-widest animate-pulse">
                                                    Sincronizando con el Libro de órdenes...
                                                </p>
                                            </div>
                                        </td>
                                    </tr>
                                ) : offers.length > 0 ? (
                                    offers.map((offer, i) => (
                                        <P2POfferRow
                                            key={i}
                                            offer={offer}
                                            activeTab={activeTab}
                                            isRecommended={aiRecommendation?.best_offer?.advertiser === offer.advertiser}
                                        />
                                    ))
                                ) : (
                                    <tr>
                                        <td colSpan={5} className="py-20 text-center text-slate-500">
                                            No se encontraron ofertas vigentes para estos criterios.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Footer disclaimer */}
                <div className="mt-8 flex items-center justify-center gap-4 text-slate-600 bg-white/[0.02] p-4 rounded-2xl border border-white/5">
                    <Info className="h-4 w-4" />
                    <p className="text-[10px] font-medium tracking-tight uppercase">
                        SIC ULTRA NO CUSTODIA FONDOS DURANTE LAS TRANSACCIONES P2P. TODAS LAS OPERACIONES ESTÁN SUJETAS A VERIFICACIÓN NEURAL DE RIESGO.
                    </p>
                </div>
            </div>
        </DashboardLayout>
    )
}
