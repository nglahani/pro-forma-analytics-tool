# Frontend-Backend Integration - Implementation Tasks

**Feature ID:** FE-INTEGRATION-001
**Created:** 2025-11-05
**Status:** Draft → Awaiting Approval

---

## Task Checklist

### Phase 1: Core User Flow (CRITICAL - MVP Blocker)

**Estimated Time:** 2-3 hours
**Dependencies:** Backend API operational ✅

#### 1. Analysis Results Display Components

##### 1.1 Create AnalysisResultsModal Component
- [ ] Create `frontend/src/components/analysis/AnalysisResultsModal.tsx`
- [ ] Implement modal using Radix UI Dialog
- [ ] Add props interface (isOpen, onClose, results, propertyName)
- [ ] Design layout with financial metrics cards
- [ ] Add recommendation color coding logic
- [ ] Implement "View Details" and "Run Another" buttons
- [ ] Add responsive design for mobile
- [ ] **Test:** Component renders with mock data
- [ ] **Test:** Modal opens/closes correctly
- [ ] **Test:** Numbers formatted correctly (currency, percentage, multiple)
- [ ] **Requirement:** AC-2 (Analysis Results Display)

##### 1.2 Create AnalysisResultsCard Component
- [ ] Create `frontend/src/components/analysis/AnalysisResultsCard.tsx`
- [ ] Design metric card with label and value
- [ ] Add icon support for metrics
- [ ] Style with Tailwind CSS following design system
- [ ] Add hover states and animations
- [ ] **Test:** Card displays metric correctly
- [ ] **Test:** Card responsive on mobile
- [ ] **Requirement:** AC-2

##### 1.3 Create Number Formatting Utilities
- [ ] Create `frontend/src/lib/utils/formatters.ts`
- [ ] Implement `formatCurrency(value)` function
- [ ] Implement `formatPercentage(value)` function
- [ ] Implement `formatMultiple(value)` function
- [ ] Implement `formatTimestamp(date)` function
- [ ] **Test:** Each formatter with edge cases (negative, zero, large numbers)
- [ ] **Requirement:** AC-2

#### 2. Wire Results Display to Property Input Page

##### 2.1 Update Property Input Page State Management
- [ ] Modify `frontend/src/app/(dashboard)/property-input/page.tsx`
- [ ] Add `showResultsModal` state variable
- [ ] Add `analysisResults` state variable
- [ ] Update `handleRunAnalysis` to set results state
- [ ] Open modal when analysis completes successfully
- [ ] **Test:** Modal opens after successful analysis
- [ ] **Test:** Modal shows correct data from API response
- [ ] **Requirement:** AC-1 (Property to Analysis Flow)

##### 2.2 Add Results Modal Integration
- [ ] Import AnalysisResultsModal component
- [ ] Pass analysis results as props
- [ ] Implement `onClose` handler to close modal
- [ ] Implement `onViewDetails` to navigate to analysis page
- [ ] Implement `onRunAnother` to reset form
- [ ] **Test:** All modal actions work correctly
- [ ] **Test:** Navigation flows work
- [ ] **Requirement:** AC-1

##### 2.3 Add Loading State During Analysis
- [ ] Show loading spinner when `dcfAnalysis.loading === true`
- [ ] Display progress text "Running DCF Analysis..."
- [ ] Disable "Run Analysis" button while loading
- [ ] **Test:** Loading state visible during API call
- [ ] **Test:** Button disabled during loading
- [ ] **Requirement:** AC-6 (Loading States)

##### 2.4 Add Error Handling
- [ ] Display error toast when `dcfAnalysis.error` is set
- [ ] Show user-friendly error message
- [ ] Add "Retry" button on error
- [ ] Log error details to console
- [ ] **Test:** Error toast appears on API failure
- [ ] **Test:** Retry button calls API again
- [ ] **Requirement:** AC-1, AC-6

#### 3. Properties List API Integration

##### 3.1 Create useAnalysisHistory Hook
- [ ] Add `useAnalysisHistory()` hook to `frontend/src/hooks/useAPI.ts`
- [ ] Bind to `apiService.getAnalysisHistory()`
- [ ] Add limit parameter support
- [ ] **Test:** Hook fetches data from API
- [ ] **Test:** Hook handles errors correctly
- [ ] **Requirement:** AC-3 (Properties List Integration)

