'use client'

import { useState } from 'react'
import Link from 'next/link'
import P2POpportunities from '../../components/dashboard/P2POpportunities'

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
        <main className="min-h-screen bg-sic-dark">
            {/* Header */}
            <header className="border-b border-sic-border px-6 py-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="text-2xl">🪙</Link>
                        <h1 className="text-xl font-bold">💱 Mercado P2P VES</h1>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto p-6">
                {/* AI Opportunities Panel */}
                <div className="mb-8">
                    <P2POpportunities />
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Mejor Compra</p>
                        <p className="text-2xl font-bold text-sic-green">{bestBuy} Bs</p>
                    </div>
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Mejor Venta</p>
                        <p className="text-2xl font-bold text-sic-red">{bestSell} Bs</p>
                    </div>
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Spread</p>
                        <p className="text-2xl font-bold text-sic-purple">{spread}%</p>
                    </div>
                    <div className="glass-card p-4">
                        <p className="text-gray-400 text-sm">Ganancia $100</p>
                        <p className="text-2xl font-bold text-sic-blue">
                            {((parseFloat(spread) / 100) * 100 * bestBuy).toFixed(2)} Bs
                        </p>
                    </div>
                </div>

                {/* Calculator */}
                <div className="glass-card p-6 mb-6">
                    <h2 className="text-lg font-semibold mb-4">🧮 Calculadora de Arbitraje</h2>
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                        <div>
                            <label className="text-sm text-gray-400">Cantidad USDT</label>
                            <input
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(e.target.value)}
                                placeholder="100"
                                className="w-full mt-1 bg-sic-dark border border-sic-border rounded-lg px-4 py-3 text-white"
                            />
                        </div>
                        <div className="bg-sic-dark rounded-lg p-3">
                            <p className="text-gray-400 text-sm">Compras a</p>
                            <p className="text-xl font-bold">{((parseFloat(amount || '0')) * bestBuy).toLocaleString()} Bs</p>
                        </div>
                        <div className="bg-sic-dark rounded-lg p-3">
                            <p className="text-gray-400 text-sm">Vendes a</p>
                            <p className="text-xl font-bold">{((parseFloat(amount || '0')) * bestSell).toLocaleString()} Bs</p>
                        </div>
                        <div className="bg-sic-green/20 rounded-lg p-3 border border-sic-green">
                            <p className="text-sic-green text-sm">Ganancia</p>
                            <p className="text-xl font-bold text-sic-green">
                                {((parseFloat(amount || '0')) * (bestSell - bestBuy)).toFixed(2)} Bs
                            </p>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 mb-6">
                    <button
                        onClick={() => setActiveTab('buy')}
                        className={`px-6 py-3 rounded-lg font-semibold transition-all ${activeTab === 'buy'
                            ? 'bg-sic-green text-black'
                            : 'bg-sic-card text-gray-400'
                            }`}
                    >
                        Comprar USDT
                    </button>
                    <button
                        onClick={() => setActiveTab('sell')}
                        className={`px-6 py-3 rounded-lg font-semibold transition-all ${activeTab === 'sell'
                            ? 'bg-sic-red text-white'
                            : 'bg-sic-card text-gray-400'
                            }`}
                    >
                        Vender USDT
                    </button>
                </div>

                {/* Offers Table */}
                <div className="glass-card overflow-hidden">
                    <table className="w-full">
                        <thead className="bg-sic-dark">
                            <tr>
                                <th className="text-left px-6 py-4 text-gray-400 font-medium">Anunciante</th>
                                <th className="text-left px-6 py-4 text-gray-400 font-medium">Precio</th>
                                <th className="text-left px-6 py-4 text-gray-400 font-medium">Disponible</th>
                                <th className="text-left px-6 py-4 text-gray-400 font-medium">Límites</th>
                                <th className="text-left px-6 py-4 text-gray-400 font-medium">Métodos</th>
                                <th className="text-left px-6 py-4 text-gray-400 font-medium"></th>
                            </tr>
                        </thead>
                        <tbody>
                            {offers.map((offer, i) => (
                                <tr key={i} className="border-t border-sic-border hover:bg-sic-dark/50">
                                    <td className="px-6 py-4">
                                        <p className="font-medium">{offer.advertiser}</p>
                                        <p className="text-xs text-gray-500">{offer.completion_rate}% completados</p>
                                    </td>
                                    <td className="px-6 py-4">
                                        <p className={`text-lg font-bold ${activeTab === 'buy' ? 'text-sic-green' : 'text-sic-red'}`}>
                                            {offer.price} Bs
                                        </p>
                                    </td>
                                    <td className="px-6 py-4">{offer.available} USDT</td>
                                    <td className="px-6 py-4 text-sm text-gray-400">
                                        {offer.min_amount} - {offer.max_amount} USDT
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex flex-wrap gap-1">
                                            {offer.payment_methods.map((m, j) => (
                                                <span key={j} className="px-2 py-1 bg-sic-border rounded text-xs">
                                                    {m}
                                                </span>
                                            ))}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <button className={`px-4 py-2 rounded-lg font-medium ${activeTab === 'buy'
                                            ? 'bg-sic-green text-black'
                                            : 'bg-sic-red text-white'
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
        </main>
    )
}
