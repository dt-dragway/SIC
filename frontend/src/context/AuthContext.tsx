'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface User {
    id: number;
    email: string;
    name: string;
    has_2fa: boolean;
}

interface AuthState {
    user: User | null;
    loading: boolean;
    isAuthenticated: boolean;
    token: string | null;
}

interface AuthContextType extends AuthState {
    login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
    register: (name: string, email: string, password: string) => Promise<{ success: boolean; error?: string }>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const router = useRouter();
    const [state, setState] = useState<AuthState>({
        user: null,
        loading: true,
        isAuthenticated: false,
        token: null
    });

    const logout = async () => {
        localStorage.removeItem('token');
        setState({ user: null, loading: false, isAuthenticated: false, token: null });
        router.push('/login');
    };

    const checkSession = async (token: string) => {
        try {
            const res = await fetch('/api/v1/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (res.ok) {
                const user = await res.json();
                setState({
                    user,
                    loading: false,
                    isAuthenticated: true,
                    token
                });
            } else {
                console.log("Sesión inválida, limpiando...");
                localStorage.removeItem('token');
                setState({ user: null, loading: false, isAuthenticated: false, token: null });
            }
        } catch (error) {
            console.error("Error checking session:", error);
            setState(prev => ({ ...prev, loading: false }));
        }
    };

    useEffect(() => {
        const storedToken = localStorage.getItem('token');

        // Safety timeout: Ensure loading is false after 5 seconds no matter what
        const safetyTimeout = setTimeout(() => {
            setState(prev => {
                if (prev.loading) {
                    console.warn("Safety timeout triggered: Forcing loading to false");
                    return { ...prev, loading: false };
                }
                return prev;
            });
        }, 5000);

        if (storedToken && storedToken !== 'undefined' && storedToken !== 'null') {
            checkSession(storedToken).finally(() => clearTimeout(safetyTimeout));
        } else {
            if (storedToken) localStorage.removeItem('token');
            setState(prev => ({ ...prev, loading: false }));
            clearTimeout(safetyTimeout);
        }

        return () => clearTimeout(safetyTimeout);
    }, []);

    // Inactivity Timer
    useEffect(() => {
        if (!state.isAuthenticated) return;

        const INACTIVITY_LIMIT = 60 * 60 * 1000; // 1 hour
        let timeoutId: NodeJS.Timeout;

        const handleTimeout = () => {
            console.log('⏰ Sesión cerrada por inactividad');
            logout();
        };

        const resetTimer = () => {
            if (timeoutId) clearTimeout(timeoutId);
            timeoutId = setTimeout(handleTimeout, INACTIVITY_LIMIT);
        };

        const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'mousemove'];
        events.forEach(event => window.addEventListener(event, resetTimer));

        resetTimer();

        return () => {
            if (timeoutId) clearTimeout(timeoutId);
            events.forEach(event => window.removeEventListener(event, resetTimer));
        };
    }, [state.isAuthenticated]);

    const login = async (email: string, password: string) => {
        try {
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const res = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            let data;
            try {
                data = await res.json();
            } catch (e) {
                return { success: false, error: 'Respuesta inválida del servidor' };
            }

            if (res.ok) {
                const token = data.access_token;
                localStorage.setItem('token', token);
                await checkSession(token);
                return { success: true };
            } else {
                return { success: false, error: data.detail || 'Credenciales incorrectas' };
            }
        } catch (error) {
            return { success: false, error: 'No se pudo conectar con el servidor' };
        }
    };

    const register = async (name: string, email: string, password: string) => {
        try {
            const res = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password })
            });

            const data = await res.json();
            if (res.ok) {
                return { success: true };
            } else {
                return { success: false, error: data.detail || 'Error al registrarse' };
            }
        } catch (e) {
            return { success: false, error: 'Error de conexión' };
        }
    };

    return (
        <AuthContext.Provider value={{ ...state, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuthContext() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuthContext must be used within an AuthProvider');
    }
    return context;
}
