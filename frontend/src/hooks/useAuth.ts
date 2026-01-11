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
}

export function useAuth() {
    const router = useRouter();
    const [state, setState] = useState<AuthState>({
        user: null,
        loading: true,
        isAuthenticated: false
    });

    useEffect(() => {
        // Al iniciar, intentar obtener el usuario usando la cookie de sesión
        checkSession();
    }, []);

    const checkSession = async () => {
        try {
            // Ya no necesitamos enviar el header Authorization
            // El navegador envía la cookie automáticamente
            const res = await fetch('/api/v1/auth/me');

            if (res.ok) {
                const user = await res.json();
                setState({
                    user,
                    loading: false,
                    isAuthenticated: true
                });
            } else {
                setState(prev => ({ ...prev, loading: false, isAuthenticated: false, user: null }));
            }
        } catch (error) {
            setState(prev => ({ ...prev, loading: false, isAuthenticated: false, user: null }));
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
            // El backend ya estableció la cookie HttpOnly
            // Solo necesitamos recargar el estado del usuario
            await checkSession();
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

    const logout = async () => {
        try {
            // Llamar al endpoint de logout para borrar cookies
            await fetch('/api/v1/auth/logout', { method: 'POST' });
        } catch (error) {
            console.error('Error durante logout', error);
        }

        // Limpiar estado local
        setState({
            user: null,
            loading: false,
            isAuthenticated: false
        });
        router.push('/login');
    };

    return {
        ...state,
        login,
        register,
        logout,
        checkSession // Exportamos por si necesitamos revalidar manualmente
    };
}
