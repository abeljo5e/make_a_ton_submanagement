import React, { useState, useEffect } from 'react';
import { api } from '../../../lib/api';
import { useAuth } from '../context/AuthContext';
import CreateStaffModal from '../components/CreateStaffModal';

export default function UserManagementPage() {
  const { user: currentUser, isAdmin } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [actionLoadingId, setActionLoadingId] = useState(null);

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      let endpoint = '/users?limit=100';
      if (roleFilter) endpoint += `&role=${roleFilter}`;
      if (search.trim()) endpoint += `&search=${encodeURIComponent(search.trim())}`;
      
      const data = await api.get(endpoint);
      setUsers(data);
    } catch (err) {
      setError(err.message || 'Failed to load user directory.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [roleFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchUsers();
  };

  const handleToggleStatus = async (user) => {
    const newStatus = !user.is_active;
    const confirmPrompt = `Are you sure you want to ${newStatus ? 'activate' : 'deactivate'} user ${user.email}?`;
    if (!window.confirm(confirmPrompt)) return;

    setActionLoadingId(user.id);
    try {
      const updated = await api.patch(`/users/${user.id}/status`, {
        is_active: newStatus,
      });
      setUsers((prev) =>
        prev.map((u) => (u.id === user.id ? { ...u, is_active: updated.is_active } : u))
      );
    } catch (err) {
      alert(err.message || 'Failed to update user status.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleStaffCreated = (newStaff) => {
    setUsers((prev) => [newStaff, ...prev]);
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">User Management</h1>
          <p className="page-subtitle">View and administer registered customers and staff</p>
        </div>

        {isAdmin && (
          <button
            className="btn btn-primary"
            style={{ width: 'auto' }}
            onClick={() => setIsModalOpen(true)}
          >
            + Add Staff Member
          </button>
        )}
      </div>

      {error && (
        <div className="alert alert-error">
          <span>⚠️</span>
          <div>{error}</div>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '1.5rem', padding: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '240px' }}>
            <input
              type="text"
              className="form-input"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name or email..."
            />
          </div>

          <div style={{ minWidth: '180px' }}>
            <select
              className="form-select"
              value={roleFilter}
              onChange={(e) => setRoleFilter(e.target.value)}
            >
              <option value="">All Roles</option>
              <option value="admin">Administrators</option>
              <option value="staff">Internal Staff</option>
              <option value="customer">Customers</option>
            </select>
          </div>

          <button type="submit" className="btn btn-secondary" style={{ width: 'auto' }}>
            Filter
          </button>
        </form>
      </div>

      {/* Users Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Company / Phone</th>
                <th>Status</th>
                <th>Joined</th>
                {isAdmin && <th style={{ textAlign: 'right' }}>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={isAdmin ? 6 : 5} style={{ textAlign: 'center', padding: '3rem' }}>
                    <div className="spinner"></div>
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan={isAdmin ? 6 : 5} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
                    No users matching criteria.
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id}>
                    <td>
                      <div style={{ fontWeight: 600, color: '#ffffff' }}>{u.full_name}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{u.email}</div>
                    </td>
                    <td>
                      <span className={`role-pill role-${u.role}`}>{u.role}</span>
                    </td>
                    <td>
                      <div style={{ color: '#e5e7eb' }}>
                        {u.customer_profile?.company_name || '—'}
                      </div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        {u.customer_profile?.phone || ''}
                      </div>
                    </td>
                    <td>
                      <span className={`status-badge ${u.is_active ? 'status-active' : 'status-inactive'}`}>
                        ● {u.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                    {isAdmin && (
                      <td style={{ textAlign: 'right' }}>
                        {u.id === currentUser?.id ? (
                          <span style={{ fontSize: '0.8rem', color: 'var(--text-sub)' }}>Current User</span>
                        ) : (
                          <button
                            className={`btn ${u.is_active ? 'btn-danger' : 'btn-secondary'}`}
                            style={{ fontSize: '0.75rem', padding: '0.35rem 0.75rem', width: 'auto' }}
                            onClick={() => handleToggleStatus(u)}
                            disabled={actionLoadingId === u.id}
                          >
                            {actionLoadingId === u.id
                              ? 'Updating...'
                              : u.is_active
                              ? 'Deactivate'
                              : 'Activate'}
                          </button>
                        )}
                      </td>
                    )}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <CreateStaffModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onStaffCreated={handleStaffCreated}
      />
    </div>
  );
}
