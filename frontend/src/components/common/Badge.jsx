import React from 'react';

export default function Badge({ status }) {
  const normalized = (status || '').toLowerCase();
  return (
    <span className={`badge badge-${normalized}`}>
      {status}
    </span>
  );
}

