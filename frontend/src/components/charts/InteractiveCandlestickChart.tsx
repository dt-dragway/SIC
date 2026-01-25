'use client'

import { createChart, ColorType, IChartApi, ISeriesApi, MouseEventParams } from 'lightweight-charts';
import React, { useEffect, useRef, useState } from 'react';

interface PriceLine {
    id: string
    type: 'entry' | 'stop_loss' | 'take_profit'
    price: number
    color: string
}

interface ChartProps {
    symbol: string
    onPriceClick?: (price: number) => void
    priceLines?: PriceLine[]
    onLineUpdate?: (lineId: string, newPrice: number) => void
    colors?: {
        backgroundColor?: string
        textColor?: string
    }
}

export const InteractiveCandlestickChart = ({
    symbol,
    onPriceClick,
    priceLines = [],
    onLineUpdate,
    colors: {
        backgroundColor = 'transparent',
        textColor = '#A3A3A3',
    } = {}
}: ChartProps) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [hoveredPrice, setHoveredPrice] = useState<number | null>(null);

    useEffect(() => {
        if (!chartContainerRef.current) return;

        const handleResize = () => {
            if (chartRef.current && chartContainerRef.current) {
                chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: backgroundColor },
                textColor,
            },
            width: chartContainerRef.current.clientWidth,
            height: 500,
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
            },
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            crosshair: {
                mode: 1, // Normal crosshair
                vertLine: {
                    width: 1,
                    color: 'rgba(224, 227, 235, 0.5)',
                    style: 3,
                },
                horzLine: {
                    width: 1,
                    color: 'rgba(224, 227, 235, 0.5)',
                    style: 3,
                },
            }
        });

        chartRef.current = chart;

        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10B981', // Emerald 500
            downColor: '#F43F5E', // Rose 500
            borderVisible: false,
            wickUpColor: '#10B981',
            wickDownColor: '#F43F5E',
        });

        candlestickSeriesRef.current = candlestickSeries;

        // Suscribirse a eventos de crosshair para mostrar precio al hacer hover
        chart.subscribeCrosshairMove((param: MouseEventParams) => {
            if (param.point === undefined || param.time === undefined) {
                setHoveredPrice(null);
                return;
            }

            const price = candlestickSeries.coordinateToPrice(param.point.y);
            if (price !== null) {
                setHoveredPrice(price);
            }
        });

        // Evento de clic en el gráfico
        chartContainerRef.current.addEventListener('click', (event) => {
            if (!chartRef.current || !candlestickSeriesRef.current) return;

            const rect = chartContainerRef.current!.getBoundingClientRect();
            const y = event.clientY - rect.top;

            // Convertir coordenada Y a precio
            const price = candlestickSeriesRef.current.coordinateToPrice(y);

            if (price !== null && onPriceClick) {
                onPriceClick(price);
            }
        });

        // Fetch Real Data from Binance
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null);
                const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=15m&limit=200`);
                if (!response.ok) throw new Error('Error fetching data');
                const data = await response.json();

                const candles = data.map((d: any) => ({
                    time: d[0] / 1000,
                    open: parseFloat(d[1]),
                    high: parseFloat(d[2]),
                    low: parseFloat(d[3]),
                    close: parseFloat(d[4]),
                }));

                candlestickSeries.setData(candles);
                chart.timeScale().fitContent();
                setLoading(false);
            } catch (err) {
                console.error("Failed to load chart data", err);
                setError("Market data unavailable");
                setLoading(false);
            }
        };

        fetchData();

        // Actualizar cada 15 segundos
        const interval = setInterval(fetchData, 15000);

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            clearInterval(interval);
            chart.remove();
        };
    }, [symbol, backgroundColor, textColor, onPriceClick]);

    // Agregar/actualizar líneas de precio cuando cambien
    useEffect(() => {
        if (!candlestickSeriesRef.current) return;

        // Limpiar líneas anteriores
        candlestickSeriesRef.current.createPriceLine

        // Agregar nuevas líneas
        priceLines.forEach(line => {
            if (candlestickSeriesRef.current) {
                candlestickSeriesRef.current.createPriceLine({
                    price: line.price,
                    color: line.color,
                    lineWidth: 2,
                    lineStyle: line.type === 'entry' ? 0 : 2, // Sólida para entry, punteada para SL/TP
                    axisLabelVisible: true,
                    title: line.type === 'entry' ? 'Entry' : line.type === 'stop_loss' ? 'SL' : 'TP',
                });
            }
        });
    }, [priceLines]);

    return (
        <div className="relative w-full h-full min-h-[500px]">
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50 z-10 backdrop-blur-sm">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
                </div>
            )}
            {error && (
                <div className="absolute inset-0 flex items-center justify-center z-10">
                    <p className="text-rose-500 font-medium bg-rose-500/10 px-4 py-2 rounded-lg border border-rose-500/20">{error}</p>
                </div>
            )}

            {/* Precio al hacer hover */}
            {hoveredPrice !== null && (
                <div className="absolute top-4 left-4 z-20 bg-black/80 px-3 py-1.5 rounded-lg border border-white/20">
                    <span className="text-white font-mono text-sm font-medium">
                        ${hoveredPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </span>
                </div>
            )}

            {/* Instrucción */}
            <div className="absolute bottom-4 left-4 z-20 bg-black/60 px-3 py-1.5 rounded-lg border border-white/10">
                <span className="text-slate-400 text-xs">
                    💡 Haz clic en el gráfico para marcar un nivel de entrada
                </span>
            </div>

            <div ref={chartContainerRef} className="w-full h-full cursor-crosshair" />
        </div>
    );
};
