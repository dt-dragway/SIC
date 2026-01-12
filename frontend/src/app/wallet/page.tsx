'use client';

import { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { RefreshCw, Eye, EyeOff, Wallet, TrendingUp, ArrowUpRight, ArrowDownRight, CreditCard } from 'lucide-react';
import { toast } from 'sonner';

interface Balance {
    asset: string;
    free: number;
    locked: number;
    total: number;
    usd_value: number;
}

interface WalletData {
    total_usd: number;
    balances: Balance[];
    connected: boolean;
}

export default function WalletPage() {
    const { isAuthenticated, loading: authLoading } = useAuth();
    const [loading, setLoading] = useState(true);
    const [data, setData] = useState<WalletData | null>(null);
    const [hideBalance, setHideBalance] = useState(false);
    const [mode, setMode] = useState<'real' | 'practice'>('real'); // Default to real per user request

    const fetchWallet = async () => {
        try {
            setLoading(true);
            const res = await fetch('/api/v1/wallet/');
            if (res.ok) {
                const walletData = await res.json();
                setData(walletData);
            } else {
                toast.error('Error al cargar la billetera');
            }
        } catch (error) {
            console.error(error);
            toast.error('Error de conexión');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isAuthenticated) {
            fetchWallet();
        }
    }, [isAuthenticated]);

    if (authLoading || (!data && loading)) return <LoadingSpinner />;

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header Section */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
                            Billetera
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">Gestión de activos y balances en tiempo real</p>
                    </div>

                    <div className="flex bg-white/5 p-1 rounded-xl border border-white/10">
                        <button
                            onClick={() => setMode('practice')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'practice'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'text-slate-400 hover:text-white'}`}
                        >
                            Simulado
                        </button>
                        <button
                            onClick={() => setMode('real')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${mode === 'real'
                                ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                                : 'text-slate-400 hover:text-white'}`}
                        >
                            Real (Binance)
                        </button>
                    </div>
                </div>

                {/* Total Balance Card */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="md:col-span-2 glass-card p-8 rounded-3xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Wallet size={120} />
                        </div>
                        <div className="relative z-10">
                            <div className="flex items-center gap-2 mb-2 text-slate-400">
                                <span className="text-sm font-medium uppercase tracking-wider">Balance Total Estimado</span>
                                <button onClick={() => setHideBalance(!hideBalance)} className="hover:text-white transition-colors">
                                    {hideBalance ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            </div>

                            <div className="text-5xl font-bold text-white font-mono tracking-tight mb-6">
                                {hideBalance ? '••••••' : `$${(data?.total_usd ?? 0).toLocaleString('en-US', { minimumFractionDigits: 2 })}`}
                                <span className="text-lg text-slate-500 ml-2 font-sans font-normal">USD</span>
                            </div>

                            <div className="flex gap-4">
                                <button className="btn-primary flex items-center gap-2">
                                    <CreditCard size={18} />
                                    Depositar
                                </button>
                                <button className="btn-secondary flex items-center gap-2">
                                    <ArrowUpRight size={18} />
                                    Retirar
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Stats Card */}
                    <div className="glass-card p-8 rounded-3xl flex flex-col justify-between">
                        <div>
                            <h3 className="text-slate-400 text-sm font-medium uppercase tracking-wider mb-4">Rendimiento (24h)</h3>
                            <div className="flex items-baseline gap-2">
                                <span className="text-3xl font-bold text-emerald-400">+2.45%</span>
                                <ArrowUpRight className="text-emerald-400" size={20} />
                            </div>
                            <p className="text-slate-500 text-sm mt-1">+$124.50 USD</p>
                        </div>

                        <div className="mt-6 pt-6 border-t border-white/5">
                            <div className="flex justify-between items-center text-sm text-slate-400 mb-2">
                                <span>Activos Totales</span>
                                <span className="text-white font-medium">{data?.balances.length || 0}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm text-slate-400">
                                <span>Estado API</span>
                                <span className={`flex items-center gap-2 font-medium ${data?.connected ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    <span className={`w-2 h-2 rounded-full ${data?.connected ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                                    {data?.connected ? 'Conectado' : 'Desconectado'}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Assets Table */}
                <div className="glass-card overflow-hidden rounded-3xl border border-white/5">
                    <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                        <h2 className="font-bold text-lg text-white">Mis Activos</h2>
                        <button onClick={fetchWallet} disabled={loading} className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-colors">
                            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                        </button>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-[#0f1219]">
                                <tr>
                                    <th className="text-left py-4 px-6 text-xs font-medium text-slate-500 uppercase tracking-wider">Activo</th>
                                    <th className="text-right py-4 px-6 text-xs font-medium text-slate-500 uppercase tracking-wider">Balance Total</th>
                                    <th className="text-right py-4 px-6 text-xs font-medium text-slate-500 uppercase tracking-wider">Disponible</th>
                                    <th className="text-right py-4 px-6 text-xs font-medium text-slate-500 uppercase tracking-wider">En Órdenes</th>
                                    <th className="text-right py-4 px-6 text-xs font-medium text-slate-500 uppercase tracking-wider">Valor (USD)</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {data?.balances.map((asset) => (
                                    <tr key={asset.asset} className="hover:bg-white/[0.02] transition-colors group">
                                        <td className="py-4 px-6">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold text-xs ring-1 ring-indigo-500/30">
                                                    {asset.asset[0]}
                                                </div>
                                                <span className="font-bold text-white">{asset.asset}</span>
                                            </div>
                                        </td>
                                        <td className="py-4 px-6 text-right font-mono text-slate-300">
                                            {hideBalance ? '••••' : asset.total.toLocaleString()}
                                        </td>
                                        <td className="py-4 px-6 text-right font-mono text-slate-400">
                                            {hideBalance ? '••••' : asset.free.toLocaleString()}
                                        </td>
                                        <td className="py-4 px-6 text-right font-mono text-slate-500">
                                            {hideBalance ? '••••' : asset.locked.toLocaleString()}
                                        </td>
                                        <td className="py-4 px-6 text-right font-mono font-medium text-emerald-400">
                                            {hideBalance ? '••••' : `$${asset.usd_value?.toLocaleString(undefined, { minimumFractionDigits: 2 })}`}
                                        </td>
                                    </tr>
                                ))}
                                {data?.balances.length === 0 && (
                                    <tr>
                                        <td colSpan={5} className="py-12 text-center text-slate-500">
                                            No tienes activos con balance positivo.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </DashboardLayout>
    );
}
