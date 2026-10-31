import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import { api } from '../../../lib/api';

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const [token, setToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (tokenParam) {
      setToken(tokenParam);
    }
  }, [searchParams]);

  const checks = {
    length: newPassword.length > 8,
    upper: /[A-Z]/.test(newPassword),
    lower: /[a-z]/.test(newPassword),
    digit: /\d/.test(newPassword),
    special: /[!@#$%^&*(),.?":{}|<>\-_=+[\]/`~;\\]/.test(newPassword),
  };
  const isPasswordValid = Object.values(checks).every(Boolean);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!token.trim()) {
      setError('A valid reset token is required.');
      return;
    }
    if (!isPasswordValid) {
      setError('New password does not satisfy all complexity requirements.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      await api.post('/auth/reset-password', {
        token: token.trim(),
        new_password: newPassword,
      });
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2500);
    } catch (err) {
      setError(err.message || 'Failed to reset password. The token may be expired or already used.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-wrapper">
      <div className="auth-card">
        <div className="auth-header">
          <div className="brand-badge">
            <span className="brand-logo-dot"></span>
            Account Recovery
          </div>
          <h1 className="auth-title">Set new password</h1>
          <p className="auth-subtitle">Create a secure password for your Brightloop account</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <div>{error}</div>
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <span>✓</span>
            <div>Password successfully reset! Redirecting to login...</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="token">Reset Token *</label>
            <input
              id="token"
              type="text"
              className="form-input"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="Paste your reset token"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="newPassword">New Password *</label>
            <input
              id="newPassword"
              type="password"
              className="form-input"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Enter new strong password"
              required
            />

            <div className="password-requirements">
              <div className="req-title">New Password Requirements:</div>
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

          <div className="form-group">
            <label className="form-label" htmlFor="confirmPassword">Confirm Password *</label>
            <input
              id="confirmPassword"
              type="password"
              className="form-input"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Re-type new password"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting || !isPasswordValid || success}
            style={{ marginTop: '0.5rem' }}
          >
            {submitting ? (
              <>
                <span className="spinner"></span>
                Resetting password...
              </>
            ) : (
              'Save New Password'
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          <Link to="/login" style={{ fontWeight: 600 }}>Return to sign in</Link>
        </div>
      </div>
    </div>
  );
}
