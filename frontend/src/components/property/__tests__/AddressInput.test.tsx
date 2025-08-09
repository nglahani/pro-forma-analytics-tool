/**
 * Tests for AddressInput component
 * Tests address input functionality with validation
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AddressInput } from '../AddressInput';
import { useAddressValidation } from '@/hooks/useAddressValidation';

// Mock dependencies
jest.mock('@/hooks/useAddressValidation');
jest.mock('lucide-react', () => ({
  CheckCircle: () => <div data-testid="check-circle-icon" />,
  AlertCircle: () => <div data-testid="alert-circle-icon" />,
  Loader2: () => <div data-testid="loader-icon" />,
  MapPin: () => <div data-testid="map-pin-icon" />,
}));

const mockUseAddressValidation = useAddressValidation as jest.MockedFunction<typeof useAddressValidation>;

describe('AddressInput', () => {
  const defaultProps = {
    address: {},
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: null,
      error: null,
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });
  });

  it('renders address input fields', () => {
    render(<AddressInput {...defaultProps} />);

    expect(screen.getByLabelText('Street Address *')).toBeInTheDocument();
    expect(screen.getByLabelText('City *')).toBeInTheDocument();
    expect(screen.getByLabelText('State *')).toBeInTheDocument();
    expect(screen.getByLabelText('ZIP Code')).toBeInTheDocument();
  });

  it('displays current address values', () => {
    const address = {
      street: '123 Main St',
      city: 'New York',
      state: 'NY',
      zip_code: '10001',
    };

    render(<AddressInput address={address} onChange={jest.fn()} />);

    expect(screen.getByDisplayValue('123 Main St')).toBeInTheDocument();
    expect(screen.getByDisplayValue('New York')).toBeInTheDocument();
    expect(screen.getByDisplayValue('NY')).toBeInTheDocument();
    expect(screen.getByDisplayValue('10001')).toBeInTheDocument();
  });

  it('calls onChange when fields are modified', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    
    render(<AddressInput {...defaultProps} onChange={onChange} />);

    const streetInput = screen.getByLabelText('Street Address *');
    await user.clear(streetInput);
    await user.type(streetInput, 'Main St');

    // Check that onChange was called
    expect(onChange).toHaveBeenCalled();
    
    // Check that at least one call contains the expected text
    const calls = onChange.mock.calls;
    expect(calls.some(call => call[0].street === 'Main St')).toBe(true);
  });

  it('converts state input to uppercase', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    
    render(<AddressInput {...defaultProps} onChange={onChange} />);

    const stateInput = screen.getByLabelText('State *');
    await user.type(stateInput, 'ny');

    // Check the last call contains the uppercase text
    const lastCall = onChange.mock.calls[onChange.mock.calls.length - 1];
    expect(lastCall[0]).toEqual({
      state: 'Y',
    });
  });

  it('displays validation errors', () => {
    const errors = {
      street: 'Street is required',
      city: 'City is required',
      state: 'State is required',
      zip_code: 'Invalid ZIP code',
    };

    render(<AddressInput {...defaultProps} errors={errors} />);

    expect(screen.getByText('Street is required')).toBeInTheDocument();
    expect(screen.getByText('City is required')).toBeInTheDocument();
    expect(screen.getByText('State is required')).toBeInTheDocument();
    expect(screen.getByText('Invalid ZIP code')).toBeInTheDocument();
  });

  it('shows validating state', () => {
    mockUseAddressValidation.mockReturnValue({
      isValidating: true,
      result: null,
      error: null,
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });

    const address = { street: '123 Main St', city: 'New York', state: 'NY' };
    render(<AddressInput address={address} onChange={jest.fn()} />);

    // There are two loader icons - one in input, one in status
    expect(screen.getAllByTestId('loader-icon')).toHaveLength(2);
    expect(screen.getByText('Validating address...')).toBeInTheDocument();
  });

  it('shows valid address with MSA info', () => {
    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: {
        isValid: true,
        msa_info: {
          msa_code: '35620',
          name: 'New York-Newark-Jersey City, NY-NJ-PA',
          state: 'NY',
          major_cities: [],
          market_tier: 'primary' as const,
        },
      },
      error: null,
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });

    const address = { street: '123 Main St', city: 'New York', state: 'NY' };
    render(<AddressInput address={address} onChange={jest.fn()} />);

    expect(screen.getByText('Address Validated')).toBeInTheDocument();
    expect(screen.getByText('New York-Newark-Jersey City, NY-NJ-PA (MSA: 35620)')).toBeInTheDocument();
    expect(screen.getByTestId('check-circle-icon')).toBeInTheDocument();
    expect(screen.getByTestId('map-pin-icon')).toBeInTheDocument();
  });

  it('shows address suggestions', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();

    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: {
        isValid: false,
        suggestions: [
          {
            street: '123 Main Street',
            city: 'New York',
            state: 'NY',
            zip_code: '10001',
            msa_code: '35620',
          },
          {
            street: '123 Main St',
            city: 'New York',
            state: 'NY',
            zip_code: '10002',
            msa_code: '35620',
          },
        ],
      },
      error: null,
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });

    const address = { street: '123 Main', city: 'New York', state: 'NY' };
    render(<AddressInput address={address} onChange={onChange} />);

    expect(screen.getByText('Address suggestions available')).toBeInTheDocument();
    expect(screen.getByText('123 Main Street')).toBeInTheDocument();
    expect(screen.getByText('123 Main St')).toBeInTheDocument();

    // Click on first suggestion
    await user.click(screen.getByText('123 Main Street'));
    
    expect(onChange).toHaveBeenCalledWith({
      street: '123 Main Street',
      city: 'New York',
      state: 'NY',
      zip_code: '10001',
      msa_code: '35620',
    });
  });

  it('shows validation error', () => {
    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: null,
      error: 'Network error',
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });

    const address = { street: '123 Main St', city: 'New York', state: 'NY' };
    render(<AddressInput address={address} onChange={jest.fn()} />);

    expect(screen.getByText('Validation Error')).toBeInTheDocument();
    expect(screen.getByText('Network error')).toBeInTheDocument();
    expect(screen.getByTestId('alert-circle-icon')).toBeInTheDocument();
  });

  it('shows invalid address message', () => {
    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: { isValid: false },
      error: null,
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });

    const address = { street: '123 Main St', city: 'New York', state: 'NY' };
    render(<AddressInput address={address} onChange={jest.fn()} />);

    expect(screen.getByText('Address Not Found')).toBeInTheDocument();
    expect(screen.getByText('Please check the address details')).toBeInTheDocument();
  });

  it('calls onMSADetected when MSA is found', () => {
    const onMSADetected = jest.fn();
    
    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: {
        isValid: true,
        msa_info: {
          msa_code: '35620',
          name: 'New York-Newark-Jersey City, NY-NJ-PA',
          state: 'NY',
          major_cities: [],
          market_tier: 'primary' as const,
        },
      },
      error: null,
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });

    const address = { street: '123 Main St', city: 'New York', state: 'NY' };
    render(<AddressInput address={address} onChange={jest.fn()} onMSADetected={onMSADetected} />);

    expect(onMSADetected).toHaveBeenCalledWith('35620', expect.any(Object));
  });

  it('handles field length limits', async () => {
    const user = userEvent.setup();
    const onChange = jest.fn();
    
    render(<AddressInput {...defaultProps} onChange={onChange} />);

    // State field should limit to 2 characters
    const stateInput = screen.getByLabelText('State *');
    expect(stateInput).toHaveAttribute('maxlength', '2');

    // ZIP code field should limit to 5 characters
    const zipInput = screen.getByLabelText('ZIP Code');
    expect(zipInput).toHaveAttribute('maxlength', '5');
  });

  it('applies error styling to fields with errors', () => {
    const errors = {
      street: 'Error',
      city: 'Error',
    };

    render(<AddressInput {...defaultProps} errors={errors} />);

    const streetInput = screen.getByLabelText('Street Address *');
    const cityInput = screen.getByLabelText('City *');
    
    expect(streetInput).toHaveClass('border-red-500');
    expect(cityInput).toHaveClass('border-red-500');
  });

  it('triggers validation when address changes', () => {
    const validateAddress = jest.fn();
    const clearValidation = jest.fn();

    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: null,
      error: null,
      validateAddress,
      clearValidation,
    });

    const { rerender } = render(<AddressInput {...defaultProps} />);

    // Initially should clear validation
    expect(clearValidation).toHaveBeenCalled();

    // When address is provided, should validate
    const address = { street: '123 Main St', city: 'New York', state: 'NY' };
    rerender(<AddressInput address={address} onChange={jest.fn()} />);

    expect(validateAddress).toHaveBeenCalledWith(address);
  });

  it('limits suggestions to 3 items', () => {
    mockUseAddressValidation.mockReturnValue({
      isValidating: false,
      result: {
        isValid: false,
        suggestions: [
          { street: '123 Main St 1', city: 'NY', state: 'NY', zip_code: '10001' },
          { street: '123 Main St 2', city: 'NY', state: 'NY', zip_code: '10002' },
          { street: '123 Main St 3', city: 'NY', state: 'NY', zip_code: '10003' },
          { street: '123 Main St 4', city: 'NY', state: 'NY', zip_code: '10004' },
          { street: '123 Main St 5', city: 'NY', state: 'NY', zip_code: '10005' },
        ],
      },
      error: null,
      validateAddress: jest.fn(),
      clearValidation: jest.fn(),
    });

    const address = { street: '123 Main', city: 'New York', state: 'NY' };
    render(<AddressInput address={address} onChange={jest.fn()} />);

    // Should only show first 3 suggestions
    expect(screen.getByText('123 Main St 1')).toBeInTheDocument();
    expect(screen.getByText('123 Main St 2')).toBeInTheDocument();
    expect(screen.getByText('123 Main St 3')).toBeInTheDocument();
    expect(screen.queryByText('123 Main St 4')).not.toBeInTheDocument();
    expect(screen.queryByText('123 Main St 5')).not.toBeInTheDocument();
  });
});