##### 3.2 Create getAnalysisHistory API Method
- [ ] Add `getAnalysisHistory(limit)` to `frontend/src/lib/api/service.ts`
- [ ] Call `/api/v1/analysis/history?limit={limit}`
- [ ] Handle authentication
- [ ] Transform response to frontend format
- [ ] **Test:** Method calls correct endpoint
- [ ] **Test:** Method returns correct data structure
- [ ] **Requirement:** AC-3

##### 3.3 Update Properties Page Component
- [ ] Modify `frontend/src/app/(dashboard)/properties/page.tsx`
- [ ] Add `useAnalysisHistory()` hook call
- [ ] Fetch analysis history on page load
- [ ] Merge API data with localStorage data
- [ ] Remove hardcoded mock data
- [ ] **Test:** Page loads API data
- [ ] **Test:** API and localStorage data merged correctly
- [ ] **Requirement:** AC-3

##### 3.4 Add Property Click Handler
- [ ] Implement `onPropertyClick(propertyId)` handler
- [ ] Navigate to analysis results page or open modal
- [ ] Pass property data and analysis results
- [ ] **Test:** Clicking property shows details
- [ ] **Test:** Navigation works correctly
- [ ] **Requirement:** AC-3

##### 3.5 Add Empty State
- [ ] Create empty state component for no properties
- [ ] Add "Analyze Your First Property" CTA button
- [ ] Link to property-input page
- [ ] **Test:** Empty state shows when no properties
- [ ] **Test:** CTA button navigates correctly
- [ ] **Requirement:** AC-3

#### 4. End-to-End Testing

##### 4.1 Manual Testing
- [ ] Test: Input property → Submit → Run Analysis → See Results
- [ ] Test: Close modal → Results persisted in localStorage
- [ ] Test: Navigate to Properties → See analyzed property
- [ ] Test: Click property → View analysis details
- [ ] Test: Error scenario → See error message → Retry
- [ ] **Requirement:** All Phase 1 ACs

##### 4.2 Automated Testing
- [ ] Write integration test for complete flow
- [ ] Write component tests for AnalysisResultsModal
- [ ] Write component tests for AnalysisResultsCard
- [ ] Write tests for formatter utilities
- [ ] Ensure test coverage ≥30%
- [ ] **Requirement:** Testing Strategy

---

### Phase 2: Enhanced Features (HIGH Priority)

**Estimated Time:** 3-4 hours
**Dependencies:** Phase 1 complete

#### 5. Monte Carlo Simulation Page

##### 5.1 Create Page Structure
- [ ] Modify `frontend/src/app/(dashboard)/monte-carlo/page.tsx`
- [ ] Add property selector dropdown
- [ ] Add "New Property" option
- [ ] Add scenario count slider (500-10,000)
- [ ] Add "Run Simulation" button
- [ ] **Test:** Page renders correctly
- [ ] **Requirement:** AC-4 (Monte Carlo Simulation)

##### 5.2 Property Selection Logic
- [ ] Fetch existing properties from localStorage
- [ ] Populate dropdown with property list
- [ ] Handle "New Property" selection → navigate to property input
- [ ] Store selected property in state
- [ ] **Test:** Dropdown populated with properties
- [ ] **Test:** Selection updates state
- [ ] **Requirement:** AC-4

##### 5.3 API Integration
- [ ] Use `useMonteCarloSimulation()` hook
- [ ] Validate inputs before API call
- [ ] Call simulation endpoint with selected property
- [ ] Handle loading state
- [ ] Handle errors
- [ ] **Test:** API called with correct parameters
- [ ] **Test:** Loading state shown during simulation
- [ ] **Requirement:** AC-4

##### 5.4 Results Display
- [ ] Create `MonteCarloResultsDisplay` component
- [ ] Display scenario classification breakdown
- [ ] Display risk metrics (VaR, Expected Shortfall, etc.)
- [ ] **Test:** Results display correctly
- [ ] **Requirement:** AC-4

##### 5.5 Scenario Distribution Chart
- [ ] Create `MonteCarloCharts.tsx` component
- [ ] Use Recharts BarChart for scenario distribution
- [ ] Color-code scenarios (bull=green, bear=red, etc.)
- [ ] Add tooltips with scenario details
- [ ] **Test:** Chart renders with data
- [ ] **Test:** Chart responsive
- [ ] **Requirement:** AC-4

