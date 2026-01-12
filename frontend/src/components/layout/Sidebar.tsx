'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
    LayoutDashboard, 
    Wallet, 
    TrendingUp, 
    ArrowRightLeft, 
    Target, 
    History, 
    LogOut,
    Menu,
    X
} from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';

export default function Sidebar() {
    const pathname = usePathname();
    const { logout } = useAuth();
    const [isOpen, setIsOpen] = useState(false);

    const links = [
        { href: '/', label: 'Inicio', icon: LayoutDashboard },
        { href: '/wallet', label: 'Billetera', icon: Wallet },
        { href: '/trading', label: 'Trading', icon: TrendingUp },
        { href: '/p2p', label: 'P2P VES', icon: ArrowRightLeft },
        { href: '/signals', label: 'Señales IA', icon: Target },
        { href: '/history', label: 'Historial', icon: History },
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
                    <div className="flex items-center gap-3 mb-10 px-2">
                        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                            <span className="text-white font-bold text-xl">S</span>
                        </div>
                        <div>
                            <h1 className="text-white font-bold text-lg leading-tight">SIC Ultra</h1>
                            <p className="text-slate-500 text-xs font-mono">v1.2.0</p>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="flex-1 space-y-2">
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

                    {/* Logout */}
                    <button 
                        onClick={() => logout()}
                        className="flex items-center gap-3 px-4 py-3 text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 rounded-xl transition-colors mt-auto"
                    >
                        <LogOut size={20} />
                        <span className="font-medium">Cerrar Sesión</span>
                    </button>
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
