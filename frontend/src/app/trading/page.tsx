'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

const SYMBOLS = [
    { symbol: 'BTCUSDT', name: 'Bitcoin', icon: '₿' },
    { symbol: 'ETHUSDT', name: 'Ethereum', icon: 'Ξ' },
    { symbol: 'BNBUSDT', name: 'BNB', icon: '⬡' },
    { symbol: 'SOLUSDT', name: 'Solana', icon: '◎' },
    { symbol: 'XRPUSDT', name: 'XRP', icon: '✕' },
    { symbol: 'ADAUSDT', name: 'Cardano', icon: '₳' },
]

interface OrderForm {
    side: 'BUY' | 'SELL'
    quantity: string
    price: string
}

export default function TradingPage() {
    const [selectedSymbol, setSelectedSymbol] = useState(SYMBOLS[0])
    const [mode, setMode] = useState<'practice' | 'real'>('practice')
    const [currentPrice, setCurrentPrice] = useState(45000)
    const [change24h, setChange24h] = useState(2.5)
    const [order, setOrder] = useState<OrderForm>({ side: 'BUY', quantity: '', price: '' })
    const [balance, setBalance] = useState({ USDT: 100, BTC: 0 })

    // Simulated price updates
    useEffect(() => {
        const prices: Record<string, number> = {
            BTCUSDT: 45000,
            ETHUSDT: 2500,
            BNBUSDT: 320,
            SOLUSDT: 95,
            XRPUSDT: 0.55,
            ADAUSDT: 0.45,
        }
        setCurrentPrice(prices[selectedSymbol.symbol] || 0)
    }, [selectedSymbol])

    const handleOrder = () => {
        if (!order.quantity) {
            alert('Ingresa una cantidad')
            return
        }

        const qty = parseFloat(order.quantity)
        const total = qty * currentPrice

        if (order.side === 'BUY' && total > balance.USDT) {
            alert('Saldo USDT insuficiente')
            return
        }

        alert(`${mode === 'practice' ? '🎮 PRÁCTICA: ' : '⚔️ REAL: '}${order.side} ${qty} @ $${currentPrice}`)
    }

    return (
        <main className="min-h-screen bg-sic-dark">
            {/* Header */}
            <header className="border-b border-sic-border px-6 py-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="text-2xl">🪙</Link>
                        <h1 className="text-xl font-bold">Trading</h1>

                        {/* Symbol Selector */}
                        <select
                            value={selectedSymbol.symbol}
                            onChange={(e) => setSelectedSymbol(SYMBOLS.find(s => s.symbol === e.target.value) || SYMBOLS[0])}
                            className="bg-sic-card border border-sic-border rounded-lg px-4 py-2 text-white"
                        >
                            {SYMBOLS.map(s => (
                                <option key={s.symbol} value={s.symbol}>
                                    {s.icon} {s.symbol}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Mode Toggle */}
                    <div className="flex items-center gap-4">
                        <div className="glass-card flex p-1">
                            <button
                                onClick={() => setMode('practice')}
                                className={`px-4 py-2 rounded-lg transition-all ${mode === 'practice'
                                        ? 'bg-sic-green text-black font-semibold'
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                🎮 Práctica
                            </button>
                            <button
                                onClick={() => setMode('real')}
                                className={`px-4 py-2 rounded-lg transition-all ${mode === 'real'
                                        ? 'bg-sic-red text-white font-semibold'
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                            >
                                ⚔️ Real
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto p-6">
                {/* Price Header */}
                <div className="flex items-center gap-6 mb-6">
                    <div>
                        <p className="text-gray-400 text-sm">{selectedSymbol.name}</p>
                        <p className="text-4xl font-bold text-white">
                            ${currentPrice.toLocaleString()}
                        </p>
                    </div>
                    <div className={`px-3 py-1 rounded-lg ${change24h >= 0 ? 'bg-sic-green/20 text-sic-green' : 'bg-sic-red/20 text-sic-red'}`}>
                        {change24h >= 0 ? '+' : ''}{change24h}%
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Chart */}
                    <div className="lg:col-span-2 glass-card p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-semibold">📈 {selectedSymbol.symbol}</h2>
                            <div className="flex gap-2">
                                {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
                                    <button
                                        key={tf}
                                        className="px-3 py-1 text-sm rounded bg-sic-border hover:bg-sic-green hover:text-black transition-all"
                                    >
                                        {tf}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="bg-sic-dark rounded-lg h-[400px] flex items-center justify-center border border-sic-border">
                            <p className="text-gray-500">📊 Gráfico TradingView</p>
                        </div>
                    </div>

                    {/* Order Form */}
                    <div className="glass-card p-6">
                        <h2 className="text-lg font-semibold mb-4">💹 Nueva Orden</h2>

                        {/* Balance */}
                        <div className="bg-sic-dark rounded-lg p-3 mb-4">
                            <p className="text-gray-400 text-sm">Balance disponible</p>
                            <p className="text-xl font-bold text-sic-green">${balance.USDT.toFixed(2)} USDT</p>
                        </div>

                        {/* Side Toggle */}
                        <div className="grid grid-cols-2 gap-2 mb-4">
                            <button
                                onClick={() => setOrder({ ...order, side: 'BUY' })}
                                className={`py-3 rounded-lg font-semibold transition-all ${order.side === 'BUY'
                                        ? 'bg-sic-green text-black'
                                        : 'bg-sic-border text-gray-400'
                                    }`}
                            >
                                Comprar
                            </button>
                            <button
                                onClick={() => setOrder({ ...order, side: 'SELL' })}
                                className={`py-3 rounded-lg font-semibold transition-all ${order.side === 'SELL'
                                        ? 'bg-sic-red text-white'
                                        : 'bg-sic-border text-gray-400'
                                    }`}
                            >
                                Vender
                            </button>
                        </div>

                        {/* Quantity Input */}
                        <div className="mb-4">
                            <label className="text-sm text-gray-400">Cantidad</label>
                            <input
                                type="number"
                                value={order.quantity}
                                onChange={(e) => setOrder({ ...order, quantity: e.target.value })}
                                placeholder="0.001"
                                className="w-full mt-1 bg-sic-dark border border-sic-border rounded-lg px-4 py-3 text-white"
                            />
                        </div>

                        {/* Price Display */}
                        <div className="mb-4">
                            <label className="text-sm text-gray-400">Precio (Market)</label>
                            <div className="w-full mt-1 bg-sic-dark border border-sic-border rounded-lg px-4 py-3 text-white">
                                ${currentPrice.toLocaleString()}
                            </div>
                        </div>

                        {/* Total */}
                        <div className="mb-4">
                            <label className="text-sm text-gray-400">Total</label>
                            <div className="w-full mt-1 bg-sic-dark border border-sic-border rounded-lg px-4 py-3 text-white font-bold">
                                ${(parseFloat(order.quantity || '0') * currentPrice).toFixed(2)} USDT
                            </div>
                        </div>

                        {/* Submit Button */}
                        <button
                            onClick={handleOrder}
                            className={`w-full py-4 rounded-lg font-bold transition-all ${order.side === 'BUY'
                                    ? 'bg-sic-green text-black hover:bg-sic-green/80'
                                    : 'bg-sic-red text-white hover:bg-sic-red/80'
                                }`}
                        >
                            {order.side === 'BUY' ? '🟢 Comprar' : '🔴 Vender'} {selectedSymbol.symbol.replace('USDT', '')}
                        </button>

                        {mode === 'practice' && (
                            <p className="text-center text-xs text-gray-500 mt-3">
                                🎮 Modo práctica - Sin dinero real
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </main>
    )
}
