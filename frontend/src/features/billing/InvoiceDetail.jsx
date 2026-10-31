import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../lib/api';
import Badge from '../../components/common/Badge';
import Modal from '../../components/common/Modal';

export default function InvoiceDetail() {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Payment Modal
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState('upi');
  const [payReference, setPayReference] = useState('');
  const [submittingPayment, setSubmittingPayment] = useState(false);

  const fetchInvoiceData = async () => {
    try {
      setLoading(true);
      const invData = await api.getInvoice(id);
      setInvoice(invData);
      setPayAmount(invData.balance_due);

      const payData = await api.getPayments({ invoice_id: id });
      setPayments(payData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoiceData();
  }, [id]);

  const handleRecordPayment = async (e) => {
    e.preventDefault();
    setSubmittingPayment(true);
    try {
      await api.recordPayment({
        invoice_id: id,
        amount: payAmount,
        currency: invoice.currency,
        payment_method: payMethod,
        payment_reference: payReference || `PAY-REF-${Date.now().toString().slice(-6)}`,
      });
      setPaymentModalOpen(false);
      setPayReference('');
      fetchInvoiceData();
    } catch (err) {
      alert(`Error recording payment: ${err.message}`);
    } finally {
      setSubmittingPayment(false);
    }
  };

  if (loading) return <div className="empty-state">Loading invoice details...</div>;
  if (error) return <div className="empty-state" style={{ color: 'var(--danger)' }}>{error}</div>;
  if (!invoice) return <div className="empty-state">Invoice not found</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h2 className="page-title">{invoice.invoice_number}</h2>
            <Badge status={invoice.status} />
          </div>
          <p className="page-subtitle">Due Date: {new Date(invoice.due_date).toLocaleDateString()}</p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/invoices" className="btn btn-secondary">
            &larr; Back to Invoices
          </Link>
          {Number(invoice.balance_due) > 0 && invoice.status !== 'CANCELED' && (
            <button onClick={() => setPaymentModalOpen(true)} className="btn btn-primary" style={{ background: 'var(--success)' }}>
              💳 Record Payment
            </button>
          )}
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
        <div>
          <div className="table-card" style={{ marginBottom: '24px' }}>
            <div className="table-header-bar">
              <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Invoiced Items</h3>
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
                {invoice.lines.map((l) => (
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

          {/* Payment Transactions Table */}
          <div className="table-card">
            <div className="table-header-bar">
              <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Settlement & Payment Records</h3>
            </div>
            {payments.length === 0 ? (
              <div className="empty-state">No payments recorded against this invoice yet.</div>
            ) : (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Payment #</th>
                    <th>Method</th>
                    <th>Reference</th>
                    <th>Date</th>
                    <th>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {payments.map((p) => (
                    <tr key={p.id}>
                      <td><strong>{p.payment_number}</strong></td>
                      <td style={{ textTransform: 'uppercase' }}>{p.payment_method}</td>
                      <td><code>{p.payment_reference}</code></td>
                      <td>{new Date(p.payment_date).toLocaleString()}</td>
                      <td style={{ color: 'var(--success)' }}>
                        <strong>+ ₹{Number(p.amount).toFixed(2)}</strong>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        <div>
          <div className="form-card" style={{ marginBottom: '20px' }}>
            <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '16px' }}>Balance & Receivables</h3>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
              <span style={{ color: 'var(--text-muted)' }}>Total Invoiced:</span>
              <strong>₹{Number(invoice.total_amount).toFixed(2)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', color: 'var(--success)' }}>
              <span>Paid So Far:</span>
              <span>- ₹{Number(invoice.amount_paid).toFixed(2)}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '18px', fontWeight: '700', borderTop: '1px solid var(--border)', paddingTop: '10px', marginTop: '10px' }}>
              <span>Balance Due:</span>
              <span style={{ color: Number(invoice.balance_due) > 0 ? 'var(--warning)' : 'var(--success)' }}>
                ₹{Number(invoice.balance_due).toFixed(2)}
              </span>
            </div>
          </div>

          <div className="form-card">
            <h3 style={{ fontSize: '15px', fontWeight: '700', marginBottom: '14px' }}>Billing Period</h3>
            <div style={{ marginBottom: '10px', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block' }}>Period:</span>
              <span>{new Date(invoice.billing_period_start).toLocaleDateString()} to {new Date(invoice.billing_period_end).toLocaleDateString()}</span>
            </div>
            <div style={{ marginBottom: '10px', fontSize: '13px' }}>
              <span style={{ color: 'var(--text-muted)', display: 'block' }}>Customer ID:</span>
              <code style={{ fontSize: '12px' }}>{invoice.customer_id}</code>
            </div>
          </div>
        </div>
      </div>

      <Modal isOpen={paymentModalOpen} onClose={() => setPaymentModalOpen(false)} title="Record Payment Receipt">
        <form onSubmit={handleRecordPayment}>
          <div className="form-group">
            <label className="form-label">Payment Amount (₹)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              max={invoice.balance_due}
              className="form-control"
              value={payAmount}
              onChange={(e) => setPayAmount(e.target.value)}
              required
            />
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Current balance due: ₹{Number(invoice.balance_due).toFixed(2)}
            </span>
          </div>

          <div className="form-group">
            <label className="form-label">Payment Method</label>
            <select
              className="form-control"
              value={payMethod}
              onChange={(e) => setPayMethod(e.target.value)}
            >
              <option value="upi">UPI (Instant)</option>
              <option value="bank_transfer">NEFT / RTGS Bank Transfer</option>
              <option value="card">Credit / Debit Card</option>
              <option value="simulation">Sandbox / Demo Simulation</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Transaction Reference #</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. UPI-REF-89472"
              value={payReference}
              onChange={(e) => setPayReference(e.target.value)}
              required
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '20px' }}>
            <button type="button" onClick={() => setPaymentModalOpen(false)} className="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={submittingPayment} className="btn btn-primary" style={{ background: 'var(--success)' }}>
              {submittingPayment ? 'Settling Payment...' : 'Confirm Receipt'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
