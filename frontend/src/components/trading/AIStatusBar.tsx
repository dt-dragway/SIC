'use client'

import { useEffect, useState } from 'react'
import { Trophy, TrendingUp, Star, Zap } from 'lucide-react'

interface AIStats {
    level: number
    xp: number
    next_level_xp: number
    win_rate: number
    total_pnl: number
    total_trades: number
}

export default function AIStatusBar() {
    const [stats, setStats] = useState<AIStats | null>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const token = localStorage.getItem('token')
                if (!token) return

                const response = await fetch('/api/v1/practice/stats', {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })

                if (response.ok) {
                    const data = await response.json()
                    setStats({
                        level: data.level || 1,
                        xp: data.xp || 0,
                        next_level_xp: data.next_level_xp || 100,
                        win_rate: data.win_rate || 0,
                        total_pnl: data.total_pnl || 0,
                        total_trades: data.total_trades || 0
                    })
                }
            } catch (error) {
                console.error('Error fetching AI stats:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchStats()
        const interval = setInterval(fetchStats, 30000) // Update every 30s
        return () => clearInterval(interval)
    }, [])

    if (loading || !stats) {
        return (
            <div className="flex items-center gap-3 text-slate-500 text-xs">
                <span>Cargando...</span>
            </div>
        )
    }

    const xpProgress = stats.next_level_xp > 0
        ? Math.min(100, (stats.xp / stats.next_level_xp) * 100)
        : 0

    return (
        <div className="flex items-center gap-4">
            {/* Level Badge */}
            <div className="flex items-center gap-1.5 bg-purple-500/20 px-2.5 py-1 rounded-lg border border-purple-500/30">
                <Star className="h-3.5 w-3.5 text-purple-400" />
                <span className="text-xs font-semibold text-purple-300">Lvl {stats.level}</span>
                {/* Mini XP Bar */}
                <div className="w-10 h-1.5 bg-purple-900/50 rounded-full overflow-hidden">
                    <div
                        className="h-full bg-purple-400 transition-all duration-500"
                        style={{ width: `${xpProgress}%` }}
                    />
                </div>
            </div>

            {/* Win Rate */}
            <div className="flex items-center gap-1.5 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                <Trophy className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-xs font-medium text-emerald-300">
                    {stats.win_rate.toFixed(0)}%
                </span>
            </div>

            {/* PNL */}
            <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${stats.total_pnl >= 0
                    ? 'bg-emerald-500/10 border-emerald-500/20'
                    : 'bg-rose-500/10 border-rose-500/20'
                }`}>
                <TrendingUp className={`h-3.5 w-3.5 ${stats.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`} />
                <span className={`text-xs font-medium ${stats.total_pnl >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                    {stats.total_pnl >= 0 ? '+' : ''}${stats.total_pnl.toFixed(2)}
                </span>
            </div>

            {/* Trades Count */}
            <div className="flex items-center gap-1.5 text-slate-400 text-xs">
                <Zap className="h-3 w-3" />
                <span>{stats.total_trades} trades</span>
            </div>
        </div>
    )
}
