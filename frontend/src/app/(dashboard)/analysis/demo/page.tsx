/**
 * Demo Analysis Results Page
 * Showcases DCF results dashboard and cash flow projections with sample data
 */

'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { DCFResultsDashboard } from '@/components/analysis/DCFResultsDashboard';
import { CashFlowTable } from '@/components/analysis/CashFlowTable';
import { MonteCarloResults } from '@/components/analysis/MonteCarloResults';
import { SensitivityControls, SensitivityConfiguration } from '@/components/analysis/SensitivityControls';
import { MarketDataExplorer } from '@/components/market/MarketDataExplorer';
import { 
  DCFAnalysisResult, 
  InvestmentRecommendation, 
  RiskAssessment,
  MonteCarloResult,
  MarketClassification 
} from '@/types/analysis';
import { textColors } from '@/lib/utils';

// Sample data for demonstration
const sampleAnalysis: DCFAnalysisResult = {
  property_id: 'DEMO-001',
  analysis_date: new Date().toISOString(),
  success: true,
  execution_time_ms: 1247,
  financial_metrics: {
    npv: 7847901,
    irr: 64.8,
    equity_multiple: 9.79,
    total_return: 879.2,
    payback_period: 3.2,
    average_annual_return: 28.4,
    investment_recommendation: InvestmentRecommendation.STRONG_BUY,
    risk_assessment: RiskAssessment.MODERATE,
    total_cash_invested: 875000,
    total_proceeds: 8570432,
    terminal_value: 6234567,
  },
  cash_flow_projections: [
    {
      year: 1,
      gross_rental_income: 360000,
      vacancy_loss: 18000,
      effective_gross_income: 342000,
      operating_expenses: 108000,
      net_operating_income: 234000,
      debt_service: 156000,
      net_cash_flow: 78000,
      cumulative_cash_flow: 78000,
    },
    {
      year: 2,
      gross_rental_income: 378000,
      vacancy_loss: 18900,
      effective_gross_income: 359100,
      operating_expenses: 113400,
      net_operating_income: 245700,
      debt_service: 156000,
      net_cash_flow: 89700,
      cumulative_cash_flow: 167700,
    },
    {
      year: 3,
      gross_rental_income: 396900,
      vacancy_loss: 19845,
      effective_gross_income: 377055,
      operating_expenses: 119007,
      net_operating_income: 258048,
      debt_service: 156000,
      net_cash_flow: 102048,
      cumulative_cash_flow: 269748,
    },
    {
      year: 4,
      gross_rental_income: 416745,
      vacancy_loss: 20837,
      effective_gross_income: 395908,
      operating_expenses: 124957,
      net_operating_income: 270951,
      debt_service: 156000,
      net_cash_flow: 114951,
      cumulative_cash_flow: 384699,
    },
    {
      year: 5,
      gross_rental_income: 437582,
      vacancy_loss: 21879,
      effective_gross_income: 415703,
      operating_expenses: 131205,
      net_operating_income: 284498,
      debt_service: 156000,
      net_cash_flow: 128498,
      cumulative_cash_flow: 513197,
    },
    {
      year: 6,
      gross_rental_income: 459461,
      vacancy_loss: 22973,
      effective_gross_income: 436488,
      operating_expenses: 137765,
      net_operating_income: 298723,
      debt_service: 156000,
      net_cash_flow: 142723,
      cumulative_cash_flow: 655920,
    },
  ],
  initial_numbers: {
    purchase_price: 2500000,
    loan_amount: 1875000,
    cash_required: 625000,
    closing_costs: 75000,
    renovation_cost: 175000,
    total_acquisition_cost: 2675000,
    lender_reserves: 25000,
    total_cash_investment: 875000,
    loan_to_value_ratio: 75.0,
    debt_coverage_ratio: 1.5,
  },
};

// Sample Monte Carlo results data
const sampleMonteCarloResults: MonteCarloResult = {
  simulation_id: 'MC-DEMO-001',
  property_id: 'DEMO-001',
  total_scenarios: 500,
  execution_time_ms: 3247,
  success: true,
  scenarios: [], // Would contain all 500 scenarios
  statistics: {
    npv_stats: {
      mean: 7200000,
      median: 7100000,
      std_dev: 2800000,
      min: 1200000,
      max: 15600000,
      percentile_5: 2800000,
      percentile_25: 5400000,
      percentile_75: 9200000,
      percentile_95: 12800000,
    },
    irr_stats: {
      mean: 58.2,
      median: 56.8,
      std_dev: 28.4,
      min: 8.2,
      max: 125.6,
      percentile_5: 18.4,
      percentile_25: 35.6,
      percentile_75: 78.2,
      percentile_95: 108.4,
    },
    risk_metrics: {
      probability_of_loss: 12.4,
      value_at_risk_5pct: 2800000,
      expected_shortfall: 1850000,
    },
  },
  percentiles: {
    npv: {
      p5: 2800000,
      p25: 5400000,
      median: 7100000,
      p75: 9200000,
      p95: 12800000,
    },
    irr: {
      p5: 18.4,
      p25: 35.6,
      median: 56.8,
      p75: 78.2,
      p95: 108.4,
    },
    total_cash_flow: {
      p5: 420000,
      p25: 680000,
      median: 890000,
      p75: 1150000,
      p95: 1420000,
    },
  },
  distribution: Array.from({ length: 100 }, (_, i) => ({
    scenario_id: i + 1,
    npv: 3000000 + Math.random() * 10000000,
    irr: 20 + Math.random() * 80,
    total_cash_flow: 500000 + Math.random() * 1000000,
    risk_score: Math.random(),
    market_classification: [
      MarketClassification.BULL,
      MarketClassification.BEAR,
      MarketClassification.NEUTRAL,
      MarketClassification.GROWTH,
      MarketClassification.STRESS,
    ][Math.floor(Math.random() * 5)],
  })),
  risk_distribution: {
    low: 156,
    moderate: 267,
    high: 77,
  },
  overall_risk_assessment: 'Moderate',
};

