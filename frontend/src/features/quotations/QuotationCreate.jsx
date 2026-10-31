import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../../lib/api';

export default function QuotationCreate() {
  const navigate = useNavigate();
  const [customerId, setCustomerId] = useState('c1000000-0000-0000-0000-000000000001');
  const [validUntilDays, setValidUntilDays] = useState(30);
  const [notes, setNotes] = useState('Brightloop Software Annual Subscription Proposal');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const [lines, setLines] = useState([
    {
      description: 'Brightloop Cloud ERP - Professional Edition',
      quantity: 1,
      unit_price: '2500.00',
      discount_pct: '10.00',
      tax_rate_pct: '18.00',
    },
  ]);

  const addLine = () => {
    setLines([
      ...lines,
      {
        description: 'Add-on Module / Service',
        quantity: 1,
        unit_price: '500.00',
        discount_pct: '0.00',
        tax_rate_pct: '18.00',
      },
    ]);
  };

  const removeLine = (index) => {
    if (lines.length > 1) {
      setLines(lines.filter((_, i) => i !== index));
    }
  };

  const updateLine = (index, field, value) => {
    const updated = [...lines];
    updated[index][field] = value;
    setLines(updated);
  };

  // Live calculation of totals
  const calculatedTotals = lines.reduce(
    (acc, line) => {
      const qty = Number(line.quantity) || 0;
      const price = Number(line.unit_price) || 0;
      const discPct = Number(line.discount_pct) || 0;
      const taxPct = Number(line.tax_rate_pct) || 0;

      const sub = qty * price;
      const disc = sub * (discPct / 100);
      const taxable = sub - disc;
      const tax = taxable * (taxPct / 100);
      const total = taxable + tax;

      return {
        subtotal: acc.subtotal + sub,
        discount: acc.discount + disc,
        tax: acc.tax + tax,
        total: acc.total + total,
      };
    },
    { subtotal: 0, discount: 0, tax: 0, total: 0 }
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    const validUntilDate = new Date();
    validUntilDate.setDate(validUntilDate.getDate() + Number(validUntilDays));

    const payload = {
      customer_id: customerId,
      currency: 'INR',
      valid_until: validUntilDate.toISOString(),
      notes: notes,
      lines: lines.map((l) => ({
        description: l.description,
        quantity: Number(l.quantity),
        unit_price: l.unit_price,
        discount_pct: l.discount_pct,
        tax_rate_pct: l.tax_rate_pct,
      })),
    };

    try {
      const created = await api.createQuotation(payload);
      navigate(`/quotations/${created.id}`);
    } catch (err) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="page-header">
        <div>
          <h2 className="page-title">Draft New Quotation</h2>
          <p className="page-subtitle">Configure proposal items, discounts, and customer tax rates</p>
        </div>
        <Link to="/quotations" className="btn btn-secondary">
          Cancel
        </Link>
      </div>

      {error && (
        <div style={{ padding: '12px 16px', background: 'var(--danger-light)', color: 'var(--danger)', borderRadius: '6px', marginBottom: '20px', fontWeight: '500' }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="form-card">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Customer UUID</label>
            <input
              type="text"
              className="form-control"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label className="form-label">Validity Window (Days)</label>
            <input
              type="number"
              min="1"
              max="365"
              className="form-control"
              value={validUntilDays}
              onChange={(e) => setValidUntilDays(e.target.value)}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Quotation Notes / Terms</label>
          <input
            type="text"
            className="form-control"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
        </div>

        <div style={{ marginTop: '28px', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Line Items</h3>
          <button type="button" onClick={addLine} className="btn btn-secondary btn-sm">
            + Add Line
          </button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
          {lines.map((line, idx) => (
            <div
              key={idx}
              style={{
                display: 'grid',
                gridTemplateColumns: '3fr 1fr 1.5fr 1fr 1fr auto',
                gap: '10px',
                alignItems: 'center',
                padding: '12px',
                background: '#f8fafc',
                borderRadius: '8px',
                border: '1px solid var(--border)',
              }}
            >
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Description</label>
                <input
                  type="text"
                  className="form-control"
                  value={line.description}
                  onChange={(e) => updateLine(idx, 'description', e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Qty</label>
                <input
                  type="number"
                  min="1"
                  className="form-control"
                  value={line.quantity}
                  onChange={(e) => updateLine(idx, 'quantity', e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Unit Price (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-control"
                  value={line.unit_price}
                  onChange={(e) => updateLine(idx, 'unit_price', e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Disc %</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  className="form-control"
                  value={line.discount_pct}
                  onChange={(e) => updateLine(idx, 'discount_pct', e.target.value)}
                  required
                />
              </div>
              <div>
                <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block' }}>Tax %</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-control"
                  value={line.tax_rate_pct}
                  onChange={(e) => updateLine(idx, 'tax_rate_pct', e.target.value)}
                  required
                />
              </div>
              <button
                type="button"
                onClick={() => removeLine(idx)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--danger)',
                  cursor: 'pointer',
                  fontSize: '18px',
                  padding: '8px',
                }}
                disabled={lines.length === 1}
              >
                &times;
              </button>
            </div>
          ))}
        </div>

        {/* Live Calculation Summary */}
        <div style={{ background: '#f1f5f9', padding: '16px 20px', borderRadius: '8px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px' }}>
            <span>Subtotal:</span>
            <span>₹{calculatedTotals.subtotal.toFixed(2)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>
            <span>Discount:</span>
            <span>- ₹{calculatedTotals.discount.toFixed(2)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '14px', color: 'var(--text-muted)' }}>
            <span>GST / Tax:</span>
            <span>+ ₹{calculatedTotals.tax.toFixed(2)}</span>
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '18px', fontWeight: '700', borderTop: '1px solid var(--border)', paddingTop: '8px' }}>
            <span>Estimated Total:</span>
            <span style={{ color: 'var(--primary)' }}>₹{calculatedTotals.total.toFixed(2)}</span>
          </div>
        </div>

        <button type="submit" disabled={submitting} className="btn btn-primary" style={{ width: '100%', justifyContent: 'center' }}>
          {submitting ? 'Generating Proposal...' : 'Create Quotation'}
        </button>
      </form>
    </div>
  );
}

