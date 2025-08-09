/**
 * Accessibility Provider
 * Global accessibility context and utilities
 */

'use client';

import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';
import { keyboard, screenReader } from '@/lib/accessibility';

interface AccessibilityContextType {
  // Announcements
  announce: (message: string, priority?: 'polite' | 'assertive') => void;
  
  // Focus management
  focusElement: (selector: string) => boolean;
  trapFocus: (containerRef: React.RefObject<HTMLElement>) => () => void;
  
  // Skip links
  registerSkipLink: (id: string, label: string, target: string) => void;
  unregisterSkipLink: (id: string) => void;
  
  // Preferences
  reducedMotion: boolean;
  highContrast: boolean;
  setReducedMotion: (value: boolean) => void;
  setHighContrast: (value: boolean) => void;
  
  // Keyboard navigation
  enableKeyboardNavigation: boolean;
  setEnableKeyboardNavigation: (value: boolean) => void;
}

const AccessibilityContext = createContext<AccessibilityContextType | null>(null);

export function useAccessibility() {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within AccessibilityProvider');
  }
  return context;
}

interface SkipLink {
  id: string;
  label: string;
  target: string;
}

interface AccessibilityProviderProps {
  children: React.ReactNode;
}

export function AccessibilityProvider({ children }: AccessibilityProviderProps) {
  // State
  const [skipLinks, setSkipLinks] = useState<SkipLink[]>([]);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [enableKeyboardNavigation, setEnableKeyboardNavigation] = useState(true);
  
  // Refs
  const announcementRef = useRef<HTMLDivElement>(null);
  const politeAnnouncementRef = useRef<HTMLDivElement>(null);
  const assertiveAnnouncementRef = useRef<HTMLDivElement>(null);

  // Initialize accessibility preferences
  useEffect(() => {
    // Check for system preferences
    if (typeof window !== 'undefined') {
      // Reduced motion
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      setReducedMotion(prefersReducedMotion);
      
      // High contrast
      const prefersHighContrast = window.matchMedia('(prefers-contrast: high)').matches;
      setHighContrast(prefersHighContrast);
      
      // Load saved preferences
      const savedReducedMotion = localStorage.getItem('accessibility-reduced-motion');
      const savedHighContrast = localStorage.getItem('accessibility-high-contrast');
      const savedKeyboardNav = localStorage.getItem('accessibility-keyboard-navigation');
      
      if (savedReducedMotion !== null) {
        setReducedMotion(savedReducedMotion === 'true');
      }
      if (savedHighContrast !== null) {
        setHighContrast(savedHighContrast === 'true');
      }
      if (savedKeyboardNav !== null) {
        setEnableKeyboardNavigation(savedKeyboardNav === 'true');
      }
    }
  }, []);

  // Apply CSS custom properties based on preferences
  useEffect(() => {
    if (typeof document !== 'undefined') {
      document.documentElement.style.setProperty(
        '--motion-duration',
        reducedMotion ? '0ms' : '150ms'
      );
      
      if (highContrast) {
        document.documentElement.classList.add('high-contrast');
      } else {
        document.documentElement.classList.remove('high-contrast');
      }
      
      if (!enableKeyboardNavigation) {
        document.documentElement.classList.add('no-focus-visible');
      } else {
        document.documentElement.classList.remove('no-focus-visible');
      }
    }
  }, [reducedMotion, highContrast, enableKeyboardNavigation]);

  // Save preferences to localStorage
  useEffect(() => {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('accessibility-reduced-motion', reducedMotion.toString());
      localStorage.setItem('accessibility-high-contrast', highContrast.toString());
      localStorage.setItem('accessibility-keyboard-navigation', enableKeyboardNavigation.toString());
    }
  }, [reducedMotion, highContrast, enableKeyboardNavigation]);

  // Announce messages to screen readers
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const targetRef = priority === 'assertive' ? assertiveAnnouncementRef : politeAnnouncementRef;
    
    if (targetRef.current) {
      // Clear previous announcement
      targetRef.current.textContent = '';
      
      // Add new announcement
      requestAnimationFrame(() => {
        if (targetRef.current) {
          targetRef.current.textContent = message;
        }
      });
      
      // Clear after announcement is made
      setTimeout(() => {
        if (targetRef.current) {
          targetRef.current.textContent = '';
        }
      }, 1000);
    }
  }, []);

  // Focus an element by selector
  const focusElement = useCallback((selector: string): boolean => {
    try {
      const element = document.querySelector(selector) as HTMLElement;
      if (element) {
        element.focus();
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }, []);

  // Trap focus within a container
  const trapFocus = useCallback((containerRef: React.RefObject<HTMLElement>) => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key !== keyboard.keys.TAB || !containerRef.current) return;

      const focusableElements = containerRef.current.querySelectorAll(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select, [tabindex]:not([tabindex="-1"])'
      );
      
      const firstElement = focusableElements[0] as HTMLElement;
      const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

      if (event.shiftKey && document.activeElement === firstElement) {
        event.preventDefault();
        lastElement.focus();
      } else if (!event.shiftKey && document.activeElement === lastElement) {
        event.preventDefault();
        firstElement.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  // Skip link management
  const registerSkipLink = useCallback((id: string, label: string, target: string) => {
    setSkipLinks(prev => {
      const exists = prev.find(link => link.id === id);
      if (exists) return prev;
      return [...prev, { id, label, target }];
    });
  }, []);

  const unregisterSkipLink = useCallback((id: string) => {
    setSkipLinks(prev => prev.filter(link => link.id !== id));
  }, []);

  const contextValue: AccessibilityContextType = {
    announce,
    focusElement,
    trapFocus,
    registerSkipLink,
    unregisterSkipLink,
    reducedMotion,
    highContrast,
    setReducedMotion,
    setHighContrast,
    enableKeyboardNavigation,
    setEnableKeyboardNavigation,
  };

  return (
    <AccessibilityContext.Provider value={contextValue}>
      {/* Skip Links */}
      {skipLinks.length > 0 && (
        <div className="sr-only focus-within:not-sr-only">
          <nav aria-label="Skip navigation links" className="fixed top-0 left-0 z-50">
            {skipLinks.map((link) => (
              <a
                key={link.id}
                href={`#${link.target}`}
                className="block bg-blue-600 text-white p-2 m-1 rounded focus:not-sr-only"
                onClick={(e) => {
                  e.preventDefault();
                  focusElement(`#${link.target}`);
                }}
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
      )}

      {/* Screen Reader Announcements */}
      <div aria-live="polite" aria-atomic="true" className="sr-only" ref={politeAnnouncementRef} />
      <div aria-live="assertive" aria-atomic="true" className="sr-only" ref={assertiveAnnouncementRef} />

      {/* Main Content */}
      {children}
    </AccessibilityContext.Provider>
  );
}

// Hook for managing skip links
export function useSkipLinks(links: Array<{ id: string; label: string; target: string }>) {
  const { registerSkipLink, unregisterSkipLink } = useAccessibility();

  useEffect(() => {
    links.forEach(link => {
      registerSkipLink(link.id, link.label, link.target);
    });

    return () => {
      links.forEach(link => {
        unregisterSkipLink(link.id);
      });
    };
  }, [links, registerSkipLink, unregisterSkipLink]);
}

// Hook for focus management
export function useFocusManagement(containerRef: React.RefObject<HTMLElement>, enabled = true) {
  const { trapFocus } = useAccessibility();

  useEffect(() => {
    if (!enabled) return;
    
    return trapFocus(containerRef);
  }, [trapFocus, containerRef, enabled]);
}

// Hook for announcements
export function useAnnouncements() {
  const { announce } = useAccessibility();
  
  return {
    announce,
    announceNavigation: (page: string) => announce(screenReader.announcements.navigation(page)),
    announceFormSubmit: (status: 'success' | 'error', message?: string) => 
      announce(screenReader.announcements.formSubmit(status, message), status === 'error' ? 'assertive' : 'polite'),
    announceDataUpdate: (description: string) => announce(screenReader.announcements.dataUpdate(description)),
  };
}