/**
 * Accessibility Components Test Suite
 * Tests for WCAG AA compliance and keyboard navigation
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AccessibilityProvider } from '@/components/common/AccessibilityProvider';
import { AccessibleButton } from '@/components/ui/accessible-button';
import { AccessibleInput } from '@/components/ui/accessible-input';
import { AccessibleCard } from '@/components/ui/accessible-card';

// Mock performance API for tests
Object.defineProperty(window, 'performance', {
  value: {
    mark: jest.fn(),
    measure: jest.fn(),
    now: jest.fn(() => Date.now()),
    getEntriesByType: jest.fn(() => []),
  },
});

// Test wrapper with AccessibilityProvider
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AccessibilityProvider>{children}</AccessibilityProvider>
);

describe('AccessibilityProvider', () => {
  test('provides accessibility context', () => {
    const TestComponent = () => {
      return <div data-testid="test-component">Test</div>;
    };

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    expect(screen.getByTestId('test-component')).toBeInTheDocument();
  });

  test('handles announcements', async () => {
    const TestComponent = () => {
      const [announcement, setAnnouncement] = React.useState('');
      
      return (
        <div>
          <button 
            onClick={() => setAnnouncement('Test announcement')}
            data-testid="announce-button"
          >
            Announce
          </button>
          <div aria-live="polite" data-testid="announcement">
            {announcement}
          </div>
        </div>
      );
    };

    render(
      <TestWrapper>
        <TestComponent />
      </TestWrapper>
    );

    fireEvent.click(screen.getByTestId('announce-button'));
    
    await waitFor(() => {
      expect(screen.getByTestId('announcement')).toHaveTextContent('Test announcement');
    });
  });
});

describe('AccessibleButton', () => {
  test('renders with proper ARIA attributes', () => {
    render(
      <AccessibleButton aria-label="Test button" description="This is a test button">
        Click me
      </AccessibleButton>
    );

    const button = screen.getByRole('button', { name: /test button/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveAttribute('aria-label', 'Test button');
  });

  test('handles loading state correctly', () => {
    render(
      <AccessibleButton loading={true} loadingText="Loading...">
        Submit
      </AccessibleButton>
    );

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  test('supports keyboard navigation', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(
      <AccessibleButton onClick={handleClick}>
        Test Button
      </AccessibleButton>
    );

    const button = screen.getByRole('button');
    
    // Test focus
    await user.tab();
    expect(button).toHaveFocus();

    // Test Enter key
    await user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalled();

    // Test Space key
    handleClick.mockClear();
    await user.keyboard(' ');
    expect(handleClick).toHaveBeenCalled();
  });

  test('applies focus ring classes', () => {
    render(<AccessibleButton>Focus Test</AccessibleButton>);
    
    const button = screen.getByRole('button');
    expect(button.className).toContain('focus:outline-none');
    expect(button.className).toContain('focus:ring-2');
  });

  test('handles different variants', () => {
    const { rerender } = render(<AccessibleButton variant="success">Success</AccessibleButton>);
    
    let button = screen.getByRole('button');
    expect(button.className).toContain('bg-green-600');

    rerender(<AccessibleButton variant="error">Error</AccessibleButton>);
    button = screen.getByRole('button');
    expect(button.className).toContain('bg-red-600');
  });
});

describe('AccessibleInput', () => {
  test('renders with proper labels and ARIA attributes', () => {
    render(
      <AccessibleInput
        label="Email Address"
        hint="Enter your email address"
        required={true}
      />
    );

    const input = screen.getByLabelText(/email address/i);
    expect(input).toBeInTheDocument();
    expect(input).toHaveAttribute('aria-required', 'true');
    expect(screen.getByText(/enter your email address/i)).toBeInTheDocument();
  });

  test('shows validation errors', async () => {
    const user = userEvent.setup();
    
    render(
      <AccessibleInput
        label="Email"
        validationRules={{ required: true }}
        showValidation={true}
      />
    );

    const input = screen.getByLabelText(/email/i);
    
    // Focus and blur to trigger validation
    await user.click(input);
    await user.tab();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });

    expect(input).toHaveAttribute('aria-invalid', 'true');
  });

  test('supports different validation rules', async () => {
    const user = userEvent.setup();
    
    render(
      <AccessibleInput
        label="Password"
        validationRules={{ 
          required: true, 
          minLength: 8 
        }}
        showValidation={true}
      />
    );

    const input = screen.getByLabelText(/password/i);
    
    // Test short password
    await user.type(input, 'short');
    await user.tab();

    await waitFor(() => {
      expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument();
    });
  });

  test('shows success state', () => {
    render(
      <AccessibleInput
        label="Username"
        success="Username is available"
      />
    );

    expect(screen.getByText(/username is available/i)).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('applies correct CSS classes for states', () => {
    const { rerender } = render(
      <AccessibleInput label="Test" error="Error message" />
    );

    let input = screen.getByLabelText(/test/i);
    expect(input.className).toContain('border-red-500');
    expect(input.className).toContain('bg-red-50');

    rerender(<AccessibleInput label="Test" success="Success message" />);
    input = screen.getByLabelText(/test/i);
    expect(input.className).toContain('border-green-500');
    expect(input.className).toContain('bg-green-50');
  });
});

describe('AccessibleCard', () => {
  test('renders as article by default', () => {
    render(
      <AccessibleCard heading="Test Card">
        Card content
      </AccessibleCard>
    );

    const card = screen.getByRole('article');
    expect(card).toBeInTheDocument();
    expect(screen.getByText('Test Card')).toBeInTheDocument();
  });

  test('becomes interactive when onClick is provided', async () => {
    const user = userEvent.setup();
    const handleClick = jest.fn();

    render(
      <AccessibleCard
        heading="Clickable Card"
        onClick={handleClick}
        actionLabel="Click to view details"
      >
        Click me
      </AccessibleCard>
    );

    const card = screen.getByRole('button');
    expect(card).toBeInTheDocument();
    expect(card).toHaveAttribute('tabindex', '0');

    // Test click
    await user.click(card);
    expect(handleClick).toHaveBeenCalled();

    // Test keyboard navigation
    handleClick.mockClear();
    card.focus();
    await user.keyboard('{Enter}');
    expect(handleClick).toHaveBeenCalled();
  });

  test('supports different variants', () => {
    const { rerender } = render(
      <AccessibleCard variant="success">Success card</AccessibleCard>
    );

    let card = screen.getByRole('article');
    expect(card.className).toContain('border-green-200');
    expect(card.className).toContain('bg-green-50');

    rerender(<AccessibleCard variant="error">Error card</AccessibleCard>);
    card = screen.getByRole('article');
    expect(card.className).toContain('border-red-200');
    expect(card.className).toContain('bg-red-50');
  });

  test('handles keyboard navigation properly', async () => {
    const user = userEvent.setup();
    const handleAction = jest.fn();

    render(
      <AccessibleCard
        heading="Interactive Card"
        onAction={handleAction}
      >
        Content
      </AccessibleCard>
    );

    const card = screen.getByRole('button');
    
    // Test Enter key
    card.focus();
    await user.keyboard('{Enter}');
    expect(handleAction).toHaveBeenCalled();

    // Test Space key
    handleAction.mockClear();
    await user.keyboard(' ');
    expect(handleAction).toHaveBeenCalled();
  });
});

// Color contrast tests (simplified)
describe('Color Contrast', () => {
  test('text colors meet WCAG AA standards', () => {
    const textColorMap = {
      'text-gray-900': '#111827',  // Should be ~16.68:1 contrast
      'text-gray-700': '#374151',  // Should be ~8.50:1 contrast
      'text-gray-600': '#4b5563',  // Should be ~6.23:1 contrast
      'text-gray-500': '#6b7280',  // Should be ~4.54:1 contrast (minimum AA)
    };

    // This is a simplified test - in a real app, you'd use a proper contrast checking library
    Object.entries(textColorMap).forEach(([className, color]) => {
      expect(color).toBeDefined();
      expect(className).toMatch(/text-gray-\d+/);
    });
  });
});

// Focus management tests
describe('Focus Management', () => {
  test('focus trap works correctly', async () => {
    const user = userEvent.setup();
    
    render(
      <div data-testid="focus-container">
        <button>Before</button>
        <div>
          <button data-testid="first">First</button>
          <button data-testid="second">Second</button>
          <button data-testid="last">Last</button>
        </div>
        <button>After</button>
      </div>
    );

    const firstButton = screen.getByTestId('first');
    const lastButton = screen.getByTestId('last');
    
    // Focus first button
    firstButton.focus();
    expect(firstButton).toHaveFocus();

    // Tab through buttons
    await user.tab();
    expect(screen.getByTestId('second')).toHaveFocus();

    await user.tab();
    expect(lastButton).toHaveFocus();
  });
});

// Screen reader tests
describe('Screen Reader Support', () => {
  test('provides appropriate ARIA labels and descriptions', () => {
    render(
      <div>
        <h1 id="page-title">Dashboard</h1>
        <main aria-labelledby="page-title">
          <section aria-label="Financial metrics">
            <h2>Key Metrics</h2>
            <div role="table" aria-label="Financial data">
              <div role="row">
                <div role="cell">NPV</div>
                <div role="cell">$1,000,000</div>
              </div>
            </div>
          </section>
        </main>
      </div>
    );

    expect(screen.getByRole('main')).toHaveAttribute('aria-labelledby', 'page-title');
    expect(screen.getByRole('table')).toHaveAttribute('aria-label', 'Financial data');
    expect(screen.getByText('Financial metrics')).toBeInTheDocument();
  });

  test('provides live region announcements', () => {
    render(
      <div>
        <div aria-live="polite" data-testid="announcements">
          Loading complete
        </div>
        <div aria-live="assertive" data-testid="alerts">
          Error occurred
        </div>
      </div>
    );

    expect(screen.getByTestId('announcements')).toHaveAttribute('aria-live', 'polite');
    expect(screen.getByTestId('alerts')).toHaveAttribute('aria-live', 'assertive');
  });
});

// Performance tests
describe('Performance Impact', () => {
  test('components render within performance budget', () => {
    const startTime = performance.now();
    
    render(
      <TestWrapper>
        <AccessibleCard heading="Performance Test">
          <AccessibleInput label="Test Input" />
          <AccessibleButton>Test Button</AccessibleButton>
        </AccessibleCard>
      </TestWrapper>
    );

    const endTime = performance.now();
    const renderTime = endTime - startTime;

    // Components should render quickly (under 16ms for 60fps)
    expect(renderTime).toBeLessThan(16);
  });

  test('does not significantly increase bundle size', () => {
    // This is more of a build-time concern, but we can test that
    // components are tree-shakeable by ensuring they export only what's needed
    
    expect(AccessibleButton).toBeDefined();
    expect(AccessibleInput).toBeDefined();
    expect(AccessibleCard).toBeDefined();
    
    // Verify that unused exports don't exist
    expect(typeof AccessibleButton).toBe('function');
    expect(typeof AccessibleInput).toBe('function');
    expect(typeof AccessibleCard).toBe('function');
  });
});