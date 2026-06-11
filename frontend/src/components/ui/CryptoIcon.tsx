import { useState, useEffect } from 'react';
import Image from 'next/image';

interface CryptoIconProps {
    symbol: string;
    className?: string;
    size?: number;
}

export default function CryptoIcon({ symbol, className = "", size = 32 }: CryptoIconProps) {
    const [error, setError] = useState(false);
    const [mounted, setMounted] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    // Color deterministico para el fallback basado en el simbolo
    const getFallbackColor = (sym: string) => {
        const colors = [
            'bg-blue-500', 'bg-emerald-500', 'bg-orange-500',
            'bg-purple-500', 'bg-pink-500', 'bg-indigo-500',
            'bg-cyan-500', 'bg-rose-500'
        ];
        const index = sym.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
        return colors[index % colors.length];
    };

    if (!mounted) {
        // Render simple fallback on server/hydration to match structure
        return (
            <div
                className={`rounded-full flex items-center justify-center font-bold text-white text-xs ${getFallbackColor(symbol)} ${className}`}
                style={{ width: size, height: size, minWidth: size }}
            >
                {symbol[0]?.toUpperCase()}
            </div>
        );
    }

    if (error) {
        return (
            <div
                className={`rounded-full flex items-center justify-center font-bold text-white text-xs ${getFallbackColor(symbol)} ${className}`}
                style={{ width: size, height: size, minWidth: size }}
            >
                {symbol[0]?.toUpperCase()}
            </div>
        );
    }

    // Usar CDN de iconos
    // Opción A: cryptologos (svg) - Alta calidad
    // Opción B: cryptocompare - Muy completo
    // Opción C: github (spothq) - Simple Png
    // Vamos con spothq como backup y cryptologos como primaria si fuera necesario, pero spothq es muy estable.

    // Algunos mappings manuales para casos conocidos
    const symbolMap: Record<string, string> = {
        'USDT': 'usdt',
        'BTC': 'btc',
        'ETH': 'eth',
        'BNB': 'bnb',
        'SOL': 'sol',
        'XRP': 'xrp',
        'ADA': 'ada',
        'DOGE': 'doge',
        'DOT': 'dot',
        'MATIC': 'matic', // Polygon ahora es POL a veces, pero matic_icon suele existir
        'LINK': 'link',
        'LTC': 'ltc',
        'AVAX': 'avax',
        'UNI': 'uni',
        'ATOM': 'atom'
    };

    const ticker = symbolMap[symbol.toUpperCase()] || symbol.toLowerCase();
    const src = `https://raw.githubusercontent.com/spothq/cryptocurrency-icons/master/128/color/${ticker}.png`;

    return (
        <div
            className={`relative rounded-full overflow-hidden ${className}`}
            style={{ width: size, height: size, minWidth: size }}
        >
            <img
                src={src}
                alt={symbol}
                className="w-full h-full object-cover"
                onError={() => setError(true)}
            />
        </div>
    );
}
