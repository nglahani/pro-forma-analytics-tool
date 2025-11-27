# Frontend-Backend Integration - Design Specification

**Feature ID:** FE-INTEGRATION-001
**Created:** 2025-11-05
**Status:** Draft → Awaiting Approval

---

## Architecture Placement

**Layer:** Presentation (Frontend)

**Component Structure:**
```
frontend/src/
├── app/(dashboard)/
│   ├── property-input/page.tsx          [MODIFY] Add results display
│   ├── properties/page.tsx              [MODIFY] Add API integration
│   ├── analysis/page.tsx                [MODIFY] Wire to show results
│   ├── monte-carlo/page.tsx             [MODIFY] Add simulation integration
│   └── market-data/page.tsx             [MODIFY] Add market data integration
├── components/
│   ├── analysis/
│   │   ├── AnalysisResultsModal.tsx     [CREATE] Results modal component
│   │   ├── AnalysisResultsCard.tsx      [CREATE] Financial metrics display
│   │   ├── CashFlowTable.tsx            [CREATE] Detailed cash flows
│   │   └── MonteCarloCharts.tsx         [CREATE] Simulation visualizations
│   ├── market-data/
│   │   ├── MarketDataChart.tsx          [CREATE] Historical data chart
│   │   └── ForecastChart.tsx            [CREATE] Forecast visualization
│   └── ui/
│       └── loading-states.tsx           [CREATE] Reusable loading components
├── hooks/
│   └── useAPI.ts                        [EXISTS] Already implemented ✅
└── lib/api/
    ├── client.ts                        [EXISTS] Already implemented ✅
    └── service.ts                       [EXISTS] Already implemented ✅
```

**Dependencies Flow:**
```
Page Components → useAPI Hooks → API Service → API Client → Backend API
     ↓                ↓              ↓              ↓
 UI Components    State Mgmt    Auth Layer    HTTP Client
```

---

## Data Model Changes

### Analysis Results State
```typescript
// frontend/src/types/analysis.ts
interface AnalysisResultsState {
  propertyId: string;
  analysisDate: string;
  financialMetrics: {
    npv: number;
    irr: number;
    equity_multiple: number;
    payback_period: number;
    total_cash_flow: number;
  };
  investmentRecommendation: 'STRONG_BUY' | 'BUY' | 'HOLD' | 'SELL' | 'STRONG_SELL';
  cashFlows?: CashFlowProjection[];
  metadata: {
    processingTimeSeconds: number;
    analysisTimestamp: string;
    dataSources: Record<string, string>;
  };
}
```

### Monte Carlo Results State
```typescript
// frontend/src/types/simulation.ts
interface MonteCarloResultsState {
  simulationId: string;
  propertyId: string;
  scenarioCount: number;
  scenarios: Scenario[];
  riskMetrics: {
    value_at_risk_5: number;
    expected_shortfall_5: number;
    maximum_drawdown: number;
    volatility: number;
  };
  scenarioClassification: {
    bull_market: number;
    bear_market: number;
    neutral_market: number;
    growth_market: number;
    stress_market: number;
  };
}
```

### Market Data State
```typescript
// frontend/src/types/marketData.ts
interface MarketDataState {
  msa: string;
  parameter: string;
  dataPoints: MarketDataPoint[];
  currentValue: number | null;
  lastUpdated: string;
  dataCoverage: {
    historicalYears: number;
    parametersAvailable: number;
    dataQuality: string;
    updateFrequency: string;
  };
}
```

---

## Component Design

### 1. AnalysisResultsModal Component

**Purpose:** Display DCF analysis results in modal overlay

**Props:**
```typescript
interface AnalysisResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  results: AnalysisResultsState;
  propertyName: string;
  onViewDetails?: () => void;
  onRunAnother?: () => void;
}
```

**Layout:**
```
┌─────────────────────────────────────────┐
│  ✕  DCF Analysis Results                │
│                                         │
│  Property: Brooklyn Heights Investment │
│  Analyzed: 2025-11-05 10:30 AM         │
│                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │   NPV   │ │   IRR   │ │ Equity  │  │
│  │ $8.6M   │ │  90.4%  │ │ 13.7x   │  │
│  └─────────┘ └─────────┘ └─────────┘  │
│                                         │
│  Investment Recommendation:             │
│  ┌─────────────────────────────────┐   │
│  │  🟢 STRONG BUY                  │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Processing Time: 1.23s                │
│                                         │
│  [View Details] [Run Another Analysis] │
└─────────────────────────────────────────┘
```

