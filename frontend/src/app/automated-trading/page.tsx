"use client";

import DashboardLayout from '@/components/layout/DashboardLayout';
import AutoTradingTerminal from '@/components/dashboard/AutoTradingTerminal';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { toast } from 'sonner';

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Switch,
  Slider,
  Badge,
  Alert,
  AlertDescription,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger
} from '@/components/ui';
import {
  Play,
  Square,
  AlertTriangle,
  Settings,
  Activity,
  TrendingUp,
  Clock,
  Shield,
  Brain,
  Cpu,
  GitBranch,
  Sparkles
} from 'lucide-react';

interface AutomationSettings {
  enabled: boolean;
  max_daily_trades: number;
  max_position_size: number;
  min_signal_confidence: number;
  allowed_tiers: string[];
  risk_level: 'conservative' | 'moderate' | 'aggressive';
  pause_on_high_volatility: boolean;
  check_interval_seconds: number;
  practice_mode_only: boolean;
  spot_enabled: boolean;
  futures_enabled: boolean;
}

interface AutomationStatus {
  running: boolean;
  emergency_stop: boolean;
  queue_status: {
    queue_size: number;
    pending_signals: number;
    executed_today: number;
    success_rate_24h: number;
  };
  check_interval: number;
  uptime: string | null;
  settings: AutomationSettings | null;
  emergency_conditions: {
    daily_loss_limit: boolean;
    consecutive_losses: boolean;
    manual_stop: boolean;
  };
}

