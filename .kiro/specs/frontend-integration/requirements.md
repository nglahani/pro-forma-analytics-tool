# Frontend-Backend Integration - Requirements Specification

**Feature ID:** FE-INTEGRATION-001
**Created:** 2025-11-05
**Status:** Draft → Awaiting Approval

---

## User Stories

### Story 1: Complete Property Analysis Flow
**As a** real estate investor
**I want to** input property data, run DCF analysis, and immediately see investment recommendations
**So that** I can make informed investment decisions without manual calculations

**Priority:** CRITICAL
**Effort:** Medium (2-3 hours)

### Story 2: View Analysis History
**As a** real estate investor
**I want to** view all my previously analyzed properties with their financial metrics
**So that** I can compare multiple investment opportunities and track my analysis history

**Priority:** HIGH
**Effort:** Small (1 hour)

### Story 3: Monte Carlo Risk Analysis
**As a** real estate investor
**I want to** run Monte Carlo simulations to understand investment risk profiles
**So that** I can evaluate downside scenarios and make risk-adjusted decisions

**Priority:** MEDIUM
**Effort:** Medium (3 hours)

### Story 4: Market Data Exploration
**As a** real estate investor
**I want to** explore historical and forecast market data for different MSAs
**So that** I can understand market trends and validate analysis assumptions

**Priority:** MEDIUM
**Effort:** Medium (2 hours)

### Story 5: Visual Feedback & Error Handling
**As a** user
**I want to** see clear loading states, success confirmations, and helpful error messages
**So that** I understand what's happening and can recover from errors

**Priority:** HIGH
**Effort:** Small (1-2 hours)

---

## Acceptance Criteria (EARS Format)

### AC-1: Property to Analysis Flow
**WHEN** user completes property input form and clicks "Submit"
**THEN** system SHALL save property data to localStorage

**WHEN** user clicks "Run Analysis" button
**THEN** system SHALL call `/api/v1/analysis/dcf` with property data

**WHEN** DCF analysis completes successfully
**THEN** system SHALL display results modal with NPV, IRR, equity multiple, and recommendation

**WHEN** user views results
**THEN** system SHALL show color-coded recommendation (green=BUY, red=SELL)

**WHEN** analysis fails
**THEN** system SHALL display user-friendly error message with suggested fixes

### AC-2: Analysis Results Display
**WHEN** analysis results are displayed
**THEN** system SHALL show:
- Net Present Value (NPV) formatted as currency
- Internal Rate of Return (IRR) formatted as percentage
- Equity Multiple formatted with 2 decimal places
- Investment Recommendation (STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL)
- Processing time in seconds
- Analysis timestamp

**WHEN** detailed cash flows are available
**THEN** system SHALL provide "View Details" button to show annual projections

### AC-3: Properties List Integration
**WHEN** user navigates to Properties page
**THEN** system SHALL call `/api/v1/analysis/history` to fetch recent analyses

**WHEN** API returns analysis history
**THEN** system SHALL merge API data with localStorage data

**WHEN** user clicks on a property
**THEN** system SHALL navigate to analysis results page for that property

**WHEN** no analyses exist
**THEN** system SHALL display empty state with "Analyze Your First Property" CTA

### AC-4: Monte Carlo Simulation
**WHEN** user navigates to Monte Carlo page
**THEN** system SHALL display property selector (from existing or new)

**WHEN** user selects property and scenario count
**THEN** system SHALL validate inputs (scenarios: 500-10,000)

**WHEN** user clicks "Run Simulation"
**THEN** system SHALL call `/api/v1/simulation/monte-carlo` endpoint

**WHEN** simulation completes
**THEN** system SHALL display:
- Scenario distribution charts
- Risk metrics (VaR, Expected Shortfall)
- Scenario classification breakdown
- Confidence intervals

### AC-5: Market Data Explorer
**WHEN** user navigates to Market Data page
**THEN** system SHALL display MSA selector dropdown

