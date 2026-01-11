'use client'

import { useState, useEffect } from 'react'
import Header from '../../components/layout/Header'
import {
    TrendingUp,
    TrendingDown,
    Clock,
    BarChart2,
    Zap,
    Wallet,
    ArrowUpRight,
    ArrowDownRight,
    Search,
    ChevronDown,
    Gamepad2,
    Swords
} from 'lucide-react'
import { toast } from 'sonner'

const SYMBOLS = [
    { symbol: 'BTCUSDT', name: 'Bitcoin', icon: 'BTC' },
    { symbol: 'ETHUSDT', name: 'Ethereum', icon: 'ETH' },
    { symbol: 'BNBUSDT', name: 'BNB', icon: 'BNB' },
    { symbol: 'SOLUSDT', name: 'Solana', icon: 'SOL' },
    { symbol: 'XRPUSDT', name: 'XRP', icon: 'XRP' },
    { symbol: 'ADAUSDT', name: 'Cardano', icon: 'ADA' },
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
            toast.error('Por favor ingresa una cantidad válida')
            return
        }

        const qty = parseFloat(order.quantity)
        const total = qty * currentPrice

        if (order.side === 'BUY' && total > balance.USDT) {
            toast.error('Saldo USDT insuficiente para esta operación')
            return
        }

        const message = `${order.side === 'BUY' ? 'Compra' : 'Venta'} de ${qty} ${selectedSymbol.symbol.replace('USDT', '')} ejecutada correctamente`

        if (mode === 'practice') {
            toast.success('Orden de Práctica Exitosa', { description: message })
        } else {
            toast.success('Orden Real Enviada', { description: 'Tu orden ha sido enviada al mercado' })
        }
    }

    return (
        <main className="min-h-screen bg-[#0B0E14] text-slate-100 font-sans selection:bg-cyan-500/30">
            <Header />

            <div className="max-w-7xl mx-auto p-6">
                {/* Top Bar: Price & Selector */}
                <div className="flex flex-col md:flex-row justify-between items-center gap-6 mb-8">
                    <div className="flex items-center gap-6">
                        {/* Symbol Selector */}
                        <div className="relative group">
                            <select
                                value={selectedSymbol.symbol}
                                onChange={(e) => setSelectedSymbol(SYMBOLS.find(s => s.symbol === e.target.value) || SYMBOLS[0])}
                                className="appearance-none bg-white/5 border border-white/10 hover:border-cyan-500/50 rounded-xl pl-5 pr-12 py-3 text-white font-medium focus:outline-none transition-all cursor-pointer min-w-[180px]"
                            >
                                {SYMBOLS.map(s => (
                                    <option key={s.symbol} value={s.symbol} className="bg-slate-900 text-white">
                                        {s.symbol}
                                    </option>
                                ))}
                            </select>
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 group-hover:text-cyan-400 transition-colors">
                                <ChevronDown className="h-4 w-4" />
                            </div>
                        </div>

                        {/* Price Info */}
                        <div>
                            <p className="text-slate-400 text-xs font-medium uppercase tracking-wider mb-1">{selectedSymbol.name}</p>
                            <div className="flex items-baseline gap-3">
                                <p className="text-3xl font-bold text-white tracking-tight">
                                    ${currentPrice.toLocaleString()}
                                </p>
                                <div className={`flex items-center gap-1 px-2 py-0.5 rounded-lg text-xs font-bold ${change24h >= 0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                    {change24h >= 0 ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                                    {change24h}%
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Mode Toggle */}
                    <div className="bg-white/5 p-1 rounded-lg border border-white/10 flex relative">
                        <div className={`absolute top-1 bottom-1 w-[calc(50%-4px)] bg-gradient-to-r transition-all duration-300 rounded-md shadow-sm ${mode === 'practice'
                            ? 'left-1 from-emerald-500/20 to-emerald-600/20 border border-emerald-500/30'
                            : 'left-[50%] from-rose-500/20 to-rose-600/20 border border-rose-500/30'
                            }`}></div>

                        <button
                            onClick={() => setMode('practice')}
                            className={`relative z-10 flex items-center gap-2 px-6 py-2 rounded-md text-sm font-medium transition-all ${mode === 'practice' ? 'text-emerald-400' : 'text-slate-400 hover:text-slate-200'
                                }`}
                        >
                            <Gamepad2 className="h-4 w-4" />
                            Práctica
                        </button>
                        <button
                            onClick={() => setMode('real')}
                            className={`relative z-10 flex items-center gap-2 px-6 py-2 rounded-md text-sm font-medium transition-all ${mode === 'real' ? 'text-rose-400' : 'text-slate-400 hover:text-slate-200'
                                }`}
                        >
                            <Swords className="h-4 w-4" />
                            Real
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Chart */}
                    <div className="lg:col-span-2 glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl md:min-h-[600px] flex flex-col">
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-lg font-semibold flex items-center gap-2 text-white">
                                <BarChart2 className="h-5 w-5 text-cyan-400" />
                                Gráfico de Mercado
                            </h2>
                            <div className="flex bg-white/5 p-1 rounded-lg gap-1">
                                {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
                                    <button
                                        key={tf}
                                        className="px-3 py-1 text-xs rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-all font-medium"
                                    >
                                        {tf}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="flex-1 bg-black/40 rounded-xl border border-white/5 flex items-center justify-center relative overflow-hidden group">
                            {/* Grid decorative background */}
                            <div className="absolute inset-0 opacity-20" style={{ backgroundImage: 'linear-gradient(#333 1px, transparent 1px), linear-gradient(90deg, #333 1px, transparent 1px)', backgroundSize: '40px 40px' }}></div>
                            <div className="relative z-10 text-center flex flex-col items-center gap-3">
                                <div className="p-4 rounded-full bg-white/5 group-hover:bg-white/10 transition-colors">
                                    <BarChart2 className="h-12 w-12 text-slate-600 group-hover:text-cyan-400 transition-colors" />
                                </div>
                                <p className="text-slate-500 font-medium">Vista de TradingView Profesional</p>
                            </div>
                        </div>
                    </div>

                    {/* Order Form */}
                    <div className="glass-card p-6 border border-white/5 bg-white/[0.02] rounded-2xl h-fit">
                        <h2 className="text-lg font-semibold mb-6 text-white flex items-center gap-2">
                            <Zap className="h-5 w-5 text-violet-400" />
                            Ejecución Rápida
                        </h2>

                        {/* Balance */}
                        <div className="bg-white/5 rounded-xl p-4 mb-6 border border-white/5 flex items-center justify-between">
                            <div>
                                <p className="text-slate-400 text-xs uppercase tracking-wider font-medium mb-1">Balance Disponible</p>
                                <p className="text-xl font-bold text-emerald-400 tracking-tight">${balance.USDT.toFixed(2)}</p>
                            </div>
                            <div className="h-10 w-10 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                                <Wallet className="h-5 w-5 text-emerald-400" />
                            </div>
                        </div>

                        {/* Side Toggle */}
                        <div className="grid grid-cols-2 gap-2 mb-6 bg-white/5 p-1 rounded-xl">
                            <button
                                onClick={() => setOrder({ ...order, side: 'BUY' })}
                                className={`py-3 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 ${order.side === 'BUY'
                                    ? 'bg-emerald-500 text-black shadow-lg shadow-emerald-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                <TrendingUp className="h-4 w-4" />
                                Comprar
                            </button>
                            <button
                                onClick={() => setOrder({ ...order, side: 'SELL' })}
                                className={`py-3 rounded-lg font-bold text-sm transition-all flex items-center justify-center gap-2 ${order.side === 'SELL'
                                    ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                <TrendingDown className="h-4 w-4" />
                                Vender
                            </button>
                        </div>

                        {/* Quantity Input */}
                        <div className="mb-4">
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">Cantidad</label>
                            <div className="relative">
                                <input
                                    type="number"
                                    value={order.quantity}
                                    onChange={(e) => setOrder({ ...order, quantity: e.target.value })}
                                    placeholder="0.001"
                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-cyan-500/50 focus:bg-white/5 transition-all font-mono text-lg"
                                />
                                <span className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 text-sm font-medium">{selectedSymbol.symbol.replace('USDT', '')}</span>
                            </div>
                        </div>

                        {/* Price Display */}
                        <div className="mb-4">
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-2 block">Precio de Mercado</label>
                            <div className="w-full bg-white/5 border border-white/5 rounded-xl px-4 py-3 text-slate-300 font-mono flex justify-between items-center cursor-not-allowed">
                                <span>${currentPrice.toLocaleString()}</span>
                                <span className="text-xs text-slate-500">USDT</span>
                            </div>
                        </div>

                        {/* Total */}
                        <div className="mb-8">
                            <div className="flex justify-between items-center mb-2">
                                <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Total Estimado</label>
                            </div>
                            <div className="w-full bg-gradient-to-r from-white/5 to-white/[0.02] border border-white/10 rounded-xl px-4 py-4 text-white font-bold font-mono text-xl flex justify-between items-center">
                                <span>${(parseFloat(order.quantity || '0') * currentPrice).toFixed(2)}</span>
                                <span className="text-sm text-slate-500 font-sans">USDT</span>
                            </div>
                        </div>

                        {/* Submit Button */}
                        <button
                            onClick={handleOrder}
                            className={`w-full py-4 rounded-xl font-bold text-lg transition-all active:scale-95 shadow-lg flex items-center justify-center gap-2 ${order.side === 'BUY'
                                ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-black hover:from-emerald-400 hover:to-emerald-500 shadow-emerald-500/20'
                                : 'bg-gradient-to-r from-rose-500 to-rose-600 text-white hover:from-rose-400 hover:to-rose-500 shadow-rose-500/20'
                                }`}
                        >
                            {order.side === 'BUY' ? 'Comprar Ahora' : 'Vender Ahora'}
                        </button>

                        {mode === 'practice' && (
                            <div className="mt-4 flex items-center justify-center gap-2 text-xs text-emerald-400/80 bg-emerald-500/5 py-2 rounded-lg border border-emerald-500/10">
                                <Gamepad2 className="h-4 w-4" />
                                Modo Simulación Activo
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </main>
    )
}
