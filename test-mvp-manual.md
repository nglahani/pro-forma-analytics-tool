# MVP Manual Testing Guide

## World-Class Architecture Review & Manual Testing Protocol

### Pre-Test System Validation

#### 1. Backend Health Check
```bash
curl -s http://127.0.0.1:8001/api/v1/health | python -m json.tool
```
**Expected**: Status "healthy", all dependencies "healthy"

#### 2. Frontend Accessibility
```bash
curl -s http://localhost:3003 | grep -i "pro forma\|next"
```
**Expected**: Response contains "Pro Forma Analytics" or Next.js content

#### 3. Integration Test Validation
```bash
python -m pytest tests/integration/test_frontend_backend_integration.py -v
```
**Expected**: All tests pass

---

### MVP User Flow Testing

#### Phase 1: Authentication Flow

**1.1 Registration Process**
1. Navigate to: http://localhost:3003
2. Should redirect to: http://localhost:3003/auth/login?redirect=%2F
3. Click "Sign up" or navigate to registration
4. Fill form:
   - Email: `test@proforma.dev`
   - Password: `test123456`
   - Confirm Password: `test123456`
5. Submit registration

**Expected Results:**
- ✅ Registration succeeds
- ✅ User is logged in automatically
- ✅ API key is generated and stored
- ✅ Redirected to dashboard

**1.2 Login Process**
1. Logout from dashboard
2. Should redirect to login page
3. Login with:
   - Email: `test@proforma.dev`
   - Password: `test123456`

**Expected Results:**
- ✅ Login succeeds
- ✅ Dashboard loads with health check data
- ✅ Navigation works (sidebar/header)

#### Phase 2: Property Input Flow

**2.1 Property Template Selection**
1. Navigate to "Property Input" from sidebar
2. Review available templates:
   - Multifamily Residential
   - Commercial Office  
   - Mixed-Use Property
   - Retail & Shopping
3. Select "Mixed-Use Property" template
4. Review template preview data
5. Click "Continue with Template"

**Expected Results:**
- ✅ Template selector loads
- ✅ Template data displays correctly
- ✅ Template selection advances to form

**2.2 Multi-Step Property Form**
**Step 1: Property Details**
- Property Name: `Test Mixed-Use NYC`
- Purchase Price: `2500000`
- City: `New York`
- State: `NY`
- Property Address: `123 Test Street, New York, NY 10001`
- Notes: `Manual testing property for MVP validation`
- Click "Next"

**Step 2: Unit Information**
- Residential Units: 8 (pre-filled from template)
- Avg Rent per Unit: $2,200 (pre-filled)
- Avg SqFt per Unit: 750 (pre-filled)
- Commercial Units: 3 (pre-filled)
- Avg Rent per Unit: $22,400 (pre-filled)
- Avg SqFt per Unit: 800 (pre-filled)
- Click "Next"

**Step 3: Renovation & Costs**
- Renovation Period: 8 months (pre-filled)
- Renovation Budget: $180,000 (pre-filled)
- Click "Next"

**Step 4: Equity Structure**
- Investor Equity Share: 25% (pre-filled)
- Self Cash Percentage: 85% (pre-filled)
- Click "Next"

**Step 5: Review & Submit**
- Review all entered data
- Click "Submit for Analysis"

**Expected Results:**
- ✅ All form steps work without errors
- ✅ Data validation works appropriately
- ✅ Navigation between steps works
- ✅ Template defaults populate correctly
- ✅ Form submission succeeds

#### Phase 3: Analysis Integration

**3.1 Property Submission Success**
After form submission:
1. Should show success page with property name
2. Should display "What's Next?" guidance
3. Should show "Run DCF Analysis" button

**3.2 DCF Analysis Execution**
1. Click "Run DCF Analysis" button
2. Button should show "Analyzing..." state
3. Wait for analysis completion

