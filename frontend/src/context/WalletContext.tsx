'use client'

import { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { useAuth } from '../hooks/useAuth';

export type Mode = 'practice' | 'real';

interface Balance {
    asset: string;
    total: number;
    usd_value: number;
    free?: number;
    locked?: number;
}

interface WalletState {
    mode: Mode;
    isLoading: boolean;
    totalUsd: number;
    balances: Balance[];
    setMode: (mode: Mode) => void;
    refreshWallet: () => Promise<void>;
    refreshBalances: () => Promise<void>;
}

const WalletContext = createContext<WalletState | undefined>(undefined);

export function WalletProvider({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, token, logout } = useAuth();
    const [mode, setMode] = useState<Mode>('practice');
    const [isLoading, setIsLoading] = useState(false);
    const [mounted, setMounted] = useState(false);

    // Unified State
    const [totalUsd, setTotalUsd] = useState(0.00);
    const [balances, setBalances] = useState<Balance[]>([]);

    // Track mount state for client-side only operations
    useEffect(() => {
        setMounted(true);
    }, []);

    // Load persisted mode (only on client)
    useEffect(() => {
        if (!mounted) return;
        const savedMode = localStorage.getItem('sic_mode') as Mode;
        if (savedMode) setMode(savedMode);
    }, [mounted]);

    // Persist mode change
    const handleSetMode = (newMode: Mode) => {
        setMode(newMode);
        if (mounted) {
            localStorage.setItem('sic_mode', newMode);
        }
        // No limpiamos los saldos aquí - esperamos a que lleguen los nuevos datos
        // Esto evita el flash de "$0.00" mientras carga
    };

    const refreshWallet = useCallback(async (silent: boolean = false) => {
        if (!isAuthenticated || !token) {
            setBalances([]);
            setTotalUsd(0);
            return;
        }

        if (!silent) setIsLoading(true);

        try {
            // Determinar endpoint según el modo
            const endpoint = mode === 'practice'
                ? '/api/v1/practice/wallet'
                : '/api/v1/wallet'; // CORREGIDO: era /api/v1/wallet/balance

            const res = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (res.ok) {
                const data = await res.json();

                if (mode === 'practice') {
                    // Practice API response structure
                    setTotalUsd(data.total_usd || 0);

                    // Map practice balances to unified structure
                    const formattedBalances = (data.balances || []).map((b: any) => ({
                        asset: b.asset,
                        total: b.amount || 0,
                        usd_value: b.usd_value || 0,
                        free: b.amount || 0,
                        locked: 0
                    }));
                    setBalances(formattedBalances);

                } else {
                    // Real API returns { total_usd, balances: [...] }
                    setTotalUsd(data.total_usd || 0);
                    const fetchedBalances: Balance[] = data.balances || [];
                    setBalances(fetchedBalances);
                }
            } else {
                console.error(`Failed to fetch ${mode} wallet`, res.status);
                if (res.status === 401) {
                    console.log("Sesión expirada en wallet fetch -> Logout");
                    logout();
                    return;
                }
            }
        } catch (error) {
            console.error("Error fetching wallet", error);
        } finally {
            if (!silent) setIsLoading(false);
        }
    }, [mode, token, isAuthenticated]);

    // Auto-refresh when mode or auth changes (only after mount)
    useEffect(() => {
        if (!mounted) return;
        refreshWallet();
    }, [mode, isAuthenticated, token, mounted]);

    // Polling (every 10s for practice, 30s for real) - SILENT
    useEffect(() => {
        if (!mounted || !isAuthenticated) return;

        const intervalTime = mode === 'practice' ? 10000 : 30000;
        const interval = setInterval(() => refreshWallet(true), intervalTime);
        return () => clearInterval(interval);
    }, [mode, isAuthenticated, mounted]);

    return (
        <WalletContext.Provider value={{
            mode,
            isLoading,
            totalUsd,
            balances,
            setMode: handleSetMode,
            refreshWallet: () => refreshWallet(false),
            refreshBalances: () => refreshWallet(false)
        }}>
            {children}
        </WalletContext.Provider>
    );
}

export function useWallet() {
    const context = useContext(WalletContext);
    if (context === undefined) {
        throw new Error('useWallet must be used within a WalletProvider');
    }
    return context;
}
