'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    LayoutGrid,
    Wallet,
    TrendingUp,
    ArrowRightLeft,
    LogOut,
    Menu,
    X,
    Brain,
    BookOpen,
    User,
    Zap,
    Monitor,
    BarChart3,
    Newspaper,
    Droplet,
    Bot,
    Scale,
    Target,
    History
} from 'lucide-react';
import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useAIContext } from '@/context/AIContext';
import { useWallet } from '@/context/WalletContext';
import { toast } from 'sonner';

export default function Sidebar() {
    const pathname = usePathname();
    const { token, logout } = useAuth();
    const { analysis, status: aiStatus, toggleBrain } = useAIContext();
    const { mode, setMode } = useWallet();
    const [isOpen, setIsOpen] = useState(false);
    
    // Controles globales
    const [aiActive, setAiActive] = useState(false);
    const [spotEnabled, setSpotEnabled] = useState(true);
    const [futuresEnabled, setFuturesEnabled] = useState(true);
    const [syncing, setSyncing] = useState(false);

    const fetchAutomationStatus = async () => {
        if (!token) return;
        try {
            const res = await fetch('/api/v1/automated-trading/status', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setAiActive(data.running);
            }
        } catch (error) {
            console.error("Error fetching automation status in Sidebar:", error);
        }
    };

    const fetchAutomationSettings = async () => {
        if (!token) return;
        try {
            const res = await fetch('/api/v1/automated-trading/settings', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                setSpotEnabled(data.spot_enabled ?? true);
                setFuturesEnabled(data.futures_enabled ?? true);
            }
        } catch (error) {
            console.error("Error fetching settings in Sidebar:", error);
        }
    };

    useEffect(() => {
        if (!token) return;
        fetchAutomationStatus();
        fetchAutomationSettings();
        const interval = setInterval(() => {
            fetchAutomationStatus();
            fetchAutomationSettings();
        }, 8000); // Rápido sincronizado
        return () => clearInterval(interval);
    }, [token]);

    const handleToggleSpot = async (checked: boolean) => {
        if (!token) return;
        setSyncing(true);
        setSpotEnabled(checked);
        try {
            const getRes = await fetch('/api/v1/automated-trading/settings', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (getRes.ok) {
                const currentSettings = await getRes.json();
                const updatedSettings = { ...currentSettings, spot_enabled: checked };
                
                const res = await fetch('/api/v1/automated-trading/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(updatedSettings)
                });
                
                if (res.ok) {
                    toast.success(checked ? "🟢 IA para Mercado SPOT activada." : "🟡 IA para Mercado SPOT desactivada.");
                } else {
                    toast.error("Error al actualizar la configuración SPOT.");
                    setSpotEnabled(!checked);
                }
            }
        } catch (error) {
            console.error("Error toggling spot AI:", error);
            toast.error("Error de conexión al guardar configuración.");
            setSpotEnabled(!checked);
        } finally {
            setSyncing(false);
        }
    };

    const handleToggleFutures = async (checked: boolean) => {
        if (!token) return;
        setSyncing(true);
        setFuturesEnabled(checked);
        try {
            const getRes = await fetch('/api/v1/automated-trading/settings', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (getRes.ok) {
                const currentSettings = await getRes.json();
                const updatedSettings = { ...currentSettings, futures_enabled: checked };
                
                const res = await fetch('/api/v1/automated-trading/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(updatedSettings)
                });
                
                if (res.ok) {
                    toast.success(checked ? "🟢 IA para Mercado FUTUROS activada." : "🟡 IA para Mercado FUTUROS desactivada.");
                } else {
                    toast.error("Error al actualizar la configuración de FUTUROS.");
                    setFuturesEnabled(!checked);
                }
            }
        } catch (error) {
            console.error("Error toggling futures AI:", error);
            toast.error("Error de conexión al guardar configuración.");
            setFuturesEnabled(!checked);
        } finally {
            setSyncing(false);
        }
    };

    const handleToggleAI = async (checked: boolean) => {
        if (!token) return;
        setSyncing(true);
        setAiActive(checked);
        try {
            const endpoint = checked ? '/api/v1/automated-trading/start' : '/api/v1/automated-trading/stop';
            let body = null;
            
            if (checked) {
                // Obtener settings actuales para no sobreescribir otros valores
                const getRes = await fetch('/api/v1/automated-trading/settings', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (getRes.ok) {
                    const currentSettings = await getRes.json();
                    body = JSON.stringify({
                        settings: { ...currentSettings, practice_mode_only: mode === 'practice' },
                        symbols: []
                    });
                } else {
                    body = JSON.stringify({
                        settings: {
                            enabled: true,
                            max_daily_trades: 10,
                            max_position_size: 50.0,
                            min_signal_confidence: 70,
                            allowed_tiers: ['S', 'A'],
                            risk_level: 'moderate',
                            pause_on_high_volatility: true,
                            check_interval_seconds: 30,
                            practice_mode_only: mode === 'practice'
                        },
                        symbols: []
                    });
                }
            }
            
            const res = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: body
            });
            
            if (res.ok) {
                toast.success(checked ? "🤖 IA Encendida 24/7 con éxito." : "🛑 IA Apagada y pausada por completo.");
            } else {
                const errData = await res.json().catch(() => ({}));
                const isAlreadyActive = errData?.detail?.includes("ya está activa") || errData?.detail?.includes("ya está corriendo");
                
                if (checked && isAlreadyActive) {
                    toast.success("🤖 IA ya se encuentra activa.");
                    setAiActive(true); // Asegurar que quede activo
                } else {
                    toast.error(errData?.detail || "Error al cambiar estado de la IA.");
                    setAiActive(!checked); // Revert
                }
            }
        } catch (error) {
            console.error("Error toggling AI in Sidebar:", error);
            toast.error("Error de conexión con el servidor.");
            setAiActive(!checked); // Revert
        } finally {
            setSyncing(false);
        }
    };

    const handleToggleMode = async (checked: boolean) => {
        const newMode = checked ? 'practice' : 'real';
        setMode(newMode);
        
        if (!token) return;
        setSyncing(true);
        try {
            const getRes = await fetch('/api/v1/automated-trading/settings', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (getRes.ok) {
                const currentSettings = await getRes.json();
                const updatedSettings = { ...currentSettings, practice_mode_only: checked };
                
                const res = await fetch('/api/v1/automated-trading/settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(updatedSettings)
                });
                
                if (res.ok) {
                    toast.success(`Ecosistema configurado en MODO ${newMode.toUpperCase()}`);
                }
            }
        } catch (error) {
            console.error("Error syncing mode with DB:", error);
            toast.error("Error al sincronizar modo con la base de datos.");
        } finally {
            setSyncing(false);
        }
    };

    const links = [
        { href: '/', label: 'Inicio', icon: LayoutDashboard },
        { href: '/automated-trading', label: 'Trading IA Auto', icon: Brain },
        { href: '/wallet', label: 'Billetera', icon: Wallet },
        { href: '/history', label: 'Historial de Órdenes', icon: History },
        { href: '/trading', label: 'Trading', icon: TrendingUp },
        { href: '/execution', label: 'Smart Execution', icon: Zap },
        { href: '/terminal', label: 'Terminal Pro', icon: Monitor },
        { href: '/heatmap', label: 'Heatmap Hub', icon: LayoutGrid },
        { href: '/derivatives', label: 'Delta Neutral', icon: BarChart3 },
        { href: '/sentiment', label: 'Sentiment Hub', icon: Newspaper },
        { href: '/journal', label: 'Trading Journal', icon: BookOpen },
        { href: '/automation', label: 'Automation', icon: Bot },
        { href: '/trade-markers', label: 'Trade Markers', icon: Target },
        { href: '/risk', label: 'Riesgo & Macro', icon: Scale },
        { href: '/agente-ia', label: 'Agente IA', icon: Brain },
        { href: '/p2p', label: 'P2P VES', icon: ArrowRightLeft },
    ];

    const isActive = (path: string) => pathname === path;

    return (
        <>
            {/* Mobile Toggle */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="lg:hidden fixed top-4 right-4 z-50 p-2 bg-sic-card rounded-lg border border-white/10 text-white"
            >
                {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>

            {/* Sidebar Container */}
            <aside className={`
                fixed top-0 left-0 h-screen w-64 bg-[#0B0E14]/95 backdrop-blur-xl border-r border-white/5
                transform transition-transform duration-300 ease-in-out z-40
                ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
            `}>
                <div className="flex flex-col h-full p-6">
                    {/* Brand */}
                    <div className="flex items-center gap-3 mb-6 px-2">
                        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                            <span className="text-white font-bold text-xl">S</span>
                        </div>
                        <div>
                            <h1 className="text-white font-bold text-lg leading-tight">SIC Ultra</h1>
                            <p className="text-slate-500 text-xs font-mono">v1.2.0</p>
                        </div>
                    </div>

                    {/* Neural Engine Global Status */}
                    <div
                        onClick={toggleBrain}
                        className="mx-2 mb-6 px-3 py-2 rounded-lg bg-gradient-to-r from-violet-500/10 to-indigo-500/10 border border-violet-500/20 flex items-center gap-3 cursor-pointer hover:bg-violet-500/20 transition-all group"
                    >
                        <div className="relative">
                            <Brain size={16} className="text-violet-400" />
                            <span className="absolute -top-0.5 -right-0.5 flex h-1.5 w-1.5">
                                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${analysis ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                                <span className={`relative inline-flex rounded-full h-1.5 w-1.5 ${analysis ? 'bg-emerald-500' : 'bg-amber-500'}`}></span>
                            </span>
                        </div>
                        <div className="flex-1">
                            <p className="text-[10px] text-violet-300 font-bold uppercase tracking-wider">Neural Engine</p>
                            {analysis ? (
                                <div className="flex items-center gap-1.5">
                                    {/* Mostrar símbolo de la cripto (ej: BTC) */}
                                    <span className="text-[10px] text-cyan-400 font-bold">
                                        {analysis.symbol?.replace('USDT', '') || 'BTC'}:
                                    </span>
                                    <span className={`text-[10px] font-bold ${analysis.signal === 'BUY' || analysis.signal === 'LONG' || (analysis.signal === 'HOLD' && analysis.confidence > 50) ? 'text-emerald-400' :
                                        analysis.signal === 'SELL' || analysis.signal === 'SHORT' ? 'text-rose-400' : 'text-slate-400'
                                        }`}>
                                        {analysis.signal}
                                    </span>
                                    <span className="text-[9px] text-slate-500 font-mono">
                                        {Math.round(analysis.confidence)}%
                                    </span>
                                </div>
                            ) : (
                                <div className="flex items-center gap-1.5">
                                    {/* Skeleton loader durante carga */}
                                    <div className="h-2.5 w-8 bg-slate-700/50 rounded animate-pulse"></div>
                                    <div className="h-2.5 w-12 bg-slate-700/50 rounded animate-pulse"></div>
                                    <div className="h-2 w-6 bg-slate-700/50 rounded animate-pulse"></div>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Global Ecosystem Switches */}
                    <div className="mx-2 mb-6 p-4 rounded-xl bg-white/[0.02] border border-white/5 space-y-4">
                        <p className="text-[9px] text-slate-500 font-bold uppercase tracking-wider font-mono">Eje Central de Control</p>
                        
                        {/* Switch 1: IA Global Status */}
                        <div className="flex items-center justify-between text-xs">
                            <div className="flex flex-col">
                                <span className="text-white font-bold">IA 24/7</span>
                                <span className="text-[9px] text-slate-500 font-mono">{aiActive ? 'Encendido' : 'Apagado'}</span>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                    type="checkbox" 
                                    checked={aiActive}
                                    onChange={(e) => handleToggleAI(e.target.checked)}
                                    disabled={syncing}
                                    className="sr-only peer" 
                                />
                                <div className="w-9 h-5 bg-slate-700/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-500"></div>
                            </label>
                        </div>

                        {/* Switch 1.1: IA Spot Status */}
                        <div className="flex items-center justify-between text-xs pl-2 border-l border-white/10">
                            <div className="flex flex-col">
                                <span className="text-slate-300 font-bold">IA Spot</span>
                                <span className="text-[9px] text-slate-500 font-mono">{spotEnabled ? 'Activa' : 'Pausada'}</span>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                    type="checkbox" 
                                    checked={spotEnabled}
                                    onChange={(e) => handleToggleSpot(e.target.checked)}
                                    disabled={syncing || !aiActive}
                                    className="sr-only peer" 
                                />
                                <div className="w-9 h-5 bg-slate-700/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-cyan-500"></div>
                            </label>
                        </div>

                        {/* Switch 1.2: IA Futuros Status */}
                        <div className="flex items-center justify-between text-xs pl-2 border-l border-white/10">
                            <div className="flex flex-col">
                                <span className="text-slate-300 font-bold">IA Futuros</span>
                                <span className="text-[9px] text-slate-500 font-mono">{futuresEnabled ? 'Activa' : 'Pausada'}</span>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                    type="checkbox" 
                                    checked={futuresEnabled}
                                    onChange={(e) => handleToggleFutures(e.target.checked)}
                                    disabled={syncing || !aiActive}
                                    className="sr-only peer" 
                                />
                                <div className="w-9 h-5 bg-slate-700/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-violet-500"></div>
                            </label>
                        </div>

                        {/* Switch 2: Global Mode Switcher */}
                        <div className="flex items-center justify-between text-xs">
                            <div className="flex flex-col">
                                <span className="text-white font-bold">Modo Operativo</span>
                                <span className={`text-[9px] font-mono font-bold ${mode === 'practice' ? 'text-emerald-400' : 'text-blue-400'}`}>
                                    {mode === 'practice' ? 'PRÁCTICA' : 'REAL'}
                                </span>
                            </div>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input 
                                    type="checkbox" 
                                    checked={mode === 'practice'}
                                    onChange={(e) => handleToggleMode(e.target.checked)}
                                    disabled={syncing}
                                    className="sr-only peer" 
                                />
                                <div className="w-9 h-5 bg-slate-700/50 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-emerald-500"></div>
                            </label>
                        </div>
                    </div>

                    {/* Navigation - Scrollable Area */}
                    <nav className="flex-1 min-h-0 space-y-2 overflow-y-auto pr-2 custom-scrollbar">
                        {links.map((link) => {
                            const Icon = link.icon;
                            const active = isActive(link.href);

                            return (
                                <Link
                                    key={link.href}
                                    href={link.href}
                                    onClick={() => setIsOpen(false)}
                                    className={`
                                        flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
                                        ${active
                                            ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/20'
                                            : 'text-slate-400 hover:text-white hover:bg-white/5'}
                                    `}
                                >
                                    <Icon size={20} className={active ? 'text-cyan-400' : 'text-slate-500'} />
                                    <span className="font-medium">{link.label}</span>
                                </Link>
                            );
                        })}
                    </nav>

                    {/* Logout - Sticky at bottom */}
                    <div className="pt-4 mt-4 border-t border-white/5">
                        <button
                            onClick={() => logout()}
                            className="w-full flex items-center gap-3 px-4 py-3 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-xl transition-colors"
                        >
                            <LogOut size={20} />
                            <span className="font-medium">Cerrar Sesión</span>
                        </button>
                    </div>
                </div>
            </aside>

            {/* Overlay for mobile */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
                    onClick={() => setIsOpen(false)}
                />
            )}
        </>
    );
}
