'use client';

interface FearGreedMeterProps {
    value: number;
    label: string;
}

export default function FearGreedMeter({ value, label }: FearGreedMeterProps) {
    // Calcular rotación para la aguja o el gradiente
    const rotation = (value / 100) * 180 - 90; // -90 a 90 grados

    const getColor = (val: number) => {
        if (val < 25) return '#f43f5e'; // rose-500
        if (val < 45) return '#fb923c'; // orange-400
        if (val < 55) return '#94a3b8'; // slate-400
        if (val < 75) return '#22d3ee'; // cyan-400
        return '#10b981'; // emerald-500
    };

    return (
        <div className="flex flex-col items-center">
            <div className="relative w-48 h-24 overflow-hidden">
                {/* Arco del medidor */}
                <div
                    className="absolute top-0 left-0 w-48 h-48 rounded-full border-[12px] border-slate-800"
                    style={{
                        background: 'conic-gradient(from 270deg, #f43f5e, #fb923c, #94a3b8, #22d3ee, #10b981)',
                        maskImage: 'radial-gradient(transparent 58%, black 60%)',
                        WebkitMaskImage: 'radial-gradient(transparent 58%, black 60%)'
                    }}
                ></div>

                {/* Aguja */}
                <div
                    className="absolute bottom-0 left-1/2 w-1 h-20 bg-white origin-bottom transition-transform duration-1000 ease-out z-10"
                    style={{ transform: `translateX(-50%) rotate(${rotation}deg)` }}
                >
                    <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 bg-white rounded-full shadow-lg"></div>
                </div>
            </div>

            <div className="mt-4 text-center">
                <p className="text-4xl font-black font-mono" style={{ color: getColor(value) }}>{value}</p>
                <p className="text-sm font-bold uppercase tracking-widest text-slate-400 mt-1">{label}</p>
            </div>

            <div className="flex justify-between w-full mt-6 px-2 text-[8px] uppercase font-bold text-slate-600">
                <span>Miedo Extremo</span>
                <span>Neutral</span>
                <span>Codicia Extrema</span>
            </div>
        </div>
    );
}
