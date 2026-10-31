import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
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

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          
          {/* Dashboard & Analytics Routes (Member 4) */}
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="staff-dashboard" element={<StaffDashboard />} />
          <Route path="my-dashboard" element={<CustomerDashboard />} />
          <Route path="analytics" element={<Analytics />} />

          {/* Quotation Routes (Member 3) */}
          <Route path="quotations" element={<QuotationList />} />
          <Route path="quotations/new" element={<QuotationCreate />} />
          <Route path="quotations/:id" element={<QuotationDetail />} />

          {/* Subscription Routes (Member 3) */}
          <Route path="subscriptions" element={<SubscriptionList />} />
          <Route path="subscriptions/:id" element={<SubscriptionDetail />} />

          {/* Invoice & Payment Routes (Member 3) */}
          <Route path="invoices" element={<InvoiceList />} />
          <Route path="invoices/:id" element={<InvoiceDetail />} />
          <Route path="payments" element={<PaymentHistory />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
