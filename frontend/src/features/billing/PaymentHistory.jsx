import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';
import Badge from '../../components/common/Badge';

export default function PaymentHistory() {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const data = await api.getPayments();
      setPayments(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPayments();
  }, []);

  const totalCollected = payments.reduce((sum, p) => sum + Number(p.amount), 0);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Payment Transactions</h2>
          <p className="page-subtitle">Audit trail of all settled partial and full payment transactions</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Transactions</div>
          <div className="stat-value">{payments.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Revenue Collected</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>
            ₹{totalCollected.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Active Currency</div>
          <div className="stat-value">INR (₹)</div>
        </div>
      </div>

      <div className="table-card">
        <div className="table-header-bar">
          <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Recent Payment Records</h3>
        </div>

        {loading ? (
          <div className="empty-state">Loading payment transactions...</div>
        ) : error ? (
          <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>
        ) : payments.length === 0 ? (
          <div className="empty-state">No payment records found. View an invoice to record a payment.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Payment #</th>
                <th>Invoice ID</th>
                <th>Method</th>
                <th>Reference</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {payments.map((p) => (
                <tr key={p.id}>
                  <td><strong>{p.payment_number}</strong></td>
                  <td>
                    <Link to={`/invoices/${p.invoice_id}`} style={{ color: 'var(--primary)', fontWeight: '500' }}>
                      {p.invoice_id.substring(0, 18)}...
                    </Link>
                  </td>
                  <td style={{ textTransform: 'uppercase' }}>{p.payment_method}</td>
                  <td><code>{p.payment_reference}</code></td>
                  <td>{new Date(p.payment_date).toLocaleString()}</td>
                  <td style={{ color: 'var(--success)' }}>
                    <strong>+ ₹{Number(p.amount).toFixed(2)}</strong>
                  </td>
                  <td><Badge status={p.payment_status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

