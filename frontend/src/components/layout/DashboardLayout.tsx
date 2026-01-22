'use client';

import Sidebar from './Sidebar';
import Header from './Header'; // Reuse existing header if possible, or create new

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="min-h-screen bg-[#0B0E14] flex">
            {/* Sidebar (Fixed width) */}
            <div className="hidden lg:block w-64 flex-shrink-0">
                <Sidebar />
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col min-w-0">
                {/* Mobile Header usually goes here if needed, or inside pages */}

                <main className="flex-1 p-4 md:p-6 lg:p-8 overflow-y-auto">
                    {children}
                </main>
            </div>
        </div>
    );
}
