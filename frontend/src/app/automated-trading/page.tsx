"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { Button } from '@/components/ui';
import { Switch } from '@/components/ui';
import { Slider } from '@/components/ui';
import { Badge } from '@/components/ui';
import { Alert, AlertDescription } from '@/components/ui';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui';
import { 
  Play, 
  Square, 
  AlertTriangle, 
  Settings, 
  Activity,
  TrendingUp,
  Clock,
  Shield
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
    practice_mode_only: true
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Cargar estado inicial
  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Actualizar cada 5 segundos
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/v1/automated-trading/status');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        if (data.settings) {
          setSettings(data.settings);
        }
      }
    } catch (err) {
      console.error('Error fetching status:', err);
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
        },
        body: JSON.stringify({
          settings: settings,
          symbols: [] // TODO: Configurar símbolos
        })
      });

      if (response.ok) {
        const data = await response.json();
        await fetchStatus();
        console.log('Automation started:', data);
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
        method: 'POST'
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
        method: 'POST'
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

  return (
    <div className="container mx-auto p-6 space-y-6">
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
        <TabsList className="bg-gray-800 border-gray-700">
          <TabsTrigger value="control" className="text-white">Control</TabsTrigger>
          <TabsTrigger value="settings" className="text-white">Configuración</TabsTrigger>
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
                  <p className="text-gray-400 text-sm mt-2">
                    {settings.practice_mode_only 
                      ? "Solo se ejecutarán trades en modo práctica (sin riesgo real)"
                      : "Se ejecutarán trades reales según configuración"}
                  </p>
                </div>

                <div className="bg-gray-900 p-4 rounded-lg">
                  <h4 className="text-white font-semibold mb-2">Nivel de Riesgo</h4>
                  <div className="flex items-center space-x-2">
                    <Badge className={`${getRiskLevelColor(settings.risk_level)} text-white`}>
                      {settings.risk_level.toUpperCase()}
                    </Badge>
                  </div>
                  <p className="text-gray-400 text-sm mt-2">
                    Configuración actual: {settings.max_daily_trades} trades/día, 
                    max ${settings.max_position_size} por posición
                  </p>
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

              <div>
                <label className="text-white text-sm font-medium">Intervalo de Revisión (segundos)</label>
                <div className="flex items-center space-x-4 mt-2">
                  <Slider
                    value={[settings.check_interval_seconds]}
                    onValueChange={([value]) => {
                      const newSettings = { ...settings, check_interval_seconds: value };
                      setSettings(newSettings);
                      updateSettings(newSettings);
                    }}
                    max={300}
                    min={10}
                    step={10}
                    className="flex-1"
                  />
                  <span className="text-white w-12">{settings.check_interval_seconds}s</span>
                </div>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">Tiers de Señal Permitidos</p>
                    <p className="text-gray-400 text-sm">Selecciona los tiers de señal que se ejecutarán automáticamente</p>
                  </div>
                  <div className="flex space-x-2">
                    {['S', 'A', 'B', 'C'].map((tier) => (
                      <Badge
                        key={tier}
                        className={`cursor-pointer ${
                          settings.allowed_tiers.includes(tier)
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

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">Pausar en Alta Volatilidad</p>
                    <p className="text-gray-400 text-sm">Detiene automáticamente el trading durante períodos de alta volatilidad</p>
                  </div>
                  <Switch
                    checked={settings.pause_on_high_volatility}
                    onCheckedChange={(checked) => {
                      const newSettings = { ...settings, pause_on_high_volatility: checked };
                      setSettings(newSettings);
                      updateSettings(newSettings);
                    }}
                  />
                </div>
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
              <div className="space-y-4">
                <div className="bg-gray-900 p-4 rounded-lg">
                  <h4 className="text-white font-semibold mb-2">Estado del Sistema</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400">Tiempo Activo</p>
                      <p className="text-white">{status?.uptime ? 'Activo' : 'Inactivo'}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Intervalo</p>
                      <p className="text-white">{status?.check_interval}s</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Parada Emergencia</p>
                      <p className={status?.emergency_stop ? 'text-red-400' : 'text-green-400'}>
                        {status?.emergency_stop ? 'Activada' : 'Inactiva'}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400">Señales Pendientes</p>
                      <p className="text-white">{status?.queue_status?.pending_signals || 0}</p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-900 p-4 rounded-lg">
                  <h4 className="text-white font-semibold mb-2">Condiciones de Seguridad</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div className={`p-3 rounded-lg ${status?.emergency_conditions?.daily_loss_limit ? 'bg-red-900/50 border border-red-700' : 'bg-green-900/50 border border-green-700'}`}>
                      <p className="text-gray-300">Límite Pérdidas Diario</p>
                      <p className={status?.emergency_conditions?.daily_loss_limit ? 'text-red-400 font-semibold' : 'text-green-400 font-semibold'}>
                        {status?.emergency_conditions?.daily_loss_limit ? 'ACTIVADO' : 'Normal'}
                      </p>
                    </div>
                    <div className={`p-3 rounded-lg ${status?.emergency_conditions?.consecutive_losses ? 'bg-red-900/50 border border-red-700' : 'bg-green-900/50 border border-green-700'}`}>
                      <p className="text-gray-300">Pérdidas Consecutivas</p>
                      <p className={status?.emergency_conditions?.consecutive_losses ? 'text-red-400 font-semibold' : 'text-green-400 font-semibold'}>
                        {status?.emergency_conditions?.consecutive_losses ? 'ACTIVADO' : 'Normal'}
                      </p>
                    </div>
                    <div className={`p-3 rounded-lg ${status?.emergency_conditions?.manual_stop ? 'bg-red-900/50 border border-red-700' : 'bg-green-900/50 border border-green-700'}`}>
                      <p className="text-gray-300">Parada Manual</p>
                      <p className={status?.emergency_conditions?.manual_stop ? 'text-red-400 font-semibold' : 'text-green-400 font-semibold'}>
                        {status?.emergency_conditions?.manual_stop ? 'ACTIVADO' : 'Normal'}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-900 p-4 rounded-lg">
                  <h4 className="text-white font-semibold mb-2">Rendimiento Últimas 24h</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-gray-400">Ejecutados</p>
                      <p className="text-white">{status?.queue_status?.executed_today || 0}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Tasa Éxito</p>
                      <p className="text-white">{status?.queue_status?.success_rate_24h?.toFixed(1) || 0}%</p>
                    </div>
                    <div>
                      <p className="text-gray-400">En Cola</p>
                      <p className="text-white">{status?.queue_status?.queue_size || 0}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Última Ejecución</p>
                      <p className="text-white">Hoy</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}