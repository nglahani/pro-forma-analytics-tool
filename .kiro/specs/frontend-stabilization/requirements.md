# Frontend Stabilization Requirements

**Epic**: Frontend TypeScript Type Safety & Test Suite Stabilization  
**Priority**: HIGH  
**Target**: Achieve 100% frontend TypeScript compilation and test suite success  

## User Stories

### Primary Stakeholder: Frontend Developer
**As a** frontend developer working on the Pro-Forma Analytics Tool,  
**I want** TypeScript to compile without errors and all tests to pass,  
**So that** I can confidently develop new features and maintain code quality.

### Secondary Stakeholder: CI/CD Pipeline
**As a** CI/CD pipeline,  
**I want** consistent frontend builds and test execution,  
**So that** deployment readiness can be automatically validated.

## Acceptance Criteria (EARS Format)

### AC1: TypeScript Compilation
**WHEN** the frontend codebase is compiled with TypeScript  
**THEN** the system SHALL produce zero compilation errors  
**AND** all type definitions SHALL accurately reflect the backend API contracts

### AC2: Test Suite Success
**WHEN** the frontend test suite is executed  
**THEN** all tests SHALL pass without failures  
**AND** no React testing warnings SHALL be present  
**AND** test coverage SHALL be maintained at current levels

### AC3: API Contract Synchronization
**WHEN** frontend interfaces are compared to backend Pydantic models  
**THEN** all property names, types, and enum values SHALL match exactly  
**AND** no missing or extra properties SHALL exist in type definitions

### AC4: Component Integration
**WHEN** React components consume API types  
**THEN** all component props SHALL be correctly typed  
**AND** no runtime type mismatches SHALL occur

## Detailed Requirements

### Type System Issues (Critical)
1. **InitialNumbers Interface Mismatch**
   - Frontend expects: `loan_to_value_ratio`, `total_cash_required`
   - Backend provides: `loan_amount`, `cash_required`
   - Impact: Property input and DCF analysis components fail

2. **PropertyInput Location Fields Missing**
   - Frontend expects: `city`, `state`, `msa_code` as direct properties
   - Backend structure: Location data may be nested or derived
   - Impact: Property input form cannot bind to form fields

3. **Enum Value Misalignment**
   - Frontend: `InvestmentRecommendation.STRONG_BUY`
   - Backend: Domain enum may use different string values
   - Impact: Analysis results display incorrect recommendations

4. **CashFlowProjection Schema Gaps**
   - Frontend expects: `vacancy_loss`, `effective_gross_income`
   - Backend: May use different field names or calculations
   - Impact: Cash flow table displays undefined values

### Test Suite Issues (High)
1. **React Testing Library Warnings**
   - 17 failing tests due to type mismatches
   - `act()` warnings in component state updates
   - Missing component imports and mock data

2. **Component Test Coverage**
   - DCFResultsDashboard tests failing on property access
   - MonteCarloResults tests expect different data shapes
   - Form validation tests broken by schema changes

### Package Management (Medium)
1. **Node Modules Cleanup**
   - Git status shows deleted node_modules files
   - Package-lock.json may be out of sync
   - Dependencies may need version updates

## Out of Scope

1. **New Feature Development**: No new UI components or functionality
2. **Performance Optimization**: Focus is on correctness, not performance
3. **Visual Design Changes**: Maintain existing UI/UX patterns
4. **Backend API Changes**: Backend schema is considered stable
5. **End-to-End Testing**: Focus on unit and component tests only

## Assumptions

1. **Backend API Stability**: Current backend Pydantic models are final
2. **Test Environment**: Node.js 18+ and Jest testing framework
3. **TypeScript Version**: Current TS configuration is appropriate
4. **Component Architecture**: Existing component structure is sound
5. **Package Ecosystem**: Current React/Next.js versions are compatible

## Open Questions

1. **Schema Generation**: Should we implement automated TypeScript generation from Pydantic models?
2. **Migration Strategy**: Do we need to preserve any legacy type definitions?
3. **Test Data**: Should we update mock data to match current schemas or create new fixtures?
4. **Breaking Changes**: Are there any acceptable breaking changes in component interfaces?
5. **Validation**: Should we add runtime type validation alongside compile-time checks?

## Success Metrics

### Definition of Ready
- [ ] All TypeScript compilation errors are cataloged and understood
- [ ] Backend API schema is documented and stable
- [ ] Test failure root causes are identified
- [ ] Development environment is set up and validated

### Definition of Done
- [ ] `npm run type-check` passes with zero errors
- [ ] `npm test` passes with zero failures
- [ ] No React testing warnings in console output
- [ ] All component prop types are correctly defined
- [ ] API response types match backend exactly
- [ ] CI/CD frontend pipeline passes consistently

## Dependencies

### Upstream Dependencies
1. **Backend API Schema**: Pydantic models must be stable and documented
2. **Domain Entities**: Core business objects must be finalized

### Downstream Dependencies  
1. **Integration Testing**: Full frontend-backend integration depends on this work
2. **Feature Development**: New UI features blocked until type safety is restored
3. **Production Deployment**: Cannot deploy with compilation errors

## Risk Assessment

### High Risk
- **Time Estimation**: TypeScript errors may reveal deeper architectural issues
- **Backward Compatibility**: Type changes might break existing component contracts

### Medium Risk
- **Test Complexity**: Some tests may require significant refactoring
- **Package Dependencies**: Node module issues might require dependency updates

### Low Risk
- **Component Logic**: Business logic in components should remain unchanged
- **User Experience**: No visible changes expected for end users