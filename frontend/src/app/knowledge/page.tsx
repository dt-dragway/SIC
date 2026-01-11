'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useKnowledge } from '@/hooks/useKnowledge'

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
        <main className="min-h-screen bg-sic-dark">
            <header className="border-b border-sic-border px-6 py-4">
                <div className="max-w-7xl mx-auto flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="text-2xl">🪙</Link>
                        <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                            🧠 Biblioteca de Conocimientos
                        </h1>
                    </div>
                </div>
            </header>

            <div className="max-w-7xl mx-auto p-6 space-y-8">

                {/* Stats Overview */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="glass-card p-6 flex items-center gap-4">
                        <div className="h-12 w-12 rounded-full bg-cyan-500/20 flex items-center justify-center text-2xl">📚</div>
                        <div>
                            <p className="text-gray-400 text-sm">Libros Estudiados</p>
                            <p className="text-3xl font-bold text-white">{stats?.unique_documents || 0}</p>
                        </div>
                    </div>
                    <div className="glass-card p-6 flex items-center gap-4">
                        <div className="h-12 w-12 rounded-full bg-violet-500/20 flex items-center justify-center text-2xl">🧩</div>
                        <div>
                            <p className="text-gray-400 text-sm">Fragmentos de Saber</p>
                            <p className="text-3xl font-bold text-white">{stats?.total_chunks || 0}</p>
                        </div>
                    </div>
                    <div className="glass-card p-6 flex items-center gap-4">
                        <div className="h-12 w-12 rounded-full bg-emerald-500/20 flex items-center justify-center text-2xl">🤖</div>
                        <div>
                            <p className="text-gray-400 text-sm">Estado del Sistema</p>
                            <p className="text-lg font-bold text-emerald-400">RAG Activo</p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                    {/* Upload Section */}
                    <div className="glass-card p-8">
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <span>📥</span> Alimentar al Agente
                        </h2>
                        <p className="text-gray-400 text-sm mb-6">
                            Sube libros en PDF, DOCX o TXT. El agente leerá, procesará y aprenderá todo el contenido para usarlo en sus análisis.
                        </p>

                        <div className="mb-4">
                            <label className="text-sm text-gray-400 mb-2 block">Categoría del Libro</label>
                            <div className="flex gap-2 flex-wrap">
                                {['trading', 'finanzas', 'psicologia', 'analisis_tecnico', 'cripto'].map(cat => (
                                    <button
                                        key={cat}
                                        onClick={() => setSelectedCategory(cat)}
                                        className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${selectedCategory === cat
                                                ? 'bg-cyan-500 text-black'
                                                : 'bg-white/5 text-gray-400 hover:bg-white/10'
                                            }`}
                                    >
                                        #{cat}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div
                            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${dragActive ? 'border-cyan-500 bg-cyan-500/10' : 'border-gray-700 hover:border-gray-500'
                                }`}
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
                                accept=".pdf,.docx,.txt,.md"
                            />

                            {uploading ? (
                                <div className="space-y-4">
                                    <div className="h-8 w-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                                    <p className="text-cyan-400 animate-pulse">Procesando conocimiento...</p>
                                </div>
                            ) : (
                                <label htmlFor="file-upload" className="cursor-pointer space-y-2">
                                    <div className="text-4xl mb-2">📄</div>
                                    <p className="text-lg font-medium text-white">Arrastra un libro aquí</p>
                                    <p className="text-sm text-gray-500">o haz clic para seleccionar</p>
                                </label>
                            )}
                        </div>

                        {uploadStatus && (
                            <div className={`mt-4 p-3 rounded-lg text-center font-medium ${uploadStatus.includes('Error') ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/20 text-emerald-400'
                                }`}>
                                {uploadStatus}
                            </div>
                        )}
                    </div>

                    {/* Search / Test Section */}
                    <div className="glass-card p-8 flex flex-col h-full">
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <span>🧠</span> Probar Conocimiento
                        </h2>

                        <form onSubmit={handleSearch} className="mb-6 relative">
                            <input
                                type="text"
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                placeholder="Pregunta algo (ej: ¿Qué es el RSI?)"
                                className="w-full bg-black/30 border border-gray-700 rounded-xl px-4 py-3 pr-12 text-white focus:border-cyan-500 focus:outline-none transition-all"
                            />
                            <button
                                type="submit"
                                className="absolute right-2 top-2 p-1.5 bg-cyan-500/20 rounded-lg text-cyan-400 hover:bg-cyan-500 hover:text-black transition-all"
                            >
                                🔍
                            </button>
                        </form>

                        <div className="flex-1 overflow-y-auto space-y-4 pr-2 custom-scrollbar max-h-[400px]">
                            {loading ? (
                                <div className="text-center py-8 text-gray-500">Buscando en la mente del agente...</div>
                            ) : searchResults.length > 0 ? (
                                searchResults.map((result, i) => (
                                    <div key={i} className="bg-white/5 border border-white/10 rounded-lg p-4 hover:border-cyan-500/30 transition-all">
                                        <div className="flex justify-between items-start mb-2">
                                            <span className="text-xs font-bold text-cyan-400 bg-cyan-900/30 px-2 py-0.5 rounded">
                                                {(result.relevance * 100).toFixed(0)}% Relevancia
                                            </span>
                                            <span className="text-xs text-gray-500 truncate max-w-[150px]">{result.source}</span>
                                        </div>
                                        <p className="text-sm text-gray-300 line-clamp-4 leading-relaxed">
                                            {result.content}
                                        </p>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-12 text-gray-600 border border-dashed border-gray-800 rounded-xl">
                                    <p>Haz una búsqueda para ver qué ha aprendido el agente</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Library List */}
                <div className="glass-card p-8">
                    <h2 className="text-xl font-bold mb-6">📚 Estantería Virtual</h2>
                    {stats?.documents && stats.documents.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {stats.documents.map((doc, i) => (
                                <div key={i} className="bg-sic-card border border-sic-border p-4 rounded-xl flex items-center gap-3 hover:border-cyan-500/50 transition-all group">
                                    <div className="h-10 w-10 bg-cyan-500/10 rounded-lg flex items-center justify-center text-xl group-hover:scale-110 transition-transform">
                                        📄
                                    </div>
                                    <div className="overflow-hidden">
                                        <h3 className="font-bold text-white truncate text-sm" title={doc}>{doc}</h3>
                                        <p className="text-xs text-gray-500">Procesado</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500 italic">La biblioteca está vacía.</p>
                    )}
                </div>

            </div>
        </main>
    )
}
