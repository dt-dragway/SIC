"use client";

import DashboardLayout from '@/components/layout/DashboardLayout';
import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Badge,
  Button,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/components/ui';
import {
  TrendingUp,
  TrendingDown,
  Target,
  Activity,
  Clock,
  DollarSign,
  BarChart3,
  Eye
} from 'lucide-react';

interface TradeMarker {
  id: string;
  symbol: string;
  side: 'LONG' | 'SHORT';
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  quantity: number;
  entry_time: string;
  status: 'ACTIVE' | 'CLOSED' | 'STOPPED' | 'PROFIT_TAKEN';
  pnl?: number;
  exit_price?: number;
  exit_time?: string;
  confidence?: number;
  tier?: string;
  time?: string;
}

interface ChartData {
  symbol: string;
  markers: Array<{
    id: string;
    position: 'entry' | 'exit' | 'stop_loss' | 'take_profit';
    price: number;
    time: string;
    side: string;
    color: string;
    label: string;
    confidence?: number;
    tier?: string;
    status?: string;
    sl?: number;
    tp?: number;
    pnl?: number;
  }>;
  active_count: number;
  recent_pnl: number;
  stats: {
    total_trades: number;
    win_rate: number;
    avg_pnl: number;
    best_trade: number;
    worst_trade: number;
  };
}

export default function TradeMarkersPage() {
  const [activeTrades, setActiveTrades] = useState<TradeMarker[]>([]);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('BTCUSDT');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'];

  useEffect(() => {
    fetchTradeData();
    const interval = setInterval(fetchTradeData, 10000);
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const fetchTradeData = async () => {
    try {
      setLoading(true);
      const chartResponse = await fetch(`/api/v1/trade-markers/chart-data/${selectedSymbol}`);
      if (chartResponse.ok) {
        const data = await chartResponse.json();
        setChartData(data.chart_data);
      }

      const activeResponse = await fetch(`/api/v1/trade-markers/active-markers/${selectedSymbol}`);
      if (activeResponse.ok) {
        const data = await activeResponse.json();
        setActiveTrades(data.data.markers.filter((m: any) => m.position === 'entry'));
      }
    } catch (err) {
      setError('Error cargando datos de trades');
    } finally {
      setLoading(false);
    }
  };

  const closeTrade = async (tradeId: string, exitPrice: number, pnl: number) => {
    try {
      const response = await fetch(`/api/v1/trade-markers/close-marker/${tradeId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exit_price: exitPrice, pnl: pnl, exit_reason: 'MANUAL' })
      });
      if (response.ok) await fetchTradeData();
    } catch (err) {
      setError('Error cerrando trade');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE': return 'bg-green-500';
      case 'CLOSED': return 'bg-blue-500';
      case 'STOPPED': return 'bg-red-500';
      case 'PROFIT_TAKEN': return 'bg-emerald-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading && !chartData) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Trade Markers</h1>
            <p className="text-gray-400 mt-2">Monitoreo de trades activos y marcadores en gráficos</p>
          </div>
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700"
          >
            {symbols.map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>

        {error && (
          <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-2 rounded-lg">
            {error}
          </div>
        )}

        {chartData && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Win Rate</p>
                    <p className="text-white font-semibold text-lg">{chartData.stats.win_rate}%</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-green-400" />
                </div>
              </CardContent>
            </Card>
            {/* Otros stats... */}
          </div>
        )}

        <Tabs defaultValue="active" className="space-y-4">
          <TabsList className="bg-gray-800 border-gray-700">
            <TabsTrigger value="active" className="text-white">Trades Activos</TabsTrigger>
            <TabsTrigger value="markers" className="text-white">Marcadores</TabsTrigger>
          </TabsList>

          <TabsContent value="active">
            <Card className="bg-gray-800 border-gray-700">
              <CardContent className="pt-6">
                {activeTrades.length === 0 ? (
                  <p className="text-center text-gray-500">No hay trades activos</p>
                ) : (
                  <div className="space-y-4">
                    {activeTrades.map(trade => (
                      <div key={trade.id} className="p-4 bg-gray-900 rounded-lg flex justify-between items-center">
                        <div>
                          <p className="text-white font-bold">{trade.symbol} - {trade.side}</p>
                          <p className="text-gray-400 text-sm">Entrada: ${trade.entry_price}</p>
                        </div>
                        <Badge className={getStatusColor(trade.status)}>{trade.status}</Badge>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}