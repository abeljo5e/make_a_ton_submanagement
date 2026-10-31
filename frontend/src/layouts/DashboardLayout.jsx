import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';

export default function DashboardLayout() {
  return (
    <div className="app-container">
      <Navbar />
      <main style={{ flex: 1 }}>
        <Outlet />
      </main>
    </div>
  );
}
