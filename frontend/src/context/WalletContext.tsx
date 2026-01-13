'use client'

import React, { createContext, useContext, useState, useEffect } from 'react';
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
}

const WalletContext = createContext<WalletState | undefined>(undefined);

export function WalletProvider({ children }: { children: React.ReactNode }) {
    const { isAuthenticated, token } = useAuth();
    const [mode, setMode] = useState<Mode>('practice');
    const [isLoading, setIsLoading] = useState(false);

    // Unified State
    const [totalUsd, setTotalUsd] = useState(0.00);
    const [balances, setBalances] = useState<Balance[]>([]);

    // Load persisted mode
    useEffect(() => {
        const savedMode = localStorage.getItem('sic_mode') as Mode;
        if (savedMode) setMode(savedMode);
    }, []);

    // Persist mode change
    const handleSetMode = (newMode: Mode) => {
        setMode(newMode);
        localStorage.setItem('sic_mode', newMode);
        // Trigger refresh immediately on mode change
        setBalances([]); // Clear previous balances
        setTotalUsd(0);
    };

    const refreshWallet = async (silent: boolean = false) => {
        if (!isAuthenticated || !token) {
            setBalances([]);
            setTotalUsd(0);
            return;
        }

        if (!silent) setIsLoading(true);

        try {
            let endpoint = '';
            if (mode === 'practice') {
                endpoint = '/api/v1/practice/wallet';
            } else {
                endpoint = '/api/v1/wallet';
            }

            const res = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (res.ok) {
                const data = await res.json();

                if (mode === 'practice') {
                    // Practice API returns { current_value, balances: [...] }
                    setTotalUsd(data.current_value || 0);
                    // Map practice balances to unified structure if needed, 
                    // though the API should return compatible structures.
                    // Practice API: { asset, amount, usd_value, avg_buy_price }
                    // We map 'amount' to 'total' to match interface
                    const formattedBalances = data.balances.map((b: any) => ({
                        asset: b.asset,
                        total: b.amount,
                        usd_value: b.usd_value,
                        free: b.amount, // In practice, all is free for now
                        locked: 0
                    }));
                    setBalances(formattedBalances);

                } else {
                    // Real API returns { balances: [{ asset, free, locked, total, usd_value }] }
                    const fetchedBalances: Balance[] = data.balances || [];
                    setBalances(fetchedBalances);

                    // Calculate total USD for real wallet
                    const total = fetchedBalances.reduce((acc, b) => acc + (b.usd_value || 0), 0);
                    setTotalUsd(total);
                }
            } else {
                console.error(`Failed to fetch ${mode} wallet`, res.status);
                if (res.status === 401) {
                    // Token might be expired
                }
            }
        } catch (error) {
            console.error("Error fetching wallet", error);
        } finally {
            if (!silent) setIsLoading(false);
        }
    };

    // Auto-refresh when mode or auth changes
    useEffect(() => {
        refreshWallet();
    }, [mode, isAuthenticated, token]);

    // Polling (every 10s for practice, 30s for real) - SILENT
    useEffect(() => {
        if (!isAuthenticated) return;

        const intervalTime = mode === 'practice' ? 10000 : 30000;
        const interval = setInterval(() => refreshWallet(true), intervalTime);
        return () => clearInterval(interval);
    }, [mode, isAuthenticated]);

    return (
        <WalletContext.Provider value={{
            mode,
            isLoading,
            totalUsd,
            balances,
            setMode: handleSetMode,
            refreshWallet: () => refreshWallet(false)
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