**Behavior:**
- Auto-opens when analysis completes
- Color-codes recommendation (green=buy, yellow=hold, red=sell)
- Formats numbers with proper units
- Provides navigation buttons

---

### 2. Enhanced Properties List Page

**Current:** Shows mock data
**After:** Integrates with `/api/v1/analysis/history`

**Data Flow:**
```
1. Page loads → useAnalysisHistory() hook
2. Fetch from API: /api/v1/analysis/history?limit=20
3. Merge with localStorage data
4. Display in table with sorting/filtering
```

**Table Columns:**
- Property Name
- City, State
- Purchase Price
- NPV
- IRR
- Recommendation
- Analysis Date
- Actions (View, Re-run)

**Interaction:**
- Click row → Navigate to analysis details
- Click "View" → Open analysis modal
- Click "Re-run" → Navigate to property input with pre-filled data

---

### 3. Monte Carlo Simulation Page

**Layout:**
```
┌────────────────────────────────────────┐
│  Monte Carlo Risk Analysis             │
│                                        │
│  Property Selection:                   │
│  [Select from Existing ▼] [Or New]    │
│                                        │
│  Simulation Parameters:                │
│  Scenarios: [─────●─────] 1,000       │
│              500        10,000         │
│                                        │
│  [Run Simulation]                      │
│                                        │
│  Results:                              │
│  ┌──────────────────────────────────┐ │
│  │  Scenario Distribution Chart      │ │
│  │  [Bar chart showing scenario      │ │
│  │   classification]                 │ │
│  └──────────────────────────────────┘ │
│                                        │
│  Risk Metrics:                         │
│  VaR (5%): -15.0%                     │
│  Expected Shortfall: -22.0%            │
│  Maximum Drawdown: -35.0%              │
│  Volatility: 18.0%                     │
└────────────────────────────────────────┘
```

**Implementation:**
```typescript
// frontend/src/app/(dashboard)/monte-carlo/page.tsx
const MonteCarloPage = () => {
  const [selectedProperty, setSelectedProperty] = useState<string | null>(null);
  const [scenarioCount, setScenarioCount] = useState(1000);
  const monteCarloSim = useMonteCarloSimulation();

  const handleRunSimulation = async () => {
    if (!selectedProperty) return;

    const propertyData = await fetchPropertyData(selectedProperty);
    await monteCarloSim.execute(propertyData, scenarioCount);
  };

  return (
    // Layout implementation
  );
};
```

---

### 4. Market Data Explorer Page

**Layout:**
```
┌────────────────────────────────────────┐
│  Market Data Explorer                  │
│                                        │
│  MSA: [New York (35620) ▼]            │
│                                        │
│  Parameters:                           │
│  ☑ Cap Rate  ☑ Rent Growth            │
│  ☐ Interest Rates  ☐ Vacancy          │
│                                        │
│  Time Range:                           │
│  [2010-01-01] to [2025-11-05]         │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │  Historical Data Chart            │ │
│  │  [Line chart with multiple        │ │
│  │   parameters over time]           │ │
│  └──────────────────────────────────┘ │
│                                        │
│  Current Values:                       │
│  Cap Rate: 6.5%  (as of Oct 2025)    │
│  Rent Growth: 3.2%  (YoY)             │
│                                        │
│  [☐ Show Forecasts]                   │
└────────────────────────────────────────┘
```

---

## API Integration Patterns

### Pattern 1: Optimistic UI Updates
```typescript
// Update UI immediately, sync with API in background
const handlePropertySubmit = async (data) => {
  // 1. Update localStorage immediately
  saveToLocalStorage(data);

  // 2. Update UI
  setProperties(prev => [...prev, data]);

  // 3. Sync to API (if needed in future)
  // await apiService.saveProperty(data);
};
```

### Pattern 2: Loading States
```typescript
const ResultsModal = ({ isOpen, results }) => {
  if (!results) {
    return <LoadingSpinner text="Running DCF analysis..." />;
  }

  return <ResultsDisplay results={results} />;
};
```

### Pattern 3: Error Boundaries
```typescript
// Wrap API calls in error handling
try {
  const results = await dcfAnalysis.execute(propertyData);
  showSuccessToast('Analysis completed successfully');
} catch (error) {
  showErrorToast(`Analysis failed: ${error.message}`);
  logErrorToConsole(error);
}
```

---

## Algorithms & Formulas

