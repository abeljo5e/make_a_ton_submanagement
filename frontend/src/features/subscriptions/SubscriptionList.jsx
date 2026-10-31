import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';
import Badge from '../../components/common/Badge';

export default function SubscriptionList() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [error, setError] = useState(null);

  const fetchSubscriptions = async () => {
    try {
      setLoading(true);
      const params = filterStatus ? { status: filterStatus } : {};
      const data = await api.getSubscriptions(params);
      setSubscriptions(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscriptions();
  }, [filterStatus]);

  const stats = {
    total: subscriptions.length,
    active: subscriptions.filter(s => s.status === 'ACTIVE').length,
    paused: subscriptions.filter(s => s.status === 'PAUSED').length,
    canceled: subscriptions.filter(s => s.status === 'CANCELED').length,
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Active Subscriptions</h2>
          <p className="page-subtitle">Track recurring customer lifecycles, billing frequency, and renewals</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Subscriptions</div>
          <div className="stat-value">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active (Billing)</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.active}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Paused</div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>{stats.paused}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Canceled</div>
          <div className="stat-value" style={{ color: 'var(--danger)' }}>{stats.canceled}</div>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header-bar">
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              className={`btn btn-sm ${filterStatus === '' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('')}
            >
              All
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'ACTIVE' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('ACTIVE')}
            >
              Active
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'PAUSED' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('PAUSED')}
            >
              Paused
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'CANCELED' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('CANCELED')}
            >
              Canceled
            </button>
          </div>
        </div>

        {loading ? (
          <div className="empty-state">Loading subscriptions...</div>
        ) : error ? (
          <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>
        ) : subscriptions.length === 0 ? (
          <div className="empty-state">No subscriptions found. Convert an accepted quotation to create one.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Subscription #</th>
                <th>Customer ID</th>
                <th>Status</th>
                <th>Cycle</th>
                <th>Next Billing Date</th>
                <th>Recurring Amount</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {subscriptions.map((s) => (
                <tr key={s.id}>
                  <td><strong>{s.subscription_number}</strong></td>
                  <td style={{ fontFamily: 'monospace', fontSize: '13px', color: 'var(--text-muted)' }}>
                    {s.customer_id.substring(0, 18)}...
                  </td>
                  <td><Badge status={s.status} /></td>
                  <td style={{ textTransform: 'capitalize' }}>{s.billing_frequency}</td>
                  <td>{s.next_billing_date ? new Date(s.next_billing_date).toLocaleDateString() : 'N/A'}</td>
                  <td><strong>₹{Number(s.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong></td>
                  <td>
                    <Link to={`/subscriptions/${s.id}`} className="btn btn-secondary btn-sm">
                      Manage
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