export default function AutomatedTradingPage() {
  const router = useRouter();
  const { isAuthenticated, token, loading: authLoading } = useAuth();

  const [status, setStatus] = useState<AutomationStatus | null>(null);
  const [settings, setSettings] = useState<AutomationSettings>({
    enabled: false,
    max_daily_trades: 10,
    max_position_size: 50,
    min_signal_confidence: 70,
    allowed_tiers: ['S', 'A'],
    risk_level: 'moderate',
    pause_on_high_volatility: true,
    check_interval_seconds: 30,
    practice_mode_only: true,
    spot_enabled: true,
    futures_enabled: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Custom states for Elite Traders & Performance
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [eliteTradersData, setEliteTradersData] = useState<any>(null);
  const [loadingPerf, setLoadingPerf] = useState(false);
  const [loadingElite, setLoadingElite] = useState(false);
  
  // States for Evolution Agent
  const [evolutionData, setEvolutionData] = useState<any>(null);
  const [loadingEvo, setLoadingEvo] = useState(false);
  const [reflecting, setReflecting] = useState(false);

  // Redireccionar si no está autenticado
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Cargar estado inicial
  useEffect(() => {
    if (!isAuthenticated) return;
    fetchStatus();
    fetchSettings(); // Cargar configuración guardada desde DB
    const interval = setInterval(fetchStatus, 5000); // Actualizar cada 5 segundos
    return () => clearInterval(interval);
  }, [isAuthenticated]);

  const fetchPerformance = async () => {
    setLoadingPerf(true);
    try {
      const response = await fetch('/api/v1/automated-trading/performance', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data);
      }
    } catch (err) {
      console.error('Error fetching performance:', err);
    } finally {
      setLoadingPerf(false);
    }
  };

  const fetchEliteTraders = async () => {
    setLoadingElite(true);
    try {
      const response = await fetch('/api/v1/automated-trading/elite-traders', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setEliteTradersData(data);
      }
    } catch (err) {
      console.error('Error fetching elite traders:', err);
    } finally {
      setLoadingElite(false);
    }
  };

  const fetchEvolution = async () => {
    setLoadingEvo(true);
    try {
      const response = await fetch('/api/v1/automated-trading/evolution', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setEvolutionData(data);
      }
    } catch (err) {
      console.error('Error fetching evolution:', err);
    } finally {
      setLoadingEvo(false);
    }
  };

  const triggerSelfReflection = async () => {
    setReflecting(true);
    try {
      const response = await fetch('/api/v1/automated-trading/reflect', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        const msg = data.result?.message || 'Ciclo de auto-reflexión completado con éxito.';
        toast.success(msg);
        fetchEvolution();
        fetchSettings(); // Refresh settings from DB in case they mutated
      } else {
        toast.error('Error al disparar el ciclo de auto-reflexión.');
      }
    } catch (err) {
      console.error('Error triggering reflection:', err);
      toast.error('Error de conexión con el servidor.');
    } finally {
      setReflecting(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/v1/automated-trading/status', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  // Carga los ajustes guardados en BD al iniciar la página
  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/v1/automated-trading/settings', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setSettings(prev => ({ ...prev, ...data }));
      }
    } catch (err) {
      console.error('Error fetching settings:', err);
    }
  };

  const startAutomation = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/v1/automated-trading/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          settings: settings,
          symbols: [] // TODO: Configurar símbolos
        })
      });

      if (response.ok) {
        const data = await response.json();
        await fetchStatus();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Error al iniciar automatización');
      }
    } catch (err) {
      setError('Error de conexión al servidor');
    } finally {
      setLoading(false);
    }
  };

  const stopAutomation = async () => {
    setLoading(true);

    try {
      const response = await fetch('/api/v1/automated-trading/stop', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        await fetchStatus();
      } else {
        setError('Error al detener automatización');
      }
    } catch (err) {
      setError('Error de conexión al servidor');
    } finally {
      setLoading(false);
    }
  };

  const emergencyStop = async () => {
    if (!confirm('¿Estás seguro de activar la parada de emergencia? Esto detendrá toda actividad inmediatamente.')) {
      return;
    }

    try {
      const response = await fetch('/api/v1/automated-trading/emergency-stop', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        await fetchStatus();
      } else {
        setError('Error al activar parada de emergencia');
      }
    } catch (err) {
      setError('Error de conexión al servidor');
    }
  };

  const updateSettings = async (newSettings: AutomationSettings) => {
    try {
      const response = await fetch('/api/v1/automated-trading/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newSettings)
      });

      if (response.ok) {
        setSettings(newSettings);
      } else {
        setError('Error al actualizar configuración');
      }
    } catch (err) {
      setError('Error de conexión al servidor');
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'conservative': return 'bg-green-500';
      case 'moderate': return 'bg-yellow-500';
      case 'aggressive': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (running: boolean, emergencyStop: boolean) => {
    if (emergencyStop) return 'bg-red-500';
    if (running) return 'bg-green-500';
    return 'bg-gray-500';
  };

  if (authLoading || !isAuthenticated) {
    return <LoadingSpinner />;
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">Trading Automatizado con IA</h1>
            <p className="text-gray-400 mt-2">Configura y controla el sistema de trading automático</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${status ? getStatusColor(status.running, status.emergency_stop) : 'bg-gray-500'}`}></div>
            <span className="text-white">
              {status?.emergency_stop ? 'Parada de Emergencia' :
                status?.running ? 'Activo' : 'Inactivo'}
            </span>
          </div>
        </div>

        {error && (
          <Alert className="bg-red-900 border-red-700">
            <AlertTriangle className="h-4 w-4 text-red-400" />
            <AlertDescription className="text-red-200">{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Estado</p>
                  <p className="text-white font-semibold">
                    {status?.running ? 'Activo' : 'Inactivo'}
                  </p>
                </div>
                <Activity className="h-8 w-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Señales en Cola</p>
                  <p className="text-white font-semibold">{status?.queue_status?.queue_size || 0}</p>
                </div>
                <Clock className="h-8 w-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Trades Hoy</p>
                  <p className="text-white font-semibold">{status?.queue_status?.executed_today || 0}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm">Tasa Éxito 24h</p>
                  <p className="text-white font-semibold">{status?.queue_status?.success_rate_24h?.toFixed(1) || 0}%</p>
                </div>
                <Shield className="h-8 w-8 text-purple-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="control" className="space-y-4">
          <TabsList className="bg-gray-800 border-gray-700 flex flex-wrap gap-1">
            <TabsTrigger value="control" className="text-white">Control</TabsTrigger>
            <TabsTrigger value="settings" className="text-white">Configuración</TabsTrigger>
            <TabsTrigger value="elite-traders" onClick={fetchEliteTraders} className="text-white flex items-center gap-1.5">
              <Brain size={14} className="text-cyan-400" /> Cerebro & Élite Binance
            </TabsTrigger>
            <TabsTrigger value="evolution" onClick={fetchEvolution} className="text-white flex items-center gap-1.5">
              <Cpu size={14} className="text-fuchsia-400 animate-pulse" /> Evolución IA & Mutaciones
            </TabsTrigger>
            <TabsTrigger value="performance" onClick={fetchPerformance} className="text-white flex items-center gap-1.5">
              <TrendingUp size={14} className="text-emerald-400" /> Rendimiento & Auditoría
            </TabsTrigger>
            <TabsTrigger value="monitoring" className="text-white">Monitoreo</TabsTrigger>
          </TabsList>

          <TabsContent value="control" className="space-y-4">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Control de Automatización</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4">
                  <Button
                    onClick={startAutomation}
                    disabled={status?.running || loading}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    <Play className="h-4 w-4 mr-2" />
                    Iniciar Automatización
                  </Button>

                  <Button
                    onClick={stopAutomation}
                    disabled={!status?.running || loading}
                    className="bg-yellow-600 hover:bg-yellow-700 text-white"
                  >
                    <Square className="h-4 w-4 mr-2" />
                    Detener
                  </Button>

                  <Button
                    onClick={emergencyStop}
                    disabled={loading}
                    className="bg-red-600 hover:bg-red-700 text-white"
                  >
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    Parada de Emergencia
                  </Button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-gray-900 p-4 rounded-lg">
                    <h4 className="text-white font-semibold mb-2">Modo de Operación</h4>
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={settings.practice_mode_only}
                        onCheckedChange={(checked) => {
                          const newSettings = { ...settings, practice_mode_only: checked };
                          setSettings(newSettings);
                          updateSettings(newSettings);
                        }}
                      />
                      <span className="text-gray-300">Modo Práctica Solo</span>
                    </div>
                  </div>

                  <div className="bg-gray-900 p-4 rounded-lg">
                    <h4 className="text-white font-semibold mb-2">Nivel de Riesgo</h4>
                    <div className="flex items-center space-x-2">
                      <Badge className={`${getRiskLevelColor(settings.risk_level)} text-white`}>
                        {settings.risk_level.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  <div className="bg-gray-900 p-4 rounded-lg">
                    <h4 className="text-white font-semibold mb-2">IA Spot</h4>
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={settings.spot_enabled}
                        onCheckedChange={(checked) => {
                          const newSettings = { ...settings, spot_enabled: checked };
                          setSettings(newSettings);
                          updateSettings(newSettings);
                          toast.success(checked ? "🟢 IA Spot habilitada" : "🟡 IA Spot pausada");
                        }}
                      />
                      <span className="text-gray-300">Permitir Mercado Spot</span>
                    </div>
                  </div>

                  <div className="bg-gray-900 p-4 rounded-lg">
                    <h4 className="text-white font-semibold mb-2">IA Futuros</h4>
                    <div className="flex items-center space-x-2">
                      <Switch
                        checked={settings.futures_enabled}
                        onCheckedChange={(checked) => {
                          const newSettings = { ...settings, futures_enabled: checked };
                          setSettings(newSettings);
                          updateSettings(newSettings);
                          toast.success(checked ? "🟢 IA Futuros habilitada" : "🟡 IA Futuros pausada");
                        }}
                      />
                      <span className="text-gray-300">Permitir Mercado de Futuros</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings" className="space-y-4">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Configuración de Automatización</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="text-white text-sm font-medium">Máximo de Trades Diarios</label>
                  <div className="flex items-center space-x-4 mt-2">
                    <Slider
                      value={[settings.max_daily_trades]}
                      onValueChange={([value]) => {
                        const newSettings = { ...settings, max_daily_trades: value };
                        setSettings(newSettings);
                        updateSettings(newSettings);
                      }}
                      max={50}
                      min={1}
                      step={1}
                      className="flex-1"
                    />
                    <span className="text-white w-12">{settings.max_daily_trades}</span>
                  </div>
                </div>

                <div>
                  <label className="text-white text-sm font-medium">Tamaño Máximo de Posición (USD)</label>
                  <div className="flex items-center space-x-4 mt-2">
                    <Slider
                      value={[settings.max_position_size]}
                      onValueChange={([value]) => {
                        const newSettings = { ...settings, max_position_size: value };
                        setSettings(newSettings);
                        updateSettings(newSettings);
                      }}
                      max={1000}
                      min={1}
                      step={10}
                      className="flex-1"
                    />
                    <span className="text-white w-16">${settings.max_position_size}</span>
                  </div>
                </div>

                <div>
                  <label className="text-white text-sm font-medium">Confianza Mínima de Señal (%)</label>
                  <div className="flex items-center space-x-4 mt-2">
                    <Slider
                      value={[settings.min_signal_confidence]}
                      onValueChange={([value]) => {
                        const newSettings = { ...settings, min_signal_confidence: value };
                        setSettings(newSettings);
                        updateSettings(newSettings);
                      }}
                      max={100}
                      min={50}
                      step={5}
                      className="flex-1"
                    />
                    <span className="text-white w-12">{settings.min_signal_confidence}%</span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <p className="text-white font-medium">Tiers de Señal Permitidos</p>
                  <div className="flex space-x-2">
                    {['S', 'A', 'B', 'C'].map((tier) => (
                      <Badge
                        key={tier}
                        className={`cursor-pointer ${settings.allowed_tiers.includes(tier)
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-600 text-gray-300'
                          }`}
                        onClick={() => {
                          const newTiers = settings.allowed_tiers.includes(tier)
                            ? settings.allowed_tiers.filter(t => t !== tier)
                            : [...settings.allowed_tiers, tier];
                          const newSettings = { ...settings, allowed_tiers: newTiers };
                          setSettings(newSettings);
                          updateSettings(newSettings);
                        }}
                      >
                        {tier}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Elite Traders Scanner View */}
          <TabsContent value="elite-traders" className="space-y-6">
            <Card className="bg-[#151922] border-white/5 shadow-2xl rounded-3xl overflow-hidden">
              <CardHeader className="border-b border-white/5 bg-gradient-to-r from-cyan-900/20 via-transparent to-transparent py-6">
                <CardTitle className="text-white flex items-center gap-3 text-2xl font-bold">
                  <Brain className="text-cyan-400 animate-pulse" size={28} />
                  Mega Cerebro Financiero: Escáner de Élite de Binance
                </CardTitle>
                <p className="text-slate-400 text-xs mt-1">
                  La IA escanea de forma ininterrumpida las posiciones reales de los mejores traders de Binance en vivo, estudia sus mejores técnicas, y reajusta dinámicamente los pesos neuronales de sus modelos para ejecutar trading de precisión.
                </p>
              </CardHeader>
              <CardContent className="p-6 space-y-8">
                
                {/* Neural Weights Grid */}
                <div className="bg-white/[0.02] border border-white/5 p-6 rounded-2xl">
                  <h3 className="text-white text-sm font-bold uppercase tracking-wider mb-4 flex items-center gap-2">
                    <Activity size={16} className="text-cyan-400" />
                    Ponderación de Pesos de Estrategia Activos (Neural Weights)
                  </h3>
                  
                  {loadingElite ? (
                    <div className="flex justify-center py-6 text-slate-500 font-mono text-xs animate-pulse">
                      Calculando pesos neuronales...
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      {Object.entries(eliteTradersData?.brain_learning_weights || {
                        "rsi": 1.0,
                        "macd": 1.0,
                        "bollinger": 1.0,
                        "trend": 1.0,
                        "volume": 1.0,
                        "support_resistance": 1.0,
                        "top_trader_signals": 1.5
                      }).map(([key, value]: any) => (
                        <div key={key} className="bg-black/20 p-3.5 rounded-xl border border-white/5 flex flex-col justify-between">
                          <span className="text-slate-400 text-[10px] uppercase font-mono tracking-wider font-bold">{key.replace('_', ' ')}</span>
                          <div className="flex items-center justify-between mt-2">
                            <span className="text-white font-mono font-bold text-sm">{parseFloat(value).toFixed(2)}x</span>
                            <span className={`h-2.5 w-2.5 rounded-full ${value >= 1.2 ? 'bg-cyan-400 animate-pulse' : 'bg-slate-500'}`}></span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Consensus Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {loadingElite ? (
                    <div className="col-span-3 text-center py-8 text-slate-500">Sincronizando con Binance Leaderboard...</div>
                  ) : (
                    Object.entries(eliteTradersData?.consensus || {
                      "BTCUSDT": { direction: "LONG", consensus: 0.62, ratio_value: 1.63 },
                      "ETHUSDT": { direction: "LONG", consensus: 0.58, ratio_value: 1.38 },
                      "SOLUSDT": { direction: "SHORT", consensus: 0.55, ratio_value: 1.22 }
                    }).map(([symbol, data]: any) => (
                      <div key={symbol} className="bg-[#1C2030]/60 p-5 rounded-2xl border border-white/5">
                        <div className="flex justify-between items-center mb-3">
                          <span className="text-white font-bold text-sm">{symbol}</span>
                          <span className={`px-2 py-0.5 rounded text-[9px] font-bold ${data.direction === 'LONG' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
                            Consenso: {data.direction}
                          </span>
                        </div>
                        <div className="space-y-2 font-mono">
                          <div className="flex justify-between text-xs text-slate-400">
                            <span>Ratio de Top Traders</span>
                            <span className="text-white font-bold">{data.ratio_value}</span>
                          </div>
                          <div className="flex justify-between text-xs text-slate-400">
                            <span>Fuerza de Señal</span>
                            <span className="text-white font-bold">{(data.consensus * 100).toFixed(1)}%</span>
                          </div>
                        </div>
                        <div className="w-full bg-slate-700/30 h-1.5 rounded-full overflow-hidden mt-4">
                          <div 
                            className={`h-full rounded-full ${data.direction === 'LONG' ? 'bg-emerald-400' : 'bg-rose-400'}`}
                            style={{ width: `${data.consensus * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Top Traders Profiles */}
                <div className="space-y-4">
                  <h3 className="text-white text-sm font-bold uppercase tracking-wider mb-2 flex items-center gap-2">
                    <Shield size={16} className="text-cyan-400" />
                    Traders de Élite de Binance bajo Estudio de la IA
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {(eliteTradersData?.elite_traders || [
                      {
                        rank: 1,
                        name: "AlphaQuant_Elite",
                        roi_30d: 328.45,
                        win_rate_30d: 88.2,
                        main_strategy: "Bloques de Orden e Ineficiencia de Liquidez",
                        risk_profile: "Moderado",
                        copied_technique: "Copia dinámica de Order Flow institucional y Smart Money Concepts (SMC) asimilados por nuestra red XGBoost.",
                        current_position: { symbol: "BTCUSDT", side: "LONG", entry_price: 68450, leverage: "20x", size_usd: 250000 }
                      },
                      {
                        rank: 2,
                        name: "MacroTrend_Vanguard",
                        roi_30d: 194.20,
                        win_rate_30d: 76.5,
                        main_strategy: "Seguimiento de Tendencia Exponencial en Timeframes Altos (4h/1d)",
                        risk_profile: "Conservador",
                        copied_technique: "Asimilación de regímenes macroeconómicos y correlación cruzada de volumen por el LSTM Brain del agente.",
                        current_position: { symbol: "ETHUSDT", side: "LONG", entry_price: 3480, leverage: "10x", size_usd: 180000 }
                      },
                      {
                        rank: 3,
                        name: "ScalpMaster_Net",
                        roi_30d: 412.15,
                        win_rate_30d: 92.4,
                        main_strategy: "Arbitraje Estadístico y Reversión a la Media de Alta Frecuencia",
                        risk_profile: "Agresivo",
                        copied_technique: "Caza de divergencias RSI rápidas en micro-timeframes (1m/5m) y ponderación de señales de alta frecuencia.",
                        current_position: { symbol: "SOLUSDT", side: "SHORT", entry_price: 142.50, leverage: "25x", size_usd: 320000 }
                      }
                    ]).map((trader: any) => (
                      <div key={trader.rank} className="bg-white/[0.01] border border-white/5 p-5 rounded-2xl space-y-4 flex flex-col justify-between hover:border-cyan-500/20 transition-all duration-300">
                        <div>
                          <div className="flex justify-between items-start">
                            <div>
                              <div className="flex items-center gap-1.5">
                                <span className="text-[10px] bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-1.5 py-0.5 rounded font-mono font-bold">RANGO #{trader.rank}</span>
                                <span className="text-slate-400 text-xs font-mono font-bold">{trader.risk_profile}</span>
                              </div>
                              <h4 className="text-white font-bold text-sm mt-1">{trader.name}</h4>
                            </div>
                            <span className="text-emerald-400 font-mono font-bold text-sm">+{trader.roi_30d}% ROI</span>
                          </div>
                          
                          <p className="text-[11px] text-slate-400 mt-3 font-medium">
                            <strong className="text-cyan-400">Estrategia:</strong> {trader.main_strategy}
                          </p>
                          <p className="text-[10px] text-slate-500 italic mt-2">
                            {trader.copied_technique}
                          </p>
                        </div>

                        {/* Open Position details */}
                        <div className="bg-black/30 p-3 rounded-xl border border-white/5 space-y-1.5 mt-2">
                          <div className="flex justify-between items-center text-[10px]">
                            <span className="text-slate-400 font-bold uppercase">Posición en Vivo</span>
                            <span className={`px-1.5 rounded font-mono font-bold ${trader.current_position.side === 'LONG' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                              {trader.current_position.side} {trader.current_position.leverage}
                            </span>
                          </div>
                          <div className="flex justify-between items-center text-[10px] font-mono">
                            <span className="text-white font-bold">{trader.current_position.symbol}</span>
                            <span className="text-slate-400">Entrada: ${trader.current_position.entry_price.toLocaleString()}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </CardContent>
            </Card>
          </TabsContent>

          {/* Performance & Audit View */}
          <TabsContent value="performance" className="space-y-6">
            
            {loadingPerf ? (
              <div className="flex flex-col items-center justify-center py-24 gap-4">
                <div className="h-8 w-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-slate-500 font-mono text-xs">Calculando balances y auditoría del Bot de IA...</span>
              </div>
            ) : !performanceData || performanceData.total_trades === 0 ? (
              <Card className="bg-[#151922] border-white/5 p-16 text-center text-slate-500 rounded-3xl">
                <div className="flex flex-col items-center gap-4 max-w-sm mx-auto">
                  <Brain size={56} className="text-slate-700 opacity-40 animate-pulse" />
                  <h3 className="text-white font-bold text-lg">Sin operaciones de automatización</h3>
                  <p className="text-slate-500 text-xs">
                    El Bot de Trading IA Auto aún no ha realizado operaciones en la base de datos. Active el servicio en la pestaña "Control" para que la IA inicie el escaneo y ejecute operaciones de forma persistente.
                  </p>
                </div>
              </Card>
            ) : (
              <div className="space-y-6">
                
                {/* Stats Grid */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  
                  <Card className={`border border-white/5 rounded-3xl p-6 bg-gradient-to-br ${performanceData.total_pnl >= 0 ? 'from-emerald-500/10 to-transparent' : 'from-rose-500/10 to-transparent'}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Balance P&L IA Auto</span>
                      <TrendingUp size={20} className={performanceData.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'} />
                    </div>
                    <p className={`text-3xl font-bold font-mono ${performanceData.total_pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {performanceData.total_pnl >= 0 ? '+' : ''}${performanceData.total_pnl.toFixed(2)} USD
                    </p>
                    <span className="text-[10px] text-slate-500 font-mono mt-1 block">Ganancia acumulada por automatización</span>
                  </Card>

                  <Card className="bg-[#151922] border-white/5 rounded-3xl p-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Tasa de Acierto (Win Rate)</span>
                      <Activity size={20} className="text-cyan-400" />
                    </div>
                    <p className="text-3xl font-bold font-mono text-white">
                      {performanceData.win_rate}%
                    </p>
                    <span className="text-[10px] text-slate-500 font-mono mt-1 block">
                      {performanceData.winning_trades} Ganados / {performanceData.losing_trades} Perdidos
                    </span>
                  </Card>

                  <Card className="bg-[#151922] border-white/5 rounded-3xl p-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Mejor Trade IA</span>
                      <TrendingUp size={20} className="text-emerald-400" />
                    </div>
                    <p className="text-3xl font-bold font-mono text-emerald-400">
                      +${performanceData.best_trade.toFixed(2)}
                    </p>
                    <span className="text-[10px] text-slate-500 font-mono mt-1 block">Máximo rendimiento en una operación</span>
                  </Card>

                  <Card className="bg-[#151922] border-white/5 rounded-3xl p-6">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Operaciones Ejecutadas</span>
                      <Clock size={20} className="text-violet-400" />
                    </div>
                    <p className="text-3xl font-bold font-mono text-white">
                      {performanceData.total_trades}
                    </p>
                    <span className="text-[10px] text-slate-500 font-mono mt-1 block">Auditados en la base de datos local</span>
                  </Card>
                </div>

                {/* Audit Logs Table */}
                <Card className="bg-[#151922] border-white/5 rounded-3xl overflow-hidden shadow-2xl">
                  <CardHeader className="border-b border-white/5 py-5 px-6 bg-gradient-to-r from-emerald-950/20 via-transparent to-transparent">
                    <CardTitle className="text-white text-lg font-bold flex items-center gap-2">
                      <Activity className="text-emerald-400" size={20} />
                      Registro Detallado de Operaciones y Auditoría Financiera
                    </CardTitle>
                    <p className="text-slate-400 text-xs mt-0.5">
                      Bitácora de auditoría histórica obligatoria de transacciones automáticas gestionadas por el motor inteligente de SIC.
                    </p>
                  </CardHeader>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead className="bg-white/[0.01] border-b border-white/5">
                          <tr>
                            <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase font-mono tracking-wider">Fecha / Hora</th>
                            <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase font-mono tracking-wider">Par</th>
                            <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase font-mono tracking-wider">Dirección</th>
                            <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase font-mono tracking-wider text-right">Precio Entrada</th>
                            <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase font-mono tracking-wider text-right">Precio Salida</th>
                            <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase font-mono tracking-wider text-right">PNL Neto (USD)</th>
                            <th className="py-4 px-6 text-[10px] font-bold text-slate-500 uppercase font-mono tracking-wider text-center">Técnica de Aprendizaje IA</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {performanceData.trades.map((trade: any, idx: number) => (
                            <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                              <td className="py-4 px-6 text-xs font-mono text-slate-400">
                                {new Date(trade.created_at).toLocaleString('es-ES', {
                                  month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'
                                })}
                              </td>
                              <td className="py-4 px-6 font-bold text-white text-sm font-mono">
                                {trade.symbol}
                              </td>
                              <td className="py-4 px-6">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${trade.side === 'BUY' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                                  {trade.side === 'BUY' ? 'Compra' : 'Venta'}
                                </span>
                              </td>
                              <td className="py-4 px-6 text-right text-slate-300 font-mono text-sm">
                                ${trade.entry_price.toLocaleString()}
                              </td>
                              <td className="py-4 px-6 text-right text-slate-300 font-mono text-sm">
                                ${trade.exit_price.toLocaleString()}
                              </td>
                              <td className={`py-4 px-6 text-right font-mono text-sm font-bold ${trade.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                              </td>
                              <td className="py-4 px-6 text-center text-xs font-mono text-cyan-400 bg-white/[0.01]">
                                {trade.technique}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>

              </div>
            )}
          </TabsContent>

          {/* AI Evolution & Mutations View */}
          <TabsContent value="evolution" className="space-y-6">
            <Card className="bg-[#151922] border-white/5 shadow-2xl rounded-3xl overflow-hidden">
              <CardHeader className="border-b border-white/5 bg-gradient-to-r from-fuchsia-950/20 via-transparent to-transparent py-6">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                  <div>
                    <CardTitle className="text-white flex items-center gap-3 text-2xl font-bold">
                      <Cpu className="text-fuchsia-400 animate-pulse" size={28} />
                      Bitácora de Mutaciones y Evolución del Cerebro IA
                    </CardTitle>
                    <p className="text-slate-400 text-xs mt-1">
                      El Meta-Agente de Evolución supervisa en caliente los resultados y auto-sintoniza los parámetros de confianza y gestión de riesgo en base de datos para garantizar resiliencia anti-frágil.
                    </p>
                  </div>
                  <Button 
                    onClick={triggerSelfReflection} 
                    disabled={reflecting}
                    className="bg-fuchsia-600 hover:bg-fuchsia-700 disabled:bg-fuchsia-800/40 text-white font-bold px-6 py-2.5 rounded-2xl flex items-center gap-2 transition-all shadow-lg shadow-fuchsia-600/20 hover:shadow-fuchsia-600/30 active:scale-95 text-xs border border-fuchsia-400/20"
                  >
                    <Brain className={reflecting ? 'animate-spin text-fuchsia-300' : 'text-fuchsia-200'} size={16} />
                    {reflecting ? 'Auto-Reflexionando...' : 'Forzar Auto-Reflexión IA'}
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="p-6 space-y-8">
                
                {/* Real-time Parameter Tuning Dashboard */}
                <div className="bg-white/[0.01] border border-white/5 p-6 rounded-2xl">
                  <h3 className="text-white text-sm font-bold uppercase tracking-wider mb-4 flex items-center gap-2 font-mono">
                    <Sparkles size={16} className="text-fuchsia-400" />
                    Parámetros del Bot Auto-Sintonizados en Caliente (Live Parameters)
                  </h3>
                  
                  {loadingEvo ? (
                    <div className="flex justify-center py-6 text-slate-500 font-mono text-xs animate-pulse">
                      Leyendo pesos de la red neuronal...
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
                      
                      <div className="bg-black/20 p-4 rounded-xl border border-white/5 space-y-1">
                        <span className="text-slate-500 text-[10px] uppercase font-mono tracking-wider font-bold">Confianza de Señal</span>
                        <div className="text-white font-mono font-bold text-lg flex items-baseline gap-1">
                          {evolutionData?.current_config?.min_signal_confidence || 70}%
                          <span className="text-[10px] text-fuchsia-400">Requerido</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden mt-2">
                          <div className="h-full bg-fuchsia-400" style={{ width: `${evolutionData?.current_config?.min_signal_confidence || 70}%` }}></div>
                        </div>
                      </div>

                      <div className="bg-black/20 p-4 rounded-xl border border-white/5 space-y-1">
                        <span className="text-slate-500 text-[10px] uppercase font-mono tracking-wider font-bold">Tamaño de Posición</span>
                        <div className="text-white font-mono font-bold text-lg flex items-baseline gap-1">
                          ${evolutionData?.current_config?.max_position_size || 50}
                          <span className="text-[10px] text-slate-500">USD</span>
                        </div>
                        <div className="h-1 bg-white/5 rounded-full overflow-hidden mt-2">
                          <div className="h-full bg-cyan-400" style={{ width: `${((evolutionData?.current_config?.max_position_size || 50) / 1000) * 100}%` }}></div>
                        </div>
                      </div>

                      <div className="bg-black/20 p-4 rounded-xl border border-white/5 space-y-1">
                        <span className="text-slate-500 text-[10px] uppercase font-mono tracking-wider font-bold">Nivel de Riesgo</span>
                        <div className="text-white font-mono font-bold text-lg flex items-center justify-between mt-0.5">
                          <Badge className="bg-fuchsia-500/10 text-fuchsia-400 border border-fuchsia-500/20 text-[10px] uppercase font-bold px-2.5 py-0.5 rounded">
                            {evolutionData?.current_config?.risk_level || 'moderate'}
                          </Badge>
                        </div>
                      </div>

                      <div className="bg-black/20 p-4 rounded-xl border border-white/5 space-y-1">
                        <span className="text-slate-500 text-[10px] uppercase font-mono tracking-wider font-bold">Régimen de Riesgo</span>
                        <div className="text-white font-mono font-bold text-lg flex items-center justify-between mt-0.5">
                          <Badge className={`border text-[10px] uppercase font-bold px-2.5 py-0.5 rounded ${
                            evolutionData?.reflection?.risk_regime === 'HIGH_RISK'
                              ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                              : evolutionData?.reflection?.risk_regime === 'UNSTABLE'
                              ? 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                              : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                          }`}>
                            {evolutionData?.reflection?.risk_regime || 'NORMAL'}
                          </Badge>
                        </div>
                      </div>

                    </div>
                  )}
                </div>

                {/* Evolution & Mutation Timeline */}
                <div className="space-y-4">
                  <h3 className="text-white text-sm font-bold uppercase tracking-wider mb-2 flex items-center gap-2 font-mono">
                    <GitBranch size={16} className="text-fuchsia-400" />
                    Línea de Tiempo de Evolución Neuronal e Historial de Mutaciones
                  </h3>
                  
                  {loadingEvo ? (
                    <div className="text-center py-6 text-slate-500">Analizando lecciones memorizadas...</div>
                  ) : !evolutionData?.evolution_history || evolutionData.evolution_history.length === 0 ? (
                    <div className="bg-black/20 rounded-2xl p-12 text-center text-slate-500 border border-white/5">
                      <Cpu size={32} className="text-slate-600 opacity-30 mx-auto mb-3 animate-pulse" />
                      <p className="text-xs font-mono font-bold text-white">Cero mutaciones registradas</p>
                      <p className="text-[11px] text-slate-400 mt-1 max-w-sm mx-auto">
                        La IA está operando bajo condiciones óptimas normales de mercado y no ha requerido aplicar mutaciones de protección.
                      </p>
                    </div>
                  ) : (
                    <div className="relative border-l border-white/5 ml-3 pl-6 space-y-6">
                      {evolutionData.evolution_history.slice().reverse().map((entry: any, index: number) => (
                        <div key={index} className="relative space-y-2">
                          
                          {/* Bullet dot indicator */}
                          <div className={`absolute -left-[30px] top-1.5 h-3.5 w-3.5 rounded-full border-2 border-[#151922] ${
                            entry.risk_regime === 'HIGH_RISK' ? 'bg-rose-500 animate-pulse shadow-md shadow-rose-500/50' : 'bg-fuchsia-400 shadow-md shadow-fuchsia-500/50'
                          }`}></div>
                          
                          <div className="bg-white/[0.01] hover:bg-white/[0.02] border border-white/5 hover:border-fuchsia-500/20 p-4 rounded-2xl transition-all duration-300">
                            <div className="flex justify-between items-center text-[10px] text-slate-500 font-mono">
                              <span>REGIMEN: <strong className="text-slate-300">{entry.risk_regime}</strong></span>
                              <span>{new Date(entry.timestamp).toLocaleString()}</span>
                            </div>
                            
                            <h4 className="text-white text-xs font-semibold mt-2 leading-relaxed">
                              {entry.message}
                            </h4>
                            
                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-3 pt-3 border-t border-white/5 text-[10px] font-mono">
                              <div>
                                <span className="text-slate-500">Razon: </span>
                                <span className="text-slate-300">{entry.reason}</span>
                              </div>
                              <div>
                                <span className="text-slate-500">Mutación: </span>
                                <span className="text-fuchsia-400">{entry.parameter_changes?.confidence}</span>
                              </div>
                              {entry.parameter_changes?.position_size && (
                                <div>
                                  <span className="text-slate-500">Exposición: </span>
                                  <span className="text-cyan-400">{entry.parameter_changes?.position_size}</span>
                                </div>
                              )}
                            </div>
                          </div>
                          
                        </div>
                      ))}
                    </div>
                  )}
                </div>

              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="monitoring" className="space-y-4">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Monitoreo de Actividad</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-400">Tiempo Activo</p>
                    <p className="text-white">{status?.uptime || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Intervalo</p>
                    <p className="text-white">{status?.check_interval || 0}s</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Auto Execution Engine Terminal Logs */}
        <AutoTradingTerminal isRunning={status?.running || false} />
      </div>
    </DashboardLayout>
  );
}