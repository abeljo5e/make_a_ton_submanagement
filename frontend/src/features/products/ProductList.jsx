import React, { useState, useEffect } from 'react';
import { productApi } from './services/productApi';

export default function ProductList({ onSelectProduct, onCreateNew }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const loadProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (search) params.search = search;
      if (statusFilter !== '') params.is_active = statusFilter === 'active';
      const data = await productApi.listProducts(params);
      setProducts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadProducts();
  };

  const handleDeactivate = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to deactivate this product?')) return;
    try {
      await productApi.deactivateProduct(id);
      loadProducts();
    } catch (err) {
      alert(`Deactivation failed: ${err.message}`);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Products Management</h2>
        <button className="btn btn-primary" onClick={onCreateNew}>
          + Add Product
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '1rem', marginBottom: '1.25rem' }}>
        <input
          type="text"
          className="form-control"
          placeholder="Search product name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ maxWidth: '300px' }}
        />
        <select
          className="form-control"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{ maxWidth: '160px' }}
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <button type="submit" className="btn btn-secondary">
          Filter
        </button>
      </form>

      {loading ? (
        <p style={{ color: 'var(--gray-500)', padding: '1rem' }}>Loading products...</p>
      ) : products.length === 0 ? (
        <p style={{ color: 'var(--gray-500)', padding: '1rem' }}>No products found.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Category</th>
              <th>Sales Price</th>
              <th>Cost Price</th>
              <th>Variants</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} style={{ cursor: 'pointer' }} onClick={() => onSelectProduct(p.id)}>
                <td>
                  <strong>{p.name}</strong>
                  {p.description && <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>{p.description}</div>}
                </td>
                <td>{p.type || 'Standard'}</td>
                <td>{p.currency} {p.sales_price}</td>
                <td>{p.currency} {p.cost_price}</td>
                <td>{p.variants?.length || 0} variants</td>
                <td>
                  <span className={`badge ${p.status === 'active' ? 'badge-active' : 'badge-inactive'}`}>
                    {p.status}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectProduct(p.id);
                      }}
                    >
                      View / Edit
                    </button>
                    {p.status === 'active' && (
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={(e) => handleDeactivate(p.id, e)}
                      >
                        Deactivate
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
