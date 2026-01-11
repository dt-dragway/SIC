import { useState, useEffect } from 'react';

export interface GoldenOpportunity {
    type: 'ARBITRAGE' | 'TIMING' | 'TRADER' | 'VOLUME';
    score: number;
    action: string;
    current_price: number;
    target_price: number;
    potential_profit_percent: number;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
    risk_factors: string[];
    valid_until: string;
    best_time: string | null;
    reasoning: string[];
}

export function useP2POpportunities() {
    const [opportunities, setOpportunities] = useState<GoldenOpportunity[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchOpportunities = async () => {
        setLoading(true);
        try {
            // Simulamos llamada a API (reemplazar con fetch real al endpoint que crearemos)
            // const res = await fetch('/api/v1/p2p/opportunities');
            // const data = await res.json();

            // Datos simulados para desarrollo visual inmediato
            const mockData: GoldenOpportunity[] = [
                {
                    type: 'ARBITRAGE',
                    score: 95,
                    action: 'BUY_THEN_SELL',
                    current_price: 36.50,
                    target_price: 37.80,
                    potential_profit_percent: 3.56,
                    risk_level: 'LOW',
                    risk_factors: ['Volatilidad normal'],
                    valid_until: new Date(Date.now() + 15 * 60000).toISOString(),
                    best_time: null,
                    reasoning: [
                        'Spread inusualmente alto detectado',
                        'Diferencia de precio > 3%',
                        'Liquidez suficiente en ambos lados'
                    ]
                },
                {
                    type: 'TRADER',
                    score: 88,
                    action: 'COPY_BUY',
                    current_price: 36.45,
                    target_price: 36.45,
                    potential_profit_percent: 0,
                    risk_level: 'LOW',
                    risk_factors: [],
                    valid_until: new Date(Date.now() + 60 * 60000).toISOString(),
                    best_time: null,
                    reasoning: [
                        'Trader "CryptoKing" activo ahora',
                        'Historial de precios muy competitivo',
                        'Tasa de completación 99.8%'
                    ]
                }
            ];

            setOpportunities(mockData);
        } catch (e) {
            console.error("Error fetching P2P opportunities", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOpportunities();
        const interval = setInterval(fetchOpportunities, 60000); // Actualizar cada minuto
        return () => clearInterval(interval);
    }, []);

    return {
        opportunities,
        loading,
        refresh: fetchOpportunities
    };
}
