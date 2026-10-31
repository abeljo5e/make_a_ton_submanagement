import React, { useEffect, useState } from 'react';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, Tooltip,
  XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend
} from 'recharts';
import { api } from '../../lib/api';

const COLORS = ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

function fmtCurrency(val) {
  const n = parseFloat(val);
  if (isNaN(n)) return '—';
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n);
}

export default function Analytics() {
  const [months, setMonths] = useState(12);
  const [revenue, setRevenue] = useState(null);
  const [subs, setSubs] = useState(null);
  const [invs, setInvs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  function loadData(m) {
    setLoading(true);
    setError(null);
    Promise.all([
      api.getAnalyticsRevenue(m),
      api.getAnalyticsSubscriptions(m),
      api.getAnalyticsInvoices(m),
    ])
      .then(([r, s, i]) => {
        setRevenue(r);
        setSubs(s);
        setInvs(i);
      })
      .catch((e) => setError(e.message || 'Failed to load analytics trends.'))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadData(months);
  }, []);

  const handleMonthsChange = (e) => {
    const m = parseInt(e.target.value, 10);
    setMonths(m);
    loadData(m);
  };

  if (loading) {
    return <div className="loading-state">Loading financial and subscription analytics...</div>;
  }

  if (error) {
    return <div className="alert alert-error">{error}</div>;
  }

  const planData = subs?.plan_popularity?.slice(0, 5) || [];
  const invoiceMonthly = invs?.monthly || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      <div className="page-header">
        <div>
          <h1 className="page-title">Platform Business Analytics</h1>
          <p className="page-subtitle">Revenue run-rate, new subscription adoption, and collection efficiency</p>
        </div>
        <div>
          <select
            value={months}
            onChange={handleMonthsChange}
            className="form-control"
            style={{ width: '160px', fontWeight: 600 }}
          >
            {[3, 6, 12, 24].map((m) => (
              <option key={m} value={m}>{m} Months Window</option>
            ))}
          </select>
        </div>
      </div>

      {/* Summary Row */}
      {revenue && (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Total Period Revenue</div>
            <div className="stat-value" style={{ color: 'var(--primary)' }}>
              {fmtCurrency(revenue.total_revenue)}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Total Amount Settled</div>
            <div className="stat-value" style={{ color: 'var(--success)' }}>
              {fmtCurrency(invs?.totals?.paid_amount)}
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Outstanding Invoices Balance</div>
            <div className="stat-value" style={{ color: 'var(--warning)' }}>
              {fmtCurrency(invs?.totals?.outstanding_amount)}
            </div>
          </div>
        </div>
      )}

      {/* Monthly Revenue Chart */}
      <div className="card" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>
          Monthly Revenue Trend (Last {months} Months)
        </h2>
        {revenue?.data?.length === 0 ? (
          <div className="empty-state">No revenue data found for this period.</div>
        ) : (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={revenue?.data} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
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

      {/* Monthly Subscription Growth */}
      <div className="card" style={{ padding: '24px' }}>
        <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '20px' }}>
          New Customer Subscriptions Acquired
        </h2>
        {subs?.growth?.length === 0 ? (
          <div className="empty-state">No new subscriptions recorded.</div>
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={subs?.growth} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 12 }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} allowDecimals={false} />
              <Tooltip
                formatter={(val) => [val, 'New Subscriptions']}
                contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px' }}
              />
              <Bar dataKey="new_subscriptions" fill="#4f46e5" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* Popularity and Invoices Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {/* Plan Popularity Pie */}
        <div className="card" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '16px' }}>
            Subscription Plan Popularity
          </h2>
          {planData.length === 0 ? (
            <div className="empty-state">No active plan subscriptions.</div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <ResponsiveContainer width="50%" height={180}>
                <PieChart>
                  <Pie
                    data={planData}
                    dataKey="active_count"
                    nameKey="plan_name"
                    cx="50%"
                    cy="50%"
                    outerRadius={65}
                    paddingAngle={3}
                  >
                    {planData.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '13px' }}>
                {planData.map((p, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          width: '10px',
                          height: '10px',
                          borderRadius: '50%',
                          background: COLORS[i % COLORS.length],
                          display: 'inline-block'
                        }}
                      />
                      <span>{p.plan_name}</span>
                    </div>
                    <span style={{ fontWeight: 700 }}>{p.active_count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Invoice Payment Rate */}
        <div className="card" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h2 style={{ fontSize: '16px', fontWeight: 700 }}>Collection Efficiency Rate</h2>
            <span style={{ fontSize: '24px', fontWeight: 700, color: 'var(--success)' }}>
              {invs?.payment_rate ?? '0'}%
            </span>
          </div>
          {invoiceMonthly.length === 0 ? (
            <div className="empty-state">No invoice payment records.</div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={invoiceMonthly.slice(-6)} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" tick={{ fill: '#64748b', fontSize: 11 }} />
                <YAxis tick={{ fill: '#64748b', fontSize: 11 }} allowDecimals={false} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
                <Bar dataKey="paid" fill="#10b981" name="Paid Invoices" radius={[4, 4, 0, 0]} />
                <Bar dataKey="outstanding" fill="#f59e0b" name="Outstanding" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
}
