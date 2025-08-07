/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { MonteCarloPanel } from '../MonteCarloPanel';
import { MonteCarloResult } from '@/types/analysis';

// Mock the API client
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    startMonteCarloSimulation: jest.fn(),
    getMonteCarloStatus: jest.fn(),
    stopMonteCarloSimulation: jest.fn(),
  },
}));

// Mock the hooks
jest.mock('@/hooks/useToast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

// Mock the UI components
jest.mock('@/components/ui/card', () => ({
  Card: ({ children, className }: any) => <div className={className} data-testid="card">{children}</div>,
  CardHeader: ({ children }: any) => <div data-testid="card-header">{children}</div>,
  CardTitle: ({ children }: any) => <h2 data-testid="card-title">{children}</h2>,
  CardDescription: ({ children }: any) => <p data-testid="card-description">{children}</p>,
  CardContent: ({ children }: any) => <div data-testid="card-content">{children}</div>,
}));

jest.mock('@/components/ui/button', () => ({
  Button: ({ children, onClick, disabled, className, ...props }: any) => (
    <button
      onClick={onClick}
      disabled={disabled}
      className={className}
      data-testid={props['data-testid'] || 'button'}
      {...props}
    >
      {children}
    </button>
  ),
}));

jest.mock('@/components/ui/input', () => ({
  Input: ({ value, onChange, ...props }: any) => (
    <input
      value={value}
      onChange={onChange}
      data-testid={props.id || 'input'}
      {...props}
    />
  ),
}));

jest.mock('@/components/ui/label', () => ({
  Label: ({ children, htmlFor }: any) => <label htmlFor={htmlFor}>{children}</label>,
}));

jest.mock('@/components/ui/badge', () => ({
  Badge: ({ children, className }: any) => <span className={className} data-testid="badge">{children}</span>,
}));

jest.mock('@/components/ui/progress', () => ({
  Progress: ({ value, className }: any) => (
    <div className={className} data-testid="progress">
      <div data-testid="progress-value" data-value={value}>{value}%</div>
    </div>
  ),
}));

jest.mock('@/components/ui/tabs', () => ({
  Tabs: ({ children, defaultValue }: any) => <div data-testid="tabs" data-default-value={defaultValue}>{children}</div>,
  TabsList: ({ children }: any) => <div data-testid="tabs-list">{children}</div>,
  TabsTrigger: ({ children, value }: any) => <button data-testid={`tab-${value}`}>{children}</button>,
  TabsContent: ({ children, value }: any) => <div data-testid={`tab-content-${value}`}>{children}</div>,
}));

// Mock utils
jest.mock('@/lib/utils', () => ({
  formatCurrency: (value: number) => `$${value.toLocaleString()}`,
  textColors: {
    primary: 'text-gray-900',
    secondary: 'text-gray-600',
    muted: 'text-gray-500',
    body: 'text-gray-800',
  },
}));

describe('MonteCarloPanel', () => {
  const mockProps = {
    propertyId: 'test-property-123',
    baselineNPV: 1000000,
    baselineIRR: 15.5,
    onSimulationStart: jest.fn(),
    onSimulationComplete: jest.fn(),
    onSimulationError: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders without crashing', () => {
    render(<MonteCarloPanel {...mockProps} />);
    expect(screen.getByTestId('card')).toBeInTheDocument();
    expect(screen.getByText('Monte Carlo Risk Analysis')).toBeInTheDocument();
  });

  it('displays baseline property information', () => {
    render(<MonteCarloPanel {...mockProps} />);
    
    expect(screen.getByText('Baseline Analysis')).toBeInTheDocument();
    expect(screen.getByText('$1,000,000')).toBeInTheDocument();
    expect(screen.getByText('15.5%')).toBeInTheDocument();
  });

  it('allows users to configure simulation settings', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    // Test number of scenarios input
    const scenariosInput = screen.getByTestId('numScenarios');
    await user.clear(scenariosInput);
    await user.type(scenariosInput, '2000');
    
    expect(scenariosInput).toHaveValue(2000);
    
    // Test confidence level input
    const confidenceInput = screen.getByTestId('confidenceLevel');
    await user.clear(confidenceInput);
    await user.type(confidenceInput, '99');
    
    expect(confidenceInput).toHaveValue(99);
  });

  it('allows users to toggle advanced options', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    // Find checkboxes by their associated labels
    const correlationsCheckbox = screen.getByRole('checkbox', { name: /include parameter correlations/i });
    const marketCyclesCheckbox = screen.getByRole('checkbox', { name: /include market cycles/i });
    
    expect(correlationsCheckbox).toBeChecked();
    expect(marketCyclesCheckbox).toBeChecked();
    
    // Toggle correlations checkbox
    await user.click(correlationsCheckbox);
    expect(correlationsCheckbox).not.toBeChecked();
  });

  it('starts simulation when Run Simulation button is clicked', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    await user.click(runButton);
    
    expect(mockProps.onSimulationStart).toHaveBeenCalledWith({
      numScenarios: 1000,
      includeCorrelations: true,
      includeMarketCycles: true,
      confidenceLevel: 95,
    });
  });

  it('shows progress during simulation', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    
    // Start simulation
    await user.click(runButton);
    
    // Switch to progress tab to see progress
    const progressTab = screen.getByTestId('tab-progress');
    await user.click(progressTab);
    
    // Check that progress indicators appear
    await waitFor(() => {
      expect(screen.getByTestId('progress')).toBeInTheDocument();
    });
  });

  it('displays stop button during simulation', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    await user.click(runButton);
    
    // Should show stop button during simulation
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument();
    });
  });

  it('calls onSimulationComplete when simulation finishes', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    await user.click(runButton);
    
    // Wait for simulation to complete (mocked)
    await waitFor(() => {
      expect(mockProps.onSimulationComplete).toHaveBeenCalled();
    }, { timeout: 15000 });
  });

  it('shows simulation history when available', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    // Run a simulation first
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    await user.click(runButton);
    
    // Wait for completion
    await waitFor(() => {
      expect(mockProps.onSimulationComplete).toHaveBeenCalled();
    }, { timeout: 15000 });
    
    // Switch to history tab
    const historyTab = screen.getByTestId('tab-history');
    await user.click(historyTab);
    
    // Should show history
    await waitFor(() => {
      expect(screen.getByText(/run #1/i)).toBeInTheDocument();
    });
  });

  it('handles simulation errors gracefully', async () => {
    const user = userEvent.setup();
    
    // Mock simulation to throw error
    const originalConsoleError = console.error;
    console.error = jest.fn();
    
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    
    // Simulate an error by mocking a rejected promise
    jest.spyOn(global, 'setTimeout').mockImplementationOnce((callback: any) => {
      // Instead of successful completion, trigger an error
      throw new Error('Simulation failed');
    });
    
    await user.click(runButton);
    
    // Should handle the error
    await waitFor(() => {
      expect(mockProps.onSimulationError).toHaveBeenCalled();
    });
    
    console.error = originalConsoleError;
  });

  it('disables controls during simulation', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    const scenariosInput = screen.getByTestId('numScenarios');
    
    // Start simulation
    await user.click(runButton);
    
    // Controls should be disabled during simulation
    await waitFor(() => {
      expect(runButton).toBeDisabled();
      expect(scenariosInput).toBeDisabled();
    });
  });

  it('validates simulation settings', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    // Test minimum scenarios validation
    const scenariosInput = screen.getByTestId('numScenarios');
    await user.clear(scenariosInput);
    await user.type(scenariosInput, '50'); // Below minimum
    
    expect(scenariosInput).toHaveAttribute('min', '100');
    
    // Test maximum scenarios validation
    await user.clear(scenariosInput);
    await user.type(scenariosInput, '15000'); // Above maximum
    
    expect(scenariosInput).toHaveAttribute('max', '10000');
  });

  it('shows correct simulation stages', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    await user.click(runButton);
    
    // Switch to progress tab
    const progressTab = screen.getByTestId('tab-progress');
    await user.click(progressTab);
    
    // Should show initializing stage first
    await waitFor(() => {
      expect(screen.getByText(/setting up correlation matrix/i)).toBeInTheDocument();
    });
  });

  it('handles disabled state correctly', () => {
    render(<MonteCarloPanel {...mockProps} isDisabled={true} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    expect(runButton).toBeDisabled();
  });

  it('applies custom className', () => {
    const customClass = 'custom-panel-class';
    render(<MonteCarloPanel {...mockProps} className={customClass} />);
    
    const panel = screen.getByTestId('card');
    expect(panel).toHaveClass(customClass);
  });
});

