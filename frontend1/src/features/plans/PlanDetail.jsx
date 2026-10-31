import React, { useState, useEffect } from 'react';
import { planApi } from './services/planApi';
import { productApi } from '../products/services/productApi';

export default function PlanDetail({ planId, onBack, onPlanUpdated }) {
  const [plan, setPlan] = useState(null);
  const [availableProducts, setAvailableProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit basic settings state
  const [isEditing, setIsEditing] = useState(false);
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

  // Bundle product form state
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [bundleForm, setBundleForm] = useState({
    product_id: '',
    variant_id: '',
    quantity: 1,
  });

  const loadPlanData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [planData, productsList] = await Promise.all([
        planApi.getPlan(planId),
        productApi.listProducts({ is_active: true }),
      ]);
      setPlan(planData);
      setAvailableProducts(productsList);

      setFormData({
        name: planData.name,
        description: planData.description || '',
        price: planData.price,
        currency: planData.currency || 'INR',
        billing_frequency: planData.billing_frequency,
        minimum_quantity: planData.minimum_quantity || 1,
        available_from: planData.available_from || '',
        available_until: planData.available_until || '',
        auto_close: planData.auto_close ?? true,
        allow_early_cancellation: planData.allow_early_cancellation ?? true,
        allow_pause: planData.allow_pause ?? true,
        allow_renewal: planData.allow_renewal ?? true,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (planId) loadPlanData();
  }, [planId]);

  const handleUpdatePlan = async (e) => {
    e.preventDefault();
    try {
      await planApi.updatePlan(planId, formData);
      setIsEditing(false);
      loadPlanData();
      if (onPlanUpdated) onPlanUpdated();
    } catch (err) {
      alert(`Plan update failed: ${err.message}`);
    }
  };

  const handleAddProductToPlan = async (e) => {
    e.preventDefault();
    if (!bundleForm.product_id) {
      alert('Please select a product');
      return;
    }
    try {
      const payload = [{
        product_id: bundleForm.product_id,
        variant_id: bundleForm.variant_id || null,
        quantity: parseInt(bundleForm.quantity, 10) || 1,
      }];
      await planApi.addProductsToPlan(planId, payload);
      setShowAddProduct(false);
      setBundleForm({ product_id: '', variant_id: '', quantity: 1 });
      loadPlanData();
    } catch (err) {
      alert(`Failed to add product bundle: ${err.message}`);
    }
  };

  const handleRemoveProduct = async (productId, variantId) => {
    if (!window.confirm('Remove this product from the plan bundle?')) return;
    try {
      await planApi.removeProductFromPlan(planId, productId, variantId);
      loadPlanData();
    } catch (err) {
      alert(`Remove failed: ${err.message}`);
    }
  };

  // Selected product variants for dropdown
  const selectedProductObj = availableProducts.find((p) => p.id === bundleForm.product_id);
  const selectedVariants = selectedProductObj?.variants || [];

  if (loading) return <div className="card">Loading plan details...</div>;
  if (error) return <div className="card"><div className="alert alert-danger">{error}</div><button className="btn btn-secondary" onClick={onBack}>Back</button></div>;
  if (!plan) return null;

  return (
    <div>
      <div style={{ marginBottom: '1rem' }}>
        <button className="btn btn-secondary" onClick={onBack}>
          &larr; Back to Plans
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <h2 className="card-title">
            {plan.name}
            <span className={`badge ${plan.is_active ? 'badge-active' : 'badge-inactive'}`} style={{ marginLeft: '0.75rem' }}>
              {plan.is_active ? 'active' : 'inactive'}
            </span>
          </h2>
          <button className="btn btn-secondary btn-sm" onClick={() => setIsEditing(!isEditing)}>
            {isEditing ? 'Cancel Edit' : 'Edit Plan Configuration'}
          </button>
        </div>

        {isEditing ? (
          <form onSubmit={handleUpdatePlan}>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Plan Name *</label>
                <input
                  type="text"
                  className="form-control"
                  required
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
                  <option value="daily">Daily</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Price *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  className="form-control"
                  required
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
                  value={formData.available_from || ''}
                  onChange={(e) => setFormData({ ...formData, available_from: e.target.value || null })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Available Until</label>
                <input
                  type="date"
                  className="form-control"
                  value={formData.available_until || ''}
                  onChange={(e) => setFormData({ ...formData, available_until: e.target.value || null })}
                />
              </div>
            </div>

            <div className="form-group" style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', margin: '1rem 0' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem' }}>
                <input
                  type="checkbox"
                  checked={formData.allow_renewal}
                  onChange={(e) => setFormData({ ...formData, allow_renewal: e.target.checked })}
                />
                Allow Renewal
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem' }}>
                <input
                  type="checkbox"
                  checked={formData.allow_pause}
                  onChange={(e) => setFormData({ ...formData, allow_pause: e.target.checked })}
                />
                Allow Pause
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem' }}>
                <input
                  type="checkbox"
                  checked={formData.allow_early_cancellation}
                  onChange={(e) => setFormData({ ...formData, allow_early_cancellation: e.target.checked })}
                />
                Allow Cancellation
              </label>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.875rem' }}>
                <input
                  type="checkbox"
                  checked={formData.auto_close}
                  onChange={(e) => setFormData({ ...formData, auto_close: e.target.checked })}
                />
                Auto Close
              </label>
            </div>

            <div className="form-group">
              <label className="form-label">Plan Description</label>
              <textarea
                className="form-control"
                rows="3"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <button type="submit" className="btn btn-primary">
              Save Plan
            </button>
          </form>
        ) : (
          <div>
            <div className="form-row" style={{ marginBottom: '1.25rem' }}>
              <div>
                <strong>Recurring Price:</strong> {plan.currency} {plan.price} / {plan.billing_frequency}
              </div>
              <div>
                <strong>Min Quantity:</strong> {plan.minimum_quantity}
              </div>
              <div>
                <strong>Availability:</strong> {plan.available_from || 'Immediate'} &rarr; {plan.available_until || 'Indefinite'}
              </div>
            </div>
            {plan.description && <p style={{ color: 'var(--gray-700)', marginBottom: '1rem' }}>{plan.description}</p>}
          </div>
        )}
      </div>

      {/* Included Products Bundling Section */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Included Products & Bundles</h3>
          <button className="btn btn-primary btn-sm" onClick={() => setShowAddProduct(!showAddProduct)}>
            {showAddProduct ? 'Cancel' : '+ Bundle Product'}
          </button>
        </div>

        {showAddProduct && (
          <form onSubmit={handleAddProductToPlan} style={{ background: 'var(--gray-50)', padding: '1rem', borderRadius: 'var(--radius)', marginBottom: '1.5rem' }}>
            <h4 style={{ marginBottom: '0.75rem', fontSize: '0.95rem' }}>Add Product to Plan</h4>
            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Select Product *</label>
                <select
                  className="form-control"
                  required
                  value={bundleForm.product_id}
                  onChange={(e) => setBundleForm({ ...bundleForm, product_id: e.target.value, variant_id: '' })}
                >
                  <option value="">-- Choose a Product --</option>
                  {availableProducts.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.currency} {p.sales_price})
                    </option>
                  ))}
                </select>
              </div>

              {selectedVariants.length > 0 && (
                <div className="form-group">
                  <label className="form-label">Select Variant (Optional)</label>
                  <select
                    className="form-control"
                    value={bundleForm.variant_id}
                    onChange={(e) => setBundleForm({ ...bundleForm, variant_id: e.target.value })}
                  >
                    <option value="">-- Base Product (No Variant) --</option>
                    {selectedVariants.map((v) => (
                      <option key={v.id} value={v.id}>
                        {v.name} (+{v.additional_price})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="form-group">
                <label className="form-label">Quantity</label>
                <input
                  type="number"
                  min="1"
                  className="form-control"
                  value={bundleForm.quantity}
                  onChange={(e) => setBundleForm({ ...bundleForm, quantity: e.target.value })}
                />
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-sm">
              Add to Bundle
            </button>
          </form>
        )}

        {plan.products?.length === 0 ? (
          <p style={{ color: 'var(--gray-500)' }}>No products bundled in this plan yet.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Product ID</th>
                <th>Variant ID</th>
                <th>Quantity Included</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {plan.products.map((item, idx) => {
                const prodMatch = availableProducts.find((p) => p.id === item.product_id);
                return (
                  <tr key={`${item.product_id}-${item.variant_id || idx}`}>
                    <td>
                      <strong>{prodMatch ? prodMatch.name : item.product_id}</strong>
                    </td>
                    <td>{item.variant_id || 'Base Product'}</td>
                    <td>{item.quantity} unit(s)</td>
                    <td>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleRemoveProduct(item.product_id, item.variant_id)}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
