import React, { useState, useEffect } from 'react';
import { planApi } from './services/planApi';
import { productApi } from '../products/services/productApi';

export default function PlanCatalogue() {
  const [plans, setPlans] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [intervalFilter, setIntervalFilter] = useState('all');

  useEffect(() => {
    async function fetchCatalogue() {
      try {
        setLoading(true);
        setError(null);
        // Fetch only available plans and active products
        const [plansData, prodsData] = await Promise.all([
          planApi.listPlans({ available_only: true, is_active: true }),
          productApi.listProducts({ is_active: true }),
        ]);
        setPlans(plansData);
        setAllProducts(prodsData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchCatalogue();
  }, []);

  const filteredPlans = plans.filter((p) => {
    if (intervalFilter === 'all') return true;
    return p.billing_frequency.toLowerCase() === intervalFilter.toLowerCase();
  });

  return (
    <div>
      <div style={{ textAlign: 'center', marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--gray-900)', marginBottom: '0.5rem' }}>
          Choose the Perfect Subscription Plan
        </h1>
        <p style={{ color: 'var(--gray-500)', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto 1.5rem auto' }}>
          Transparent pricing designed for growing businesses. Select a billing interval that fits your budget.
        </p>

        {/* Interval Selector Tabs */}
        <div style={{ display: 'inline-flex', background: 'var(--gray-200)', padding: '0.25rem', borderRadius: '9999px' }}>
          {['all', 'monthly', 'yearly', 'quarterly'].map((interval) => (
            <button
              key={interval}
              onClick={() => setIntervalFilter(interval)}
              style={{
                border: 'none',
                background: intervalFilter === interval ? 'white' : 'transparent',
                color: intervalFilter === interval ? 'var(--primary)' : 'var(--gray-700)',
                padding: '0.4rem 1.25rem',
                borderRadius: '9999px',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                boxShadow: intervalFilter === interval ? 'var(--shadow)' : 'none',
                transition: 'all 0.2s',
                textTransform: 'capitalize',
              }}
            >
              {interval === 'all' ? 'All Plans' : interval}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      {loading ? (
        <p style={{ textAlign: 'center', color: 'var(--gray-500)', padding: '2rem' }}>
          Loading subscription catalogue...
        </p>
      ) : filteredPlans.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--gray-500)', fontSize: '1.1rem' }}>
            No active subscription plans found for this interval.
          </p>
        </div>
      ) : (
        <div className="catalogue-grid">
          {filteredPlans.map((plan) => (
            <div key={plan.id} className="plan-card">
              <h3 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--gray-900)' }}>
                {plan.name}
              </h3>

              <div className="plan-price-box">
                <span className="plan-price">
                  {plan.currency} {plan.price}
                </span>
                <span className="plan-interval">/ {plan.billing_frequency}</span>
              </div>

              {plan.description && (
                <p style={{ color: 'var(--gray-500)', fontSize: '0.9rem', marginBottom: '1rem', minHeight: '40px' }}>
                  {plan.description}
                </p>
              )}

              <hr style={{ border: 'none', borderTop: '1px solid var(--gray-100)', margin: '1rem 0' }} />

              <div style={{ fontWeight: 600, fontSize: '0.85rem', color: 'var(--gray-700)', marginBottom: '0.5rem' }}>
                Included Products & Features:
              </div>

              <ul className="plan-features">
                {plan.products?.length > 0 ? (
                  plan.products.map((item, idx) => {
                    const matchedProd = allProducts.find((p) => p.id === item.product_id);
                    return (
                      <li key={`${item.product_id}-${idx}`}>
                        <span style={{ color: 'var(--success)', fontWeight: 700 }}>&#10003;</span>
                        <span>
                          {matchedProd ? matchedProd.name : 'Software License'}{' '}
                          {item.quantity > 1 && `(${item.quantity} units)`}
                        </span>
                      </li>
                    );
                  })
                ) : (
                  <li style={{ color: 'var(--gray-500)' }}>Full platform access</li>
                )}

                {plan.allow_renewal && (
                  <li>
                    <span style={{ color: 'var(--success)', fontWeight: 700 }}>&#10003;</span>
                    <span>Guaranteed renewal pricing</span>
                  </li>
                )}
                {plan.allow_pause && (
                  <li>
                    <span style={{ color: 'var(--success)', fontWeight: 700 }}>&#10003;</span>
                    <span>Pause subscription anytime</span>
                  </li>
                )}
                {plan.allow_early_cancellation && (
                  <li>
                    <span style={{ color: 'var(--success)', fontWeight: 700 }}>&#10003;</span>
                    <span>No lock-in / cancel anytime</span>
                  </li>
                )}
              </ul>

              <div style={{ marginTop: 'auto', paddingTop: '1.5rem' }}>
                <button
                  className="btn btn-primary"
                  style={{ width: '100%', padding: '0.75rem', fontWeight: 600 }}
                  onClick={() => alert(`Selected plan: ${plan.name}. Proceed to Quotations / Subscriptions (Member 3 module).`)}
                >
                  Choose {plan.name}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
