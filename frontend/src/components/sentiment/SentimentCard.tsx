'use client';

import { TrendingUp, TrendingDown, Minus, Clock, ExternalLink } from 'lucide-react';

interface NewsItem {
    id: number;
    title: string;
    source: string;
    sentiment: 'bullish' | 'bearish' | 'neutral';
    impact_score: number;
    time_ago: string;
}

interface SentimentCardProps {
    news: NewsItem[];
}

export default function SentimentCard({ news }: SentimentCardProps) {
    if (!news || news.length === 0) return null;

    return (
        <div className="space-y-3">
            {news.map((item) => (
                <div
                    key={item.id}
                    className="p-4 rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.06] transition-all group"
                >
                    <div className="flex justify-between items-start gap-3 mb-2">
                        <h4 className="text-sm font-medium text-slate-200 leading-snug group-hover:text-white transition-colors">
                            {item.title}
                        </h4>
                        <div className={`p-1.5 rounded-lg ${item.sentiment === 'bullish' ? 'bg-emerald-500/10 text-emerald-400' :
                                item.sentiment === 'bearish' ? 'bg-rose-500/10 text-rose-400' :
                                    'bg-slate-500/10 text-slate-400'
                            }`}>
                            {item.sentiment === 'bullish' ? <TrendingUp size={14} /> :
                                item.sentiment === 'bearish' ? <TrendingDown size={14} /> :
                                    <Minus size={14} />}
                        </div>
                    </div>

                    <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-wider">
                        <div className="flex items-center gap-3">
                            <span className="text-cyan-400/80">{item.source}</span>
                            <div className="flex items-center gap-1 text-slate-500">
                                <Clock size={10} />
                                <span>{item.time_ago}</span>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-slate-500 italic lowercase flex items-center gap-1">
                                impacto: <span className={item.impact_score > 70 ? 'text-amber-400' : 'text-slate-400'}>{item.impact_score}%</span>
                            </span>
                            <ExternalLink size={10} className="text-slate-600 group-hover:text-cyan-400 cursor-pointer" />
                        </div>
                    </div>
                </div>
            ))}
        </div>
    );
}
