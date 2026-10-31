import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';
import Badge from '../../components/common/Badge';

export default function QuotationList() {
  const [quotations, setQuotations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [error, setError] = useState(null);

  const fetchQuotations = async () => {
    try {
      setLoading(true);
      const params = filterStatus ? { status: filterStatus } : {};
      const data = await api.getQuotations(params);
      setQuotations(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotations();
  }, [filterStatus]);

  const stats = {
    total: quotations.length,
    draft: quotations.filter(q => q.status === 'DRAFT').length,
    accepted: quotations.filter(q => q.status === 'ACCEPTED').length,
    converted: quotations.filter(q => q.status === 'CONVERTED').length,
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Quotations</h2>
          <p className="page-subtitle">Manage customer proposals, price locking, and conversion workflows</p>
        </div>
        <Link to="/quotations/new" className="btn btn-primary">
          + Create Quotation
        </Link>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Proposals</div>
          <div className="stat-value">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Drafts</div>
          <div className="stat-value">{stats.draft}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Accepted by Customer</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.accepted}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Converted to Subscriptions</div>
          <div className="stat-value" style={{ color: 'var(--primary)' }}>{stats.converted}</div>
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
              className={`btn btn-sm ${filterStatus === 'DRAFT' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('DRAFT')}
            >
              Draft
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'SENT' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('SENT')}
            >
              Sent
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'ACCEPTED' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('ACCEPTED')}
            >
              Accepted
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'CONVERTED' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('CONVERTED')}
            >
              Converted
            </button>
          </div>
        </div>

        {loading ? (
          <div className="empty-state">Loading quotations...</div>
        ) : error ? (
          <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>
        ) : quotations.length === 0 ? (
          <div className="empty-state">No quotations found. Click "+ Create Quotation" to create one.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Quotation #</th>
                <th>Customer ID</th>
                <th>Status</th>
                <th>Total (INR)</th>
                <th>Valid Until</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {quotations.map((q) => (
                <tr key={q.id}>
                  <td>
                    <strong>{q.quotation_number}</strong>
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '13px', color: 'var(--text-muted)' }}>
                    {q.customer_id.substring(0, 18)}...
                  </td>
                  <td>
                    <Badge status={q.status} />
                  </td>
                  <td>
                    <strong>₹{Number(q.total_amount).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</strong>
                  </td>
                  <td>
                    {q.valid_until ? new Date(q.valid_until).toLocaleDateString() : 'N/A'}
                  </td>
                  <td>
                    <Link to={`/quotations/${q.id}`} className="btn btn-secondary btn-sm">
                      View Proposal
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

