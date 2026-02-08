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
    Target
} from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useAIContext } from '@/context/AIContext';

export default function Sidebar() {
    const pathname = usePathname();
    const { logout } = useAuth();
    const { analysis, status, toggleBrain } = useAIContext();
    const [isOpen, setIsOpen] = useState(false);

    const links = [
        { href: '/', label: 'Inicio', icon: LayoutDashboard },
        { href: '/wallet', label: 'Billetera', icon: Wallet },
        { href: '/trading', label: 'Trading', icon: TrendingUp },
        { href: '/execution', label: 'Smart Execution', icon: Zap },
        { href: '/terminal', label: 'Terminal Pro', icon: Monitor },
        { href: '/heatmap', label: 'Heatmap Hub', icon: LayoutGrid },
        { href: '/derivatives', label: 'Delta Neutral', icon: BarChart3 },
        { href: '/sentiment', label: 'Sentiment Hub', icon: Newspaper },
        { href: '/journal', label: 'Trading Journal', icon: BookOpen },
        { href: '/automation', label: 'Automation', icon: Bot },
        { href: '/automated-trading', label: 'Trading IA Auto', icon: Brain },
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

                    {/* Navigation - Scrollable Area */}
                    <nav className="flex-1 space-y-2 overflow-y-auto pr-2 custom-scrollbar">
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
