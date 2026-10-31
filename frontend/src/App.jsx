import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/common/Layout';
import AdminDashboard from './features/dashboard/AdminDashboard';
import StaffDashboard from './features/dashboard/StaffDashboard';
import CustomerDashboard from './features/dashboard/CustomerDashboard';
import Analytics from './features/analytics/Analytics';
import QuotationList from './features/quotations/QuotationList';
import QuotationCreate from './features/quotations/QuotationCreate';
import QuotationDetail from './features/quotations/QuotationDetail';
import SubscriptionList from './features/subscriptions/SubscriptionList';
import SubscriptionDetail from './features/subscriptions/SubscriptionDetail';
import InvoiceList from './features/billing/InvoiceList';
import InvoiceDetail from './features/billing/InvoiceDetail';
import PaymentHistory from './features/billing/PaymentHistory';

// Member 1 Auth Pages
import LoginPage from './features/auth/pages/LoginPage';
import RegisterPage from './features/auth/pages/RegisterPage';
import ForgotPasswordPage from './features/auth/pages/ForgotPasswordPage';
import ResetPasswordPage from './features/auth/pages/ResetPasswordPage';
import ProfilePage from './features/auth/pages/ProfilePage';
import UserManagementPage from './features/auth/pages/UserManagementPage';

export default function App() {
  return (
    <Routes>
      {/* Public Auth Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Main Application Layout */}
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        
        {/* Dashboard & Analytics (Member 4) */}
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="staff-dashboard" element={<StaffDashboard />} />
        <Route path="my-dashboard" element={<CustomerDashboard />} />
        <Route path="analytics" element={<Analytics />} />

        {/* Quotation Management (Member 3) */}
        <Route path="quotations" element={<QuotationList />} />
        <Route path="quotations/new" element={<QuotationCreate />} />
        <Route path="quotations/:id" element={<QuotationDetail />} />

        {/* Subscription Lifecycle (Member 3) */}
        <Route path="subscriptions" element={<SubscriptionList />} />
        <Route path="subscriptions/:id" element={<SubscriptionDetail />} />

        {/* Billing & Payments (Member 3) */}
        <Route path="invoices" element={<InvoiceList />} />
        <Route path="invoices/:id" element={<InvoiceDetail />} />
        <Route path="payments" element={<PaymentHistory />} />

        {/* Profile & User Management (Member 1) */}
        <Route path="profile" element={<ProfilePage />} />
        <Route path="users" element={<UserManagementPage />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
