import React, { useState } from 'react';
import ProductList from './ProductList';
import ProductForm from './ProductForm';
import ProductDetail from './ProductDetail';

export default function ProductsPage() {
  const [view, setView] = useState('list'); // 'list' | 'create' | 'detail'
  const [selectedProductId, setSelectedProductId] = useState(null);

  const handleSelectProduct = (id) => {
    setSelectedProductId(id);
    setView('detail');
  };

  return (
    <div>
      {view === 'list' && (
        <ProductList
          onSelectProduct={handleSelectProduct}
          onCreateNew={() => setView('create')}
        />
      )}

      {view === 'create' && (
        <ProductForm
          onCancel={() => setView('list')}
          onProductCreated={() => setView('list')}
        />
      )}

      {view === 'detail' && (
        <ProductDetail
          productId={selectedProductId}
          onBack={() => setView('list')}
          onProductUpdated={() => {}}
        />
      )}
    </div>
  );
}
