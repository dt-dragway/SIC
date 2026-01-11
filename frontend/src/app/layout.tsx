import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const jetbrains = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' })

export const metadata: Metadata = {
    title: 'SIC Ultra - Sistema Integral Criptofinanciero',
    description: 'Trading inteligente con IA para criptomonedas',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="es">
            <body className={`${inter.variable} ${jetbrains.variable} antialiased`}>
                {children}
            </body>
        </html>
    )
}
