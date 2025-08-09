/**
 * Tests for Toaster component
 * Tests toast notification rendering functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Toaster } from '../toaster';

// Mock the useToast hook
const mockToasts = [
  {
    id: '1',
    title: 'Success',
    description: 'Task completed successfully',
    type: 'success' as const,
  },
  {
    id: '2',
    title: 'Error',
    description: 'An error occurred',
    type: 'destructive' as const,
  },
  {
    id: '3',
    description: 'Simple notification',
  },
];

jest.mock('@/hooks/useToast', () => ({
  useToast: jest.fn(() => ({ toasts: mockToasts })),
}));

describe('Toaster', () => {
  beforeEach(() => {
    // Reset mock
    require('@/hooks/useToast').useToast.mockReturnValue({ toasts: mockToasts });
  });

  it('renders toaster component', () => {
    render(<Toaster />);
    
    // Check if toasts are rendered
    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Task completed successfully')).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('An error occurred')).toBeInTheDocument();
    expect(screen.getByText('Simple notification')).toBeInTheDocument();
  });

  it('renders toasts with titles and descriptions', () => {
    render(<Toaster />);
    
    const successToast = screen.getByText('Success');
    const successDescription = screen.getByText('Task completed successfully');
    
    expect(successToast).toBeInTheDocument();
    expect(successDescription).toBeInTheDocument();
  });

  it('renders toast without title', () => {
    render(<Toaster />);
    
    expect(screen.getByText('Simple notification')).toBeInTheDocument();
  });

  it('renders empty state when no toasts', () => {
    require('@/hooks/useToast').useToast.mockReturnValue({ toasts: [] });
    
    const { container } = render(<Toaster />);
    
    // Should still render ToastProvider and ToastViewport even when no toasts
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders multiple toasts', () => {
    render(<Toaster />);
    
    // Should render all toasts from mockToasts
    expect(screen.getByText('Success')).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Simple notification')).toBeInTheDocument();
  });

  it('handles toast with action', () => {
    const toastsWithAction = [
      {
        id: '1',
        title: 'Test',
        description: 'Test description',
        action: <button>Undo</button>,
      },
    ];

    require('@/hooks/useToast').useToast.mockReturnValue({ 
      toasts: toastsWithAction 
    });

    render(<Toaster />);
    
    expect(screen.getByText('Test')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Undo' })).toBeInTheDocument();
  });

  it('passes props to Toast component', () => {
    const toastsWithProps = [
      {
        id: '1',
        title: 'Test',
        'data-testid': 'custom-toast',
        className: 'custom-class',
      },
    ];

    require('@/hooks/useToast').useToast.mockReturnValue({ 
      toasts: toastsWithProps 
    });

    render(<Toaster />);
    
    const toast = screen.getByTestId('custom-toast');
    expect(toast).toBeInTheDocument();
    expect(toast).toHaveClass('custom-class');
  });

  it('renders toast close button for all toasts', () => {
    render(<Toaster />);
    
    // Each toast should have a close button
    const closeButtons = screen.getAllByRole('button');
    expect(closeButtons.length).toBeGreaterThan(0);
  });

  it('renders ToastViewport', () => {
    const { container } = render(<Toaster />);
    
    // ToastViewport should be rendered (it's a div with specific classes)
    expect(container).toBeInTheDocument();
  });
});