// Sample sensitivity configuration
const sampleSensitivityConfig: SensitivityConfiguration = {
  scenarioCount: 500,
  correlationStrength: 0.7,
  parameters: {
    interest_rate: {
      enabled: true,
      variationRange: 15,
      distributionType: 'normal',
    },
    cap_rate: {
      enabled: true,
      variationRange: 20,
      distributionType: 'normal',
    },
    vacancy_rate: {
      enabled: true,
      variationRange: 25,
      distributionType: 'uniform',
    },
    rent_growth_rate: {
      enabled: true,
      variationRange: 30,
      distributionType: 'triangular',
    },
    expense_growth_rate: {
      enabled: false,
      variationRange: 10,
      distributionType: 'normal',
    },
    property_growth_rate: {
      enabled: false,
      variationRange: 15,
      distributionType: 'normal',
    },
    ltv_ratio: {
      enabled: false,
      variationRange: 5,
      distributionType: 'uniform',
    },
    closing_costs_pct: {
      enabled: false,
      variationRange: 10,
      distributionType: 'normal',
    },
  },
};

export default function DemoAnalysisPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('overview');
  const [isExporting, setIsExporting] = useState(false);
  const [sensitivityConfig, setSensitivityConfig] = useState(sampleSensitivityConfig);

  const handleExport = async (format: 'pdf' | 'excel' | 'csv') => {
    setIsExporting(true);
    // Simulate export delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log(`Exporting analysis as ${format.toUpperCase()}`);
    setIsExporting(false);
  };

  const handleRunMonteCarlo = () => {
    console.log('Running Monte Carlo simulation...');
    // This would trigger the Monte Carlo analysis
  };

  const handleSensitivityConfigChange = (config: SensitivityConfiguration) => {
    setSensitivityConfig(config);
  };

  const handleRunSensitivityAnalysis = (config: SensitivityConfiguration) => {
    console.log('Running sensitivity analysis with config:', config);
    // This would trigger the sensitivity analysis
  };

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/analysis')}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Analysis</span>
            </Button>
            <div>
              <h1 className={`text-2xl font-bold ${textColors.primary}`}>
                Demo Property Analysis
              </h1>
              <p className={`${textColors.muted} mt-1`}>
                Sample 6-year DCF analysis results • 875 Main Street, Manhattan, NY
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
              Analysis Complete
            </Badge>
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              Demo Data
            </Badge>
          </div>
        </div>

        {/* Analysis Navigation */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview">Financial Overview</TabsTrigger>
            <TabsTrigger value="cashflow">Cash Flow Projections</TabsTrigger>
            <TabsTrigger value="sensitivity">Monte Carlo Results</TabsTrigger>
            <TabsTrigger value="controls">Sensitivity Controls</TabsTrigger>
            <TabsTrigger value="market">Market Data</TabsTrigger>
          </TabsList>

          {/* Financial Overview Tab */}
          <TabsContent value="overview" className="space-y-6 mt-6">
            <DCFResultsDashboard
              analysis={sampleAnalysis}
              onExport={handleExport}
              onRunMonteCarlos={handleRunMonteCarlo}
              isExporting={isExporting}
            />
          </TabsContent>

          {/* Cash Flow Projections Tab */}
          <TabsContent value="cashflow" className="space-y-6 mt-6">
            <CashFlowTable
              projections={sampleAnalysis.cash_flow_projections}
              onExport={handleExport}
              isExporting={isExporting}
            />
          </TabsContent>

          {/* Monte Carlo Results Tab */}
          <TabsContent value="sensitivity" className="space-y-6 mt-6">
            <MonteCarloResults
              results={sampleMonteCarloResults}
              onRerun={handleRunMonteCarlo}
              onExport={handleExport}
              isRunning={isExporting}
            />
          </TabsContent>

          {/* Sensitivity Controls Tab */}
          <TabsContent value="controls" className="space-y-6 mt-6">
            <SensitivityControls
              parameters={[]} // Uses default parameters
              configuration={sensitivityConfig}
              onConfigurationChange={handleSensitivityConfigChange}
              onRunSimulation={handleRunSensitivityAnalysis}
              isRunning={isExporting}
            />
          </TabsContent>

          {/* Market Data Tab */}
          <TabsContent value="market" className="space-y-6 mt-6">
            <MarketDataExplorer
              selectedMSA="NYC"
              onMSAChange={(msa) => console.log('Selected MSA:', msa)}
              onDataExport={(format, data) => console.log(`Exporting ${format}:`, data)}
              isLoading={isExporting}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}