**WHEN** user selects MSA
**THEN** system SHALL call `/api/v1/data/markets/{msa_code}`

**WHEN** market data loads
**THEN** system SHALL display:
- Historical data charts for selected parameters
- Current market values
- Data coverage information
- Last updated timestamp

**WHEN** user requests forecasts
**THEN** system SHALL call `/api/v1/data/forecasts/{parameter}/{msa_code}`

### AC-6: Loading States & Error Handling
**WHEN** any API call is in progress
**THEN** system SHALL display loading spinner with descriptive text

**WHEN** API call succeeds
**THEN** system SHALL show success toast notification

**WHEN** API call fails
**THEN** system SHALL:
- Display error toast with message
- Log error details to console
- Provide actionable error message
- Allow user to retry operation

**WHEN** network is unavailable
**THEN** system SHALL fall back to localStorage data if available

---

## Out of Scope

The following are explicitly excluded from this feature:
- User authentication system (demo mode sufficient for MVP)
- Property data persistence to backend database (localStorage only)
- Real-time collaboration features
- PDF/Excel export functionality (backend endpoints exist but UI not required)
- Advanced charting beyond basic line/bar charts
- Property comparison tool
- Portfolio optimization features
- Email notifications

---

## Assumptions

1. **Backend API is stable and tested** - All backend endpoints are functional and tested
2. **Authentication uses dev key** - Development mode uses hardcoded dev API key
3. **Browser compatibility** - Modern browsers (Chrome, Firefox, Safari, Edge) latest 2 versions
4. **localStorage availability** - Users have localStorage enabled
5. **Network connectivity** - Users have stable internet connection
6. **MSA coverage** - Limited to 5 supported MSAs (NYC, LA, Chicago, DC, Miami)
7. **Data freshness** - Market data updates are monthly, not real-time

---

## Open Questions

1. **Results Navigation:** Should analysis results open in modal or navigate to dedicated page?
   - **Impact:** Affects navigation flow and state management
   - **Options:** A) Modal overlay (simpler), B) Dedicated route (more features)

2. **Chart Library:** Which charting library to use for visualizations?
   - **Impact:** Bundle size and feature set
   - **Options:** A) Recharts (already in package.json), B) Chart.js, C) D3.js

3. **Error Retry Strategy:** How many retries before giving up on failed API calls?
   - **Impact:** User experience during network issues
   - **Options:** A) 3 retries with exponential backoff, B) Manual retry only

4. **Cache Strategy:** How long should localStorage data be considered valid?
   - **Impact:** Data freshness vs offline capability
   - **Options:** A) 24 hours, B) 7 days, C) No expiration

5. **Results Persistence:** Should we persist full analysis results or just summary?
   - **Impact:** localStorage size limits
   - **Options:** A) Full results (detailed), B) Summary only (smaller)

---

## Dependencies

**External:**
- Backend API availability at `http://localhost:8000` (dev) or configured URL (prod)
- Recharts library for charting (already installed)
- Radix UI components for modals/dialogs (already installed)
- TanStack Query for data fetching (already installed)

**Internal:**
- `frontend/src/lib/api/client.ts` - API client working ✅
- `frontend/src/lib/api/service.ts` - API service layer working ✅
- `frontend/src/hooks/useAPI.ts` - React hooks for API calls working ✅
- `frontend/src/types/property.ts` - Property type definitions ✅

---

## Success Criteria

**Minimum Viable (Definition of Done):**
1. User can input property → run analysis → see results (complete flow)
2. Properties list displays analyzed properties from API
3. All API integration tests pass
4. Zero console errors during happy path
5. Loading states visible during API calls
6. Error messages displayed for failed calls

**Complete Success:**
1. All acceptance criteria met
2. Monte Carlo simulation working
3. Market data explorer working
4. All three phases implemented
5. End-to-end user journey tested and validated
6. Frontend test coverage ≥30%

---

**Next Step:** Awaiting approval to proceed to `design.md`
