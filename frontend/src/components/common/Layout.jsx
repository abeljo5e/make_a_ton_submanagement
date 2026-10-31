import React from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { useAuth } from '../../features/auth/context/AuthContext';

export default function Layout() {
  const { user, isAuthenticated, isStaff, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

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

          {isAuthenticated && (
            <NavLink to="/profile" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <span>👤</span> Profile
            </NavLink>
          )}

          {isStaff && (
            <NavLink to="/users" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
              <span>👥</span> Users &amp; Staff
            </NavLink>
          )}
        </nav>

        <div style={{ marginTop: 'auto', padding: '16px', borderTop: '1px solid var(--border)' }}>
          {isAuthenticated ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ fontSize: '13px', fontWeight: 600 }}>{user?.full_name}</div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Role: {user?.role}</div>
              <button onClick={handleLogout} className="btn btn-outline" style={{ width: '100%', padding: '6px' }}>
                Log Out
              </button>
            </div>
          ) : (
            <NavLink to="/login" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
              Log In
            </NavLink>
          )}
        </div>
      </aside>

      <div className="main-content">
        <header className="topbar">
          <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
            System Mode: <strong>Integrated Platform (FastAPI + React 19)</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge badge-active">Live System</span>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: '#4f46e5', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
              {user ? user.full_name?.charAt(0) : 'BL'}
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
