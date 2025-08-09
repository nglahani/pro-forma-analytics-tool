/**
 * Tests for Textarea component
 * Comprehensive coverage for textarea functionality
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Textarea } from '../textarea';

describe('Textarea', () => {
  it('renders with default styling', () => {
    render(<Textarea data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveClass('flex', 'min-h-[60px]', 'w-full', 'rounded-md', 'border');
  });

  it('applies custom className', () => {
    render(<Textarea className="custom-textarea" data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveClass('custom-textarea');
  });

  it('forwards ref correctly', () => {
    const ref = React.createRef<HTMLTextAreaElement>();
    render(<Textarea ref={ref} />);
    
    expect(ref.current).toBeInstanceOf(HTMLTextAreaElement);
  });

  it('handles placeholder text', () => {
    render(<Textarea placeholder="Enter your message" data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('placeholder', 'Enter your message');
  });

  it('handles value prop', () => {
    render(<Textarea value="test value" readOnly data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveValue('test value');
  });

  it('handles onChange events', async () => {
    const user = userEvent.setup();
    const handleChange = jest.fn();
    
    render(<Textarea onChange={handleChange} data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    await user.type(textarea, 'hello world');
    
    expect(handleChange).toHaveBeenCalledTimes(11); // Once for each character
  });

  it('handles onFocus and onBlur events', async () => {
    const user = userEvent.setup();
    const handleFocus = jest.fn();
    const handleBlur = jest.fn();
    
    render(<Textarea onFocus={handleFocus} onBlur={handleBlur} data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    await user.click(textarea);
    expect(handleFocus).toHaveBeenCalledTimes(1);
    
    await user.tab(); // Move focus away
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Textarea disabled data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toBeDisabled();
    expect(textarea).toHaveClass('disabled:cursor-not-allowed', 'disabled:opacity-50');
  });

  it('is required when required prop is true', () => {
    render(<Textarea required data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toBeRequired();
  });

  it('handles rows and cols attributes', () => {
    render(<Textarea rows={10} cols={50} data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('rows', '10');
    expect(textarea).toHaveAttribute('cols', '50');
  });

  it('handles maxLength and minLength', () => {
    render(
      <Textarea 
        maxLength={100} 
        minLength={10} 
        data-testid="textarea" 
      />
    );
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('maxLength', '100');
    expect(textarea).toHaveAttribute('minLength', '10');
  });

  it('handles resize attribute', () => {
    render(
      <Textarea 
        style={{ resize: 'vertical' }}
        data-testid="textarea" 
      />
    );
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveStyle('resize: vertical');
  });

  it('supports accessibility attributes', () => {
    render(
      <Textarea
        aria-label="Message input"
        aria-describedby="message-help"
        aria-invalid="true"
        data-testid="textarea"
      />
    );
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('aria-label', 'Message input');
    expect(textarea).toHaveAttribute('aria-describedby', 'message-help');
    expect(textarea).toHaveAttribute('aria-invalid', 'true');
  });

  it('handles keyboard events', () => {
    const handleKeyDown = jest.fn();
    const handleKeyUp = jest.fn();
    
    render(
      <Textarea 
        onKeyDown={handleKeyDown} 
        onKeyUp={handleKeyUp} 
        data-testid="textarea" 
      />
    );
    
    const textarea = screen.getByTestId('textarea');
    fireEvent.keyDown(textarea, { key: 'Enter' });
    fireEvent.keyUp(textarea, { key: 'Enter' });
    
    expect(handleKeyDown).toHaveBeenCalledTimes(1);
    expect(handleKeyUp).toHaveBeenCalledTimes(1);
  });

  it('handles defaultValue', () => {
    render(<Textarea defaultValue="initial value" data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveValue('initial value');
  });

  it('can be read-only', () => {
    render(<Textarea readOnly value="readonly value" data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('readOnly');
    expect(textarea).toHaveValue('readonly value');
  });

  it('supports form validation', () => {
    render(
      <Textarea 
        required
        minLength={10}
        maxLength={100}
        data-testid="textarea"
      />
    );
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toBeRequired();
    expect(textarea).toHaveAttribute('minLength', '10');
    expect(textarea).toHaveAttribute('maxLength', '100');
  });

  it('handles custom attributes', () => {
    render(
      <Textarea
        name="message"
        id="message-input"
        autoComplete="off"
        spellCheck="false"
        data-testid="textarea"
      />
    );
    
    const textarea = screen.getByTestId('textarea');
    expect(textarea).toHaveAttribute('name', 'message');
    expect(textarea).toHaveAttribute('id', 'message-input');
    expect(textarea).toHaveAttribute('autoComplete', 'off');
    expect(textarea).toHaveAttribute('spellCheck', 'false');
  });

  it('handles multiline text input', async () => {
    const user = userEvent.setup();
    render(<Textarea data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    const multilineText = 'Line 1\nLine 2\nLine 3';
    
    await user.type(textarea, multilineText);
    expect(textarea).toHaveValue(multilineText);
  });

  it('maintains focus states correctly', async () => {
    const user = userEvent.setup();
    render(<Textarea data-testid="textarea" />);
    
    const textarea = screen.getByTestId('textarea');
    
    await user.click(textarea);
    expect(textarea).toHaveFocus();
    
    await user.tab();
    expect(textarea).not.toHaveFocus();
  });
});