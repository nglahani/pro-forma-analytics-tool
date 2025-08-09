/**
 * Tests for useAddressValidation Hook
 * Comprehensive coverage for address validation and MSA detection
 */

import { renderHook, act, waitFor } from '@testing-library/react';
import { useAddressValidation } from '../useAddressValidation';
import { apiService } from '@/lib/api/service';

// Mock the API service
jest.mock('@/lib/api/service', () => ({
  apiService: {
    validateAddress: jest.fn(),
  },
}));

// Mock debounce to make tests more predictable
jest.mock('@/lib/utils', () => ({
  debounce: (fn: Function) => fn, // Return function as-is for immediate execution in tests
}));

const mockApiService = apiService as jest.Mocked<typeof apiService>;

describe('useAddressValidation', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should initialize with default state', () => {
    const { result } = renderHook(() => useAddressValidation());

    expect(result.current.isValidating).toBe(false);
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should not validate when required fields are missing', async () => {
    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        street: '123 Main St', // Missing city and state
      });
    });

    expect(result.current.isValidating).toBe(false);
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
    expect(mockApiService.validateAddress).not.toHaveBeenCalled();
  });

  it('should validate address when all required fields are present', async () => {
    const mockValidationResult = {
      isValid: true,
      formattedAddress: '123 Main St, New York, NY 10001',
      msaInfo: {
        code: 'NYC',
        name: 'New York Metro',
        state: 'NY',
      },
      suggestions: [],
    };

    mockApiService.validateAddress.mockResolvedValue({
      success: true,
      data: mockValidationResult,
      error: null,
    });

    const { result } = renderHook(() => useAddressValidation());

    const address = {
      street: '123 Main St',
      city: 'New York',
      state: 'NY',
      zip_code: '10001',
    };

    await act(async () => {
      await result.current.validateAddress(address);
    });

    await waitFor(() => {
      expect(result.current.isValidating).toBe(false);
    });

    expect(result.current.result?.isValid).toBe(true);
    expect(result.current.error).toBeNull();
    expect(mockApiService.validateAddress).toHaveBeenCalledWith({
      street: address.street,
      city: address.city,
      state: address.state,
      zip_code: address.zip_code,
    });
  });

  it('should handle validation API errors', async () => {
    mockApiService.validateAddress.mockResolvedValue({
      success: false,
      data: null,
      error: 'Address validation service unavailable',
    });

    const { result } = renderHook(() => useAddressValidation());

    const address = {
      street: '123 Main St',
      city: 'New York',
      state: 'NY',
    };

    await act(async () => {
      await result.current.validateAddress(address);
    });

    await waitFor(() => {
      expect(result.current.isValidating).toBe(false);
    });

    expect(result.current.result).toBeNull();
    expect(result.current.error).toBe('Address validation service unavailable');
  });

  it('should handle validation exceptions', async () => {
    mockApiService.validateAddress.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useAddressValidation());

    const address = {
      street: '123 Main St',
      city: 'New York',
      state: 'NY',
    };

    await act(async () => {
      await result.current.validateAddress(address);
    });

    await waitFor(() => {
      expect(result.current.isValidating).toBe(false);
    });

    expect(result.current.result).toBeNull();
    expect(result.current.error).toBe('Network error');
  });

  it('should clear validation state when address is incomplete', async () => {
    // First, set up a successful validation
    const mockValidationResult = {
      isValid: true,
      formattedAddress: '123 Main St, New York, NY 10001',
      msaInfo: { code: 'NYC', name: 'New York Metro', state: 'NY' },
      suggestions: [],
    };

    mockApiService.validateAddress.mockResolvedValue({
      success: true,
      data: mockValidationResult,
      error: null,
    });

    const { result } = renderHook(() => useAddressValidation());

    // Validate complete address
    await act(async () => {
      await result.current.validateAddress({
        street: '123 Main St',
        city: 'New York',
        state: 'NY',
      });
    });

    await waitFor(() => {
      expect(result.current.result?.isValid).toBe(true);
    });

    // Now validate incomplete address
    await act(async () => {
      await result.current.validateAddress({
        street: '123 Main St', // Missing city and state
      });
    });

    expect(result.current.isValidating).toBe(false);
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should set validating state during API call', async () => {
    let resolveValidation: (value: any) => void;
    const validationPromise = new Promise((resolve) => {
      resolveValidation = resolve;
    });

    mockApiService.validateAddress.mockReturnValue(validationPromise);

    const { result } = renderHook(() => useAddressValidation());

    const address = {
      street: '123 Main St',
      city: 'New York',
      state: 'NY',
    };

    act(() => {
      result.current.validateAddress(address);
    });

    // Should be validating
    expect(result.current.isValidating).toBe(true);

    // Resolve the promise
    act(() => {
      resolveValidation!({
        success: true,
        data: { isValid: true, formattedAddress: '123 Main St, New York, NY', msaInfo: null, suggestions: [] },
        error: null,
      });
    });

    await waitFor(() => {
      expect(result.current.isValidating).toBe(false);
    });
  });

  it('should clear error when starting new validation', async () => {
    // First, create an error state
    mockApiService.validateAddress.mockResolvedValue({
      success: false,
      data: null,
      error: 'Validation failed',
    });

    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        street: '123 Main St',
        city: 'New York',
        state: 'NY',
      });
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Validation failed');
    });

    // Now mock a successful response
    mockApiService.validateAddress.mockResolvedValue({
      success: true,
      data: { isValid: true, formattedAddress: '456 Oak Ave, Boston, MA', msaInfo: null, suggestions: [] },
      error: null,
    });

    await act(async () => {
      await result.current.validateAddress({
        street: '456 Oak Ave',
        city: 'Boston',
        state: 'MA',
      });
    });

    await waitFor(() => {
      expect(result.current.error).toBeNull();
    });
  });

  it('should handle validation result with suggestions', async () => {
    const mockValidationResult = {
      isValid: false,
      formattedAddress: null,
      msa_info: null,
      suggestions: [
        { street: '123 Main Street', city: 'New York', state: 'NY', zip_code: '10001', msa_code: 'NYC' },
        { street: '123 Main St', city: 'New York', state: 'NY', zip_code: '10002', msa_code: 'NYC' },
      ],
    };

    mockApiService.validateAddress.mockResolvedValue({
      success: true,
      data: mockValidationResult,
      error: null,
    });

    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        street: '123 Main',
        city: 'New York',
        state: 'NY',
      });
    });

    await waitFor(() => {
      expect(result.current.result?.isValid).toBe(false);
    });

    expect(result.current.result?.suggestions).toHaveLength(2);
    expect(result.current.result?.isValid).toBe(false);
  });

  it('should handle validation result with MSA information', async () => {
    const mockValidationResult = {
      isValid: true,
      formattedAddress: '123 Michigan Ave, Chicago, IL 60601',
      msa_info: {
        msa_code: 'CHI',
        name: 'Chicago Metro', 
        state: 'IL',
      },
      suggestions: [],
    };

    mockApiService.validateAddress.mockResolvedValue({
      success: true,
      data: mockValidationResult,
      error: null,
    });

    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        street: '123 Michigan Ave',
        city: 'Chicago',
        state: 'IL',
        zip: '60601',
      });
    });

    await waitFor(() => {
      expect(result.current.result?.msa_info?.msa_code).toBe('CHI');
    });
  });

  it('should expose validateAddress function', () => {
    const { result } = renderHook(() => useAddressValidation());

    expect(result.current.validateAddress).toBeDefined();
    expect(typeof result.current.validateAddress).toBe('function');
  });

  it('should handle edge case with empty address object', async () => {
    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({});
    });

    expect(result.current.isValidating).toBe(false);
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
    expect(mockApiService.validateAddress).not.toHaveBeenCalled();
  });

  it('should handle partial address with only street', async () => {
    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        street: '123 Main St',
        // Missing city and state
      });
    });

    expect(mockApiService.validateAddress).not.toHaveBeenCalled();
  });

  it('should handle partial address with only city', async () => {
    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        city: 'New York',
        // Missing street and state
      });
    });

    expect(mockApiService.validateAddress).not.toHaveBeenCalled();
  });

  it('should handle partial address with only state', async () => {
    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        state: 'NY',
        // Missing street and city
      });
    });

    expect(mockApiService.validateAddress).not.toHaveBeenCalled();
  });

  it('should handle non-Error exceptions gracefully', async () => {
    mockApiService.validateAddress.mockRejectedValue('String error');

    const { result } = renderHook(() => useAddressValidation());

    await act(async () => {
      await result.current.validateAddress({
        street: '123 Main St',
        city: 'New York',
        state: 'NY',
      });
    });

    await waitFor(() => {
      expect(result.current.error).toBe('Validation failed');
    });
  });
});