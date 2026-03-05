"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui";

export default function Error({
    error,
    reset,
}: {
    error: Error & { digest?: string };
    reset: () => void;
}) {
    useEffect(() => {
        console.error(error);
    }, [error]);

    return (
        <div className="flex flex-col items-center justify-center h-screen bg-[#0B0E14] text-white p-6">
            <h2 className="text-2xl font-bold mb-4">¡Ups! Algo salió mal</h2>
            <p className="text-slate-400 mb-6 text-center max-w-md">
                {error.message || "Ha ocurrido un error inesperado en la interfaz."}
            </p>
            <Button
                onClick={() => reset()}
                className="bg-cyan-600 hover:bg-cyan-700"
            >
                Intentar de nuevo
            </Button>
        </div>
    );
}
