"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  Target, 
  Shield, 
  Activity,
  Clock,
  DollarSign,
  BarChart3,
  Eye,
  X
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

  // Símbolos disponibles
  const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'];

  useEffect(() => {
    fetchTradeData();
    const interval = setInterval(fetchTradeData, 10000); // Actualizar cada 10 segundos
    return () => clearInterval(interval);
  }, [selectedSymbol]);

  const fetchTradeData = async () => {
    try {
      setLoading(true);
      
      // Obtener datos del gráfico
      const chartResponse = await fetch(`/api/v1/trade-markers/chart-data/${selectedSymbol}`);
      if (chartResponse.ok) {
        const data = await chartResponse.json();
        setChartData(data.chart_data);
      }
      
      // Obtener trades activos
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
        body: JSON.stringify({
          exit_price: exitPrice,
          pnl: pnl,
          exit_reason: 'MANUAL'
        })
      });

      if (response.ok) {
        await fetchTradeData();
      }
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

  const getSideColor = (side: string) => {
    return side === 'LONG' ? 'text-green-400' : 'text-red-400';
  };

  const getSideIcon = (side: string) => {
    return side === 'LONG' ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />;
  };

  if (loading && !chartData) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Trade Markers</h1>
          <p className="text-gray-400 mt-2">Monitoreo de trades activos y marcadores en gráficos</p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700"
          >
            {symbols.map(symbol => (
              <option key={symbol} value={symbol}>{symbol}</option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="bg-red-900 border border-red-700 text-red-200 px-4 py-2 rounded-lg">
          {error}
        </div>
      )}

      {/* Estadísticas del Símbolo */}
      {chartData && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Trades Activos</p>
                  <p className="text-white font-semibold text-lg">{chartData.active_count}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

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

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">PnL Reciente</p>
                  <p className={`font-semibold text-lg ${chartData.recent_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${chartData.recent_pnl.toFixed(2)}
                  </p>
                </div>
                <DollarSign className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Total Trades</p>
                  <p className="text-white font-semibold text-lg">{chartData.stats.total_trades}</p>
                </div>
                <Target className="h-8 w-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      <Tabs defaultValue="active" className="space-y-4">
        <TabsList className="bg-gray-800 border-gray-700">
          <TabsTrigger value="active" className="text-white">Trades Activos</TabsTrigger>
          <TabsTrigger value="markers" className="text-white">Marcadores en Gráfico</TabsTrigger>
          <TabsTrigger value="chart" className="text-white">Vista de Gráfico</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="space-y-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Trades Activos - {selectedSymbol}</CardTitle>
            </CardHeader>
            <CardContent>
              {activeTrades.length === 0 ? (
                <div className="text-center py-8">
                  <Eye className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400">No hay trades activos</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {activeTrades.map((trade) => (
                    <div key={trade.id} className="bg-gray-900 p-4 rounded-lg border border-gray-700">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className={`p-2 rounded-lg ${trade.side === 'LONG' ? 'bg-green-900' : 'bg-red-900'}`}>
                            {getSideIcon(trade.side)}
                          </div>
                          <div>
                            <div className="flex items-center space-x-2">
                              <span className="text-white font-semibold">{trade.symbol}</span>
                              <Badge className={getSideColor(trade.side)}>
                                {trade.side}
                              </Badge>
                              <Badge className={getStatusColor(trade.status)}>
                                {trade.status}
                              </Badge>
                              {trade.tier && (
                                <Badge className="bg-purple-600">
                                  {trade.tier}-Tier
                                </Badge>
                              )}
                            </div>
                            <div className="text-gray-400 text-sm mt-1">
                              Entrada: ${trade.entry_price.toFixed(2)} | 
                              SL: ${trade.stop_loss.toFixed(2)} | 
                              TP: ${trade.take_profit.toFixed(2)}
                            </div>
                            <div className="text-gray-500 text-xs mt-1">
                              {new Date(trade.time).toLocaleString()}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => closeTrade(trade.id, trade.entry_price, 0)}
                          >
                            Cerrar
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="markers" className="space-y-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Marcadores en Gráfico - {selectedSymbol}</CardTitle>
            </CardHeader>
            <CardContent>
              {chartData && chartData.markers.length > 0 ? (
                <div className="space-y-3">
                  {chartData.markers.map((marker) => (
                    <div key={marker.id} className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
                      <div className="flex items-center space-x-3">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: marker.color }}
                        ></div>
                        <div>
                          <div className="text-white font-medium">{marker.label}</div>
                          <div className="text-gray-400 text-sm">
                            {marker.position === 'entry' && marker.confidence && (
                              <>Confianza: {marker.confidence}% | </>
                            )}
                            Precio: ${marker.price.toFixed(2)}
                          </div>
                        </div>
                      </div>
                      <div className="text-gray-500 text-sm">
                        {new Date(marker.time).toLocaleTimeString()}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Target className="h-12 w-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400">No hay marcadores en el gráfico</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="chart" className="space-y-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Vista de Gráfico - {selectedSymbol}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="bg-gray-900 rounded-lg p-4 min-h-[400px] flex items-center justify-center">
                <div className="text-center">
                  <Eye className="h-16 w-16 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400 mb-2">Integración con gráfico de velas</p>
                  <p className="text-gray-500 text-sm">
                    Los marcadores se mostrarán en el gráfico interactivo
                  </p>
                  {chartData && (
                    <div className="mt-4 text-sm">
                      <p className="text-gray-400">Marcadores disponibles:</p>
                      <p className="text-cyan-400">{chartData.markers.length} puntos en el gráfico</p>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}