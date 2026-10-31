import React, { useState } from 'react';
import { productApi } from './services/productApi';

export default function ProductForm({ onCancel, onProductCreated }) {
  const [formData, setFormData] = useState({
    name: '',
    type: '',
    sales_price: '',
    cost_price: '0.00',
    currency: 'INR',
    description: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await productApi.createProduct(formData);
      onProductCreated();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Add New Product</h2>
        <button className="btn btn-secondary" onClick={onCancel}>
          Cancel
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Product Name *</label>
            <input
              type="text"
              className="form-control"
              required
              placeholder="e.g. BrightERP Cloud"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Category / Type</label>
            <input
              type="text"
              className="form-control"
              placeholder="e.g. Software, Cloud, Support"
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Base Sales Price *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              className="form-control"
              required
              placeholder="0.00"
              value={formData.sales_price}
              onChange={(e) => setFormData({ ...formData, sales_price: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Cost Price</label>
            <input
              type="number"
              step="0.01"
              min="0"
              className="form-control"
              placeholder="0.00"
              value={formData.cost_price}
              onChange={(e) => setFormData({ ...formData, cost_price: e.target.value })}
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
        </div>

        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea
            className="form-control"
            rows="3"
            placeholder="Details about product features, licensing, and usage..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', marginTop: '1.5rem' }}>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Creating Product...' : 'Create Product'}
          </button>
          <button type="button" className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
