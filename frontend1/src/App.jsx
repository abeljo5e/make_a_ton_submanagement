import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate, useLocation } from 'react-router-dom';
import ProductsPage from './features/products/ProductsPage';
import PlansPage from './features/plans/PlansPage';
import PlanCatalogue from './features/plans/PlanCatalogue';

function Navigation({ userRole, onToggleRole }) {
  const location = useLocation();

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span>⚡ Brightloop</span>
        <span className="role-badge">Role: {userRole}</span>
      </div>
      <div className="nav-links">
        <Link
          to="/plans/catalogue"
          className={`nav-link ${location.pathname.startsWith('/plans/catalogue') ? 'active' : ''}`}
        >
          Customer Catalogue
        </Link>

        {userRole !== 'customer' && (
          <>
            <Link
              to="/admin/products"
              className={`nav-link ${location.pathname.startsWith('/admin/products') ? 'active' : ''}`}
            >
              Products Management
            </Link>
            <Link
              to="/admin/plans"
              className={`nav-link ${location.pathname.startsWith('/admin/plans') ? 'active' : ''}`}
            >
              Plans Management
            </Link>
          </>
        )}

        <button
          className="btn btn-secondary btn-sm"
          onClick={onToggleRole}
          title="Toggle role for demonstration and role check testing"
        >
          Switch Role: {userRole === 'admin' ? 'Customer' : 'Admin'}
        </button>
      </div>
    </nav>
  );
}

function ProtectedStaffRoute({ userRole, children }) {
  if (userRole === 'customer') {
    return (
      <div className="card">
        <div className="alert alert-danger">
          Access Restricted: Only Admin and Staff roles have permission to manage catalog products and plans.
        </div>
        <Link to="/plans/catalogue" className="btn btn-primary">
          Go to Customer Plan Catalogue
        </Link>
      </div>
    );
  }
  return children;
}

export default function App() {
  const [userRole, setUserRole] = useState('admin');

  const handleToggleRole = () => {
    setUserRole((prev) => (prev === 'admin' ? 'customer' : 'admin'));
  };

  return (
    <BrowserRouter>
      <div className="app-container">
        <Navigation userRole={userRole} onToggleRole={handleToggleRole} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/plans/catalogue" replace />} />
            <Route path="/plans/catalogue" element={<PlanCatalogue />} />
            <Route
              path="/admin/products"
              element={
                <ProtectedStaffRoute userRole={userRole}>
                  <ProductsPage />
                </ProtectedStaffRoute>
              }
            />
            <Route
              path="/admin/plans"
              element={
                <ProtectedStaffRoute userRole={userRole}>
                  <PlansPage />
                </ProtectedStaffRoute>
              }
            />
            <Route path="*" element={<div className="card">Page not found</div>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
