/**
 * User Management Page (Admin Only)
 * ABBK Professional Theme - Clean B2B SaaS Design
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users,
  Plus,
  Edit2,
  Trash2,
  Shield,
  Mail,
  User as UserIcon,
  Lock,
  AlertCircle,
  Check,
  X,
  UserCheck,
  UserX,
  ChevronDown,
} from 'lucide-react';
import { api } from '../services/api';

const ROLES = [
  { value: 'admin', label: 'Admin', description: 'Full access + user management', icon: '👑' },
  { value: 'manager', label: 'Manager', description: 'All leads + scores + reports', icon: '📊' },
  { value: 'sales', label: 'Sales', description: 'Assigned leads only', icon: '💼' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access', icon: '👁️' },
];

const ROLE_BADGES = {
  admin: 'bg-purple-100 text-purple-700 border-purple-200',
  manager: 'bg-blue-100 text-blue-700 border-blue-200',
  sales: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  viewer: 'bg-neutral-100 text-neutral-700 border-neutral-200',
};

export default function UserManagement() {
  const [users, setUsers] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [showApproveModal, setShowApproveModal] = useState(false);
  const [approvingUser, setApprovingUser] = useState(null);

  useEffect(() => {
    fetchUsers();
    fetchPendingUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await api.get('/users/');
      setUsers(response.filter(u => u.is_active));
      setError('');
    } catch (err) {
      setError('Failed to load users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingUsers = async () => {
    try {
      const response = await api.get('/users/pending');
      setPendingUsers(response);
    } catch (err) {
      console.error('Failed to load pending users:', err);
    }
  };

  const handleCreateUser = () => {
    setEditingUser(null);
    setShowCreateModal(true);
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setShowCreateModal(true);
  };

  const handleToggleActive = async (userId, isActive) => {
    try {
      await api.patch(`/users/${userId}`, { is_active: !isActive });
      await fetchUsers();
    } catch (err) {
      alert('Failed to update user status');
      console.error(err);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      await api.delete(`/users/${userId}`);
      await fetchUsers();
      await fetchPendingUsers();
    } catch (err) {
      alert('Failed to delete user');
      console.error(err);
    }
  };

  const handleApproveUser = (user) => {
    setApprovingUser(user);
    setShowApproveModal(true);
  };

  const confirmApproval = async (role) => {
    try {
      await api.put(`/users/${approvingUser.id}/approve`, { role });
      setShowApproveModal(false);
      setApprovingUser(null);
      await fetchUsers();
      await fetchPendingUsers();
    } catch (err) {
      alert('Failed to approve user');
      console.error(err);
    }
  };

  const handleChangeRole = async (userId, newRole) => {
    try {
      await api.put(`/users/${userId}/role`, { role: newRole });
      await fetchUsers();
    } catch (err) {
      alert(err.message || 'Failed to update role');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 tracking-tight mb-1" style={{
                fontWeight: 800,
                letterSpacing: '-0.04em',
              }}>
                User Management
              </h1>
              <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                Manage team access and permissions
              </p>
            </div>
            <motion.button
              onClick={handleCreateUser}
              className="flex items-center gap-2 px-4 py-2.5 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 shadow-lg transition-all"
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.98 }}
            >
              <Plus className="w-4 h-4" strokeWidth={2.5} />
              Create User
            </motion.button>
          </div>
        </div>
      </div>

      <div className="px-8 py-6 space-y-8">
        {/* Pending Users Section */}
        {pendingUsers.length > 0 && (
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
              <h2 className="text-lg font-bold text-neutral-900" style={{ fontWeight: 700 }}>
                Pending Approval ({pendingUsers.length})
              </h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {pendingUsers.map((user) => (
                <motion.div
                  key={user.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-amber-50 border border-amber-200 rounded-xl p-5 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                        <UserIcon className="w-5 h-5 text-amber-700" />
                      </div>
                      <div>
                        <h3 className="font-bold text-neutral-900">{user.full_name}</h3>
                        <p className="text-sm text-neutral-600 flex items-center gap-1.5">
                          <Mail className="w-3.5 h-3.5" />
                          {user.email}
                        </p>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 bg-amber-100 text-amber-700 rounded-lg text-xs font-semibold">
                      Pending
                    </span>
                  </div>

                  {user.permissions?.company_role && (
                    <p className="text-sm text-neutral-600 mb-3">
                      <strong>Role:</strong> {user.permissions.company_role}
                    </p>
                  )}

                  <div className="text-sm text-neutral-600 mb-4">
                    <strong>Requested:</strong>{' '}
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </div>

                  <div className="flex items-center gap-2 pt-3 border-t border-amber-200">
                    <button
                      onClick={() => handleApproveUser(user)}
                      className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium"
                    >
                      <Check className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className="flex items-center gap-2 px-4 py-2 bg-white text-red-700 border border-red-200 rounded-lg hover:bg-red-50 transition-colors text-sm font-medium"
                    >
                      <X className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Active Users Section */}
        <div>
          <h2 className="text-lg font-bold text-neutral-900 mb-4" style={{ fontWeight: 700 }}>
            Active Users ({users.length})
          </h2>

          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div>
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 rounded-xl p-4">
              <p className="text-sm text-red-700 font-medium">{error}</p>
            </div>
          ) : users.length === 0 ? (
            <div className="bg-white border border-neutral-200 rounded-xl p-12 text-center">
              <UserX className="w-12 h-12 text-neutral-400 mx-auto mb-3" />
              <p className="text-neutral-600 font-medium">No active users found</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {users.map((user) => (
                <motion.div
                  key={user.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white border border-neutral-200 rounded-xl p-5 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-neutral-100 rounded-full flex items-center justify-center">
                        <UserIcon className="w-5 h-5 text-neutral-700" />
                      </div>
                      <div>
                        <h3 className="font-bold text-neutral-900">{user.full_name}</h3>
                        <p className="text-sm text-neutral-600 flex items-center gap-1.5">
                          <Mail className="w-3.5 h-3.5" />
                          {user.email}
                        </p>
                      </div>
                    </div>
                    <span className="flex items-center gap-1 px-2.5 py-1 bg-emerald-100 text-emerald-700 rounded-lg text-xs font-semibold">
                      <UserCheck className="w-3 h-3" />
                      Active
                    </span>
                  </div>

                  <div className="mb-4">
                    <label className="text-xs font-semibold text-neutral-500 uppercase tracking-wide mb-1.5 block">
                      Role
                    </label>
                    <div className="relative">
                      <select
                        value={user.role}
                        onChange={(e) => handleChangeRole(user.id, e.target.value)}
                        className={`w-full px-3 py-2 rounded-lg border text-sm font-semibold cursor-pointer appearance-none ${
                          ROLE_BADGES[user.role]
                        } focus:outline-none focus:ring-2 focus:ring-neutral-900`}
                      >
                        {ROLES.map((role) => (
                          <option key={role.value} value={role.value}>
                            {role.icon} {role.label}
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="w-4 h-4 text-neutral-500 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
                    </div>
                  </div>

                  <div className="text-sm text-neutral-600 mb-4 pb-4 border-b border-neutral-100">
                    <strong>Created:</strong>{' '}
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      className="flex items-center gap-2 px-3 py-1.5 text-red-700 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium border border-red-200"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                      Delete
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Approval Modal */}
      <AnimatePresence>
        {showApproveModal && approvingUser && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center">
                  <UserCheck className="w-6 h-6 text-emerald-700" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-neutral-900">Approve User</h3>
                  <p className="text-sm text-neutral-600">{approvingUser.full_name}</p>
                </div>
              </div>

              <p className="text-sm text-neutral-600 mb-4">
                Select a role to assign to this user:
              </p>

              <div className="space-y-2 mb-6">
                {ROLES.map((role) => (
                  <button
                    key={role.value}
                    onClick={() => confirmApproval(role.value)}
                    className="w-full text-left p-3 rounded-lg border border-neutral-200 hover:border-neutral-900 hover:bg-neutral-50 transition-all"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{role.icon}</span>
                      <div>
                        <div className="font-bold text-neutral-900">{role.label}</div>
                        <div className="text-xs text-neutral-600">{role.description}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <button
                onClick={() => {
                  setShowApproveModal(false);
                  setApprovingUser(null);
                }}
                className="w-full px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors font-medium"
              >
                Cancel
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Create/Edit User Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6"
            >
              <CreateUserForm
                user={editingUser}
                onClose={() => {
                  setShowCreateModal(false);
                  setEditingUser(null);
                }}
                onSuccess={() => {
                  setShowCreateModal(false);
                  setEditingUser(null);
                  fetchUsers();
                }}
              />
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Create User Form Component
function CreateUserForm({ user, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    password: '',
    role: user?.role || 'viewer',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (user) {
        // Update existing user
        const payload = {
          full_name: formData.full_name,
          email: formData.email,
          role: formData.role,
        };
        if (formData.password) {
          payload.password = formData.password;
        }
        await api.patch(`/users/${user.id}`, payload);
      } else {
        // Create new user
        await api.post('/users', formData);
      }
      onSuccess();
    } catch (err) {
      setError(err.message || 'Failed to save user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-neutral-100 rounded-full flex items-center justify-center">
          <UserIcon className="w-6 h-6 text-neutral-700" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-neutral-900">
            {user ? 'Edit User' : 'Create New User'}
          </h3>
          <p className="text-sm text-neutral-600">Fill in user details</p>
        </div>
      </div>

      <div className="space-y-4 mb-6">
        {/* Full Name */}
        <div>
          <label className="block text-sm font-semibold text-neutral-700 mb-1.5">
            Full Name
          </label>
          <input
            type="text"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
            required
          />
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-semibold text-neutral-700 mb-1.5">
            Email
          </label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
            required
          />
        </div>

        {/* Password */}
        <div>
          <label className="block text-sm font-semibold text-neutral-700 mb-1.5">
            Password {user && '(leave blank to keep current)'}
          </label>
          <input
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            className="w-full px-3 py-2 border border-neutral-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
            required={!user}
          />
        </div>

        {/* Role */}
        <div>
          <label className="block text-sm font-semibold text-neutral-700 mb-2">
            Role
          </label>
          <div className="space-y-2">
            {ROLES.map((role) => (
              <button
                key={role.value}
                type="button"
                onClick={() => setFormData({ ...formData, role: role.value })}
                className={`w-full text-left p-3 rounded-lg border transition-all ${
                  formData.role === role.value
                    ? 'border-neutral-900 bg-neutral-50'
                    : 'border-neutral-200 hover:border-neutral-400'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-xl">{role.icon}</span>
                  <div>
                    <div className="font-bold text-neutral-900">{role.label}</div>
                    <div className="text-xs text-neutral-600">{role.description}</div>
                  </div>
                  {formData.role === role.value && (
                    <Check className="w-5 h-5 text-neutral-900 ml-auto" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700 font-medium">{error}</p>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2">
        <button
          type="button"
          onClick={onClose}
          className="flex-1 px-4 py-2 text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors font-medium"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="flex-1 px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 transition-colors font-medium disabled:opacity-50"
        >
          {loading ? 'Saving...' : user ? 'Update User' : 'Create User'}
        </button>
      </div>
    </form>
  );
}
