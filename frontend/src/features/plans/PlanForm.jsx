import React, { useState, useEffect } from 'react';
import { planApi } from './services/planApi';
import { productApi } from '../products/services/productApi';

export default function PlanForm({ onCancel, onPlanCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    currency: 'INR',
    billing_frequency: 'monthly',
    minimum_quantity: 1,
    available_from: '',
    available_until: '',
    auto_close: true,
    allow_early_cancellation: true,
    allow_pause: true,
    allow_renewal: true,
  });

  const [availableProducts, setAvailableProducts] = useState([]);
  const [selectedProductIds, setSelectedProductIds] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    productApi.listProducts({ is_active: true })
      .then((data) => setAvailableProducts(data))
      .catch((err) => console.error('Failed to load products for bundling:', err));
  }, []);

  const handleProductToggle = (prodId) => {
    if (selectedProductIds.includes(prodId)) {
      setSelectedProductIds(selectedProductIds.filter((id) => id !== prodId));
    } else {
      setSelectedProductIds([...selectedProductIds, prodId]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);

      const productsPayload = selectedProductIds.map((id) => ({
        product_id: id,
        quantity: 1,
      }));

      const payload = {
        ...formData,
        available_from: formData.available_from || null,
        available_until: formData.available_until || null,
        products: productsPayload,
      };

      await planApi.createPlan(payload);
      onPlanCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Create Subscription Plan</h2>
        <button className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Plan Name *</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="e.g. Professional Monthly"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Billing Interval *</label>
            <select
              className="form-control"
              value={formData.billing_frequency}
              onChange={(e) => setFormData({ ...formData, billing_frequency: e.target.value })}
            >
              <option value="monthly">Monthly</option>
              <option value="yearly">Yearly</option>
              <option value="quarterly">Quarterly</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Recurring Price *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              className="form-control"
              required
              placeholder="0.00"
              value={formData.price}
              onChange={(e) => setFormData({ ...formData, price: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Currency</label>
            <input
              type="text"
              maxLength={3}
              className="form-control"
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value.toUpperCase() })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Minimum Quantity</label>
            <input
              type="number"
              min="1"
              className="form-control"
              value={formData.minimum_quantity}
              onChange={(e) => setFormData({ ...formData, minimum_quantity: parseInt(e.target.value, 10) })}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Available From</label>
            <input
              type="date"
              className="form-control"
              value={formData.available_from}
              onChange={(e) => setFormData({ ...formData, available_from: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Available Until</label>
            <input
              type="date"
              className="form-control"
              value={formData.available_until}
              onChange={(e) => setFormData({ ...formData, available_until: e.target.value })}
            />
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Bundle Included Products</label>
          <div style={{ maxHeight: '140px', overflowY: 'auto', border: '1px solid var(--gray-200)', borderRadius: 'var(--radius)', padding: '0.75rem', background: 'var(--gray-50)' }}>
            {availableProducts.length === 0 ? (
              <p style={{ color: 'var(--gray-500)', fontSize: '0.85rem' }}>No active products available to bundle.</p>
            ) : (
              availableProducts.map((p) => (
                <label key={p.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem', fontSize: '0.875rem' }}>
                  <input
                    type="checkbox"
                    checked={selectedProductIds.includes(p.id)}
                    onChange={() => handleProductToggle(p.id)}
                  />
                  {p.name} ({p.currency} {p.sales_price})
                </label>
              ))
            )}
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Plan Description</label>
          <textarea
            className="form-control"
            rows="3"
            placeholder="Details on what this plan covers, SLAs, user limits..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating Plan...' : 'Create Plan'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
