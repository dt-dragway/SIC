'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import { useWallet } from '@/context/WalletContext'
import {
    LayoutDashboard,
    TrendingUp,
    ArrowLeftRight,
    Radio,
    User,
    LogOut,
    LogIn,
    Activity,
    Wallet,
    RefreshCw
} from 'lucide-react'

export default function Header() {
    const { user, logout, isAuthenticated } = useAuth()
    const { mode, setMode, totalUsd, isLoading } = useWallet()
    const router = useRouter()

    return (
        <header className="border-b border-white/5 bg-black/40 backdrop-blur-xl sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-6 h-16 flex justify-between items-center">
                <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                    {/* Logo */}
                    <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <Activity className="text-white h-5 w-5" />
                    </div>
                    <h1 className="text-xl font-bold tracking-tight text-white">SIC <span className="text-cyan-400 font-light">Ultra</span></h1>
                </Link>

                <div className="flex items-center gap-6">
                    {/* Navigation - Only visible when logged in */}
                    {isAuthenticated && (
                        <nav className="hidden md:flex items-center gap-1 text-sm font-medium text-slate-400">
                            <Link href="/" className="flex items-center gap-2 hover:text-white px-3 py-2 rounded-lg hover:bg-white/5 transition-all">
                                <LayoutDashboard className="h-4 w-4" />
                                <span>Dashboard</span>
                            </Link>
                            <Link href="/trading" className="flex items-center gap-2 hover:text-white px-3 py-2 rounded-lg hover:bg-white/5 transition-all">
                                <TrendingUp className="h-4 w-4" />
                                <span>Trading</span>
                            </Link>
                            <Link href="/p2p" className="flex items-center gap-2 hover:text-white px-3 py-2 rounded-lg hover:bg-white/5 transition-all">
                                <ArrowLeftRight className="h-4 w-4" />
                                <span>P2P</span>
                            </Link>
                            <Link href="/signals" className="flex items-center gap-2 hover:text-white px-3 py-2 rounded-lg hover:bg-white/5 transition-all">
                                <Radio className="h-4 w-4" />
                                <span>Señales</span>
                            </Link>
                        </nav>
                    )}

                    {/* User Profile / Auth Actions */}
                    <div className="flex items-center gap-4">
                        {isAuthenticated ? (
                            <div className="flex items-center gap-4">
                                {/* Mode Switcher & Balance */}
                                <div className="hidden sm:flex items-center gap-3 bg-white/5 rounded-full px-1 py-1 border border-white/10">
                                    <button
                                        onClick={() => setMode('practice')}
                                        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                                            mode === 'practice' 
                                            ? 'bg-emerald-500/20 text-emerald-400 shadow-sm ring-1 ring-emerald-500/50' 
                                            : 'text-slate-400 hover:text-white'
                                        }`}
                                    >
                                        Práctica
                                    </button>
                                    <button
                                        onClick={() => setMode('real')}
                                        className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                                            mode === 'real' 
                                            ? 'bg-blue-500/20 text-blue-400 shadow-sm ring-1 ring-blue-500/50' 
                                            : 'text-slate-400 hover:text-white'
                                        }`}
                                    >
                                        Real
                                    </button>
                                </div>
                                
                                {/* Total Balance Display */}
                                <div className="flex flex-col items-end mr-2">
                                    <span className="text-[10px] text-slate-500 uppercase tracking-wider font-medium">Balance Total</span>
                                    <div className="flex items-center gap-2">
                                        <Wallet className="h-3 w-3 text-slate-400" />
                                        <span className={`text-sm font-bold tracking-tight ${isLoading ? 'animate-pulse text-slate-500' : 'text-white'}`}>
                                            ${totalUsd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                        </span>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3 pl-4 border-l border-white/10">
                                    <Link href="/profile" className="flex items-center gap-2 group">
                                        <div className="h-8 w-8 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white border border-white/10 group-hover:border-white/30 transition-all shadow-lg shadow-violet-500/20">
                                            {user?.name?.substring(0, 2).toUpperCase() || <User className="h-4 w-4" />}
                                        </div>
                                    </Link>
                                    <button
                                        onClick={logout}
                                        className="p-2 text-slate-400 hover:text-rose-400 transition-colors hover:bg-rose-500/10 rounded-lg"
                                        title="Cerrar Sesión"
                                    >
                                        <LogOut className="h-4 w-4" />
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <Link href="/login" className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-sm font-medium transition-all text-white">
                                <LogIn className="h-4 w-4" />
                                <span>Iniciar Sesión</span>
                            </Link>
                        )}
                    </div>
                </div>
            </div>
        </header>
    )
}
