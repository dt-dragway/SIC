'use client'

import { useState, useEffect } from 'react'
import { Clock, XCircle, AlertCircle, CheckCircle2 } from 'lucide-react'
import { toast } from 'sonner'

interface PendingOrder {
    id: string
    symbol: string
    type: 'LIMIT' | 'STOP_LOSS' | 'TAKE_PROFIT' | 'OCO'
    side: 'BUY' | 'SELL'
    quantity: number
    price?: number
    stop_price?: number
    status: 'ACTIVE' | 'PARTIALLY_FILLED'
    created_at: string
}

interface PendingOrdersPanelProps {
    mode: 'practice' | 'real'
    refreshTrigger?: number
}

export default function PendingOrdersPanel({ mode, refreshTrigger }: PendingOrdersPanelProps) {
    const [orders, setOrders] = useState<PendingOrder[]>([])
    const [loading, setLoading] = useState(true)
    const [cancellingId, setCancellingId] = useState<string | null>(null)

    const fetchOrders = async () => {
        try {
            const token = localStorage.getItem('token')
            if (!token) return

            // Endpoint switch based on mode
            const endpoint = mode === 'practice'
                ? '/api/v1/practice/pending-orders' // Asumimos que existe o usaremos el genérico filtrado
                : '/api/v1/trading/pending-orders'

            const response = await fetch(endpoint, {
                headers: { 'Authorization': `Bearer ${token}` }
            })

            if (response.ok) {
                const data = await response.json()
                setOrders(data.orders || [])
            }
        } catch (error) {
            console.error('Error fetching pending orders:', error)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchOrders()
        const interval = setInterval(fetchOrders, 5000) // Poll every 5s
        return () => clearInterval(interval)
    }, [mode, refreshTrigger])

    const handleCancelOrder = async (orderId: string) => {
        setCancellingId(orderId)
        try {
            const token = localStorage.getItem('token')
            const response = await fetch(`/api/v1/trading/cancel-order/${orderId}?mode=${mode}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            })

            if (response.ok) {
                toast.success('Orden cancelada exitosamente')
                fetchOrders() // Refresh immediately
            } else {
                toast.error('Error al cancelar orden')
            }
        } catch (error) {
            toast.error('Error de conexión')
        } finally {
            setCancellingId(null)
        }
    }

    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
    }

    if (loading && orders.length === 0) {
        return <div className="p-4 text-center text-xs text-slate-500">Cargando órdenes...</div>
    }

    if (orders.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 py-8">
                <Clock className="w-8 h-8 mb-2 opacity-50" />
                <p className="text-xs">No hay órdenes pendientes</p>
            </div>
        )
    }

    return (
        <div className="overflow-x-auto">
            <table className="w-full">
                <thead className="bg-white/5 border-b border-white/10 text-xs font-medium text-slate-400 sticky top-0">
                    <tr>
                        <th className="px-4 py-2 text-left">Hora</th>
                        <th className="px-4 py-2 text-left">Par</th>
                        <th className="px-4 py-2 text-left">Tipo</th>
                        <th className="px-4 py-2 text-left">Lado</th>
                        <th className="px-4 py-2 text-right">Precio</th>
                        <th className="px-4 py-2 text-right">Cantidad</th>
                        <th className="px-4 py-2 text-center">Acción</th>
                    </tr>
                </thead>
                <tbody className="divide-y divide-white/5 text-xs">
                    {orders.map((order) => (
                        <tr key={order.id} className="hover:bg-white/[0.02]">
                            <td className="px-4 py-2 text-slate-500 font-mono">{formatDate(order.created_at)}</td>
                            <td className="px-4 py-2 font-bold text-white">{order.symbol}</td>
                            <td className="px-4 py-2 text-slate-300">{order.type}</td>
                            <td className="px-4 py-2">
                                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${order.side === 'BUY' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'
                                    }`}>
                                    {order.side}
                                </span>
                            </td>
                            <td className="px-4 py-2 text-right font-mono text-slate-200">
                                ${order.price?.toLocaleString() || order.stop_price?.toLocaleString() || 'MKT'}
                            </td>
                            <td className="px-4 py-2 text-right font-mono text-slate-400">
                                {order.quantity}
                            </td>
                            <td className="px-4 py-2 text-center">
                                <button
                                    onClick={() => handleCancelOrder(order.id)}
                                    disabled={cancellingId === order.id}
                                    className="p-1 hover:bg-rose-500/20 text-rose-400 rounded transition-colors disabled:opacity-50"
                                    title="Cancelar Orden"
                                >
                                    {cancellingId === order.id ? (
                                        <div className="w-3 h-3 border-2 border-rose-400 border-t-transparent rounded-full animate-spin" />
                                    ) : (
                                        <XCircle size={14} />
                                    )}
                                </button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    )
}
