import { Loader2 } from "lucide-react";

export default function LoadingSpinner() {
    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-[#0B0E14] text-white">
            <div className="relative">
                <div className="absolute inset-0 bg-cyan-500/20 blur-xl rounded-full"></div>
                <Loader2 className="h-16 w-16 text-cyan-400 animate-spin relative z-10" />
            </div>
            <p className="mt-6 text-slate-400 font-medium tracking-wide animate-pulse">
                Cargando SIC Ultra...
            </p>
        </div>
    );
}
