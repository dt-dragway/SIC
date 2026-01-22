'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';

export default function RegisterPage() {
    const router = useRouter();
    const { register } = useAuth();

    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (password !== confirmPassword) {
            setError('Las contraseñas no coinciden');
            return;
        }

        setLoading(true);

        const res = await register(name, email, password);

        if (res.success) {
            router.push('/login?registered=true');
        } else {
            setError(res.error || 'Error desconocido');
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0B0E14] flex items-center justify-center p-4">
            {/* Background effects */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
            </div>

            <div className="w-full max-w-md relative">
                <div className="glass-card border border-white/10 bg-black/40 backdrop-blur-xl p-8 rounded-2xl shadow-2xl">
                    <div className="text-center mb-8">
                        <div className="flex justify-center mb-4">
                            <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-white">
                                    <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                    <circle cx="8.5" cy="7" r="4"></circle>
                                    <line x1="20" y1="8" x2="20" y2="14"></line>
                                    <line x1="23" y1="11" x2="17" y2="11"></line>
                                </svg>
                            </div>
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Crear Cuenta</h2>
                        <p className="text-slate-400 text-sm">Únete a la elite de traders algorítmicos</p>
                    </div>

                    {error && (
                        <div className="mb-6 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex gap-2">
                            <span className="font-bold">Error:</span> {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Nombre Completo</label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500/50 focus:bg-white/10 transition-all font-sans"
                                placeholder="Tu nombre"
                                required
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Email</label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500/50 focus:bg-white/10 transition-all font-mono"
                                placeholder="trader@sic.com"
                                required
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Contraseña</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500/50 focus:bg-white/10 transition-all font-mono"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        <div className="space-y-1">
                            <label className="text-xs font-medium text-slate-400 uppercase tracking-wider">Confirmar Contraseña</label>
                            <input
                                type="password"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-indigo-500/50 focus:bg-white/10 transition-all font-mono"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white font-bold py-3 rounded-xl shadow-lg shadow-indigo-500/20 transition-all active:scale-95 mt-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creando cuenta...' : 'Registrarse'}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-slate-500">
                        ¿Ya tienes cuenta?{' '}
                        <Link href="/login" className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors">
                            Iniciar sesión
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
