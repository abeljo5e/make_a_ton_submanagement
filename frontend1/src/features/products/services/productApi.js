import { api } from '../../../lib/api';

export const productApi = {
  listProducts: (params = {}) => {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.is_active !== undefined) query.append('is_active', params.is_active);
    if (params.search) query.append('search', params.search);
    const qs = query.toString();
    return api.get(`/products${qs ? `?${qs}` : ''}`);
  },

  getProduct: (id) => api.get(`/products/${id}`),

  createProduct: (data) => api.post('/products', data),

  updateProduct: (id, data) => api.patch(`/products/${id}`, data),

  deactivateProduct: (id) => api.post(`/products/${id}/deactivate`),

  // Variants
  createVariant: (productId, data) => api.post(`/products/${productId}/variants`, data),

  updateVariant: (variantId, data) => api.patch(`/variants/${variantId}`, data),

  deactivateVariant: (variantId) => api.delete(`/variants/${variantId}`),
};
