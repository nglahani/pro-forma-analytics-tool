/**
 * Main Dashboard Layout Component
 * NYT/Claude-inspired design with sidebar navigation and header
 */

'use client';

import { useState, useRef, useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useAccessibility, useSkipLinks, useFocusManagement } from '@/components/common/AccessibilityProvider';
import { keyboard } from '@/lib/accessibility';

interface DashboardLayoutProps {
  children: React.ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { announce, focusElement } = useAccessibility();
  const mainContentRef = useRef<HTMLElement>(null);
  const sidebarRef = useRef<HTMLDivElement>(null);
  
  // Register skip links
  useSkipLinks([
    { id: 'skip-to-main', label: 'Skip to main content', target: 'main-content' },
    { id: 'skip-to-nav', label: 'Skip to navigation', target: 'sidebar-nav' },
  ]);
  
  // Focus management for sidebar
  useFocusManagement(sidebarRef, sidebarOpen);

  // Handle escape key to close sidebar
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === keyboard.keys.ESCAPE && sidebarOpen) {
        setSidebarOpen(false);
        announce('Navigation closed', 'polite');
        // Return focus to menu button
        setTimeout(() => focusElement('[aria-label="Open navigation menu"]'), 100);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [sidebarOpen, announce, focusElement]);

  const handleSidebarToggle = (open: boolean) => {
    setSidebarOpen(open);
    announce(
      open ? 'Navigation opened' : 'Navigation closed',
      'polite'
    );
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar 
        ref={sidebarRef}
        isOpen={sidebarOpen} 
        onClose={() => handleSidebarToggle(false)} 
      />
      
      {/* Main content area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header onMenuClick={() => handleSidebarToggle(true)} />
        
        {/* Main content */}
        <main 
          ref={mainContentRef}
          id="main-content"
          className="flex-1 overflow-y-auto bg-gray-50"
          role="main"
          aria-label="Main content area"
          tabIndex={-1}
        >
          <div className="h-full">
            {children}
          </div>
        </main>
      </div>
      
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => handleSidebarToggle(false)}
          role="button"
          aria-label="Close navigation overlay"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === keyboard.keys.ENTER || e.key === keyboard.keys.SPACE) {
              e.preventDefault();
              handleSidebarToggle(false);
            }
          }}
        />
      )}
    </div>
  );
}