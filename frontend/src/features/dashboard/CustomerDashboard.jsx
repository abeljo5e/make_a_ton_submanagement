import React, { useEffect, useState } from 'react';
import { api } from '../../lib/api';

function fmtCurrency(val) {
  if (val === null || val === undefined) return '—';
  const n = parseFloat(val);
  if (isNaN(n)) return val;
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
}

export default function CustomerDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.getCustomerDashboard()
      .then((res) => setData(res))
      .catch((e) => setError(e.message || 'Failed to load customer dashboard.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="loading-state">Loading customer account details...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  const { subscription, recent_invoices, available_plans } = data || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">My Customer Portal</h1>
          <p className="page-subtitle">Manage your subscription, view billing history, and explore plans</p>
        </div>
      </div>

      {/* Active Subscription Details */}
      <div className="card" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>Current Subscription</h2>
        {!subscription ? (
          <div className="empty-state">You do not have an active subscription at this time. Choose a plan below.</div>
        ) : (
          <div className="stats-grid" style={{ marginBottom: 0 }}>
            <div className="stat-card">
              <div className="stat-label">Plan Name</div>
              <div className="stat-value" style={{ fontSize: '20px' }}>{subscription.plan_name}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Status</div>
              <div style={{ marginTop: '8px' }}>
                <span className={`badge badge-${subscription.status}`}>{subscription.status}</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Next Scheduled Billing</div>
              <div className="stat-value" style={{ fontSize: '18px' }}>
                {subscription.next_billing ? new Date(subscription.next_billing).toLocaleDateString('en-IN') : '—'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recent Invoices */}
      <div className="table-card">
        <div className="table-header-bar">
          <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Recent Invoices</h2>
        </div>
        {!recent_invoices?.length ? (
          <div className="empty-state">No invoice statements on file.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Invoice ID</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Due Date</th>
              </tr>
            </thead>
            <tbody>
              {recent_invoices.map((inv) => (
                <tr key={inv.id}>
                  <td style={{ fontFamily: 'monospace' }}>{inv.id.slice(0, 8)}...</td>
                  <td style={{ fontWeight: 600 }}>{fmtCurrency(inv.amount)}</td>
                  <td>
                    <span className={`badge badge-${inv.status}`}>{inv.status}</span>
                  </td>
                  <td>{inv.due_date ? new Date(inv.due_date).toLocaleDateString('en-IN') : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Available Plans */}
      <div>
        <h2 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '16px' }}>Available Platform Plans</h2>
        {!available_plans?.length ? (
          <div className="empty-state">No subscription plans available for upgrade.</div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
            {available_plans.map((p) => (
              <div key={p.id} className="card" style={{ padding: '24px', border: '1px solid var(--border)' }}>
                <div style={{ fontSize: '18px', fontWeight: 700 }}>{p.name}</div>
                <div style={{ fontSize: '26px', fontWeight: 700, color: 'var(--primary)', margin: '12px 0' }}>
                  {fmtCurrency(p.price)}
                </div>
                <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
                  Billed {p.billing_frequency}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
