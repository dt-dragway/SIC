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
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch('/api/v1/p2p/opportunities', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (!res.ok) throw new Error("Error obteniendo oportunidades P2P");
            
            const data = await res.json();
            setOpportunities(data.opportunities || []);
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
