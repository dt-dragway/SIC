'use client'

import { createChart, ColorType } from 'lightweight-charts';
import React, { useEffect, useRef } from 'react';

interface Trade {
    timestamp: string;
    pnl: number | null;
}

interface PnLChartProps {
    trades: Trade[];
}

export const PnLChart = ({ trades }: PnLChartProps) => {
    const chartContainerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!chartContainerRef.current || trades.length === 0) return;

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#64748b',
            },
            width: chartContainerRef.current.clientWidth,
            height: 300,
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.03)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.03)' },
            },
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
                timeVisible: true,
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            }
        });

        const lineSeries = chart.addLineSeries({
            color: '#10b981',
            lineWidth: 3,
            areaTopColor: 'rgba(16, 185, 129, 0.2)',
            areaBottomColor: 'rgba(16, 185, 129, 0)',
        } as any); // Type cast for area if needed, or use addAreaSeries

        // Calculate cumulative PnL
        let cumulativePnL = 0;
        const data = trades
            .filter(t => t.pnl !== null)
            .sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())
            .map(t => {
                cumulativePnL += t.pnl || 0;
                return {
                    time: Math.floor(new Date(t.timestamp).getTime() / 1000) as any,
                    value: cumulativePnL
                };
            });

        // Ensure unique times for lightweight-charts
        const uniqueData = data.filter((v, i, a) => a.findIndex(t => t.time === v.time) === i);

        lineSeries.setData(uniqueData);
        chart.timeScale().fitContent();

        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({ width: chartContainerRef.current.clientWidth });
            }
        };
        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, [trades]);

    return (
        <div className="w-full h-[300px] relative">
            <div ref={chartContainerRef} className="w-full h-full" />
        </div>
    );
};
