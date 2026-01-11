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
    token: string | null;
    loading: boolean;
    isAuthenticated: boolean;
}

export function useAuth() {
    const router = useRouter();
    const [state, setState] = useState<AuthState>({
        user: null,
        token: null,
        loading: true,
        isAuthenticated: false
    });

    useEffect(() => {
        // Cargar token al iniciar
        const token = localStorage.getItem('token');
        if (token) {
            fetchUser(token);
        } else {
            setState(s => ({ ...s, loading: false }));
        }
    }, []);

    const fetchUser = async (token: string) => {
        try {
            const res = await fetch('/api/v1/auth/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const user = await res.json();
                setState({
                    user,
                    token,
                    loading: false,
                    isAuthenticated: true
                });
            } else {
                logout();
            }
        } catch (error) {
            logout();
        }
    };

    const login = async (email: string, password: string) => {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const res = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem('token', data.access_token);
            await fetchUser(data.access_token);
            return { success: true };
        } else {
            return { success: false, error: data.detail || 'Error al iniciar sesión' };
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

    const logout = () => {
        localStorage.removeItem('token');
        setState({
            user: null,
            token: null,
            loading: false,
            isAuthenticated: false
        });
        router.push('/login');
    };

    return {
        ...state,
        login,
        register,
        logout
    };
}
