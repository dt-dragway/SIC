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
        user: { id: 1, email: 'admin@sic.com', name: 'Admin', has_2fa: false },
        loading: false,
        isAuthenticated: true,
        token: null
    });

    const autoLoginAdmin = async () => {
        try {
            console.log("🔑 Ejecutando Auto-Login Administrativo Persistente...");
            const formData = new URLSearchParams();
            formData.append('username', 'admin@sic.com');
            formData.append('password', 'Admin24252026**');

            const res = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (res.ok) {
                const data = await res.json();
                const token = data.access_token;
                localStorage.setItem('token', token);
                
                const userRes = await fetch('/api/v1/auth/me', {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                
                if (userRes.ok) {
                    const user = await userRes.json();
                    setState({
                        user,
                        loading: false,
                        isAuthenticated: true,
                        token
                    });
                    console.log("🟢 Auto-Login administrativo completado con éxito.");
                    return true;
                }
            }
        } catch (error) {
            console.error("❌ Falló el Auto-Login en background:", error);
        }
        setState(prev => ({ ...prev, loading: false }));
        return false;
    };

    const logout = async () => {
        console.log("🔐 Logout solicitado en entorno personal - Renovando sesión en background...");
        await autoLoginAdmin();
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
                console.log("🔄 Sesión inválida o expirada en Binance/DB. Reintentando auto-login...");
                await autoLoginAdmin();
            }
        } catch (error) {
            console.error("⚠️ Error conectando con el backend de sesión. Reintentando auto-login...", error);
            await autoLoginAdmin();
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
            autoLoginAdmin().finally(() => clearTimeout(safetyTimeout));
        }

        return () => clearTimeout(safetyTimeout);
    }, []);

    // Inactivity Timer (Disabled by request - session never expires unless manually logged out)
    /*
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
    */

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
