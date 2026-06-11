import { useState, useEffect } from 'react';

export interface KnowledgeStats {
    total_chunks: number;
    unique_documents: number;
    categories: Record<string, number>;
    documents: string[];
    status: string;
}

export interface SearchResult {
    content: string;
    source: string;
    title: string;
    relevance: number;
    category: string;
}

export function useKnowledge() {
    const [stats, setStats] = useState<KnowledgeStats | null>(null);
    const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);

    const fetchStats = async () => {
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch('/api/v1/knowledge/stats', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const data = await res.json();
            setStats(data);
        } catch (e) {
            console.error("Error fetching knowledge stats", e);
        }
    };

    const uploadBook = async (file: File, category: string = 'trading') => {
        setUploading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) throw new Error("No autenticado");

            const formData = new FormData();
            formData.append('file', file);
            formData.append('category', category);
            formData.append('title', file.name.replace(/\.[^/.]+$/, ""));

            const res = await fetch('/api/v1/knowledge/upload-book', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!res.ok) {
                const errorData = await res.json().catch(() => ({}));
                throw new Error(errorData.detail || `Error al subir archivo (${res.status})`);
            }

            await fetchStats(); // Actualizar stats
            return true;
        } catch (e) {
            console.error("Error uploading book", e);
            throw e;
        } finally {
            setUploading(false);
        }
    };

    const searchKnowledge = async (query: string) => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            if (!token) return;

            const res = await fetch('/api/v1/knowledge/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ query, n_results: 5 })
            });

            const data = await res.json();
            setSearchResults(data.results);
        } catch (e) {
            console.error("Error searching knowledge", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
    }, []);

    return {
        stats,
        searchResults,
        loading,
        uploading,
        uploadBook,
        searchKnowledge,
        refreshStats: fetchStats
    };
}
