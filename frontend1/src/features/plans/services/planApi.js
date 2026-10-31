import { api } from '../../../lib/api';

export const planApi = {
  listPlans: (params = {}) => {
    const query = new URLSearchParams();
    if (params.billing_frequency) query.append('billing_frequency', params.billing_frequency);
    if (params.is_active !== undefined) query.append('is_active', params.is_active);
    if (params.search) query.append('search', params.search);
    if (params.available_only) query.append('available_only', 'true');
    const qs = query.toString();
    return api.get(`/plans${qs ? `?${qs}` : ''}`);
  },

  getPlan: (id) => api.get(`/plans/${id}`),

  createPlan: (data) => api.post('/plans', data),

  updatePlan: (id, data) => api.patch(`/plans/${id}`, data),

  deactivatePlan: (id) => api.post(`/plans/${id}/deactivate`),

  addProductsToPlan: (planId, products) => api.post(`/plans/${planId}/products`, products),

  removeProductFromPlan: (planId, productId, variantId = null) => {
    const qs = variantId ? `?variant_id=${variantId}` : '';
    return api.delete(`/plans/${planId}/products/${productId}${qs}`);
  },
};
