/**
 * Tests for useToast Hook
 * Comprehensive coverage for toast notification system
 */

import { renderHook, act } from '@testing-library/react';
import { useToast } from '../useToast';

// Mock setTimeout and clearTimeout for predictable testing
jest.useFakeTimers();

describe('useToast', () => {
  beforeEach(() => {
    jest.clearAllTimers();
    // Reset the module state between tests
    jest.resetModules();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  it('should initialize with empty toasts', () => {
    const { result } = renderHook(() => useToast());

    expect(result.current.toasts).toEqual([]);
  });

  it('should add a toast', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.toast({
        title: 'Test Toast',
        description: 'This is a test toast',
      });
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].title).toBe('Test Toast');
    expect(result.current.toasts[0].description).toBe('This is a test toast');
  });

  it('should generate unique IDs for toasts', () => {
    const { result } = renderHook(() => useToast());

    let toast1Id: string, toast2Id: string;

    act(() => {
      const toast1 = result.current.toast({ title: 'Toast 1' });
      toast1Id = toast1.id;
      const toast2 = result.current.toast({ title: 'Toast 2' });
      toast2Id = toast2.id;
    });

    // Due to TOAST_LIMIT = 1, only the latest toast remains
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].title).toBe('Toast 2');
    expect(toast1Id).not.toBe(toast2Id);
  });

  it('should respect toast limit', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.toast({ title: 'Toast 1' });
      result.current.toast({ title: 'Toast 2' });
    });

    // With TOAST_LIMIT = 1, should only show the most recent toast
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].title).toBe('Toast 2');
  });

  it('should dismiss a specific toast', () => {
    const { result } = renderHook(() => useToast());

    let toastId: string;

    act(() => {
      const toast = result.current.toast({
        title: 'Test Toast',
        description: 'This is a test toast',
      });
      toastId = toast.id;
    });

    expect(result.current.toasts).toHaveLength(1);

    act(() => {
      result.current.dismiss(toastId);
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].open).toBe(false);
  });

  it('should dismiss all toasts when no ID provided', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.toast({ title: 'Toast 1' });
    });

    expect(result.current.toasts).toHaveLength(1);

    act(() => {
      result.current.dismiss();
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].open).toBe(false);
  });

  it('should remove toast after delay', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.toast({ title: 'Test Toast' });
    });

    expect(result.current.toasts).toHaveLength(1);

    act(() => {
      result.current.dismiss();
    });

    expect(result.current.toasts[0].open).toBe(false);

    // Fast-forward time to trigger removal
    act(() => {
      jest.advanceTimersByTime(1000000);
    });

    expect(result.current.toasts).toHaveLength(0);
  });

  it('should handle update toast action', () => {
    const { result } = renderHook(() => useToast());

    let toastId: string;

    act(() => {
      const toast = result.current.toast({
        title: 'Original Title',
        description: 'Original Description',
      });
      toastId = toast.id;
    });

    expect(result.current.toasts[0].title).toBe('Original Title');

    // Manually trigger an update (testing internal state management)
    act(() => {
      // Since there's no direct update method exposed, we test through dismiss/add cycle
      result.current.dismiss(toastId);
      result.current.toast({
        id: toastId,
        title: 'Updated Title',
        description: 'Updated Description',
      });
    });

    expect(result.current.toasts).toHaveLength(1);
  });

  it('should handle different toast variants', () => {
    const { result } = renderHook(() => useToast());

    const variants = ['default', 'destructive'] as const;

    variants.forEach((variant) => {
      act(() => {
        result.current.toast({
          title: `${variant} Toast`,
          variant,
        });
      });
    });

    // Due to toast limit, only the last one should remain
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].variant).toBe('destructive');
  });

  it('should handle toast with action', () => {
    const { result } = renderHook(() => useToast());
    const mockAction = { action: 'test-action' };

    act(() => {
      result.current.toast({
        title: 'Toast with Action',
        action: mockAction as any,
      });
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].action).toBe(mockAction);
  });

  it('should return toast object with ID when creating', () => {
    const { result } = renderHook(() => useToast());

    let returnedToast: any;

    act(() => {
      returnedToast = result.current.toast({
        title: 'Test Toast',
      });
    });

    expect(returnedToast).toBeDefined();
    expect(returnedToast.id).toBeDefined();
    expect(returnedToast.dismiss).toBeDefined();
    expect(returnedToast.update).toBeDefined();
  });

  it('should allow updating returned toast object', () => {
    const { result } = renderHook(() => useToast());

    let toastObj: any;

    act(() => {
      toastObj = result.current.toast({
        title: 'Original Title',
        description: 'Original Description',
      });
    });

    expect(result.current.toasts[0].title).toBe('Original Title');

    act(() => {
      toastObj.update({
        title: 'Updated Title',
        description: 'Updated Description',
      });
    });

    expect(result.current.toasts[0].title).toBe('Updated Title');
    expect(result.current.toasts[0].description).toBe('Updated Description');
  });

  it('should allow dismissing returned toast object', () => {
    const { result } = renderHook(() => useToast());

    let toastObj: any;

    act(() => {
      toastObj = result.current.toast({
        title: 'Test Toast',
      });
    });

    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].open).toBe(true);

    act(() => {
      toastObj.dismiss();
    });

    expect(result.current.toasts[0].open).toBe(false);
  });

  it('should handle multiple rapid toast creations', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      // Add multiple toasts rapidly
      for (let i = 0; i < 5; i++) {
        result.current.toast({ title: `Toast ${i}` });
      }
    });

    // Due to toast limit, should only show the last one
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].title).toBe('Toast 4');
  });

  it('should handle edge case with invalid toast ID for dismiss', () => {
    const { result } = renderHook(() => useToast());

    act(() => {
      result.current.toast({ title: 'Test Toast' });
    });

    expect(result.current.toasts).toHaveLength(1);

    // Try to dismiss with non-existent ID
    act(() => {
      result.current.dismiss('non-existent-id');
    });

    // Toast should still be there and unaffected
    expect(result.current.toasts).toHaveLength(1);
    expect(result.current.toasts[0].open).toBe(true);
  });

  it('should generate sequential IDs', () => {
    const { result } = renderHook(() => useToast());

    const ids: string[] = [];

    act(() => {
      for (let i = 0; i < 3; i++) {
        const toast = result.current.toast({ title: `Toast ${i}` });
        ids.push(toast.id);
      }
    });

    // IDs should be different and sequential
    const numericIds = ids.map(Number);
    expect(numericIds[0]).toBeLessThan(numericIds[1]);
    expect(numericIds[1]).toBeLessThan(numericIds[2]);
  });

  it('should preserve toast properties', () => {
    const { result } = renderHook(() => useToast());

    const toastProps = {
      title: 'Test Title',
      description: 'Test Description',
      variant: 'destructive' as const,
      duration: 5000,
    };

    act(() => {
      result.current.toast(toastProps);
    });

    const createdToast = result.current.toasts[0];
    expect(createdToast.title).toBe(toastProps.title);
    expect(createdToast.description).toBe(toastProps.description);
    expect(createdToast.variant).toBe(toastProps.variant);
    expect(createdToast.duration).toBe(toastProps.duration);
  });
});