import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { Toaster } from 'sonner'
import { WalletProvider } from '../context/WalletContext'

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
                <WalletProvider>
                    {children}
                    <Toaster
                        richColors
                        position="top-right"
                        theme="dark"
                        closeButton
                        toastOptions={{
                            style: {
                                background: 'rgba(11, 14, 20, 0.85)',
                                backdropFilter: 'blur(12px)',
                                border: '1px solid rgba(255, 255, 255, 0.08)',
                                color: '#e2e8f0',
                                borderRadius: '12px'
                            },
                            className: 'font-sans'
                        }}
                    />
                </WalletProvider>
            </body>
        </html>
    )
}