**Expected Results:**
- ✅ Analysis request is sent to backend
- ✅ Loading state is displayed
- ✅ Analysis results are returned
- ✅ Results display: NPV, IRR, Equity Multiple, Recommendation

**3.3 Analysis Results Validation**
Expected analysis results should include:
- NPV: Positive value (investment recommendation)
- IRR: Percentage value (typically 15-50% for good deals)
- Equity Multiple: Multiplier (typically 1.5-3.0x)
- Recommendation: One of STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL

---

### Technical Deep Dive Testing

#### 4.1 Browser Console Validation
**Open Browser Developer Tools (F12)**
1. Check Console tab for errors
2. Check Network tab for failed requests
3. Check Application tab for localStorage data:
   - `pro_forma_user` (authentication session)
   - `pro_forma_users` (simulated user database)

**Expected Results:**
- ✅ No JavaScript errors in console
- ✅ All API requests succeed (200/201 status codes)
- ✅ Authentication data properly stored
- ✅ No CORS errors

#### 4.2 API Integration Validation
**Check Backend Integration:**
1. Monitor backend logs during frontend operations
2. Verify API key authentication works
3. Test health check endpoint integration
4. Validate property data serialization

**Expected Results:**
- ✅ Backend receives properly formatted requests
- ✅ Authentication headers are included
- ✅ Property data matches backend schema
- ✅ No serialization errors

#### 4.3 Error Handling Testing
**Test Error Scenarios:**
1. Submit form with missing required fields
2. Submit property with invalid data (negative values)
3. Test analysis with backend temporarily down
4. Test authentication with invalid credentials

**Expected Results:**
- ✅ Form validation prevents invalid submissions
- ✅ Clear error messages displayed to user
- ✅ System recovers gracefully from failures
- ✅ User can retry operations after errors

---

### Performance & Quality Validation

#### 5.1 Performance Metrics
- Initial page load: < 3 seconds
- Form navigation: < 1 second per step
- Analysis execution: < 10 seconds
- Authentication operations: < 2 seconds

#### 5.2 UI/UX Quality
- ✅ Responsive design works on different screen sizes
- ✅ Loading states provide user feedback
- ✅ Navigation is intuitive and consistent
- ✅ Error messages are clear and actionable

#### 5.3 Data Consistency
- ✅ Template data matches backend expectations
- ✅ MSA code mapping works for major cities
- ✅ Calculated metrics display correctly
- ✅ Property data persists through workflow

---

### Critical Issues Checklist

If any of these fail, it indicates a critical MVP issue:

❌ **Authentication Flow**
- [ ] Registration creates user and API key
- [ ] Login persists session correctly
- [ ] Logout clears session data
- [ ] Protected routes require authentication

❌ **Property Input Flow**  
- [ ] Template selection works
- [ ] Multi-step form navigation works
- [ ] Form validation prevents invalid data
- [ ] Property submission succeeds

❌ **Analysis Integration**
- [ ] DCF analysis request sent to backend
- [ ] Analysis results returned and displayed
- [ ] Error handling for analysis failures
- [ ] Loading states work correctly

❌ **System Integration**
- [ ] Frontend-backend communication works
- [ ] API authentication is functional
- [ ] Data serialization/deserialization works
- [ ] Health check integration works

---

### Success Criteria

The MVP is considered successful if:

1. **Complete User Journey**: User can register → login → input property → get analysis results
2. **No Critical Errors**: No JavaScript console errors or failed API requests
3. **Data Integrity**: Property data flows correctly from frontend to backend
4. **Performance**: All operations complete within acceptable time limits
5. **Error Recovery**: System handles errors gracefully and provides clear feedback

### Next Steps After MVP Validation

If MVP testing passes:
1. Document any minor issues found
2. Create production deployment plan
3. Set up monitoring and logging
4. Plan additional features

If MVP testing fails:
1. Document specific failure points
2. Prioritize critical fixes
3. Re-test after fixes
4. Validate with stakeholders