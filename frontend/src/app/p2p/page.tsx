'use client'

import { useState, useEffect, useCallback, useRef } from 'react'
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
    ShieldCheck,
    Brain
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

    // IA P2P Criteria Config States
    const [isCriteriaOpen, setIsCriteriaOpen] = useState(false)
    const [profile, setProfile] = useState<string>('balanced')
    const [priceWeight, setPriceWeight] = useState<number>(0.5)
    const [safetyWeight, setSafetyWeight] = useState<number>(0.5)
    const [minCompletionRate, setMinCompletionRate] = useState<number>(90)
    const [minOrdersCount, setMinOrdersCount] = useState<number>(10)
    const [onlyVerified, setOnlyVerified] = useState<boolean>(false)
    const [strictLimits, setStrictLimits] = useState<boolean>(false)

    // Reference to debounce timer to prevent LLM overload
    const analyzeTimeoutRef = useRef<any>(null)

    const paymentMethods = ["Banesco", "Mercantil", "Pago Movil", "Provincial", "BNC", "Bancaribe"]
    const cryptos = ["USDT", "BTC", "ETH", "BNB", "FDUSD"]

    // Engine de Scoring Local (0ms latency - 60fps)
    const computeLocalScores = useCallback((offersList: P2POffer[], currentCriteria?: any) => {
        if (!offersList || offersList.length === 0) return null

        let pWeight = currentCriteria?.priceWeight ?? priceWeight
        let sWeight = currentCriteria?.safetyWeight ?? safetyWeight
        let minComp = currentCriteria?.minCompletionRate ?? minCompletionRate
        let minOrd = currentCriteria?.minOrdersCount ?? minOrdersCount
        let verif = currentCriteria?.onlyVerified ?? onlyVerified

        const activeProfile = currentCriteria?.profile || profile
        if (activeProfile === 'safe') {
            pWeight = 0.2
            sWeight = 0.8
            minComp = 98
            minOrd = 100
            verif = true
        } else if (activeProfile === 'perf') {
            pWeight = 0.8
            sWeight = 0.2
            minComp = 85
            minOrd = 5
            verif = false
        } else if (activeProfile === 'balanced') {
            pWeight = 0.5
            sWeight = 0.5
            minComp = 90
            minOrd = 20
            verif = false
        }

        const isStrict = currentCriteria?.strictLimits ?? strictLimits
        const targetAmt = isStrict && amount ? parseFloat(amount) : null
        
        let bestOffer: P2POffer | null = null
        let bestScore = -1.0
        let riskyAdvertisers: string[] = []

        const prices = offersList.map(o => o.price).filter(p => p > 0)
        const minPrice = prices.length > 0 ? Math.min(...prices) : 1.0
        const maxPrice = prices.length > 0 ? Math.max(...prices) : 1.0

        const isBuy = activeTab === 'buy'

        for (const offer of offersList) {
            const price = offer.price
            const completionRate = offer.completion_rate
            const ordersCount = offer.orders_count || 0
            const isVerified = !!offer.is_verified

            // A. Filtros estrictos generales
            if (completionRate < 80.0 || ordersCount < 5) {
                if (!riskyAdvertisers.includes(offer.advertiser)) {
                    riskyAdvertisers.push(offer.advertiser)
                }
                continue
            }

            // B. Filtros de perfil elegidos
            if (completionRate < minComp) continue
            if (ordersCount < minOrd) continue
            if (verif && !isVerified) continue

            // C. Filtro de límites transaccionales
            if (targetAmt !== null && targetAmt > 0) {
                if (targetAmt < offer.min_amount || targetAmt > offer.max_amount) {
                    continue
                }
            }

            // D. Cálculo de Price Score
            let priceScore = 100.0
            if (maxPrice !== minPrice) {
                if (isBuy) {
                    priceScore = 100.0 * (maxPrice - price) / (maxPrice - minPrice)
                } else {
                    priceScore = 100.0 * (price - minPrice) / (maxPrice - minPrice)
                }
            }

            // E. Cálculo de Safety Score
            const completionScore = completionRate
            const ordersScore = Math.min(100.0, ordersCount / 10.0)
            const merchantScore = isVerified ? 100.0 : 0.0
            const safetyScore = (completionScore * 0.6) + (ordersScore * 0.3) + (merchantScore * 0.1)

            // F. Boost por métodos de pago
            let paymentBoost = 0.0
            if (selectedMethods.length > 0) {
                const hasMatchingMethod = offer.payment_methods.some(m => 
                    selectedMethods.some(pm => m.toLowerCase().includes(pm.toLowerCase()))
                )
                if (hasMatchingMethod) {
                    paymentBoost = 10.0
                }
            }

            const totalScore = Math.min(100.0, Math.max(0.0, (priceScore * pWeight) + (safetyScore * sWeight) + paymentBoost))

            if (totalScore > bestScore) {
                bestScore = totalScore
                bestOffer = offer
            }
        }

        // Fallback robusto en caso de exclusión total
        if (!bestOffer && offersList.length > 0) {
            for (const offer of offersList) {
                if (offer.completion_rate >= 80.0 && (offer.orders_count || 0) >= 5) {
                    const totalScore = (offer.completion_rate * 0.7) + (Math.min(100.0, (offer.orders_count || 0) / 10.0) * 0.3)
                    if (totalScore > bestScore) {
                        bestScore = totalScore
                        bestOffer = offer
                    }
                }
            }
        }

        return {
            best_offer: bestOffer,
            score: Math.round(bestScore * 10) / 10,
            risky_advertisers: riskyAdvertisers,
            reason: aiRecommendation?.reason || "IA analizando coherencia semántica del mercado..."
        }
    }, [activeTab, selectedMethods, amount, priceWeight, safetyWeight, minCompletionRate, minOrdersCount, onlyVerified, strictLimits, profile])

    const analyzeOffers = async (offersList: P2POffer[], currentCriteria?: any) => {
        setIsAnalyzing(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            let pWeight = priceWeight
            let sWeight = safetyWeight
            let minComp = minCompletionRate
            let minOrd = minOrdersCount
            let verif = onlyVerified

            const activeProfile = currentCriteria?.profile || profile
            if (activeProfile === 'safe') {
                pWeight = 0.2
                sWeight = 0.8
                minComp = 98
                minOrd = 100
                verif = true
            } else if (activeProfile === 'perf') {
                pWeight = 0.8
                sWeight = 0.2
                minComp = 85
                minOrd = 5
                verif = false
            } else if (activeProfile === 'balanced') {
                pWeight = 0.5
                sWeight = 0.5
                minComp = 90
                minOrd = 20
                verif = false
            } else {
                pWeight = currentCriteria?.priceWeight ?? priceWeight
                sWeight = currentCriteria?.safetyWeight ?? safetyWeight
                minComp = currentCriteria?.minCompletionRate ?? minCompletionRate
                minOrd = currentCriteria?.minOrdersCount ?? minOrdersCount
                verif = currentCriteria?.onlyVerified ?? onlyVerified
            }

            const reqBody = {
                offers: offersList,
                criteria: {
                    min_completion_rate: minComp,
                    min_orders_count: minOrd,
                    only_verified: verif,
                    price_weight: pWeight,
                    safety_weight: sWeight,
                    target_amount: (currentCriteria?.strictLimits ?? strictLimits) && amount ? parseFloat(amount) : null,
                    preferred_payment_methods: selectedMethods
                }
            }

            const res = await fetch('/api/v1/p2p/analyze', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(reqBody)
            })
            const data = await res.json()
            
            // Conservar el razonamiento del backend y fusionarlo con los scores locales
            setAiRecommendation((prev: any) => ({
                ...prev,
                reason: data.reason,
                best_offer: data.best_offer || prev?.best_offer,
                score: data.score !== undefined ? data.score : prev?.score
            }))
        } catch (e) {
            console.error("Error analyzing offers", e)
        } finally {
            setIsAnalyzing(false)
        }
    }

    // fetchOffers está desacoplado de las dependencias IA. Solo recarga de Binance cuando cambian filtros de red.
    const fetchOffers = useCallback(async () => {
        setLoading(true)
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            const methodsParam = selectedMethods.length > 0 ? `&payment_methods=${selectedMethods.join(',')}` : ''
            const amountParam = amount ? `&amount=${amount}` : ''
            const endpoint = `/api/v1/p2p/${activeTab}?limit=50&asset=${cryptoType}&fiat=${fiatType}${methodsParam}${amountParam}`

            const res = await fetch(endpoint, {
                headers: { 'Authorization': `Bearer ${token}` }
            })
            const data = await res.json()
            const offersList = data.offers || []
            setOffers(offersList)

            // 1. Mostrar de inmediato la recomendación local en 0ms
            if (offersList.length > 0) {
                const localRec = computeLocalScores(offersList)
                if (localRec) {
                    setAiRecommendation(localRec)
                }
                // 2. Disparar razonamiento IA del LLM en background
                analyzeOffers(offersList)
            }

        } catch (e) {
            console.error("Error fetching P2P offers", e)
        } finally {
            setLoading(false)
        }
    }, [activeTab, selectedMethods, cryptoType, fiatType, amount])

    const handleCriteriaChange = (updates: any) => {
        // 1. Recalcular scores localmente al instante (0ms) para respuesta visual inmediata
        const localRec = computeLocalScores(offers, updates)
        if (localRec) {
            setAiRecommendation(localRec)
        }

        // 2. Debouncing de 500ms para evitar saturar el LLM de backend mientras se arrastran sliders
        if (analyzeTimeoutRef.current) {
            clearTimeout(analyzeTimeoutRef.current)
        }

        analyzeTimeoutRef.current = setTimeout(() => {
            if (offers.length > 0) {
                analyzeOffers(offers, updates)
            }
        }, 500)
    }

    const toggleMethod = (method: string) => {
        setSelectedMethods(prev =>
            prev.includes(method) ? prev.filter(m => m !== method) : [...prev, method]
        )
    }

    // Limpiar timeout del ref al desmontar el componente
    useEffect(() => {
        return () => {
            if (analyzeTimeoutRef.current) {
                clearTimeout(analyzeTimeoutRef.current)
            }
        }
    }, [])

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

                {/* Panel Collapsible de Criterios IA P2P */}
                <div className="mb-8 glass-card bg-[#0d0d15]/50 border-white/[0.04] p-5 rounded-2xl">
                    <button 
                        onClick={() => setIsCriteriaOpen(!isCriteriaOpen)} 
                        className="w-full flex items-center justify-between text-left group"
                    >
                        <div className="flex items-center gap-3">
                            <div className="h-8 w-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20 group-hover:scale-105 transition-transform">
                                <Brain className="h-4 w-4" />
                            </div>
                            <div>
                                <h3 className="font-bold text-white text-sm tracking-tight flex items-center gap-2">
                                    Panel de Configuración de Criterios IA P2P
                                    <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 text-[9px] font-black uppercase tracking-wider">PREMIUM</span>
                                </h3>
                                <p className="text-slate-500 text-xs font-medium">Ajusta las ponderaciones y el comportamiento del modelo analítico de SIC Ultra en tiempo real.</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors">
                            <span className="text-xs font-semibold">{isCriteriaOpen ? 'Ocultar Ajustes' : 'Mostrar Ajustes'}</span>
                            <ChevronDown className={`h-4 w-4 transition-transform duration-300 ${isCriteriaOpen ? 'rotate-180' : ''}`} />
                        </div>
                    </button>

                    {isCriteriaOpen && (
                        <div className="mt-6 pt-6 border-t border-white/[0.04] grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
                            {/* Col 1: Perfil IA */}
                            <div className="space-y-4">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-wider">1. Perfil IA de Operación</label>
                                <div className="grid grid-cols-2 gap-2">
                                    {[
                                        { id: 'balanced', label: '⚖️ Balanceado', desc: '50% precio / 50% seguridad' },
                                        { id: 'safe', label: '🛡️ Seguridad Máxima', desc: 'Filtros y comerciantes verificados' },
                                        { id: 'perf', label: '⚡ Alto Rendimiento', desc: 'Mejor precio de tasa VES' },
                                        { id: 'custom', label: '⚙️ Personalizado', desc: 'Ajuste manual de pesos' }
                                    ].map(p => (
                                        <button
                                            key={p.id}
                                            onClick={() => {
                                                setProfile(p.id)
                                                handleCriteriaChange({ profile: p.id })
                                            }}
                                            className={`p-3 rounded-xl border text-left transition-all duration-300 ${
                                                profile === p.id 
                                                    ? 'bg-indigo-500/10 border-indigo-500/40 shadow-lg shadow-indigo-500/5' 
                                                    : 'bg-white/[0.01] border-white/[0.04] hover:bg-white/[0.03]'
                                            }`}
                                        >
                                            <span className={`block text-xs font-black uppercase tracking-tight ${profile === p.id ? 'text-indigo-400' : 'text-slate-300'}`}>
                                                {p.label}
                                            </span>
                                            <span className="block text-[10px] text-slate-500 leading-tight mt-0.5">{p.desc}</span>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            {/* Col 2: Ponderaciones (Precio vs Seguridad) */}
                            <div className="space-y-4">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-wider">2. Peso de Ponderación (Score)</label>
                                <div className="bg-[#12121a]/60 border border-white/[0.03] p-4 rounded-xl space-y-4">
                                    <div className="space-y-2">
                                        <div className="flex justify-between text-xs">
                                            <span className="text-slate-400 font-medium">Prioridad de Precio</span>
                                            <span className="text-indigo-400 font-black font-mono">{Math.round(priceWeight * 100)}%</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.05"
                                            value={priceWeight}
                                            disabled={profile !== 'custom'}
                                            onChange={(e) => {
                                                const val = parseFloat(e.target.value)
                                                setPriceWeight(val)
                                                setSafetyWeight(1 - val)
                                                handleCriteriaChange({ priceWeight: val, safetyWeight: 1 - val })
                                            }}
                                            className="w-full accent-indigo-500 cursor-pointer disabled:opacity-30"
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <div className="flex justify-between text-xs">
                                            <span className="text-slate-400 font-medium">Prioridad de Seguridad</span>
                                            <span className="text-emerald-400 font-black font-mono">{Math.round(safetyWeight * 100)}%</span>
                                        </div>
                                        <input
                                            type="range"
                                            min="0"
                                            max="1"
                                            step="0.05"
                                            value={safetyWeight}
                                            disabled={profile !== 'custom'}
                                            onChange={(e) => {
                                                const val = parseFloat(e.target.value)
                                                setSafetyWeight(val)
                                                setPriceWeight(1 - val)
                                                handleCriteriaChange({ safetyWeight: val, priceWeight: 1 - val })
                                            }}
                                            className="w-full accent-emerald-500 cursor-pointer disabled:opacity-30"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Col 3: Filtros Avanzados y Límites */}
                            <div className="space-y-4">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-wider">3. Reglas de Exclusión</label>
                                <div className="bg-[#12121a]/60 border border-white/[0.03] p-4 rounded-xl space-y-3.5">
                                    {/* Only verified */}
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <span className="block text-xs font-bold text-slate-300">Solo Comerciantes Verificados</span>
                                            <span className="block text-[10px] text-slate-500">Excluye cuentas sin insignia Merchant</span>
                                        </div>
                                        <button
                                            onClick={() => {
                                                const val = !onlyVerified
                                                setOnlyVerified(val)
                                                handleCriteriaChange({ onlyVerified: val })
                                            }}
                                            disabled={profile !== 'custom'}
                                            className={`w-10 h-6 rounded-full p-1 transition-all ${
                                                onlyVerified ? 'bg-indigo-600 flex justify-end' : 'bg-slate-700 flex justify-start'
                                            } disabled:opacity-30`}
                                        >
                                            <span className="w-4 h-4 bg-white rounded-full shadow-md transition-all" />
                                        </button>
                                    </div>

                                    {/* Strict Limits */}
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <span className="block text-xs font-bold text-slate-300">Filtro de Límites Estricto</span>
                                            <span className="block text-[10px] text-slate-500">Alinear anunciante con monto a buscar</span>
                                        </div>
                                        <button
                                            onClick={() => {
                                                const val = !strictLimits
                                                setStrictLimits(val)
                                                handleCriteriaChange({ strictLimits: val })
                                            }}
                                            className={`w-10 h-6 rounded-full p-1 transition-all ${
                                                strictLimits ? 'bg-emerald-600 flex justify-end' : 'bg-slate-700 flex justify-start'
                                            }`}
                                        >
                                            <span className="w-4 h-4 bg-white rounded-full shadow-md transition-all" />
                                        </button>
                                    </div>

                                    {/* Sliders for Min Completion Rate and Orders when custom */}
                                    {profile === 'custom' && (
                                        <div className="pt-2 space-y-2 border-t border-white/[0.04] animate-fade-in">
                                            <div className="flex justify-between text-[10px] text-slate-400">
                                                <span>Tasa Min Finalización</span>
                                                <span className="font-bold font-mono text-slate-200">{minCompletionRate}%</span>
                                            </div>
                                            <input
                                                type="range"
                                                min="80"
                                                max="100"
                                                step="1"
                                                value={minCompletionRate}
                                                onChange={(e) => {
                                                    const val = parseInt(e.target.value)
                                                    setMinCompletionRate(val)
                                                    handleCriteriaChange({ minCompletionRate: val })
                                                }}
                                                className="w-full accent-indigo-500 cursor-pointer h-1"
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    )}
                </div>

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
