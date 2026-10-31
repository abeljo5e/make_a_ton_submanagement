import React from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../features/auth/context/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, isStaff, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        <span className="brand-logo-dot"></span>
        <span>Brightloop</span>
      </Link>

      <div className="nav-links">
        {isAuthenticated ? (
          <>
            <NavLink
              to="/profile"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Profile
            </NavLink>

            {isStaff && (
              <NavLink
                to="/users"
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                Users & Staff
              </NavLink>
            )}

            <div className="user-badge">
              <span style={{ fontWeight: 600 }}>{user?.full_name?.split(' ')[0]}</span>
              <span className={`role-pill role-${user?.role}`}>{user?.role}</span>
            </div>

            <button
              onClick={handleLogout}
              className="btn btn-outline"
              style={{ width: 'auto', padding: '0.4rem 0.85rem', fontSize: '0.85rem' }}
            >
              Log Out
            </button>
          </>
        ) : (
          <>
            <NavLink
              to="/login"
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
            >
              Sign In
            </NavLink>
            <Link
              to="/register"
              className="btn btn-primary"
              style={{ width: 'auto', padding: '0.45rem 1rem', fontSize: '0.85rem' }}
            >
              Get Started
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
