import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    company_name: '',
    phone: '',
    address: '',
  });

  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const { register } = useAuth();
  const navigate = useNavigate();

  // Password rules validation logic
  const password = formData.password;
  const checks = {
    length: password.length > 8,
    upper: /[A-Z]/.test(password),
    lower: /[a-z]/.test(password),
    digit: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>\-_=+[\]/`~;\\]/.test(password),
  };
  const isPasswordValid = Object.values(checks).every(Boolean);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isPasswordValid) {
      setError('Please satisfy all password complexity requirements before proceeding.');
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      await register(formData);
      navigate('/profile');
    } catch (err) {
      setError(err.message || 'Registration failed. Please check your information.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card wide">
        <div className="auth-header">
          <div className="brand-badge">
            <span className="brand-logo-dot"></span>
            Customer Portal
          </div>
          <h1 className="auth-title">Create an account</h1>
          <p className="auth-subtitle">Join Brightloop to subscribe to plans and manage your billing</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="full_name">Full Name *</label>
              <input
                id="full_name"
                name="full_name"
                type="text"
                className="form-input"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="Jane Doe"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="email">Work Email *</label>
              <input
                id="email"
                name="email"
                type="email"
                className="form-input"
                value={formData.email}
                onChange={handleChange}
                placeholder="jane@company.com"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password *</label>
            <input
              id="password"
              name="password"
              type="password"
              className="form-input"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a strong password"
              required
            />
            
            {/* Live Password Complexity Checklist */}
            <div className="password-requirements">
              <div className="req-title">Password Requirements:</div>
              <div className={`req-item ${checks.length ? 'met' : ''}`}>
                <span className="req-dot"></span>
                Longer than 8 characters (at least 9 chars)
              </div>
              <div className={`req-item ${checks.upper ? 'met' : ''}`}>
                <span className="req-dot"></span>
                At least one uppercase letter (A-Z)
              </div>
              <div className={`req-item ${checks.lower ? 'met' : ''}`}>
                <span className="req-dot"></span>
                At least one lowercase letter (a-z)
              </div>
              <div className={`req-item ${checks.digit ? 'met' : ''}`}>
                <span className="req-dot"></span>
                At least one numeric digit (0-9)
              </div>
              <div className={`req-item ${checks.special ? 'met' : ''}`}>
                <span className="req-dot"></span>
                At least one special symbol (!@#$%^&*...)
              </div>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label className="form-label" htmlFor="company_name">Company Name</label>
              <input
                id="company_name"
                name="company_name"
                type="text"
                className="form-input"
                value={formData.company_name}
                onChange={handleChange}
                placeholder="Acme Inc."
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="phone">Phone Number</label>
              <input
                id="phone"
                name="phone"
                type="tel"
                className="form-input"
                value={formData.phone}
                onChange={handleChange}
                placeholder="+1 (555) 000-0000"
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="address">Billing Address</label>
            <textarea
              id="address"
              name="address"
              className="form-textarea"
              value={formData.address}
              onChange={handleChange}
              placeholder="Street address, city, state, zip code"
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || !isPasswordValid}
            style={{ marginTop: '0.5rem' }}
          >
            {submitting ? (
              <>
                <span className="spinner"></span>
                Creating account...
              </>
            ) : (
              'Complete Registration'
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Already have an account?{' '}
          <Link to="/login" style={{ fontWeight: 600 }}>Sign in</Link>
        </div>
      </div>
    </div>
  );
}
