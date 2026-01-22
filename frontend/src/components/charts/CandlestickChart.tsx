'use client'

import { createChart, ColorType, IChartApi } from 'lightweight-charts';
import React, { useEffect, useRef, useState } from 'react';

interface ChartProps {
    symbol: string;
    colors?: {
        backgroundColor?: string;
        lineColor?: string;
        textColor?: string;
        areaTopColor?: string;
        areaBottomColor?: string;
    };
}

export const CandlestickChart = ({
    symbol,
    colors: {
        backgroundColor = 'transparent',
        lineColor = '#2962FF',
        textColor = '#A3A3A3',
    } = {}
}: ChartProps) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);
    const chartRef = useRef<IChartApi | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

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

        // Fetch Real Data from Binance
        const fetchData = async () => {
            try {
                setLoading(true);
                setError(null); // Clear previous errors
                // Binance Public API
                const response = await fetch(`https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=1h&limit=200`);
                if (!response.ok) throw new Error('Error fetching data');
                const data = await response.json();

                // Transform data: [time, open, high, low, close, volume, ...]
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

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [symbol, backgroundColor, textColor]);

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
            <div ref={chartContainerRef} className="w-full h-full" />
        </div>
    );
};
