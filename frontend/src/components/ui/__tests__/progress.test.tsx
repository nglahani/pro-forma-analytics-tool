/**
 * Tests for Progress component
 * Comprehensive coverage for Radix UI Progress functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Progress } from '../progress';

describe('Progress', () => {
  it('renders with default styling', () => {
    render(<Progress data-testid="progress" />);
    
    const progress = screen.getByTestId('progress');
    expect(progress).toBeInTheDocument();
    expect(progress).toHaveClass('relative', 'h-4', 'w-full', 'overflow-hidden', 'rounded-full', 'bg-secondary');
  });

  it('renders with zero value by default', () => {
    render(<Progress data-testid="progress" />);
    
    const indicator = screen.getByTestId('progress').firstChild as HTMLElement;
    expect(indicator).toHaveStyle('transform: translateX(-100%)');
  });

  it('renders with specific value', () => {
    render(<Progress value={50} data-testid="progress" />);
    
    const indicator = screen.getByTestId('progress').firstChild as HTMLElement;
    expect(indicator).toHaveStyle('transform: translateX(-50%)');
  });

  it('handles different progress values', () => {
    const values = [0, 25, 50, 75, 100];
    
    values.forEach((value, index) => {
      const { unmount } = render(<Progress value={value} data-testid={`progress-${index}`} />);
      const progress = screen.getByTestId(`progress-${index}`);
      const indicator = progress.firstChild as HTMLElement;
      
      const expectedTransform = `translateX(-${100 - value}%)`;
      expect(indicator).toHaveStyle(`transform: ${expectedTransform}`);
      unmount();
    });
  });

  it('applies custom className', () => {
    render(<Progress className="custom-progress" data-testid="progress" />);
    
    const progress = screen.getByTestId('progress');
    expect(progress).toHaveClass('custom-progress');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLDivElement>();
    render(<Progress ref={ref} value={50} />);
    
    expect(ref.current).toBeInstanceOf(HTMLDivElement);
  });

  it('supports accessibility attributes', () => {
    render(
      <Progress 
        value={75}
        aria-label="Loading progress"
        aria-describedby="progress-description"
        data-testid="progress"
      />
    );
    
    const progress = screen.getByTestId('progress');
    expect(progress).toHaveAttribute('aria-label', 'Loading progress');
    expect(progress).toHaveAttribute('aria-describedby', 'progress-description');
  });

  it('accepts max and value props', () => {
    render(<Progress value={30} max={60} data-testid="progress" />);
    
    const progress = screen.getByTestId('progress');
    const indicator = progress.firstChild as HTMLElement;
    // With value 30, the indicator should be positioned at 70% from left (30% fill)
    expect(indicator).toHaveStyle('transform: translateX(-70%)');
  });

  it('has correct ARIA role', () => {
    render(<Progress value={50} data-testid="progress" />);
    
    const progress = screen.getByTestId('progress');
    expect(progress).toHaveAttribute('role', 'progressbar');
  });

  it('handles edge cases for value', () => {
    // Test with negative value
    const { rerender } = render(<Progress value={-10} data-testid="progress" />);
    let indicator = screen.getByTestId('progress').firstChild as HTMLElement;
    expect(indicator).toHaveStyle('transform: translateX(-110%)');
    
    // Test with value over 100
    rerender(<Progress value={120} data-testid="progress" />);
    indicator = screen.getByTestId('progress').firstChild as HTMLElement;
    expect(indicator).toHaveStyle('transform: translateX(--20%)');
  });

  it('displays progress indicator with correct styling', () => {
    render(<Progress value={60} data-testid="progress" />);
    
    const progress = screen.getByTestId('progress');
    const indicator = progress.firstChild as HTMLElement;
    
    expect(indicator).toHaveClass('h-full', 'w-full', 'flex-1', 'bg-primary', 'transition-all');
  });

  it('supports custom styling on indicator', () => {
    const { container } = render(
      <Progress 
        value={40} 
        data-testid="progress"
        style={{ '--progress-color': 'red' } as React.CSSProperties}
      />
    );
    
    const progress = screen.getByTestId('progress');
    expect(progress).toHaveStyle('--progress-color: red');
  });

  it('works with controlled updates', () => {
    const { rerender } = render(<Progress value={20} data-testid="progress" />);
    
    let indicator = screen.getByTestId('progress').firstChild as HTMLElement;
    expect(indicator).toHaveStyle('transform: translateX(-80%)');
    
    rerender(<Progress value={80} data-testid="progress" />);
    indicator = screen.getByTestId('progress').firstChild as HTMLElement;
    expect(indicator).toHaveStyle('transform: translateX(-20%)');
  });

  it('handles undefined value gracefully', () => {
    render(<Progress value={undefined} data-testid="progress" />);
    
    const indicator = screen.getByTestId('progress').firstChild as HTMLElement;
    expect(indicator).toHaveStyle('transform: translateX(-100%)');
  });
});