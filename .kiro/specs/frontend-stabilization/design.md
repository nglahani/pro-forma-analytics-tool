# Frontend Stabilization Design

**Epic**: Frontend TypeScript Type Safety & Test Suite Stabilization  
**Architecture**: Frontend Layer Type System Synchronization  
**Approach**: Schema-First Type Generation with Backward Compatibility  

## Architecture Placement

### Frontend Layer (Presentation/Infrastructure Boundary)
```
frontend/src/types/           # TypeScript type definitions (Infrastructure concern)
├── property.ts              # Property input and structure types
├── analysis.ts              # DCF analysis result types  
├── api.ts                   # API request/response contracts
└── index.ts                 # Centralized exports

frontend/src/components/      # React components (Presentation concern)
├── analysis/                # Analysis display components
├── property/                # Property input components
└── ui/                      # Shared UI components

frontend/src/hooks/           # React hooks (Presentation utilities)
├── useAPI.ts                # API client integration
├── useMarketData.ts         # Market data fetching
└── useMonteCarloSimulation.ts # Monte Carlo simulation
```

### Dependency Flow
```
Backend Pydantic Models → Frontend TypeScript Types → React Components
```

## Data Model Changes

### Critical Schema Mismatches Identified

#### 1. InitialNumbers Interface
**Current Frontend (Incorrect)**:
```typescript
interface InitialNumbers {
  total_cash_required: number;  // ❌ Does not exist in backend
  loan_to_value_ratio: number;  // ❌ Does not exist in backend
}
```

**Backend Reality (Correct)**:
```python
@dataclass
class InitialNumbers:
    purchase_price: float
    closing_cost_amount: float 
    renovation_capex: float
    cost_basis: float
    loan_amount: float           # ✅ Actual field
    cash_required: float         # ✅ Actual field (not total_cash_required)
```

**Frontend Fix Required**:
```typescript
interface InitialNumbers {
  purchase_price: number;
  closing_cost_amount: number;
  renovation_capex: number;
  cost_basis: number;
  loan_amount: number;          // ✅ Correct field name
  cash_required: number;        // ✅ Correct field name (not total_cash_required)
}
```

#### 2. SimplifiedPropertyInput Location Fields
**Current Frontend (Incorrect)**:
```typescript
interface SimplifiedPropertyInput {
  city: string;        // ❌ Expected as required property
  state: string;       // ❌ Expected as required property  
  msa_code: string;    // ❌ Expected as required property
}
```

**Backend Reality (Correct)**:
```python
@dataclass 
class SimplifiedPropertyInput:
    # Core required fields
    property_id: str
    property_name: str
    residential_units: ResidentialUnits
    renovation_info: RenovationInfo
    equity_structure: InvestorEquityStructure
    
    # Optional location fields
    city: Optional[str] = None        # ✅ Optional, not required
    state: Optional[str] = None       # ✅ Optional, not required
    msa_code: Optional[str] = None    # ✅ Optional, not required
```

**Frontend Fix Required**:
```typescript
interface SimplifiedPropertyInput {
  property_id: string;
  property_name: string;
  analysis_date: string;
  residential_units: ResidentialUnits;
  renovation_info: RenovationInfo;
  equity_structure: InvestorEquityStructure;
  commercial_units?: CommercialUnits;
  
  // Optional location fields (matching backend)
  city?: string;                     // ✅ Optional
  state?: string;                    // ✅ Optional  
  msa_code?: string;                 // ✅ Optional
  purchase_price?: number;
}
```

#### 3. Investment Recommendation Enum Values
**Current Frontend**:
```typescript
export enum InvestmentRecommendation {
  STRONG_BUY = "STRONG_BUY",    // ✅ Matches backend
  // ... other values need verification
}
```

**Backend Verification Needed**: Enum values in `src/domain/entities/financial_metrics.py`

#### 4. CashFlowProjection Missing Fields
**Current Frontend (Incomplete)**:
```typescript
interface CashFlowProjection {
  year: number;
  gross_rental_income: number;
  operating_expenses: number;
  net_operating_income: number;
  debt_service: number;
  net_cash_flow: number;
  cumulative_cash_flow: number;
  // ❌ Missing: vacancy_loss, effective_gross_income
}
```

**Required Addition**:
```typescript
interface CashFlowProjection {
  year: number;
  gross_rental_income: number;
  vacancy_loss: number;           // ✅ Add missing field
  effective_gross_income: number; // ✅ Add missing field
  operating_expenses: number;
  net_operating_income: number;
  debt_service: number;
  net_cash_flow: number;
  cumulative_cash_flow: number;
}
```

## Algorithm & Formulas

### Type Generation Strategy
1. **Manual Schema Mapping**: Update TypeScript interfaces to match exact backend Pydantic models
2. **Validation Layer**: Add runtime type checking for critical API boundaries
3. **Backward Compatibility**: Ensure existing components continue to work with schema updates

### Component Update Pattern
```typescript
// Before: Incorrect property access
const ltvRatio = initialNumbers.loan_to_value_ratio; // ❌ Undefined

// After: Correct property access with calculation
const ltvRatio = initialNumbers.loan_amount / initialNumbers.purchase_price; // ✅ Calculated
```

