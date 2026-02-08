"use client";

import Link from "next/link";
import { Button } from "@/components/ui";

export default function NotFound() {
    return (
        <div className="flex flex-col items-center justify-center h-screen bg-[#0B0E14] text-white p-6">
            <h2 className="text-4xl font-bold mb-4">404</h2>
            <p className="text-xl mb-6">Página no encontrada</p>
            <Link href="/">
                <Button className="bg-cyan-600 hover:bg-cyan-700">
                    Volver al Inicio
                </Button>
            </Link>
        </div>
    );
}
