import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../../../lib/api';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [statusMsg, setStatusMsg] = useState(null);
  const [devToken, setDevToken] = useState(null);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setStatusMsg(null);
    setDevToken(null);
    setSubmitting(true);

    try {
      const response = await api.post('/auth/forgot-password', { email });
      setStatusMsg(response.detail || 'Password reset link dispatched.');
      if (response.reset_token_preview) {
        setDevToken(response.reset_token_preview);
      }
    } catch (err) {
      setError(err.message || 'Failed to request password reset.');
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
            Security
          </div>
          <h1 className="auth-title">Reset password</h1>
          <p className="auth-subtitle">Enter your registered email and we'll send you recovery instructions</p>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <div>{error}</div>
          </div>
        )}

        {statusMsg && (
          <div className="alert alert-success">
            <span>✓</span>
            <div>{statusMsg}</div>
          </div>
        )}

        {devToken && (
          <div className="alert alert-info" style={{ flexDirection: 'column', alignItems: 'stretch' }}>
            <div style={{ fontWeight: 700, marginBottom: '0.25rem' }}>🛠️ Development Reset Token:</div>
            <div style={{ fontSize: '0.8rem', wordBreak: 'break-all', background: 'rgba(0,0,0,0.3)', padding: '0.4rem', borderRadius: '4px', marginBottom: '0.5rem' }}>
              {devToken}
            </div>
            <button
              className="btn btn-outline"
              style={{ fontSize: '0.85rem', padding: '0.4rem' }}
              onClick={() => navigate(`/reset-password?token=${devToken}`)}
            >
              Proceed to Reset Password →
            </button>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="email">Registered Email</label>
            <input
              id="email"
              type="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={submitting}
            style={{ marginTop: '0.5rem' }}
          >
            {submitting ? (
              <>
                <span className="spinner"></span>
                Sending instructions...
              </>
            ) : (
              'Send Reset Instructions'
            )}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '1.75rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
          Remember your password?{' '}
          <Link to="/login" style={{ fontWeight: 600 }}>Return to sign in</Link>
        </div>
      </div>
    </div>
  );
}
