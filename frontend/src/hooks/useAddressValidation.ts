/**
 * Address Validation Hook
 * Provides real-time address validation and MSA auto-detection
 */

'use client';

import { useState, useCallback, useRef } from 'react';
import { apiService } from '@/lib/api/service';
import { PropertyAddress, MSAInfo, AddressValidationResult } from '@/types/property';
import { debounce } from '@/lib/utils';

interface ValidationState {
  isValidating: boolean;
  result: AddressValidationResult | null;
  error: string | null;
}

export function useAddressValidation() {
  const [validationState, setValidationState] = useState<ValidationState>({
    isValidating: false,
    result: null,
    error: null,
  });

  // Use ref to store the latest validation function
  const validationRef = useRef<(address: Partial<PropertyAddress>) => Promise<void>>();

  const validateAddress = useCallback(async (address: Partial<PropertyAddress>) => {
    if (!address.street || !address.city || !address.state) {
      setValidationState({
        isValidating: false,
        result: null,
        error: null,
      });
      return;
    }

    setValidationState(prev => ({ ...prev, isValidating: true, error: null }));

    try {
      const response = await apiService.validateAddress({
        street: address.street,
        city: address.city,
        state: address.state,
        zip_code: address.zip_code,
      });

      if (response.success) {
        setValidationState({
          isValidating: false,
          result: {
            isValid: response.data?.isValid || false,
            suggestions: response.data?.suggestions?.map(s => ({
              street: s.street,
              city: s.city,
              state: s.state,
              zip_code: s.zip_code,
              msa_code: s.msa_code,
            })),
            msa_info: response.data?.msa_info ? {
              msa_code: response.data.msa_info.msa_code,
              name: response.data.msa_info.name,
              state: response.data.msa_info.state,
              major_cities: [],
              market_tier: 'primary',
            } : undefined,
            error: response.data?.error,
          },
          error: null,
        });
      } else {
        setValidationState({
          isValidating: false,
          result: null,
          error: response.error || 'Validation failed',
        });
      }
    } catch (error) {
      setValidationState({
        isValidating: false,
        result: null,
        error: error instanceof Error ? error.message : 'Validation failed',
      });
    }
  }, []);

  // Debounced validation to avoid excessive API calls
  const debouncedValidateAddress = useCallback(
    debounce(validateAddress as (...args: unknown[]) => unknown, 800) as (address: Partial<PropertyAddress>) => Promise<void>,
    [validateAddress]
  );

  // Store the latest validation function
  validationRef.current = debouncedValidateAddress;

  const clearValidation = useCallback(() => {
    setValidationState({
      isValidating: false,
      result: null,
      error: null,
    });
  }, []);

  return {
    ...validationState,
    validateAddress: debouncedValidateAddress,
    clearValidation,
  };
}