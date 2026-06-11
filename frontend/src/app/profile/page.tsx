'use client';

import { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import DashboardLayout from '@/components/layout/DashboardLayout';

export default function ProfilePage() {
    const { user, loading } = useAuth();
    const [currentPassword, setCurrentPassword] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
    const [isChangingPassword, setIsChangingPassword] = useState(false);

    const handlePasswordChange = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);
        setIsChangingPassword(true);

        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            });

            const data = await res.json();

            if (res.ok) {
                setMessage({ type: 'success', text: 'Contraseña actualizada correctamente' });
                setCurrentPassword('');
                setNewPassword('');
            } else {
                setMessage({ type: 'error', text: data.detail || 'Error al actualizar contraseña' });
            }
        } catch (error) {
            setMessage({ type: 'error', text: 'Error de conexión' });
        } finally {
            setIsChangingPassword(false);
        }
    };

    if (loading) return <div className="min-h-screen bg-[#0B0E14] text-white flex items-center justify-center">Cargando...</div>;

    return (
        <DashboardLayout>

            <main className="max-w-4xl mx-auto p-6 py-12">
                <h1 className="text-3xl font-bold mb-8 flex items-center gap-3">
                    <span className="text-cyan-400">👤</span> Mi Perfil
                </h1>

                <div className="grid gap-8 md:grid-cols-2">
                    {/* Tarjeta de Información Personal */}
                    <div className="glass-card p-8 border border-white/5 bg-white/[0.02] rounded-2xl">
                        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                            Detalles de la Cuenta
                        </h2>

                        <div className="space-y-6">
                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Nombre</label>
                                <div className="text-lg font-medium text-white">{user?.name}</div>
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Email</label>
                                <div className="text-lg font-medium text-white font-mono">{user?.email}</div>
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">ID de Usuario</label>
                                <div className="text-sm font-medium text-slate-400 font-mono">#{user?.id.toString().padStart(6, '0')}</div>
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-500 uppercase tracking-wider mb-1">Estado 2FA</label>
                                <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold ${user?.has_2fa ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-500'}`}>
                                    {user?.has_2fa ? '✅ Activado' : '⚠️ Desactivado'}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Tarjeta de Seguridad */}
                    <div className="glass-card p-8 border border-white/5 bg-white/[0.02] rounded-2xl">
                        <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-400"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                            Seguridad
                        </h2>

                        <form onSubmit={handlePasswordChange} className="space-y-4">
                            {message && (
                                <div className={`p-3 rounded-lg text-sm font-medium ${message.type === 'success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                                    {message.text}
                                </div>
                            )}

                            <div>
                                <label className="block text-sm text-slate-400 mb-1">Contraseña Actual</label>
                                <input
                                    type="password"
                                    value={currentPassword}
                                    onChange={(e) => setCurrentPassword(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500/50"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-slate-400 mb-1">Nueva Contraseña</label>
                                <input
                                    type="password"
                                    value={newPassword}
                                    onChange={(e) => setNewPassword(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500/50"
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={isChangingPassword}
                                className="w-full bg-white/10 hover:bg-white/20 text-white font-bold py-2 rounded-lg transition-all active:scale-95 disabled:opacity-50 mt-2"
                            >
                                {isChangingPassword ? 'Actualizando...' : 'Cambiar Contraseña'}
                            </button>
                        </form>
                    </div>
                </div>
            </main>
        </DashboardLayout>
    );
}
