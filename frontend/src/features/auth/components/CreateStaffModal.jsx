import React, { useState } from 'react';
import { api } from '../../../lib/api';

export default function CreateStaffModal({ isOpen, onClose, onStaffCreated }) {
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
  });

  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

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
      setError('Staff password must meet all complexity requirements.');
      return;
    }

    setError(null);
    setSubmitting(true);

    try {
      const newStaff = await api.post('/staff', formData);
      onStaffCreated(newStaff);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create staff account.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Create Staff Account</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        {error && (
          <div className="alert alert-error">
            <span>⚠️</span>
            <div>{error}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label" htmlFor="staff_full_name">Staff Full Name *</label>
            <input
              id="staff_full_name"
              name="full_name"
              type="text"
              className="form-input"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="e.g. Alex Morgan"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="staff_email">Internal Staff Email *</label>
            <input
              id="staff_email"
              name="email"
              type="email"
              className="form-input"
              value={formData.email}
              onChange={handleChange}
              placeholder="alex@brightloop.com"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="staff_password">Temporary Password *</label>
            <input
              id="staff_password"
              name="password"
              type="password"
              className="form-input"
              value={formData.password}
              onChange={handleChange}
              placeholder="Strong temporary password"
              required
            />

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

          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={submitting || !isPasswordValid}
            >
              {submitting ? 'Creating...' : 'Create Account'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
