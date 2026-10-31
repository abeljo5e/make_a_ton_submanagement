import React, { useState } from 'react';
import PlanList from './PlanList';
import PlanForm from './PlanForm';
import PlanDetail from './PlanDetail';

export default function PlansPage() {
  const [view, setView] = useState('list'); // 'list' | 'create' | 'detail'
  const [selectedPlanId, setSelectedPlanId] = useState(null);

  const handleSelectPlan = (id) => {
    setSelectedPlanId(id);
    setView('detail');
  };

  return (
    <div>
      {view === 'list' && (
        <PlanList
          onSelectPlan={handleSelectPlan}
          onCreateNew={() => setView('create')}
        />
      )}

      {view === 'create' && (
        <PlanForm
          onCancel={() => setView('list')}
          onPlanCreated={() => setView('list')}
        />
      )}

      {view === 'detail' && (
        <PlanDetail
          planId={selectedPlanId}
          onBack={() => setView('list')}
          onPlanUpdated={() => {}}
        />
      )}
    </div>
  );
}
