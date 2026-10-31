import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';

export default function InvoiceList() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('');
  const [error, setError] = useState(null);

  // Billing Run modal
  const [billingModalOpen, setBillingModalOpen] = useState(false);
  const [billingDate, setBillingDate] = useState(new Date().toISOString().split('T')[0]);
  const [runningBilling, setRunningBilling] = useState(false);
  const [billingResult, setBillingResult] = useState(null);

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const params = filterStatus ? { status: filterStatus } : {};
      const data = await api.getInvoices(params);
      setInvoices(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, [filterStatus]);

  const handleTriggerBilling = async (e) => {
    e.preventDefault();
    try {
      setRunningBilling(true);
      const result = await api.triggerBillingRun(new Date(billingDate).toISOString());
      setBillingResult(result);
      fetchInvoices();
    } catch (err) {
      alert(`Error triggering billing: ${err.message}`);
    } finally {
      setRunningBilling(false);
    }
  };

  const stats = {
    total: invoices.length,
    paid: invoices.filter(i => i.status === 'PAID').length,
    pending: invoices.filter(i => i.status !== 'PAID').length,
    totalAmount: invoices.reduce((sum, i) => sum + Number(i.total_amount), 0),
    balanceDue: invoices.reduce((sum, i) => sum + Number(i.balance_due), 0),
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h2 className="page-title">Invoices & Billing</h2>
          <p className="page-subtitle">Automated recurring billing cycles, receivables, and payment balances</p>
        </div>
        <button onClick={() => { setBillingResult(null); setBillingModalOpen(true); }} className="btn btn-primary">
          ⚡ Run Recurring Billing
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Invoices</div>
          <div className="stat-value">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Paid In Full</div>
          <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.paid}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Total Invoiced</div>
          <div className="stat-value">₹{stats.totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Outstanding Balance</div>
          <div className="stat-value" style={{ color: 'var(--warning)' }}>₹{stats.balanceDue.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</div>
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
              className={`btn btn-sm ${filterStatus === 'CONFIRMED' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('CONFIRMED')}
            >
              Confirmed
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'PARTIALLY_PAID' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('PARTIALLY_PAID')}
            >
              Partially Paid
            </button>
            <button
              className={`btn btn-sm ${filterStatus === 'PAID' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setFilterStatus('PAID')}
            >
              Paid
            </button>
          </div>
        </div>

        {loading ? (
          <div className="empty-state">Loading invoices...</div>
        ) : error ? (
          <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>
        ) : invoices.length === 0 ? (
          <div className="empty-state">No invoices generated yet. Click "Run Recurring Billing" to process active due subscriptions.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Status</th>
                <th>Billing Period</th>
                <th>Total</th>
                <th>Paid</th>
                <th>Balance Due</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((inv) => (
                <tr key={inv.id}>
                  <td><strong>{inv.invoice_number}</strong></td>
                  <td><Badge status={inv.status} /></td>
                  <td style={{ fontSize: '13px' }}>
                    {new Date(inv.billing_period_start).toLocaleDateString()} - {new Date(inv.billing_period_end).toLocaleDateString()}
                  </td>
                  <td><strong>₹{Number(inv.total_amount).toFixed(2)}</strong></td>
                  <td style={{ color: 'var(--success)' }}>₹{Number(inv.amount_paid).toFixed(2)}</td>
                  <td style={{ color: Number(inv.balance_due) > 0 ? 'var(--warning)' : 'var(--text-muted)' }}>
                    <strong>₹{Number(inv.balance_due).toFixed(2)}</strong>
                  </td>
                  <td>
                    <Link to={`/invoices/${inv.id}`} className="btn btn-secondary btn-sm">
                      Details / Pay
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <Modal isOpen={billingModalOpen} onClose={() => setBillingModalOpen(false)} title="Trigger Recurring Billing Run">
        {!billingResult ? (
          <form onSubmit={handleTriggerBilling}>
            <p style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '16px' }}>
              The billing engine evaluates all ACTIVE subscriptions whose next billing date is on or before the selected run date. Idempotency guarantees prevent duplicate billing.
            </p>
            <div className="form-group">
              <label className="form-label">Billing Run Evaluation Date</label>
              <input
                type="date"
                className="form-control"
                value={billingDate}
                onChange={(e) => setBillingDate(e.target.value)}
                required
              />
            </div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button type="button" onClick={() => setBillingModalOpen(false)} className="btn btn-secondary">
                Cancel
              </button>
              <button type="submit" disabled={runningBilling} className="btn btn-primary">
                {runningBilling ? 'Processing Subscriptions...' : 'Start Billing Run'}
              </button>
            </div>
          </form>
        ) : (
          <div>
            <div style={{ padding: '16px', background: 'var(--success-light)', color: 'var(--success)', borderRadius: '8px', marginBottom: '16px' }}>
              <h4 style={{ fontWeight: '700', marginBottom: '6px' }}>Billing Run Completed</h4>
              <p style={{ fontSize: '14px' }}>Batch processed successfully without errors.</p>
            </div>
            <div style={{ fontSize: '14px', lineHeight: '2' }}>
              <div>Subscriptions Evaluated: <strong>{billingResult.subscriptions_evaluated}</strong></div>
              <div>Invoices Generated: <strong>{billingResult.invoices_generated}</strong></div>
              <div>Total Invoiced Amount: <strong>₹{Number(billingResult.total_invoiced_amount).toFixed(2)}</strong></div>
            </div>
            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={() => setBillingModalOpen(false)} className="btn btn-primary">
                Close & View Invoices
              </button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
