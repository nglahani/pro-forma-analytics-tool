/**
 * Tests for Label component
 * Comprehensive coverage for Radix UI Label functionality
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { Label } from '../label';

describe('Label', () => {
  it('renders with default styling', () => {
    render(<Label data-testid="label">Label text</Label>);
    
    const label = screen.getByTestId('label');
    expect(label).toBeInTheDocument();
    expect(label).toHaveClass('text-sm', 'font-medium', 'leading-none');
  });

  it('displays text content correctly', () => {
    render(<Label>My Label</Label>);
    
    expect(screen.getByText('My Label')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    render(<Label className="custom-label" data-testid="label">Content</Label>);
    
    const label = screen.getByTestId('label');
    expect(label).toHaveClass('custom-label');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLLabelElement>();
    render(<Label ref={ref}>Label with ref</Label>);
    
    expect(ref.current).toBeInstanceOf(HTMLLabelElement);
  });

  it('supports htmlFor attribute', () => {
    render(<Label htmlFor="input-id" data-testid="label">Input Label</Label>);
    
    const label = screen.getByTestId('label');
    expect(label).toHaveAttribute('for', 'input-id');
  });

  it('supports custom attributes', () => {
    render(
      <Label 
        id="custom-id" 
        data-custom="value" 
        data-testid="label"
      >
        Custom Label
      </Label>
    );
    
    const label = screen.getByTestId('label');
    expect(label).toHaveAttribute('id', 'custom-id');
    expect(label).toHaveAttribute('data-custom', 'value');
  });

  it('renders with nested content', () => {
    render(
      <Label data-testid="label">
        <span>Icon</span>
        <span>Text</span>
      </Label>
    );
    
    expect(screen.getByText('Icon')).toBeInTheDocument();
    expect(screen.getByText('Text')).toBeInTheDocument();
  });

  it('supports accessibility attributes', () => {
    render(
      <Label 
        aria-label="Accessible label"
        aria-describedby="help-text"
        data-testid="label"
      >
        Form Label
      </Label>
    );
    
    const label = screen.getByTestId('label');
    expect(label).toHaveAttribute('aria-label', 'Accessible label');
    expect(label).toHaveAttribute('aria-describedby', 'help-text');
  });

  it('handles peer-disabled styling', () => {
    render(<Label data-testid="label">Disabled peer label</Label>);
    
    const label = screen.getByTestId('label');
    expect(label).toHaveClass('peer-disabled:cursor-not-allowed', 'peer-disabled:opacity-70');
  });

  it('integrates with form inputs', () => {
    render(
      <div>
        <Label htmlFor="username">Username</Label>
        <input type="text" id="username" />
      </div>
    );
    
    const label = screen.getByText('Username');
    const input = screen.getByRole('textbox');
    
    expect(label).toHaveAttribute('for', 'username');
    expect(input).toHaveAttribute('id', 'username');
  });
});