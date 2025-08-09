/**
 * Tests for Input component
 * Comprehensive coverage for input functionality, types, and interactions
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Input } from '../input';

describe('Input', () => {
  it('renders with default styling', () => {
    render(<Input data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toBeInTheDocument();
    expect(input).toHaveClass('flex', 'h-9', 'w-full', 'rounded-md', 'border');
  });

  it('renders with different input types', () => {
    const types = ['text', 'email', 'password', 'number', 'tel', 'url'] as const;
    
    types.forEach((type) => {
      const { unmount } = render(<Input type={type} data-testid={`${type}-input`} />);
      const input = screen.getByTestId(`${type}-input`);
      expect(input).toHaveAttribute('type', type);
      unmount();
    });
  });

  it('applies custom className', () => {
    render(<Input className="custom-input" data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toHaveClass('custom-input');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLInputElement>();
    render(<Input ref={ref} />);
    
    expect(ref.current).toBeInstanceOf(HTMLInputElement);
  });

  it('handles placeholder text', () => {
    render(<Input placeholder="Enter your name" data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('placeholder', 'Enter your name');
  });

  it('handles value prop', () => {
    render(<Input value="test value" readOnly data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toHaveValue('test value');
  });

  it('handles onChange events', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();
    
    render(<Input onChange={handleChange} data-testid="input" />);
    
    const input = screen.getByTestId('input');
    await user.type(input, 'hello');
    
    expect(handleChange).toHaveBeenCalledTimes(5); // Once for each character
  });

  it('handles onFocus and onBlur events', async () => {
    const user = userEvent.setup();
    const handleFocus = jest.fn();
    const handleBlur = jest.fn();
    
    render(<Input onFocus={handleFocus} onBlur={handleBlur} data-testid="input" />);
    
    const input = screen.getByTestId('input');
    await user.click(input);
    expect(handleFocus).toHaveBeenCalledTimes(1);
    
    await user.tab(); // Move focus away
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Input disabled data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50');
  });

  it('is required when required prop is true', () => {
    render(<Input required data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toBeRequired();
  });

  it('handles keyboard events', () => {
    const handleKeyDown = jest.fn();
    const handleKeyUp = jest.fn();
    
    render(<Input onKeyDown={handleKeyDown} onKeyUp={handleKeyUp} data-testid="input" />);
    
    const input = screen.getByTestId('input');
    fireEvent.keyDown(input, { key: 'Enter' });
    fireEvent.keyUp(input, { key: 'Enter' });
    
    expect(handleKeyDown).toHaveBeenCalledTimes(1);
    expect(handleKeyUp).toHaveBeenCalledTimes(1);
  });

  it('handles different input attributes', () => {
    render(
      <Input
        name="test-name"
        id="test-id"
        autoComplete="email"
        maxLength={50}
        minLength={3}
        data-testid="input"
      />
    );
    
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('name', 'test-name');
    expect(input).toHaveAttribute('id', 'test-id');
    expect(input).toHaveAttribute('autoComplete', 'email');
    expect(input).toHaveAttribute('maxLength', '50');
    expect(input).toHaveAttribute('minLength', '3');
  });

  it('handles number input with min/max', () => {
    render(<Input type="number" min={0} max={100} data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('type', 'number');
    expect(input).toHaveAttribute('min', '0');
    expect(input).toHaveAttribute('max', '100');
  });

  it('handles file input type', () => {
    render(<Input type="file" accept=".pdf,.doc" data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('type', 'file');
    expect(input).toHaveAttribute('accept', '.pdf,.doc');
  });

  it('handles form validation states', () => {
    render(
      <Input
        type="email"
        pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
        title="Please enter a valid email address"
        data-testid="input"
      />
    );
    
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('pattern');
    expect(input).toHaveAttribute('title', 'Please enter a valid email address');
  });

  it('supports aria attributes for accessibility', () => {
    render(
      <Input
        aria-label="Search input"
        aria-describedby="search-help"
        aria-invalid="true"
        data-testid="input"
      />
    );
    
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('aria-label', 'Search input');
    expect(input).toHaveAttribute('aria-describedby', 'search-help');
    expect(input).toHaveAttribute('aria-invalid', 'true');
  });

  it('handles defaultValue', () => {
    render(<Input defaultValue="initial value" data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toHaveValue('initial value');
  });

  it('can be read-only', () => {
    render(<Input readOnly value="readonly value" data-testid="input" />);
    
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('readOnly');
    expect(input).toHaveValue('readonly value');
  });
});