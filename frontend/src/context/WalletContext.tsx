'use client'

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';

type Mode = 'practice' | 'real';

interface Balance {
    asset: string;
    total: number;
    usd_value: number;
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
    const { isAuthenticated } = useAuth();
    const [mode, setMode] = useState<Mode>('practice');
    const [isLoading, setIsLoading] = useState(false);

    // Unified State
    const [totalUsd, setTotalUsd] = useState(100.00);
    const [balances, setBalances] = useState<Balance[]>([
        { asset: 'USDT', total: 100.00, usd_value: 100.00 } // Default Practice Balance
    ]);

    // Load persisted mode
    useEffect(() => {
        const savedMode = localStorage.getItem('sic_mode') as Mode;
        if (savedMode) setMode(savedMode);
    }, []);

    // Persist mode change
    const handleSetMode = (newMode: Mode) => {
        setMode(newMode);
        localStorage.setItem('sic_mode', newMode);
    };

    const refreshWallet = async () => {
        setIsLoading(true);

        if (mode === 'practice') {
            // UNIFIED PRACTICE WALLET: Fixed $100 USD (or loaded from local simulation state if we implemented that)
            // For now, consistent reset to $100 or keeping current if we had complex logic
            setTotalUsd(100.00);
            setBalances([
                { asset: 'USDT', total: 100.00, usd_value: 100.00 },
                { asset: 'BTC', total: 0.00, usd_value: 0.00 }
            ]);
            setIsLoading(false);
        } else {
            // REAL WALLET
            if (!isAuthenticated) return;

            try {
                // Fetch real wallet
                const res = await fetch('/api/v1/wallet/');
                if (res.ok) {
                    const data = await res.json();
                    setTotalUsd(data.total_usd);
                    setBalances(data.balances);
                } else {
                    console.error("Failed to fetch real wallet");
                }
            } catch (error) {
                console.error("Error fetching wallet", error);
            } finally {
                setIsLoading(false);
            }
        }
    };

    // Auto-refresh when mode or auth changes
    useEffect(() => {
        refreshWallet();
    }, [mode, isAuthenticated]);

    // Polling for Real mode
    useEffect(() => {
        if (mode === 'real' && isAuthenticated) {
            const interval = setInterval(refreshWallet, 30000);
            return () => clearInterval(interval);
        }
    }, [mode, isAuthenticated]);

    return (
        <WalletContext.Provider value={{
            mode,
            isLoading,
            totalUsd,
            balances,
            setMode: handleSetMode,
            refreshWallet
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
