'use client'

import React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/hooks/useAuth'
import {
    LayoutDashboard,
    TrendingUp,
    ArrowLeftRight,
    Radio,
    User,
    LogOut,
    LogIn,
    Activity
} from 'lucide-react'

export default function Header() {
    const { user, logout, isAuthenticated } = useAuth()
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
                            <div className="flex items-center gap-3 pl-6 border-l border-white/10">
                                <Link href="/profile" className="flex items-center gap-2 group">
                                    <div className="h-8 w-8 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white border border-white/10 group-hover:border-white/30 transition-all shadow-lg shadow-violet-500/20">
                                        {user?.name?.substring(0, 2).toUpperCase() || <User className="h-4 w-4" />}
                                    </div>
                                    <div className="hidden sm:block text-right">
                                        <p className="text-xs font-medium text-white group-hover:text-cyan-400 transition-colors">{user?.name}</p>
                                        <p className="text-[10px] text-slate-500 uppercase tracking-wider">Pro Trader</p>
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
