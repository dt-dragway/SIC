'use client'

import { useEffect } from 'react'
import { AlertCircle, RefreshCcw } from 'lucide-react'

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        // Log the error to an analytics service or terminal
        console.error('CRITICAL_FRONTEND_ERROR:', error)
    }, [error])

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0a0f] text-white p-6">
            <div className="mate-card max-w-md w-full p-8 text-center flex flex-col items-center gap-6 border-rose-500/20 shadow-2xl shadow-rose-500/5">
                <div className="w-16 h-16 rounded-full bg-rose-500/10 flex items-center justify-center border border-rose-500/30">
                    <AlertCircle className="text-rose-400 w-8 h-8" />
                </div>

                <div className="space-y-2">
                    <h1 className="text-2xl font-bold tracking-tight">Vulnerabilidad de Sesión Detectada</h1>
                    <p className="text-slate-400 text-sm leading-relaxed">
                        Se ha producido un desbordamiento de estado o pérdida de sincronización en el renderizado. El centinela ha bloqueado la ejecución para proteger tus datos.
                    </p>
                </div>

                <button
                    onClick={() => reset()}
                    className="w-full py-3 px-6 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all font-bold flex items-center justify-center gap-2 group"
                >
                    <RefreshCcw className="w-4 h-4 group-hover:rotate-180 transition-transform duration-500" />
                    Reiniciar Núcleo UI
                </button>

                <div className="text-[10px] text-slate-600 font-mono uppercase tracking-widest">
                    SIC_ULTRA_PROTECTED_ENVIRONMENT
                </div>
            </div>
        </div>
    )
}
