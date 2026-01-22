import React from 'react';
import { useP2POpportunities, GoldenOpportunity } from '@/hooks/useP2POpportunities';

export default function P2POpportunities() {
    const { opportunities, loading, refresh } = useP2POpportunities();

    if (loading && opportunities.length === 0) {
        return <div className="animate-pulse h-48 bg-white/5 rounded-xl"></div>;
    }

    return (
        <div className="space-y-4">
            <div className="flex justify-between items-center">
                <h2 className="text-xl font-bold bg-gradient-to-r from-amber-200 to-yellow-500 bg-clip-text text-transparent flex items-center gap-2">
                    <span>💎</span> Oportunidades de Oro P2P
                </h2>
                <button
                    onClick={refresh}
                    className="text-xs text-amber-500 hover:text-amber-400 transition-colors"
                >
                    Actualizar
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {opportunities.map((opp, idx) => (
                    <OpportunityCard key={idx} opportunity={opp} />
                ))}

                {opportunities.length === 0 && (
                    <div className="col-span-full py-8 text-center text-slate-500 border border-dashed border-slate-700 rounded-xl">
                        <p>Escaneando el mercado... No se han detectado joyas aún.</p>
                    </div>
                )}
            </div>
        </div>
    );
}

function OpportunityCard({ opportunity }: { opportunity: GoldenOpportunity }) {
    const isArbitrage = opportunity.type === 'ARBITRAGE';

    return (
        <div className={`relative overflow-hidden rounded-xl border p-5 backdrop-blur-md transition-all hover:scale-[1.02] ${isArbitrage
            ? 'bg-amber-500/10 border-amber-500/50 hover:shadow-[0_0_20px_rgba(245,158,11,0.2)]'
            : 'bg-sic-card border-sic-border hover:border-sic-blue'
            }`}>
            {/* Background glow effect */}
            <div className="absolute -top-10 -right-10 h-32 w-32 rounded-full bg-gradient-to-br from-white/10 to-transparent blur-3xl"></div>

            <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">
                        {opportunity.type === 'ARBITRAGE' && '⚖️'}
                        {opportunity.type === 'TIMING' && '⏰'}
                        {opportunity.type === 'TRADER' && '👤'}
                        {opportunity.type === 'VOLUME' && '📦'}
                    </span>
                    <div>
                        <h3 className="font-bold text-white leading-tight">
                            {opportunity.type === 'ARBITRAGE' ? 'Arbitraje Detectado' :
                                opportunity.type === 'TIMING' ? 'Mejor Horario' :
                                    opportunity.type === 'TRADER' ? 'Copiar Trader Top' : 'Oportunidad'}
                        </h3>
                        <span className="text-xs text-slate-400">Puntaje: <b className="text-white">{opportunity.score}/100</b></span>
                    </div>
                </div>

                <span className={`px-2 py-1 rounded text-[10px] font-bold tracking-wider ${opportunity.risk_level === 'LOW' ? 'bg-emerald-500/20 text-emerald-400' :
                    opportunity.risk_level === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-rose-500/20 text-rose-400'
                    }`}>
                    {opportunity.risk_level === 'LOW' ? 'RIESGO BAJO' :
                        opportunity.risk_level === 'MEDIUM' ? 'RIESGO MEDIO' : 'RIESGO ALTO'}
                </span>
            </div>

            <div className="space-y-3 mb-4">
                <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Precio Actual</span>
                    <span className="text-white font-mono">{opportunity.current_price.toFixed(2)}</span>
                </div>

                {isArbitrage && (
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Precio Objetivo</span>
                        <span className="text-emerald-400 font-mono font-bold">{opportunity.target_price.toFixed(2)}</span>
                    </div>
                )}

                {opportunity.potential_profit_percent > 0 && (
                    <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Ganancia Potencial</span>
                        <span className="text-emerald-400 font-bold">+{opportunity.potential_profit_percent.toFixed(2)}%</span>
                    </div>
                )}
            </div>

            <div className="space-y-1 mb-4">
                {opportunity.reasoning.slice(0, 2).map((reason, i) => (
                    <p key={i} className="text-xs text-slate-400 flex items-center gap-2">
                        <span className="w-1 h-1 rounded-full bg-slate-500"></span>
                        {reason}
                    </p>
                ))}
            </div>

            <button className={`w-full py-2 rounded-lg text-sm font-bold transition-all ${isArbitrage
                ? 'bg-gradient-to-r from-amber-500 to-yellow-500 text-black hover:shadow-lg'
                : 'bg-white/10 hover:bg-white/20 text-white'
                }`}>
                {isArbitrage ? '⚡ Ejecutar Arbitraje' : 'Ver Detalles'}
            </button>

        </div>
    );
}
