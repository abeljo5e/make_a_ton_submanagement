import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { api } from '../../lib/api';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';

export default function QuotationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [quotation, setQuotation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Modals
  const [rejectModalOpen, setRejectModalOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [frequency, setFrequency] = useState('monthly');

  const fetchQuotation = async () => {
    try {
      setLoading(true);
      const data = await api.getQuotation(id);
      setQuotation(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuotation();
  }, [id]);

  const handleSend = async () => {
    try {
      setActionLoading(true);
      const updated = await api.sendQuotation(id);
      setQuotation(updated);
    } catch (err) {
      alert(`Error sending quotation: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleConfirm = async () => {
    try {
      setActionLoading(true);
      const updated = await api.confirmQuotation(id);
      setQuotation(updated);
    } catch (err) {
      alert(`Error confirming quotation: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (e) => {
    e.preventDefault();
    try {
      setActionLoading(true);
      const updated = await api.rejectQuotation(id, rejectReason);
      setQuotation(updated);
      setRejectModalOpen(false);
    } catch (err) {
      alert(`Error rejecting quotation: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleConvert = async () => {
    try {
      setActionLoading(true);
      const subscription = await api.convertQuotation(id, frequency);
      navigate(`/subscriptions/${subscription.id}`);
    } catch (err) {
      alert(`Error converting quotation: ${err.message}`);
      setActionLoading(false);
    }
  };

  if (loading) return <div className="empty-state">Loading quotation details...</div>;
  if (error) return <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>;
  if (!quotation) return <div className="empty-state">Quotation not found</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h2 className="page-title">{quotation.quotation_number}</h2>
            <Badge status={quotation.status} />
          </div>
          <p className="page-subtitle">Created on {new Date(quotation.created_at).toLocaleString()}</p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/quotations" className="btn btn-secondary">
            &larr; Back to List
          </Link>

          {quotation.status === 'DRAFT' && (
            <button onClick={handleSend} disabled={actionLoading} className="btn btn-primary">
              📤 Send Proposal
            </button>
          )}

          {(quotation.status === 'SENT' || quotation.status === 'DRAFT') && (
            <>
              <button onClick={handleConfirm} disabled={actionLoading} className="btn btn-primary" style={{ background: 'var(--success)' }}>
                ✓ Customer Accept
              </button>
              <button onClick={() => setRejectModalOpen(true)} disabled={actionLoading} className="btn btn-danger">
                ✕ Reject
              </button>
            </>
          )}

          {quotation.status === 'ACCEPTED' && (
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <select
                className="form-control"
                style={{ width: 'auto' }}
                value={frequency}
                onChange={(e) => setFrequency(e.target.value)}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="yearly">Yearly</option>
              </select>
              <button onClick={handleConvert} disabled={actionLoading} className="btn btn-primary">
                ⚡ Convert to Subscription
              </button>
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div>
          <div className="table-card" style={{ marginBottom: '24px' }}>
            <div className="table-header-bar">
              <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Line Items Snapshot</h3>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Qty</th>
                  <th>Unit Price</th>
                  <th>Tax</th>
                  <th>Total</th>
                </tr>
              </thead>
              <tbody>
                {quotation.lines.map((l) => (
                  <tr key={l.id}>
                    <td><strong>{l.description}</strong></td>
                    <td>{l.quantity}</td>
                    <td>₹{Number(l.unit_price).toFixed(2)}</td>
                    <td style={{ color: 'var(--text-muted)' }}>₹{Number(l.tax_amount).toFixed(2)} ({l.tax_rate_pct}%)</td>
                    <td><strong>₹{Number(l.total_amount).toFixed(2)}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <div className="form-card" style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px' }}>Summary</h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Subtotal:</span>
              <span>₹{Number(quotation.subtotal).toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Discounts:</span>
              <span>- ₹{Number(quotation.discount_amount).toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
              <span style={{ color: 'var(--text-muted)' }}>GST / Tax:</span>
              <span>+ ₹{Number(quotation.tax_amount).toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '18px', fontWeight: '700', borderTop: '1px solid var(--border)', paddingTop: '10px', marginTop: '10px' }}>
              <span>Total:</span>
              <span style={{ color: 'var(--primary)' }}>₹{Number(quotation.total_amount).toFixed(2)}</span>
            </div>
          </div>

          <div className="form-card">
            <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '14px' }}>Details</h3>
            <div style={{ marginBottom: '10px', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block' }}>Customer ID:</span>
              <code style={{ fontSize: '12px' }}>{quotation.customer_id}</code>
            </div>
            <div style={{ marginBottom: '10px', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block' }}>Valid Until:</span>
              <strong>{quotation.valid_until ? new Date(quotation.valid_until).toLocaleDateString() : 'No expiry'}</strong>
            </div>
            {quotation.notes && (
              <div style={{ fontSize: '13px' }}>
                <span style={{ color: 'var(--text-muted)', display: 'block' }}>Notes:</span>
                <p style={{ marginTop: '4px', background: '#f8fafc', padding: '8px', borderRadius: '6px' }}>{quotation.notes}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <Modal isOpen={rejectModalOpen} onClose={() => setRejectModalOpen(false)} title="Reject Quotation">
        <form onSubmit={handleReject}>
          <div className="form-group">
            <label className="form-label">Reason for Rejection</label>
            <textarea
              className="form-control"
              rows="3"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="e.g. Price too high, customer chosen alternative vendor..."
              required
            ></textarea>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button type="button" onClick={() => setRejectModalOpen(false)} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={actionLoading} className="btn btn-danger">
              Confirm Rejection
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
