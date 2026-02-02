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
    const { isAuthenticated, token, logout, loading: authLoading } = useAuth();
    const [mode, setMode] = useState<Mode>('practice');
    const [isLoading, setIsLoading] = useState(false);
    const [mounted, setMounted] = useState(false);

    // --- State for Practice Mode ---
    const [practiceTotalUsd, setPracticeTotalUsd] = useState(0);
    const [practiceBalances, setPracticeBalances] = useState<Balance[]>([]);

    // --- State for Real Mode ---
    const [realTotalUsd, setRealTotalUsd] = useState(0);
    const [realBalances, setRealBalances] = useState<Balance[]>([]);

    // Lazy initialization from LocalStorage
    useEffect(() => {
        const loadCache = () => {
            const cachedPractice = localStorage.getItem('sic_wallet_practice');
            const cachedReal = localStorage.getItem('sic_wallet_real');

            if (cachedPractice) {
                try {
                    const parsed = JSON.parse(cachedPractice);
                    setPracticeTotalUsd(parsed.totalUsd || 0);
                    setPracticeBalances(parsed.balances || []);
                } catch (e) { console.error("Error parsing practice cache", e); }
            }

            if (cachedReal) {
                try {
                    const parsed = JSON.parse(cachedReal);
                    setRealTotalUsd(parsed.totalUsd || 0);
                    setRealBalances(parsed.balances || []);
                } catch (e) { console.error("Error parsing real cache", e); }
            }
        };
        loadCache();
        setMounted(true);
    }, []);

    // Load persisted mode
    useEffect(() => {
        if (!mounted) return;
        const savedMode = localStorage.getItem('sic_mode') as Mode;
        if (savedMode) setMode(savedMode);
    }, [mounted]);

    const handleSetMode = (newMode: Mode) => {
        setMode(newMode);
        if (mounted) localStorage.setItem('sic_mode', newMode);
        // The UI will immediately switch to using the other state variables
    };

    const refreshWallet = useCallback(async (silent: boolean = false) => {
        if (authLoading) return;
        if (!isAuthenticated || !token) return;

        if (!silent) setIsLoading(true);

        try {
            const endpoint = mode === 'practice' ? '/api/v1/practice/wallet' : '/api/v1/wallet';

            const res = await fetch(endpoint, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                let newUsd = 0;
                let newBalances: Balance[] = [];

                if (mode === 'practice') {
                    newUsd = data.total_usd || 0;
                    newBalances = (data.balances || []).map((b: any) => ({
                        asset: b.asset,
                        total: b.amount || 0,
                        usd_value: b.usd_value || 0,
                        free: b.amount || 0,
                        locked: 0
                    }));

                    // Update Practice State
                    setPracticeTotalUsd(newUsd);
                    setPracticeBalances(newBalances);
                    localStorage.setItem('sic_wallet_practice', JSON.stringify({ totalUsd: newUsd, balances: newBalances }));

                } else {
                    newUsd = data.total_usd || 0;
                    newBalances = data.balances || [];

                    // Update Real State
                    setRealTotalUsd(newUsd);
                    setRealBalances(newBalances);
                    localStorage.setItem('sic_wallet_real', JSON.stringify({ totalUsd: newUsd, balances: newBalances }));
                }

            } else {
                if (res.status === 401) logout();
            }
        } catch (error) {
            console.error("Error fetching wallet", error);
        } finally {
            if (!silent) setIsLoading(false);
        }
    }, [mode, token, isAuthenticated, authLoading, logout]);

    // Auto-refresh when mode changes
    useEffect(() => {
        if (!mounted) return;
        refreshWallet();
    }, [mode, isAuthenticated, mounted]);

    // Polling
    useEffect(() => {
        if (!mounted || !isAuthenticated) return;
        const intervalTime = mode === 'practice' ? 5000 : 30000;
        const interval = setInterval(() => refreshWallet(true), intervalTime);
        return () => clearInterval(interval);
    }, [mode, isAuthenticated, mounted, refreshWallet]);

    // Derived state for consumers
    const activeTotalUsd = mode === 'practice' ? practiceTotalUsd : realTotalUsd;
    const activeBalances = mode === 'practice' ? practiceBalances : realBalances;

    return (
        <WalletContext.Provider value={{
            mode,
            isLoading,
            totalUsd: activeTotalUsd,
            balances: activeBalances,
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
