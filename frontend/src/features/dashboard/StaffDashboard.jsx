import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';

function fmtCurrency(val) {
  if (val === null || val === undefined) return '—';
  const n = parseFloat(val);
  if (isNaN(n)) return val;
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
}

export default function StaffDashboard() {
  const [summary, setSummary] = useState(null);
  const [subs, setSubs] = useState(null);
  const [invs, setInvs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getDashboardSummary(),
      api.getDashboardSubscriptions(),
      api.getDashboardInvoices(),
    ])
      .then(([s, sb, iv]) => {
        setSummary(s);
        setSubs(sb);
        setInvs(iv);
      })
      .catch((e) => setError(e.message || 'Failed to load staff dashboard.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="loading-state">Loading staff operations dashboard...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Operations Staff Dashboard</h1>
          <p className="page-subtitle">Daily operational queue, pending invoices, and subscription renewals</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Active Subscriptions</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>
            {summary?.active_subscriptions ?? '—'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Paused Subscriptions</div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>
            {summary?.paused_subscriptions ?? '—'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Pending Invoices</div>
          <div className="stat-value" style={{ color: 'var(--danger)' }}>
            {summary?.outstanding_invoices ?? '—'}
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Outstanding Balance</div>
          <div className="stat-value">
            {fmtCurrency(invs?.outstanding_amount)}
          </div>
        </div>
      </div>

      {/* Pending Invoices */}
      <div className="table-card">
        <div className="table-header-bar">
          <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Pending Invoices Requiring Follow-up</h2>
        </div>
        {!invs?.recent?.length ? (
          <div className="empty-state">No pending invoices requiring attention.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Due Date</th>
              </tr>
            </thead>
            <tbody>
              {invs.recent
                .filter((i) => ['draft', 'confirmed'].includes(i.status))
                .map((inv) => (
                  <tr key={inv.id}>
                    <td style={{ fontWeight: 600 }}>{inv.customer_name}</td>
                    <td style={{ fontWeight: 600 }}>{fmtCurrency(inv.amount)}</td>
                    <td>
                      <span className={`badge badge-${inv.status}`}>
                        {inv.status}
                      </span>
                    </td>
                    <td>{inv.due_date ? new Date(inv.due_date).toLocaleDateString('en-IN') : '—'}</td>
                  </tr>
                ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

