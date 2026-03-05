'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, MessageSquare } from 'lucide-react';

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    data?: any;
    recommendation?: any;
}

export default function InstitutionalAIChat({ symbol = "BTCUSDT" }: { symbol?: string }) {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg: ChatMessage = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('/api/v1/ai/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    symbol: symbol,
                    query: input
                })
            });

            if (!response.ok) throw new Error('Error en el análisis');

            const data = await response.json();

            // Construir respuesta de la IA basada en la recomendación
            const aiMsg: ChatMessage = {
                role: 'assistant',
                content: `Basado en mi análisis institucional para ${symbol}:`,
                data: data.data,
                recommendation: data.recommendation
            };

            setMessages(prev => [...prev, aiMsg]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: 'Lo siento, hubo un error al procesar tu solicitud institucional.'
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[500px] glass-card rounded-2xl border border-white/5 bg-black/40 overflow-hidden">
            {/* Header */}
            <div className="p-4 border-b border-white/5 bg-gradient-to-r from-violet-500/10 to-purple-500/10 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="p-2 rounded-lg bg-violet-500/20">
                        <Bot size={20} className="text-violet-400" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-white">Consultor IA Institucional</h3>
                        <p className="text-[10px] text-slate-400">Analizando Microestructura, On-Chain y Riesgo</p>
                    </div>
                </div>
                <Sparkles size={16} className="text-violet-400 animate-pulse" />
            </div>

            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
                {messages.length === 0 && (
                    <div className="h-full flex flex-col items-center justify-center text-center p-8">
                        <MessageSquare size={48} className="text-white/5 mb-4" />
                        <p className="text-slate-400 text-sm">
                            Haz una consulta institucional.<br />
                            <span className="text-xs text-slate-500 italic">Ej: "¿Es buen momento para comprar BTC según las ballenas?"</span>
                        </p>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[85%] rounded-2xl p-3 ${msg.role === 'user'
                                ? 'bg-violet-600 text-white rounded-tr-none'
                                : 'bg-white/5 border border-white/10 text-slate-200 rounded-tl-none'
                            }`}>
                            <p className="text-sm leading-relaxed">{msg.content}</p>

                            {/* Render Recommendation Card if available */}
                            {msg.recommendation && (
                                <div className="mt-3 p-3 rounded-xl bg-black/40 border border-white/5 space-y-2">
                                    <div className="flex justify-between items-center">
                                        <span className={`text-[10px] px-2 py-0.5 rounded font-bold uppercase ${msg.recommendation.action === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' :
                                                msg.recommendation.action === 'SELL' ? 'bg-rose-500/20 text-rose-400' :
                                                    'bg-slate-500/20 text-slate-400'
                                            }`}>
                                            {msg.recommendation.action}
                                        </span>
                                        <span className="text-[10px] text-slate-500 font-bold">Confianza: {msg.recommendation.confidence}%</span>
                                    </div>
                                    <ul className="text-[11px] space-y-1">
                                        {msg.recommendation.reasoning.map((r: string, idx: number) => (
                                            <li key={idx} className="flex items-start gap-2">
                                                <span className="text-violet-400">•</span>
                                                <span>{r}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none p-3">
                            <Loader2 size={16} className="text-violet-400 animate-spin" />
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/5 bg-black/60">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                        placeholder="Pregunta algo al agente..."
                        className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:border-violet-500/50 transition-all"
                    />
                    <button
                        onClick={handleSend}
                        disabled={isLoading || !input.trim()}
                        className="p-2 bg-violet-600 hover:bg-violet-500 disabled:opacity-50 text-white rounded-xl transition-all"
                    >
                        <Send size={18} />
                    </button>
                </div>
            </div>
        </div>
    );
}
