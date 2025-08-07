/**
 * Monte Carlo Panel Component
 * Provides simulation launcher with real-time progress tracking
 */

'use client';

import { useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Activity,
  Play,
  Square,
  RefreshCw,
  Settings,
  TrendingUp,
  AlertCircle,
  Info,
  Zap,
  Target,
} from 'lucide-react';
import { MonteCarloResult } from '@/types/analysis';
import { textColors, formatCurrency } from '@/lib/utils';

export interface MonteCarloSettings {
  numScenarios: number;
  includeCorrelations: boolean;
  includeMarketCycles: boolean;
  randomSeed?: number;
  confidenceLevel: number;
}

interface MonteCarloProgressStatus {
  isRunning: boolean;
  progress: number;
  currentScenario: number;
  totalScenarios: number;
  estimatedTimeRemaining: number;
  stage: 'initializing' | 'running' | 'analyzing' | 'complete' | 'error';
  message: string;
}

interface MonteCarloControlPanelProps {
  propertyId: string;
  baselineNPV: number;
  baselineIRR: number;
  onSimulationStart?: (settings: MonteCarloSettings) => void;
  onSimulationComplete?: (results: MonteCarloResult) => void;
  onSimulationError?: (error: string) => void;
  isDisabled?: boolean;
  className?: string;
}

