import React, { useState, useEffect } from 'react';
import { planApi } from './services/planApi';

export default function PlanList({ onSelectPlan, onCreateNew }) {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');
  const [frequencyFilter, setFrequencyFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const loadPlans = async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {};
      if (search) params.search = search;
      if (frequencyFilter) params.billing_frequency = frequencyFilter;
      if (statusFilter !== '') params.is_active = statusFilter === 'active';
      const data = await planApi.listPlans(params);
      setPlans(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlans();
  }, [frequencyFilter, statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    loadPlans();
  };

  const handleDeactivate = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to deactivate this plan? Existing subscriptions will remain intact.')) return;
    try {
      await planApi.deactivatePlan(id);
      loadPlans();
    } catch (err) {
      alert(`Deactivation failed: ${err.message}`);
    }
  };

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">Subscription Plans Management</h2>
        <button className="btn btn-primary" onClick={onCreateNew}>
          + Create Plan
        </button>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
        <input
          type="text"
          className="form-control"
          placeholder="Search plan name..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ maxWidth: '280px' }}
        />
        <select
          className="form-control"
          value={frequencyFilter}
          onChange={(e) => setFrequencyFilter(e.target.value)}
          style={{ maxWidth: '170px' }}
        >
          <option value="">All Intervals</option>
          <option value="monthly">Monthly</option>
          <option value="yearly">Yearly</option>
          <option value="quarterly">Quarterly</option>
          <option value="weekly">Weekly</option>
        </select>
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
        <p style={{ color: 'var(--gray-500)', padding: '1rem' }}>Loading subscription plans...</p>
      ) : plans.length === 0 ? (
        <p style={{ color: 'var(--gray-500)', padding: '1rem' }}>No subscription plans found.</p>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>Plan Name</th>
              <th>Billing Interval</th>
              <th>Price</th>
              <th>Bundled Products</th>
              <th>Availability Window</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {plans.map((p) => (
              <tr key={p.id} style={{ cursor: 'pointer' }} onClick={() => onSelectPlan(p.id)}>
                <td>
                  <strong>{p.name}</strong>
                  {p.description && <div style={{ fontSize: '0.8rem', color: 'var(--gray-500)' }}>{p.description}</div>}
                </td>
                <td style={{ textTransform: 'capitalize' }}>{p.billing_frequency}</td>
                <td>{p.currency} {p.price}</td>
                <td>{p.products?.length || 0} product(s)</td>
                <td style={{ fontSize: '0.85rem', color: 'var(--gray-700)' }}>
                  {p.available_from ? p.available_from : 'Immediate'} &rarr;{' '}
                  {p.available_until ? p.available_until : 'Ongoing'}
                </td>
                <td>
                  <span className={`badge ${p.is_active ? 'badge-active' : 'badge-inactive'}`}>
                    {p.is_active ? 'active' : 'inactive'}
                  </span>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelectPlan(p.id);
                      }}
                    >
                      Manage
                    </button>
                    {p.is_active && (
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
