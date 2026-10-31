import React, { useState, useEffect } from 'react';
import { productApi } from './services/productApi';

export default function ProductDetail({ productId, onBack, onProductUpdated }) {
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit product form state
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: '',
    sales_price: '',
    cost_price: '',
    currency: 'INR',
  });

  // Variant create form state
  const [showVariantForm, setShowVariantForm] = useState(false);
  const [variantData, setVariantData] = useState({
    name: '',
    description: '',
    additional_price: '0.00',
  });

  const loadProduct = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await productApi.getProduct(productId);
      setProduct(data);
      setFormData({
        name: data.name,
        description: data.description || '',
        type: data.type || '',
        sales_price: data.sales_price,
        cost_price: data.cost_price,
        currency: data.currency,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (productId) loadProduct();
  }, [productId]);

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    try {
      await productApi.updateProduct(productId, formData);
      setIsEditing(false);
      loadProduct();
      if (onProductUpdated) onProductUpdated();
    } catch (err) {
      alert(`Update failed: ${err.message}`);
    }
  };

  const handleCreateVariant = async (e) => {
    e.preventDefault();
    try {
      await productApi.createVariant(productId, variantData);
      setShowVariantForm(false);
      setVariantData({ name: '', description: '', additional_price: '0.00' });
      loadProduct();
    } catch (err) {
      alert(`Failed to add variant: ${err.message}`);
    }
  };

  const handleDeactivateVariant = async (variantId) => {
    if (!window.confirm('Deactivate this variant?')) return;
    try {
      await productApi.deactivateVariant(variantId);
      loadProduct();
    } catch (err) {
      alert(`Deactivation failed: ${err.message}`);
    }
  };

  if (loading) return <div className="card">Loading product details...</div>;
  if (error) return <div className="card"><div className="alert alert-danger">{error}</div><button className="btn btn-secondary" onClick={onBack}>Back</button></div>;
  if (!product) return null;

  return (
    <div>
      <div style={{ marginBottom: '1rem' }}>
        <button className="btn btn-secondary" onClick={onBack}>
          &larr; Back to Products
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            {product.name}
            <span className={`badge ${product.status === 'active' ? 'badge-active' : 'badge-inactive'}`} style={{ marginLeft: '0.75rem' }}>
              {product.status}
            </span>
          </h2>
          <button className="btn btn-secondary btn-sm" onClick={() => setIsEditing(!isEditing)}>
            {isEditing ? 'Cancel Edit' : 'Edit Product'}
          </button>
        </div>

        {isEditing ? (
          <form onSubmit={handleUpdateProduct}>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Product Name *</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Category / Type</label>
                <input
                  type="text"
                  className="form-control"
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Sales Price *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-control"
                  required
                  value={formData.sales_price}
                  onChange={(e) => setFormData({ ...formData, sales_price: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Cost Price *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-control"
                  required
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
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <button type="submit" className="btn btn-primary">
              Save Changes
            </button>
          </form>
        ) : (
          <div>
            <div className="form-row" style={{ marginBottom: '1rem' }}>
              <div>
                <strong>Sales Price:</strong> {product.currency} {product.sales_price}
              </div>
              <div>
                <strong>Cost Price:</strong> {product.currency} {product.cost_price}
              </div>
              <div>
                <strong>Category:</strong> {product.type || 'None'}
              </div>
            </div>
            {product.description && (
              <p style={{ color: 'var(--gray-700)', marginBottom: '1rem' }}>
                {product.description}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Product Variants Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Product Variants</h3>
          <button className="btn btn-primary btn-sm" onClick={() => setShowVariantForm(!showVariantForm)}>
            {showVariantForm ? 'Cancel' : '+ Add Variant'}
          </button>
        </div>

        {showVariantForm && (
          <form onSubmit={handleCreateVariant} style={{ background: 'var(--gray-50)', padding: '1rem', borderRadius: 'var(--radius)', marginBottom: '1.5rem' }}>
            <h4 style={{ marginBottom: '0.75rem', fontSize: '0.95rem' }}>New Variant</h4>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Variant Name *</label>
                <input
                  type="text"
                  className="form-control"
                  required
                  value={variantData.name}
                  onChange={(e) => setVariantData({ ...variantData, name: e.target.value })}
                  placeholder="e.g. 100 Users License, Dedicated IP"
                />
              </div>
              <div className="form-group">
                <label className="form-label">Additional Price *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-control"
                  required
                  value={variantData.additional_price}
                  onChange={(e) => setVariantData({ ...variantData, additional_price: e.target.value })}
                />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Variant Description</label>
              <input
                type="text"
                className="form-control"
                value={variantData.description}
                onChange={(e) => setVariantData({ ...variantData, description: e.target.value })}
              />
            </div>
            <button type="submit" className="btn btn-primary btn-sm">
              Create Variant
            </button>
          </form>
        )}

        {product.variants?.length === 0 ? (
          <p style={{ color: 'var(--gray-500)' }}>No variants defined for this product.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Variant Name</th>
                <th>Additional Price</th>
                <th>Description</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {product.variants.map((v) => (
                <tr key={v.id}>
                  <td><strong>{v.name}</strong></td>
                  <td>+{product.currency} {v.additional_price}</td>
                  <td>{v.description || '—'}</td>
                  <td>
                    <span className={`badge ${v.is_active ? 'badge-active' : 'badge-inactive'}`}>
                      {v.is_active ? 'active' : 'inactive'}
                    </span>
                  </td>
                  <td>
                    {v.is_active && (
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleDeactivateVariant(v.id)}
                      >
                        Deactivate
                      </button>
                    )}
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