export function MonteCarloPanel({
  propertyId,
  baselineNPV,
  baselineIRR,
  onSimulationStart,
  onSimulationComplete,
  onSimulationError,
  isDisabled = false,
  className = '',
}: MonteCarloControlPanelProps) {
  // Simulation settings state
  const [settings, setSettings] = useState<MonteCarloSettings>({
    numScenarios: 1000,
    includeCorrelations: true,
    includeMarketCycles: true,
    confidenceLevel: 95,
  });

  // Progress tracking state
  const [progressStatus, setProgressStatus] = useState<MonteCarloProgressStatus>({
    isRunning: false,
    progress: 0,
    currentScenario: 0,
    totalScenarios: 0,
    estimatedTimeRemaining: 0,
    stage: 'complete',
    message: 'Ready to run simulation',
  });

  // Simulation history state
  const [previousResults, setPreviousResults] = useState<MonteCarloResult[]>([]);

  const handleSettingsChange = useCallback((key: keyof MonteCarloSettings, value: any) => {
    setSettings(prev => ({
      ...prev,
      [key]: value,
    }));
  }, []);

  const startSimulation = useCallback(async () => {
    if (isDisabled || progressStatus.isRunning) return;

    try {
      // Initialize progress tracking
      setProgressStatus({
        isRunning: true,
        progress: 0,
        currentScenario: 0,
        totalScenarios: settings.numScenarios,
        estimatedTimeRemaining: 0,
        stage: 'initializing',
        message: 'Initializing simulation parameters...',
      });

      // Notify parent component
      if (onSimulationStart) {
        onSimulationStart(settings);
      }

      // Simulate progress updates (in real implementation, this would come from WebSocket or polling)
      await simulateProgress();

    } catch (error) {
      setProgressStatus(prev => ({
        ...prev,
        isRunning: false,
        stage: 'error',
        message: `Simulation failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      }));

      if (onSimulationError) {
        onSimulationError(error instanceof Error ? error.message : 'Unknown error');
      }
    }
  }, [settings, isDisabled, progressStatus.isRunning, onSimulationStart, onSimulationError]);

  const stopSimulation = useCallback(() => {
    setProgressStatus(prev => ({
      ...prev,
      isRunning: false,
      stage: 'complete',
      message: 'Simulation stopped by user',
    }));
  }, []);

  // Simulate progress for demonstration (replace with real API calls)
  const simulateProgress = async () => {
    const stages = [
      { stage: 'initializing', duration: 1000, message: 'Setting up correlation matrix...' },
      { stage: 'running', duration: 8000, message: 'Running Monte Carlo scenarios...' },
      { stage: 'analyzing', duration: 2000, message: 'Analyzing results and calculating statistics...' },
    ];

    for (const stageInfo of stages) {
      setProgressStatus(prev => ({
        ...prev,
        stage: stageInfo.stage as any,
        message: stageInfo.message,
      }));

      const steps = 20;
      const stepDuration = stageInfo.duration / steps;

      for (let i = 0; i <= steps; i++) {
        await new Promise(resolve => setTimeout(resolve, stepDuration));
        
        const stageProgress = (i / steps) * 100;
        const overallProgress = stageProgress / stages.length + 
          (stages.indexOf(stageInfo) / stages.length) * 100;

        setProgressStatus(prev => ({
          ...prev,
          progress: overallProgress,
          currentScenario: Math.floor((overallProgress / 100) * settings.numScenarios),
          estimatedTimeRemaining: Math.max(0, 
            ((100 - overallProgress) / 100) * (stages.reduce((sum, s) => sum + s.duration, 0) / 1000)
          ),
        }));
      }
    }

    // Complete simulation
    setProgressStatus({
      isRunning: false,
      progress: 100,
      currentScenario: settings.numScenarios,
      totalScenarios: settings.numScenarios,
      estimatedTimeRemaining: 0,
      stage: 'complete',
      message: 'Simulation completed successfully',
    });

    // Mock results for demonstration
    const mockResults: MonteCarloResult = {
      property_id: propertyId,
      total_scenarios: settings.numScenarios,
      execution_time_ms: 11000,
      percentiles: {
        npv: {
          p5: baselineNPV * 0.6,
          p25: baselineNPV * 0.8,
          median: baselineNPV,
          p75: baselineNPV * 1.2,
          p95: baselineNPV * 1.5,
        },
        irr: {
          p5: baselineIRR * 0.7,
          p25: baselineIRR * 0.85,
          median: baselineIRR,
          p75: baselineIRR * 1.15,
          p95: baselineIRR * 1.4,
        },
        total_cash_flow: {
          p5: baselineNPV * 0.4,
          p25: baselineNPV * 0.6,
          median: baselineNPV * 0.8,
          p75: baselineNPV * 1.0,
          p95: baselineNPV * 1.3,
        },
      },
      distribution: Array.from({ length: Math.min(settings.numScenarios, 500) }, (_, i) => ({
        scenario_id: i + 1,
        npv: baselineNPV * (0.5 + Math.random()),
        irr: baselineIRR * (0.6 + Math.random() * 0.8),
        total_cash_flow: baselineNPV * 0.8 * (0.4 + Math.random() * 0.8),
        risk_score: Math.random(),
        market_scenario: ['bull', 'bear', 'neutral'][Math.floor(Math.random() * 3)],
      })),
      risk_distribution: {
        low: Math.floor(settings.numScenarios * 0.3),
        moderate: Math.floor(settings.numScenarios * 0.5),
        high: Math.floor(settings.numScenarios * 0.2),
      },
      overall_risk_assessment: 'Moderate',
    };

    if (onSimulationComplete) {
      onSimulationComplete(mockResults);
    }

    setPreviousResults(prev => [mockResults, ...prev.slice(0, 4)]); // Keep last 5 runs
  };

  const getProgressColor = () => {
    switch (progressStatus.stage) {
      case 'error': return 'bg-red-500';
      case 'complete': return 'bg-green-500';
      case 'running': return 'bg-blue-500';
      default: return 'bg-amber-500';
    }
  };

  const getStageIcon = () => {
    switch (progressStatus.stage) {
      case 'initializing': return <Settings className="h-4 w-4 animate-spin" />;
      case 'running': return <Activity className="h-4 w-4 animate-pulse" />;
      case 'analyzing': return <TrendingUp className="h-4 w-4 animate-bounce" />;
      case 'complete': return <Target className="h-4 w-4 text-green-600" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-600" />;
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Control Panel */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl flex items-center">
            <Zap className="h-5 w-5 mr-2 text-blue-600" />
            Monte Carlo Risk Analysis
          </CardTitle>
          <CardDescription>
            Run probabilistic simulations to assess investment risk and potential outcomes
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <Tabs defaultValue="settings" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="settings">Settings</TabsTrigger>
              <TabsTrigger value="progress">Progress</TabsTrigger>
              <TabsTrigger value="history">History</TabsTrigger>
            </TabsList>

            {/* Simulation Settings */}
            <TabsContent value="settings" className="space-y-4 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="numScenarios">Number of Scenarios</Label>
                  <Input
                    id="numScenarios"
                    type="number"
                    value={settings.numScenarios}
                    onChange={(e) => handleSettingsChange('numScenarios', parseInt(e.target.value) || 1000)}
                    min={100}
                    max={10000}
                    step={100}
                    disabled={progressStatus.isRunning}
                  />
                  <p className="text-xs text-gray-500">
                    More scenarios = higher accuracy (100-10,000 recommended)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confidenceLevel">Confidence Level (%)</Label>
                  <Input
                    id="confidenceLevel"
                    type="number"
                    value={settings.confidenceLevel}
                    onChange={(e) => handleSettingsChange('confidenceLevel', parseInt(e.target.value) || 95)}
                    min={80}
                    max={99}
                    step={1}
                    disabled={progressStatus.isRunning}
                  />
                  <p className="text-xs text-gray-500">
                    Statistical confidence for risk calculations
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-4">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.includeCorrelations}
                    onChange={(e) => handleSettingsChange('includeCorrelations', e.target.checked)}
                    disabled={progressStatus.isRunning}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm">Include Parameter Correlations</span>
                </label>

                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.includeMarketCycles}
                    onChange={(e) => handleSettingsChange('includeMarketCycles', e.target.checked)}
                    disabled={progressStatus.isRunning}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm">Include Market Cycles</span>
                </label>
              </div>

              {/* Baseline Information */}
              <div className="bg-blue-50 p-4 rounded-lg space-y-2">
                <h4 className="font-medium text-blue-900">Baseline Analysis</h4>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-blue-700">NPV:</span>
                    <span className="ml-2 font-mono">{formatCurrency(baselineNPV, { compact: true })}</span>
                  </div>
                  <div>
                    <span className="text-blue-700">IRR:</span>
                    <span className="ml-2 font-mono">{baselineIRR.toFixed(1)}%</span>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between pt-4">
                <div className="flex items-center space-x-2">
                  <Button
                    onClick={startSimulation}
                    disabled={isDisabled || progressStatus.isRunning}
                    className="flex items-center space-x-2"
                  >
                    <Play className="h-4 w-4" />
                    <span>Run Simulation</span>
                  </Button>

                  {progressStatus.isRunning && (
                    <Button
                      variant="outline"
                      onClick={stopSimulation}
                      className="flex items-center space-x-2"
                    >
                      <Square className="h-4 w-4" />
                      <span>Stop</span>
                    </Button>
                  )}
                </div>

                <Badge variant={progressStatus.stage === 'complete' ? 'default' : 'secondary'}>
                  {progressStatus.stage === 'complete' 
                    ? `${settings.numScenarios} scenarios` 
                    : progressStatus.stage.charAt(0).toUpperCase() + progressStatus.stage.slice(1)
                  }
                </Badge>
              </div>
            </TabsContent>

            {/* Progress Tracking */}
            <TabsContent value="progress" className="space-y-4 mt-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getStageIcon()}
                    <span className={`text-sm font-medium ${textColors.body}`}>
                      {progressStatus.message}
                    </span>
                  </div>
                  <Badge variant="outline">
                    {progressStatus.progress.toFixed(0)}% Complete
                  </Badge>
                </div>

                <Progress 
                  value={progressStatus.progress} 
                  className="w-full"
                />

                {progressStatus.isRunning && (
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className={`font-medium ${textColors.secondary}`}>Scenarios:</span>
                      <p className="font-mono">
                        {progressStatus.currentScenario.toLocaleString()} / {progressStatus.totalScenarios.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <span className={`font-medium ${textColors.secondary}`}>Time Remaining:</span>
                      <p className="font-mono">
                        ~{Math.ceil(progressStatus.estimatedTimeRemaining)}s
                      </p>
                    </div>
                    <div>
                      <span className={`font-medium ${textColors.secondary}`}>Stage:</span>
                      <p className="capitalize">
                        {progressStatus.stage}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </TabsContent>

            {/* Simulation History */}
            <TabsContent value="history" className="space-y-4 mt-6">
              {previousResults.length === 0 ? (
                <div className="text-center py-8">
                  <Info className="h-8 w-8 mx-auto text-gray-400 mb-3" />
                  <p className={`${textColors.muted} text-sm`}>
                    No simulation history available. Run your first Monte Carlo analysis to see results here.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {previousResults.map((result, index) => (
                    <div
                      key={`${result.property_id}-${index}`}
                      className="bg-gray-50 p-3 rounded-lg border"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">
                          Run #{previousResults.length - index}
                        </span>
                        <Badge variant="secondary" className="text-xs">
                          {result.total_scenarios} scenarios
                        </Badge>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-xs">
                        <div>
                          <span className="text-gray-600">Median NPV:</span>
                          <p className="font-mono">{formatCurrency(result.percentiles.npv.median, { compact: true })}</p>
                        </div>
                        <div>
                          <span className="text-gray-600">Median IRR:</span>
                          <p className="font-mono">{result.percentiles.irr.median.toFixed(1)}%</p>
                        </div>
                        <div>
                          <span className="text-gray-600">Risk:</span>
                          <p className={`capitalize ${result.overall_risk_assessment.toLowerCase() === 'low' 
                            ? 'text-green-600' 
                            : result.overall_risk_assessment.toLowerCase() === 'high' 
                            ? 'text-red-600' 
                            : 'text-amber-600'
                          }`}>
                            {result.overall_risk_assessment}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}