## Error Handling & Edge Cases

### TypeScript Compilation Errors
1. **Property Access Errors**: ~50 errors due to incorrect property names
2. **Missing Property Errors**: Components expecting fields that don't exist
3. **Enum Value Mismatches**: String literal type mismatches

### Runtime Error Prevention
```typescript
// Add type guards for critical API responses
function isValidInitialNumbers(data: any): data is InitialNumbers {
  return (
    typeof data.purchase_price === 'number' &&
    typeof data.loan_amount === 'number' &&
    typeof data.cash_required === 'number'
  );
}
```

### Test Failure Categories
1. **Mock Data Mismatches**: Test fixtures using old schema
2. **Component Prop Validation**: Props don't match updated interfaces
3. **React Testing Warnings**: Missing `act()` wrappers for async state updates

## Testing Strategy

### Unit Tests (Component Level)
```typescript
// Update test fixtures to match backend schema
const validInitialNumbers: InitialNumbers = {
  purchase_price: 1000000,
  loan_amount: 750000,        // ✅ Correct field name
  cash_required: 250000,      // ✅ Correct field name
  // Remove: loan_to_value_ratio, total_cash_required
};
```

### Integration Tests (API Contract)
```typescript
// Add API response validation tests
describe('API Contract Validation', () => {
  it('should match backend DCFAnalysisResponse schema', async () => {
    const response = await api.analyzeDCF(propertyData);
    expect(response).toMatchSchema(DCFAnalysisResponseSchema);
  });
});
```

### Architecture Tests (Type Safety)
```typescript
// Compile-time type checking tests
describe('Type Safety', () => {
  it('should prevent accessing non-existent properties', () => {
    const initialNumbers: InitialNumbers = mockInitialNumbers;
    // @ts-expect-error - Property should not exist
    expect(() => initialNumbers.loan_to_value_ratio).toThrowError();
  });
});
```

## Non-Functional Requirements

### Performance
- **Type Checking**: Should not impact runtime performance (compile-time only)
- **Bundle Size**: Type definitions have zero runtime impact
- **Development Experience**: IntelliSense and autocomplete should work correctly

### Security
- **Input Validation**: Add runtime validation for user-submitted data
- **API Contract**: Ensure type safety prevents injection attacks via malformed requests

### Compatibility
- **Node.js**: Maintain compatibility with Node 18+
- **TypeScript**: Use TypeScript 5.x features appropriately
- **React**: Maintain compatibility with React 18.x patterns

## Implementation Phases

### Phase 1: Core Type Fixes (Critical)
1. Update `InitialNumbers` interface with correct field names
2. Fix `SimplifiedPropertyInput` optional location fields
3. Verify and correct enum value alignments
4. Add missing `CashFlowProjection` fields

### Phase 2: Component Updates (High)
1. Update all components using incorrect property names
2. Fix prop type validation in component interfaces
3. Update test fixtures to match new schema

### Phase 3: Test Suite Repair (High)  
1. Fix 17 failing tests due to schema mismatches
2. Add `act()` wrappers for async state updates
3. Update mock data to match backend schema

### Phase 4: Runtime Validation (Medium)
1. Add type guards for critical API responses
2. Implement runtime schema validation for user inputs
3. Add API contract validation tests

## Migration Strategy

### Backward Compatibility Approach
```typescript
// Use type aliases during migration
type LegacyInitialNumbers = {
  total_cash_required?: number; // Deprecated
  loan_to_value_ratio?: number; // Deprecated
} & InitialNumbers;

// Provide migration helpers
function migrateLegacyInitialNumbers(legacy: LegacyInitialNumbers): InitialNumbers {
  const { total_cash_required, loan_to_value_ratio, ...current } = legacy;
  return current; // Use only current schema fields
}
```

### Component Migration Pattern
```typescript
// Before: Direct property access (unsafe)
const DisplayComponent = ({ data }) => (
  <div>{data.loan_to_value_ratio}</div>
);

// After: Safe property access with calculation
const DisplayComponent = ({ data }: { data: InitialNumbers }) => {
  const ltvRatio = data.loan_amount / data.purchase_price;
  return <div>{(ltvRatio * 100).toFixed(1)}%</div>;
};
```

## Validation Rules

### TypeScript Compilation
- Zero `tsc` errors allowed in final implementation
- All component props must be correctly typed
- Enum values must match backend exactly

### Runtime Behavior
- Components should handle optional fields gracefully
- API responses should be validated before use
- Error boundaries should catch type-related runtime errors

### Test Coverage
- All updated components must have passing tests
- API contract tests must validate response schemas
- Type guards must be tested for both valid and invalid inputs

## Dependencies

### Internal Dependencies
1. **Backend API Schema**: Must be stable before frontend updates
2. **Domain Entities**: TypeScript types must mirror Python dataclasses
3. **Component Library**: UI components must accept updated prop types

### External Dependencies
1. **TypeScript Compiler**: Must be compatible with type definitions
2. **React Testing Library**: Test utilities must work with updated components
3. **Jest**: Test runner must support updated test fixtures

This design ensures comprehensive frontend stabilization while maintaining clean architecture principles and providing a clear migration path from the current inconsistent state to a fully type-safe frontend.