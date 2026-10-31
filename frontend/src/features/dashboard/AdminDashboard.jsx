import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts';
import { api } from '../../lib/api';

function fmtCurrency(val) {
  if (val === null || val === undefined) return '—';
  const n = parseFloat(val);
  if (isNaN(n)) return val;
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
}

export default function AdminDashboard() {
  const [summary, setSummary] = useState(null);
  const [revenue, setRevenue] = useState([]);
  const [subs, setSubs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getDashboardSummary(),
      api.getDashboardRevenue(12),
      api.getDashboardSubscriptions(),
    ])
      .then(([s, r, sb]) => {
        setSummary(s);
        setRevenue(r.data || []);
        setSubs(sb);
      })
      .catch((e) => setError(e.message || 'Failed to load dashboard data.'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="loading-state">Loading executive admin dashboard...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Executive Admin Dashboard</h1>
          <p className="page-subtitle">Live KPI snapshot across subscriptions, billing, and platform revenue</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Platform Users</div>
          <div className="stat-value">{summary?.users ?? '—'}</div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            {summary?.customers ?? 0} active customers
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Active Subscriptions</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>
            {summary?.active_subscriptions ?? '—'}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            {summary?.paused_subscriptions ?? 0} paused · {summary?.cancelled_subscriptions ?? 0} closed
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Outstanding Invoices</div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>
            {summary?.outstanding_invoices ?? '—'}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            of {summary?.total_invoices ?? 0} total generated
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-label">Realized Revenue</div>
          <div className="stat-value" style={{ color: 'var(--primary)' }}>
            {fmtCurrency(summary?.revenue_total)}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Fully reconciled settled invoices
          </div>
        </div>
      </div>

      {/* Revenue Time-Series Chart */}
      <div className="card" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>
          Monthly Revenue Trend (Last 12 Months)
        </h2>
        {revenue.length === 0 ? (
          <div className="empty-state">No recorded revenue transactions yet.</div>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={revenue} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis
                tick={{ fill: '#64748b', fontSize: 12 }}
                tickFormatter={(v) => `₹${(v / 1000).toFixed(0)}k`}
              />
              <Tooltip
                formatter={(val) => [fmtCurrency(val), 'Revenue']}
                contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
              />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#4f46e5"
                strokeWidth={3}
                dot={{ r: 4, fill: '#4f46e5' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Recent Subscriptions */}
      <div className="table-card">
        <div className="table-header-bar">
          <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Recent Subscriptions</h2>
        </div>
        {!subs?.recent?.length ? (
          <div className="empty-state">No recent subscriptions recorded.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Plan Name</th>
                <th>Status</th>
                <th>Start Date</th>
              </tr>
            </thead>
            <tbody>
              {subs.recent.map((s) => (
                <tr key={s.id}>
                  <td style={{ fontWeight: 600 }}>{s.customer_name}</td>
                  <td>{s.plan_name}</td>
                  <td>
                    <span className={`badge badge-${s.status}`}>
                      {s.status}
                    </span>
                  </td>
                  <td>{s.start_date ? new Date(s.start_date).toLocaleDateString('en-IN') : '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

