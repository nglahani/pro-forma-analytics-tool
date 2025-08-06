/**
 * Dashboard Layout for Route Group
 * Wraps all dashboard pages with the DashboardLayout component
 */

'use client';

import { AuthGuard } from '@/components/auth/AuthGuard';
import { DashboardLayout } from '@/components/layout/DashboardLayout';

interface DashboardGroupLayoutProps {
  children: React.ReactNode;
}

export default function DashboardGroupLayout({ children }: DashboardGroupLayoutProps) {
  return (
    <AuthGuard requireAuth={true}>
      <DashboardLayout>
        {children}
      </DashboardLayout>
    </AuthGuard>
  );
}