describe('MonteCarloPanel Integration', () => {
  const mockProps = {
    propertyId: 'integration-test',
    baselineNPV: 2500000,
    baselineIRR: 18.2,
    onSimulationStart: jest.fn(),
    onSimulationComplete: jest.fn(),
    onSimulationError: jest.fn(),
  };

  it('maintains settings between tab switches', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    // Change settings
    const scenariosInput = screen.getByTestId('numScenarios');
    await user.clear(scenariosInput);
    await user.type(scenariosInput, '5000');
    
    // Switch tabs
    const progressTab = screen.getByTestId('tab-progress');
    await user.click(progressTab);
    
    const settingsTab = screen.getByTestId('tab-settings');
    await user.click(settingsTab);
    
    // Settings should be preserved
    expect(scenariosInput).toHaveValue(5000);
  });

  it('shows appropriate progress indicators', async () => {
    const user = userEvent.setup();
    render(<MonteCarloPanel {...mockProps} />);
    
    const runButton = screen.getByRole('button', { name: /run simulation/i });
    await user.click(runButton);
    
    // Switch to progress tab
    const progressTab = screen.getByTestId('tab-progress');
    await user.click(progressTab);
    
    // Should show progress elements
    await waitFor(() => {
      expect(screen.getByTestId('progress')).toBeInTheDocument();
      expect(screen.getByText(/scenarios:/i)).toBeInTheDocument();
      expect(screen.getByText(/time remaining:/i)).toBeInTheDocument();
    });
  });
});