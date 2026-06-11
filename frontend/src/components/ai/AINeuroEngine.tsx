'use client';

import { useState, useEffect } from 'react';
import { Brain, TrendingUp, Target, Award, Zap } from 'lucide-react';

interface AIProgress {
    level: number;
    total_analyses: number;
    accuracy: number;
    tools_mastered: number;
    experience_points: number;
    next_level_xp: number;
}

export default function AINeuroEngine() {
    const [progress, setProgress] = useState<AIProgress>({
        level: 1,
        total_analyses: 0,
        accuracy: 0,
        tools_mastered: 0,
        experience_points: 0,
        next_level_xp: 1000
    });

    useEffect(() => {
        fetchAIProgress();
    }, []);

    const fetchAIProgress = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch('/api/v1/ai/progress', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                const data = await res.json();
                setProgress(data);
            } else {
                // Datos simulados si no hay endpoint aún
                setProgress({
                    level: 12,
                    total_analyses: 847,
                    accuracy: 78.5,
                    tools_mastered: 6,
                    experience_points: 8470,
                    next_level_xp: 10000
                });
            }
        } catch (error) {
            // Fallback a datos demo
            setProgress({
                level: 12,
                total_analyses: 847,
                accuracy: 78.5,
                tools_mastered: 6,
                experience_points: 8470,
                next_level_xp: 10000
            });
        }
    };

    const progressPercent = (progress.experience_points / progress.next_level_xp) * 100;
    const getLevelTitle = (level: number) => {
        if (level < 5) return "Aprendiz";
        if (level < 10) return "Analista";
        if (level < 15) return "Trader Pro";
        if (level < 20) return "Experto Institucional";
        return "Maestro IA";
    };

    const getSkillLevel = (tools: number) => {
        if (tools < 3) return { name: "Básico", color: "text-slate-400" };
        if (tools < 5) return { name: "Intermedio", color: "text-cyan-400" };
        return { name: "Avanzado", color: "text-emerald-400" };
    };

    const skill = getSkillLevel(progress.tools_mastered);

    return (
        <div className="glass-card p-6 rounded-3xl border border-white/5 bg-gradient-to-br from-purple-500/10 to-pink-500/5">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500">
                        <Brain size={24} className="text-white" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-white">Neuro Engine IA</h3>
                        <p className="text-xs text-slate-400">Sistema de Aprendizaje Institucional</p>
                    </div>
                </div>

                <div className="text-right">
                    <div className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Nivel {progress.level}
                    </div>
                    <div className="text-xs text-purple-300">{getLevelTitle(progress.level)}</div>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
                <div className="flex justify-between text-xs mb-2">
                    <span className="text-slate-400">Experiencia</span>
                    <span className="text-white font-mono">
                        {progress.experience_points.toLocaleString()} / {progress.next_level_xp.toLocaleString()} XP
                    </span>
                </div>
                <div className="h-3 bg-white/5 rounded-full overflow-hidden border border-white/10">
                    <div
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500 relative overflow-hidden"
                        style={{ width: `${progressPercent}%` }}
                    >
                        {/* Animated shine effect */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
                    </div>
                </div>
                <p className="text-[10px] text-slate-500 mt-1">
                    {(progress.next_level_xp - progress.experience_points).toLocaleString()} XP para siguiente nivel
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                {/* Total Analyses */}
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                        <Target size={14} className="text-cyan-400" />
                        <span className="text-[10px] text-slate-400 uppercase font-bold">Análisis</span>
                    </div>
                    <div className="text-xl font-bold text-white font-mono">{progress.total_analyses}</div>
                </div>

                {/* Accuracy */}
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                        <TrendingUp size={14} className="text-emerald-400" />
                        <span className="text-[10px] text-slate-400 uppercase font-bold">Precisión</span>
                    </div>
                    <div className="text-xl font-bold text-emerald-400 font-mono">{progress.accuracy}%</div>
                </div>

                {/* Tools Mastered */}
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                        <Zap size={14} className="text-purple-400" />
                        <span className="text-[10px] text-slate-400 uppercase font-bold">Herramientas</span>
                    </div>
                    <div className="text-xl font-bold text-white font-mono">{progress.tools_mastered}/6</div>
                </div>

                {/* Skill Level */}
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center gap-2 mb-1">
                        <Award size={14} className="text-amber-400" />
                        <span className="text-[10px] text-slate-400 uppercase font-bold">Nivel</span>
                    </div>
                    <div className={`text-sm font-bold ${skill.color}`}>{skill.name}</div>
                </div>
            </div>

            {/* Skills Progress */}
            <div className="space-y-2">
                <p className="text-[10px] text-slate-500 uppercase font-bold mb-2">Dominio de Módulos</p>

                {[
                    { name: "Microstructure", mastered: true, color: "from-blue-500 to-cyan-500" },
                    { name: "On-Chain", mastered: true, color: "from-emerald-500 to-teal-500" },
                    { name: "Derivatives", mastered: true, color: "from-purple-500 to-pink-500" },
                    { name: "DeFi", mastered: true, color: "from-orange-500 to-red-500" },
                    { name: "Risk Mgmt", mastered: true, color: "from-yellow-500 to-orange-500" },
                    { name: "Backtesting", mastered: progress.tools_mastered >= 6, color: "from-indigo-500 to-purple-500" },
                ].map((skill, i) => (
                    <div key={i} className="flex items-center gap-2">
                        <div className="w-24 text-xs text-slate-400">{skill.name}</div>
                        <div className="flex-1 h-1.5 bg-white/5 rounded-full overflow-hidden">
                            <div
                                className={`h-full bg-gradient-to-r ${skill.color} ${skill.mastered ? 'w-full' : 'w-0'} transition-all duration-1000`}
                            />
                        </div>
                        {skill.mastered && <span className="text-xs text-emerald-400">✓</span>}
                    </div>
                ))}
            </div>

            {/* Learning Status */}
            <div className="mt-4 p-3 rounded-lg bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30">
                <div className="flex items-center gap-2">
                    <div className="h-2 w-2 rounded-full bg-purple-400 animate-pulse"></div>
                    <p className="text-xs text-purple-200">
                        Aprendiendo continuamente de {progress.total_analyses} análisis institucionales
                    </p>
                </div>
            </div>
        </div>
    );
}
