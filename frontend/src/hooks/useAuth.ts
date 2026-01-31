import { useState, useEffect } from 'react';
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

export function useAuth() {
    const router = useRouter();
    const [state, setState] = useState<AuthState>({
        user: null,
        loading: true,
        isAuthenticated: false,
        token: null
    });

    useEffect(() => {
        // Load token from storage on mount
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            checkSession(storedToken);
        } else {
            setState(prev => ({ ...prev, loading: false }));
        }
    }, []);

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
                localStorage.removeItem('token');
                setState({ user: null, loading: false, isAuthenticated: false, token: null });
            }
        } catch (error) {
            localStorage.removeItem('token');
            setState({ user: null, loading: false, isAuthenticated: false, token: null });
        }
    };

    // Logout function definition specifically for internal use in useEffect
    const performLogout = () => {
        localStorage.removeItem('token');
        setState({ user: null, loading: false, isAuthenticated: false, token: null });
        router.push('/login');
    };

    // Inactivity Timer Logic
    useEffect(() => {
        if (!state.isAuthenticated) return;

        const INACTIVITY_LIMIT = 60 * 60 * 1000; // 1 hour in ms
        let inactivityTimer: NodeJS.Timeout;

        const resetTimer = () => {
            if (inactivityTimer) clearTimeout(inactivityTimer);
            inactivityTimer = setTimeout(() => {
                console.log('⏰ Sesión cerrada por inactividad (1h)');
                performLogout();
            }, INACTIVITY_LIMIT);
        };

        // Events to detect activity
        const events = ['mousemove', 'keydown', 'click', 'scroll'];

        // Initial start
        resetTimer();

        // Attach listeners
        events.forEach(event => {
            window.addEventListener(event, resetTimer);
        });

        // Cleanup
        return () => {
            if (inactivityTimer) clearTimeout(inactivityTimer);
            events.forEach(event => {
                window.removeEventListener(event, resetTimer);
            });
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

            // Si falla la red o el backend devuelve 500 sin JSON válido
            let data;
            try {
                data = await res.json();
            } catch (e) {
                return { success: false, error: 'Error de comunicación con el servidor' };
            }

            if (res.ok) {
                const token = data.access_token;
                localStorage.setItem('token', token);
                await checkSession(token);
                return { success: true };
            } else {
                return { success: false, error: data.detail || 'Error al iniciar sesión' };
            }
        } catch (error) {
            console.error('Login error:', error);
            return { success: false, error: 'No se pudo conectar con el servidor' };
        }
    };

    const register = async (name: string, email: string, password: string) => {
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
    };

    const logout = async () => {
        localStorage.removeItem('token');
        setState({ user: null, loading: false, isAuthenticated: false, token: null });
        router.push('/login');
    };

    // Inactivity Timer (1 Hour)
    useEffect(() => {
        if (!state.isAuthenticated) return;

        let timeoutId: any;
        const TIMEOUT_DURATION = 3600000; // 1 hour

        const handleTimeout = () => {
            if (localStorage.getItem('token')) {
                // console.log('Session timed out due to inactivity');
                logout();
            }
        };

        const resetTimer = () => {
            if (timeoutId) clearTimeout(timeoutId);
            timeoutId = setTimeout(handleTimeout, TIMEOUT_DURATION);
        };

        // Events to monitor activity
        const events = ['mousedown', 'keydown', 'scroll', 'touchstart', 'mousemove'];

        events.forEach(event => {
            window.addEventListener(event, resetTimer);
        });

        // Initialize timer
        resetTimer();

        // Cleanup
        return () => {
            if (timeoutId) clearTimeout(timeoutId);
            events.forEach(event => {
                window.removeEventListener(event, resetTimer);
            });
        };
    }, [state.isAuthenticated]);

    return {
        ...state,
        login,
        register,
        logout
    };
}