#### 6. Market Data Explorer Page

##### 6.1 Create Page Structure
- [ ] Modify `frontend/src/app/(dashboard)/market-data/page.tsx`
- [ ] Add MSA selector dropdown
- [ ] Add parameter filter checkboxes
- [ ] Add date range selector
- [ ] Add "Show Forecasts" toggle
- [ ] **Test:** Page renders correctly
- [ ] **Requirement:** AC-5 (Market Data Explorer)

##### 6.2 MSA and Parameter Selection
- [ ] Create MSA list constant (5 supported MSAs)
- [ ] Create parameter list constant (11 parameters)
- [ ] Handle MSA selection state
- [ ] Handle parameter selection state (multi-select)
- [ ] **Test:** Selections update state correctly
- [ ] **Requirement:** AC-5

##### 6.3 Market Data API Integration
- [ ] Add `useMarketData()` hook to useAPI.ts
- [ ] Add `getMarketData(msaCode, params)` to API service
- [ ] Call `/api/v1/data/markets/{msa_code}` endpoint
- [ ] Pass parameter filters as query params
- [ ] Handle response and transform data
- [ ] **Test:** API called correctly
- [ ] **Test:** Data transformed correctly
- [ ] **Requirement:** AC-5

##### 6.4 Market Data Chart
- [ ] Create `MarketDataChart.tsx` component
- [ ] Use Recharts LineChart for historical data
- [ ] Support multiple parameters on same chart
- [ ] Add legend and axis labels
- [ ] Color-code different parameters
- [ ] **Test:** Chart renders with data
- [ ] **Test:** Multiple parameters displayed
- [ ] **Requirement:** AC-5

##### 6.5 Forecast Integration
- [ ] Add `useForecastData()` hook
- [ ] Add `getForecastData(parameter, msaCode)` to API service
- [ ] Call `/api/v1/data/forecasts/{parameter}/{msa_code}`
- [ ] Overlay forecast on historical chart
- [ ] Show confidence intervals
- [ ] **Test:** Forecasts load correctly
- [ ] **Test:** Forecast overlays on chart
- [ ] **Requirement:** AC-5

##### 6.6 Current Values Display
- [ ] Create summary cards for current values
- [ ] Extract latest value from data points
- [ ] Display with proper formatting
- [ ] Show "as of" date
- [ ] **Test:** Current values displayed correctly
- [ ] **Requirement:** AC-5

---

### Phase 3: Polish & UX (MEDIUM Priority)

**Estimated Time:** 1-2 hours
**Dependencies:** Phase 1 & 2 complete

#### 7. Loading States

##### 7.1 Create Loading Components
- [ ] Create `frontend/src/components/ui/loading-states.tsx`
- [ ] Create `LoadingSpinner` component
- [ ] Create `LoadingCard` skeleton component
- [ ] Create `LoadingTable` skeleton component
- [ ] Add animations (spin, pulse)
- [ ] **Test:** Loading components render
- [ ] **Requirement:** AC-6

##### 7.2 Apply Loading States
- [ ] Add LoadingSpinner to DCF analysis button
- [ ] Add LoadingCard to properties list
- [ ] Add LoadingTable to market data page
- [ ] Show loading text with spinner
- [ ] **Test:** Loading states show during API calls
- [ ] **Requirement:** AC-6

#### 8. Toast Notifications

##### 8.1 Toast Integration
- [ ] Use existing toast hook from `frontend/src/hooks/useToast.ts`
- [ ] Create success toast variant (green)
- [ ] Create error toast variant (red)
- [ ] Create info toast variant (blue)
- [ ] **Test:** Toasts display correctly
- [ ] **Requirement:** AC-6

##### 8.2 Add Toast Notifications
- [ ] Success toast after analysis completes
- [ ] Error toast when analysis fails
- [ ] Success toast after property saved
- [ ] Info toast for loading states (optional)
- [ ] **Test:** Toasts appear at correct times
- [ ] **Requirement:** AC-6

#### 9. Error Handling Improvements

