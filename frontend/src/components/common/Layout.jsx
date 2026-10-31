import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';

export default function Layout() {
  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">B</div>
          <div className="brand-text">
            <h1>Brightloop</h1>
            <span>Subscription Ops</span>
          </div>
        </div>

        <nav className="nav-links">
          <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span>📊</span> Dashboard
          </NavLink>
          <NavLink to="/analytics" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span>📈</span> Analytics
          </NavLink>
          <NavLink to="/quotations" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span>📋</span> Quotations
          </NavLink>
          <NavLink to="/subscriptions" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span>🔄</span> Subscriptions
          </NavLink>
          <NavLink to="/invoices" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span>🧾</span> Invoices
          </NavLink>
          <NavLink to="/payments" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span>💳</span> Payments
          </NavLink>
        </nav>
      </aside>

      <div className="main-content">
        <header className="topbar">
          <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            Active View: <strong>Billing Administration &amp; Business Intelligence</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge badge-active">FastAPI Engine</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#4f46e5', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
              BL
            </div>
          </div>
        </header>

        <main className="page-container">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
