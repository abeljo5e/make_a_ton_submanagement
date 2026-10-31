import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../lib/api';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';

export default function SubscriptionDetail() {
  const { id } = useParams();
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Cancellation modal
  const [cancelModalOpen, setCancelModalOpen] = useState(false);
  const [cancelReason, setCancelReason] = useState('');

  const fetchSubscription = async () => {
    try {
      setLoading(true);
      const data = await api.getSubscription(id);
      setSubscription(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubscription();
  }, [id]);

  const handlePause = async () => {
    try {
      setActionLoading(true);
      const updated = await api.pauseSubscription(id);
      setSubscription(updated);
    } catch (err) {
      alert(`Error pausing subscription: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResume = async () => {
    try {
      setActionLoading(true);
      const updated = await api.resumeSubscription(id);
      setSubscription(updated);
    } catch (err) {
      alert(`Error resuming subscription: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleCancel = async (e) => {
    e.preventDefault();
    try {
      setActionLoading(true);
      const updated = await api.cancelSubscription(id, cancelReason);
      setSubscription(updated);
      setCancelModalOpen(false);
    } catch (err) {
      alert(`Error canceling subscription: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRenew = async () => {
    try {
      setActionLoading(true);
      const updated = await api.renewSubscription(id);
      setSubscription(updated);
      alert('Subscription renewed successfully! Next billing date advanced.');
    } catch (err) {
      alert(`Error renewing subscription: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) return <div className="empty-state">Loading subscription details...</div>;
  if (error) return <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>;
  if (!subscription) return <div className="empty-state">Subscription not found</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h2 className="page-title">{subscription.subscription_number}</h2>
            <Badge status={subscription.status} />
          </div>
          <p className="page-subtitle">Billing Frequency: <strong style={{ textTransform: 'capitalize' }}>{subscription.billing_frequency}</strong></p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/subscriptions" className="btn btn-secondary">
            &larr; Back to List
          </Link>

          {subscription.status === 'ACTIVE' && (
            <>
              <button onClick={handlePause} disabled={actionLoading} className="btn btn-secondary">
                ⏸ Pause Billing
              </button>
              <button onClick={() => setCancelModalOpen(true)} disabled={actionLoading} className="btn btn-danger">
                ✕ Cancel Subscription
              </button>
            </>
          )}

          {subscription.status === 'PAUSED' && (
            <>
              <button onClick={handleResume} disabled={actionLoading} className="btn btn-primary" style={{ background: 'var(--success)' }}>
                ▶ Resume Subscription
              </button>
              <button onClick={() => setCancelModalOpen(true)} disabled={actionLoading} className="btn btn-danger">
                ✕ Cancel Subscription
              </button>
            </>
          )}

          {subscription.status !== 'CANCELED' && (
            <button onClick={handleRenew} disabled={actionLoading} className="btn btn-secondary">
              🔄 Renew Cycle
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div>
          <div className="table-card" style={{ marginBottom: '24px' }}>
            <div className="table-header-bar">
              <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Subscribed Products & Services</h3>
            </div>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Description</th>
                  <th>Qty</th>
                  <th>Unit Price</th>
                  <th>Tax</th>
                  <th>Recurring Total</th>
                </tr>
              </thead>
              <tbody>
                {subscription.lines.map((l) => (
                  <tr key={l.id}>
                    <td><strong>{l.description}</strong></td>
                    <td>{l.quantity}</td>
                    <td>₹{Number(l.unit_price).toFixed(2)}</td>
                    <td style={{ color: 'var(--text-muted)' }}>₹{Number(l.tax_amount).toFixed(2)}</td>
                    <td><strong>₹{Number(l.total_amount).toFixed(2)}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div>
          <div className="form-card" style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px' }}>Schedule & Billing</h3>
            <div style={{ marginBottom: '10px', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block' }}>Next Billing Date:</span>
              <strong style={{ fontSize: '15px', color: 'var(--primary)' }}>
                {subscription.next_billing_date ? new Date(subscription.next_billing_date).toLocaleDateString() : 'N/A'}
              </strong>
            </div>
            <div style={{ marginBottom: '10px', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block' }}>Start Date:</span>
              <span>{new Date(subscription.start_date).toLocaleDateString()}</span>
            </div>
            <div style={{ marginBottom: '10px', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block' }}>Customer ID:</span>
              <code style={{ fontSize: '12px' }}>{subscription.customer_id}</code>
            </div>
            {subscription.cancellation_reason && (
              <div style={{ marginTop: '12px', padding: '10px', background: 'var(--danger-light)', color: 'var(--danger)', borderRadius: '6px', fontSize: '13px' }}>
                <strong>Cancellation Reason:</strong> {subscription.cancellation_reason}
              </div>
            )}
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '18px', fontWeight: '700', borderTop: '1px solid var(--border)', paddingTop: '10px', marginTop: '14px' }}>
              <span>Recurring Fee:</span>
              <span style={{ color: 'var(--text-main)' }}>₹{Number(subscription.total_amount).toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>

      <Modal isOpen={cancelModalOpen} onClose={() => setCancelModalOpen(false)} title="Cancel Subscription">
        <form onSubmit={handleCancel}>
          <div className="form-group">
            <label className="form-label">Reason for Cancellation</label>
            <textarea
              className="form-control"
              rows="3"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
              placeholder="e.g. Project finished, downsized team, competitor switch..."
              required
            ></textarea>
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
            <button type="button" onClick={() => setCancelModalOpen(false)} className="btn btn-secondary">
              Keep Subscription
            </button>
            <button type="submit" disabled={actionLoading} className="btn btn-danger">
              Cancel Subscription
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
