'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useKnowledge } from '@/hooks/useKnowledge'
import DashboardLayout from '../../components/layout/DashboardLayout'
import { BookOpen, Brain, Sparkles, UploadCloud, Search, FileText, Hash, Command } from 'lucide-react'

export default function KnowledgePage() {
    const { stats, searchResults, loading, uploading, uploadBook, searchKnowledge, refreshStats } = useKnowledge()
    const [searchQuery, setSearchQuery] = useState('')
    const [dragActive, setDragActive] = useState(false)
    const [selectedCategory, setSelectedCategory] = useState('trading')
    const [uploadStatus, setUploadStatus] = useState<string | null>(null)

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true)
        } else if (e.type === "dragleave") {
            setDragActive(false)
        }
    }

    const handleDrop = async (e: React.DragEvent) => {
        e.preventDefault()
        e.stopPropagation()
        setDragActive(false)
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            await handleFile(e.dataTransfer.files[0])
        }
    }

    const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault()
        if (e.target.files && e.target.files[0]) {
            await handleFile(e.target.files[0])
        }
    }

    const handleFile = async (file: File) => {
        setUploadStatus('Subiendo...')
        try {
            await uploadBook(file, selectedCategory)
            setUploadStatus('✅ ¡Libro procesado correctamente!')
            setTimeout(() => setUploadStatus(null), 3000)
        } catch (error) {
            setUploadStatus('❌ Error al subir libro')
        }
    }

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault()
        if (searchQuery.trim()) {
            searchKnowledge(searchQuery)
        }
    }

    return (
        <DashboardLayout>
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header Section */}
                <div>
                    <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 bg-clip-text text-transparent flex items-center gap-3">
                        <BookOpen className="text-cyan-400" size={32} />
                        Biblioteca de Conocimientos
                    </h1>
                    <p className="text-slate-400 text-sm mt-2 max-w-2xl">
                        Alimenta el cerebro de la IA con libros, bitácoras y análisis técnicos.
                        Todo lo que subas será aprendido y usado para mejorar las señales de trading.
                    </p>
                </div>

                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="glass-card p-6 rounded-3xl border border-cyan-500/10 bg-cyan-500/[0.02] flex items-center gap-4 relative overflow-hidden group">
                        <div className="absolute right-0 top-0 opacity-5 group-hover:opacity-10 transition-opacity">
                            <BookOpen size={100} />
                        </div>
                        <div className="h-12 w-12 rounded-2xl bg-cyan-500/20 flex items-center justify-center text-cyan-400 shadow-lg shadow-cyan-500/10">
                            <BookOpen size={24} />
                        </div>
                        <div>
                            <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">Libros Estudiados</p>
                            <p className="text-3xl font-bold text-white font-mono mt-1">{stats?.unique_documents || 0}</p>
                        </div>
                    </div>

                    <div className="glass-card p-6 rounded-3xl border border-violet-500/10 bg-violet-500/[0.02] flex items-center gap-4 relative overflow-hidden group">
                        <div className="absolute right-0 top-0 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Sparkles size={100} />
                        </div>
                        <div className="h-12 w-12 rounded-2xl bg-violet-500/20 flex items-center justify-center text-violet-400 shadow-lg shadow-violet-500/10">
                            <Brain size={24} />
                        </div>
                        <div>
                            <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">Nodos de Saber</p>
                            <p className="text-3xl font-bold text-white font-mono mt-1">{stats?.total_chunks || 0}</p>
                        </div>
                    </div>

                    <div className="glass-card p-6 rounded-3xl border border-emerald-500/10 bg-emerald-500/[0.02] flex items-center gap-4 relative overflow-hidden group">
                        <div className="absolute right-0 top-0 opacity-5 group-hover:opacity-10 transition-opacity">
                            <Command size={100} />
                        </div>
                        <div className="h-12 w-12 rounded-2xl bg-emerald-500/20 flex items-center justify-center text-emerald-400 shadow-lg shadow-emerald-500/10">
                            <Command size={24} />
                        </div>
                        <div>
                            <p className="text-slate-500 text-xs font-bold uppercase tracking-wider">Estado RAG</p>
                            <p className="text-xl font-bold text-emerald-400 mt-1 flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                Activo
                            </p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">

                    {/* Left Column: Upload (5 cols) */}
                    <div className="lg:col-span-5 space-y-6">
                        <div className="glass-card p-8 rounded-3xl border border-white/5 bg-gradient-to-b from-white/[0.02] to-transparent">
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-white">
                                <UploadCloud className="text-cyan-400" size={20} />
                                Alimentar al Agente
                            </h2>

                            <div className="mb-6">
                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3 block">Categoría del Material</label>
                                <div className="flex gap-2 flex-wrap">
                                    {['trading', 'finanzas', 'psicologia', 'analisis_tecnico', 'bitacoras', 'cripto'].map(cat => (
                                        <button
                                            key={cat}
                                            onClick={() => setSelectedCategory(cat)}
                                            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all border ${selectedCategory === cat
                                                ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/50 shadow-lg shadow-cyan-500/10'
                                                : 'bg-white/5 text-slate-400 border-white/5 hover:bg-white/10 hover:border-white/10'
                                                }`}
                                        >
                                            <span className="opacity-50 mr-1">#</span>{cat}
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <div
                                className={`
                                    relative border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300
                                    ${dragActive
                                        ? 'border-cyan-500 bg-cyan-500/10 scale-[1.02]'
                                        : 'border-white/10 hover:border-white/20 hover:bg-white/[0.02]'
                                    }
                                `}
                                onDragEnter={handleDrag}
                                onDragLeave={handleDrag}
                                onDragOver={handleDrag}
                                onDrop={handleDrop}
                            >
                                <input
                                    type="file"
                                    id="file-upload"
                                    className="hidden"
                                    onChange={handleChange}
                                    accept=".pdf,.docx,.txt,.md,.png,.jpg,.jpeg"
                                />

                                {uploading ? (
                                    <div className="space-y-4 py-8">
                                        <div className="relative mx-auto h-16 w-16">
                                            <div className="absolute inset-0 rounded-full border-4 border-cyan-500/30"></div>
                                            <div className="absolute inset-0 rounded-full border-4 border-cyan-500 border-t-transparent animate-spin"></div>
                                            <UploadCloud className="absolute inset-0 m-auto text-cyan-400 animate-pulse" size={24} />
                                        </div>
                                        <div>
                                            <p className="text-white font-medium">Procesando y Aprendiendo...</p>
                                            <p className="text-xs text-slate-500 mt-1">Extrayendo conocimiento vectorial</p>
                                        </div>
                                    </div>
                                ) : (
                                    <label htmlFor="file-upload" className="cursor-pointer space-y-4 block py-8 group">
                                        <div className="h-16 w-16 mx-auto bg-white/5 rounded-full flex items-center justify-center group-hover:bg-cyan-500/20 group-hover:scale-110 transition-all duration-300">
                                            <UploadCloud className="text-slate-400 group-hover:text-cyan-400 transition-colors" size={32} />
                                        </div>
                                        <div>
                                            <p className="text-lg font-bold text-white group-hover:text-cyan-400 transition-colors">Arrastra archivos aquí</p>
                                            <p className="text-xs text-slate-500 mt-2 max-w-[200px] mx-auto leading-relaxed">
                                                Soporta PDF, DOCX, TXT e imágenes de bitácoras (.png, .jpg)
                                            </p>
                                        </div>
                                    </label>
                                )}
                            </div>

                            {uploadStatus && (
                                <div className={`mt-4 p-4 rounded-xl text-center text-sm font-bold flex items-center justify-center gap-2 ${uploadStatus.includes('Error') ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                    }`}>
                                    {uploadStatus.includes('Error') ? null : <Sparkles size={16} />}
                                    {uploadStatus}
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Right Column: Search & Test (7 cols) */}
                    <div className="lg:col-span-7 flex flex-col h-full">
                        <div className="glass-card p-8 rounded-3xl border border-white/5 bg-gradient-to-b from-white/[0.02] to-transparent h-full flex flex-col">
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-white">
                                <Search className="text-violet-400" size={20} />
                                Consultar Cerebro
                            </h2>

                            <form onSubmit={handleSearch} className="mb-6 relative group">
                                <div className="absolute inset-0 bg-gradient-to-r from-violet-500/20 to-indigo-500/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <div className="relative">
                                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500 group-focus-within:text-violet-400 transition-colors" size={20} />
                                    <input
                                        type="text"
                                        value={searchQuery}
                                        onChange={(e) => setSearchQuery(e.target.value)}
                                        placeholder="Pregúntale algo al agente (ej: ¿Qué dice el libro sobre gestión de riesgo?)"
                                        className="w-full bg-[#050508] border border-white/10 rounded-xl py-4 pl-12 pr-4 text-white focus:border-violet-500/50 focus:ring-1 focus:ring-violet-500/50 focus:outline-none transition-all placeholder:text-slate-600"
                                    />
                                </div>
                            </form>

                            <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar min-h-[300px] max-h-[500px]">
                                {loading ? (
                                    <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4 opacity-50">
                                        <div className="animate-spin text-violet-500"><Command size={32} /></div>
                                        <p className="text-sm font-mono animate-pulse">Consultando vectores...</p>
                                    </div>
                                ) : searchResults.length > 0 ? (
                                    searchResults.map((result, i) => (
                                        <div key={i} className="bg-white/[0.03] border border-white/5 rounded-2xl p-5 hover:border-violet-500/30 hover:bg-violet-500/[0.02] transition-all group">
                                            <div className="flex justify-between items-start mb-3">
                                                <div className="flex items-center gap-2">
                                                    <span className="p-1.5 rounded-md bg-white/5 text-slate-400 font-mono text-xs border border-white/5">DOC</span>
                                                    <span className="text-xs font-bold text-violet-400 bg-violet-500/10 px-2 py-1 rounded-md border border-violet-500/20">
                                                        {(result.relevance * 100).toFixed(0)}% Match
                                                    </span>
                                                </div>
                                                <span className="text-[10px] uppercase font-bold tracking-wider text-slate-500 flex items-center gap-1">
                                                    <Hash size={10} />
                                                    {result.source}
                                                </span>
                                            </div>
                                            <p className="text-sm text-slate-300 leading-relaxed font-mono text-justify opacity-80 group-hover:opacity-100 transition-opacity pl-2 border-l-2 border-slate-700/50 group-hover:border-violet-500/50">
                                                "{result.content}"
                                            </p>
                                        </div>
                                    ))
                                ) : (
                                    <div className="h-full flex flex-col items-center justify-center text-slate-600 gap-4 border-2 border-dashed border-white/5 rounded-2xl p-12">
                                        <Brain size={48} className="text-slate-800" />
                                        <div className="text-center">
                                            <p className="text-white font-medium">Búsqueda Semántica</p>
                                            <p className="text-sm mt-1">Escribe arriba para explorar la memoria del agente.</p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Library List */}
                <div className="glass-card p-8 rounded-3xl border border-white/5 bg-gradient-to-t from-black/40 to-transparent">
                    <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-white">
                        <FileText className="text-emerald-400" size={20} />
                        Estantería Virtual
                    </h2>
                    {stats?.documents && stats.documents.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {stats.documents.map((doc, i) => (
                                <div key={i} className="bg-black/20 border border-white/5 p-4 rounded-xl flex items-center gap-4 hover:border-emerald-500/30 hover:bg-emerald-500/[0.05] transition-all group cursor-default">
                                    <div className="h-10 w-10 bg-emerald-500/10 rounded-lg flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
                                        <FileText size={20} />
                                    </div>
                                    <div className="overflow-hidden">
                                        <h3 className="font-bold text-slate-200 truncate text-xs font-mono group-hover:text-emerald-300">{doc}</h3>
                                        <p className="text-[10px] text-slate-500 uppercase tracking-wider mt-0.5">Indexado</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-slate-500 italic text-center py-8">La biblioteca está vacía. Sube tu primer libro arriba.</p>
                    )}
                </div>

            </div>
        </DashboardLayout>
    )
}