### Number Formatting
```typescript
// Currency formatting
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value);
};

// Percentage formatting
const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  }).format(value);
};

// Multiple formatting
const formatMultiple = (value: number): string => {
  return `${value.toFixed(2)}x`;
};
```

### Recommendation Color Coding
```typescript
const getRecommendationColor = (rec: string): string => {
  const colorMap = {
    'STRONG_BUY': 'green',
    'BUY': 'lightgreen',
    'HOLD': 'yellow',
    'SELL': 'orange',
    'STRONG_SELL': 'red',
  };
  return colorMap[rec] || 'gray';
};
```

---

## Error Handling Strategy

### Error Types
1. **Network Errors** - API unavailable or timeout
2. **Validation Errors** - Invalid input data
3. **Calculation Errors** - Backend processing failures
4. **Authentication Errors** - Invalid/expired API key

### Error Display
```typescript
interface ErrorDisplay {
  title: string;
  message: string;
  actionable: boolean;
  retryAction?: () => void;
  suggestedFix?: string;
}

// Example
{
  title: "Analysis Failed",
  message: "Commercial units must be positive",
  actionable: true,
  suggestedFix: "Update property form to include at least 1 commercial unit"
}
```

### Retry Logic
```typescript
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(2 ** i * 1000); // Exponential backoff
    }
  }
};
```

---

## Testing Strategy

### Unit Tests
```typescript
// Component tests
describe('AnalysisResultsModal', () => {
  it('should display NPV correctly formatted', () => {
    render(<AnalysisResultsModal results={mockResults} />);
    expect(screen.getByText('$8,638,739')).toBeInTheDocument();
  });

  it('should color-code STRONG_BUY as green', () => {
    render(<AnalysisResultsModal results={mockResults} />);
    const recommendation = screen.getByText('STRONG BUY');
    expect(recommendation).toHaveClass('text-green-600');
  });
});

// Hook tests
describe('useDCFAnalysis', () => {
  it('should handle successful analysis', async () => {
    const { result } = renderHook(() => useDCFAnalysis());
    await act(() => result.current.execute(mockPropertyData));

    expect(result.current.data).toBeDefined();
    expect(result.current.error).toBeNull();
  });
});
```

### Integration Tests
```typescript
describe('Property Input to Results Flow', () => {
  it('should complete full analysis workflow', async () => {
    // 1. Render property input page
    render(<PropertyInputPage />);

    // 2. Fill out form
    fireEvent.change(screen.getByLabelText('Property Name'), {
      target: { value: 'Test Property' }
    });
    // ... more form fields

    // 3. Submit
    fireEvent.click(screen.getByText('Submit'));

    // 4. Run analysis
    await waitFor(() => screen.getByText('Run Analysis'));
    fireEvent.click(screen.getByText('Run Analysis'));

    // 5. Verify results displayed
    await waitFor(() => screen.getByText(/NPV/));
    expect(screen.getByText(/\$8,638,739/)).toBeInTheDocument();
  });
});
```

### E2E Tests (Manual for MVP)
- [ ] Input property → Submit → Run Analysis → See results
- [ ] Navigate to Properties → See analyzed property
- [ ] Click property → View analysis details
- [ ] Run Monte Carlo simulation
- [ ] Explore market data

---

## Non-Functional Requirements

### Performance
- **Page Load:** < 2 seconds for initial render
- **API Response:** < 3 seconds for DCF analysis
- **Chart Render:** < 1 second for data visualization
- **Bundle Size:** Keep increase < 100KB

### Accessibility
- All interactive elements keyboard accessible
- Proper ARIA labels for screen readers
- Color contrast ratios meet WCAG AA standards
- Focus management in modals

### Security
- No sensitive data in localStorage (API keys in memory only)
- Sanitize all user inputs before API calls
- HTTPS-only in production
- CSP headers configured (already in next.config.ts)

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

---

## Migration & Rollout

**Phase 1 Rollout (Core Flow):**
1. Deploy AnalysisResultsModal component
2. Wire to property-input page
3. Update properties list
4. Test end-to-end flow
5. Deploy to production

**Phase 2 Rollout (Enhanced Features):**
1. Deploy Monte Carlo page
2. Deploy Market Data page
3. Add chart components
4. Test visualizations
5. Deploy to production

**Phase 3 Rollout (Polish):**
1. Add loading states
2. Improve error messages
3. Add success notifications
4. Deploy to production

**Rollback Plan:**
- All changes are additive (no breaking changes)
- Can disable features via feature flags if needed
- localStorage data preserved across rollbacks

---

**Next Step:** Awaiting approval to proceed to `tasks.md`