##### 9.1 Error Message Enhancement
- [ ] Create `ErrorDisplay` component
- [ ] Show user-friendly error titles
- [ ] Provide actionable error messages
- [ ] Add suggested fixes based on error type
- [ ] Include "Retry" or "Go Back" actions
- [ ] **Test:** Errors display helpful messages
- [ ] **Requirement:** AC-6

##### 9.2 Validation Error Handling
- [ ] Parse backend validation errors
- [ ] Map to form field errors
- [ ] Display inline validation messages
- [ ] Highlight invalid fields
- [ ] **Test:** Validation errors shown correctly
- [ ] **Requirement:** AC-1, AC-6

##### 9.3 Network Error Handling
- [ ] Detect network offline state
- [ ] Show "Offline" indicator
- [ ] Fall back to localStorage data
- [ ] Queue operations for retry
- [ ] **Test:** Offline mode works
- [ ] **Requirement:** AC-6

#### 10. Empty States

##### 10.1 Create Empty State Components
- [ ] Create generic `EmptyState` component
- [ ] Add icon, title, description props
- [ ] Add CTA button option
- [ ] Style with illustrations (optional)
- [ ] **Test:** Empty states render
- [ ] **Requirement:** AC-3

##### 10.2 Apply Empty States
- [ ] Add to properties list (no properties)
- [ ] Add to market data (no data loaded)
- [ ] Add to Monte Carlo (no property selected)
- [ ] **Test:** Empty states show correctly
- [ ] **Requirement:** AC-3, AC-4, AC-5

---

## Definition of Done Checklist

### Code Quality
- [ ] All TypeScript types defined (no `any` types)
- [ ] All components properly typed with interfaces
- [ ] No console errors or warnings
- [ ] Code follows existing patterns and conventions
- [ ] ESLint passes with no errors
- [ ] Prettier formatting applied

### Testing
- [ ] Unit tests written for new components
- [ ] Integration tests for complete flows
- [ ] Test coverage ≥30% for new code
- [ ] All tests passing locally
- [ ] Manual testing completed

### Documentation
- [ ] Component prop interfaces documented
- [ ] Complex logic commented
- [ ] API integration points documented
- [ ] README updated if needed

### Performance
- [ ] No unnecessary re-renders
- [ ] API calls debounced/throttled where appropriate
- [ ] Images optimized
- [ ] Bundle size impact < 100KB

### Accessibility
- [ ] Keyboard navigation works
- [ ] ARIA labels added
- [ ] Color contrast meets WCAG AA
- [ ] Focus states visible

### Integration
- [ ] Backend API endpoints tested
- [ ] All API calls successful
- [ ] Error scenarios handled
- [ ] Loading states implemented

### User Experience
- [ ] Responsive on mobile/tablet/desktop
- [ ] Loading states smooth
- [ ] Error messages helpful
- [ ] Navigation flows intuitive

### Deployment Readiness
- [ ] Frontend builds without errors
- [ ] No breaking changes
- [ ] Environment variables documented
- [ ] Feature flags configured (if needed)

---

## Task Dependencies Graph

```
Phase 1 (Core Flow):
  1.1-1.3 (Results Components) → 2.1-2.4 (Wire to Property Input)
                                      ↓
  3.1-3.2 (API Methods)           → 3.3-3.5 (Properties List)
                                      ↓
                                  4.1-4.2 (Testing)

Phase 2 (Enhanced):
  5.1-5.5 (Monte Carlo) [Parallel] 6.1-6.6 (Market Data)
                ↓                           ↓
            Phase 2 Complete

Phase 3 (Polish):
  7.1-7.2 (Loading) → 8.1-8.2 (Toasts) → 9.1-9.3 (Errors) → 10.1-10.2 (Empty States)
```

---

## Acceptance Criteria Mapping

| Task | Acceptance Criteria |
|------|---------------------|
| 1.1-1.3, 2.1-2.4 | AC-1, AC-2 (Property to Analysis Flow) |
| 3.1-3.5 | AC-3 (Properties List Integration) |
| 5.1-5.5 | AC-4 (Monte Carlo Simulation) |
| 6.1-6.6 | AC-5 (Market Data Explorer) |
| 7.1-10.2 | AC-6 (Loading States & Error Handling) |

---

**Next Step:** Awaiting approval to begin implementation
