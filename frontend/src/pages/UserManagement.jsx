/**
 * User Management Page (Admin Only)
 * Create, edit, deactivate user accounts
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
} from 'lucide-react';
import { api } from '../services/api';

const ROLES = [
  { value: 'admin', label: 'Admin', description: 'Full access + user management', icon: '👑' },
  { value: 'manager', label: 'Manager', description: 'All leads + scores + reports', icon: '📊' },
  { value: 'sales', label: 'Sales', description: 'Assigned leads only', icon: '💼' },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access', icon: '👁️' },
];

const ROLE_COLORS = {
  admin: 'bg-purple-100 text-purple-700 border-purple-300',
  manager: 'bg-blue-100 text-blue-700 border-blue-300',
  sales: 'bg-green-100 text-green-700 border-green-300',
  viewer: 'bg-gray-100 text-gray-700 border-gray-300',
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

  const handleApproveSubmit = async (role) => {
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
      alert('Failed to update user role');
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-3">
              <Users className="w-8 h-8 text-primary-600" />
              User Management
            </h1>
            <p className="text-neutral-600 mt-2">
              Create and manage user accounts with role-based access control
            </p>
          </div>
          <button
            onClick={handleCreateUser}
            className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-colors shadow-lg hover:shadow-xl"
          >
            <Plus className="w-5 h-5" />
            Create User
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-error-50 border border-error-200 rounded-xl p-4 flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-error-600" />
          <p className="text-error-700 font-medium">{error}</p>
        </div>
      )}

      {/* Pending Users Section */}
      {pendingUsers.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold text-neutral-900 mb-4 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-warning-600" />
            Pending Approval ({pendingUsers.length})
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {pendingUsers.map((user) => (
              <motion.div
                key={user.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-warning-50 rounded-xl border-2 border-warning-200 p-5 shadow-sm"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h3 className="font-bold text-neutral-900 text-lg">{user.full_name}</h3>
                    <p className="text-sm text-neutral-600 flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      {user.email}
                    </p>
                    {user.permissions?.company_role && (
                      <p className="text-sm text-neutral-500 mt-1">
                        {user.permissions.company_role}
                      </p>
                    )}
                  </div>
                  <span className="px-3 py-1 bg-warning-100 text-warning-700 rounded-lg text-xs font-semibold">
                    Pending
                  </span>
                </div>
                <div className="text-sm text-neutral-600 mb-4">
                  <p>
                    <strong>Requested:</strong>{' '}
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })}
                  </p>
                </div>
                <div className="flex items-center gap-2 pt-3 border-t border-warning-200">
                  <button
                    onClick={() => handleApproveUser(user)}
                    className="flex items-center gap-2 px-4 py-2 bg-success-600 text-white rounded-lg hover:bg-success-700 transition-colors text-sm font-medium"
                  >
                    <Check className="w-4 h-4" />
                    Approve
                  </button>
                  <button
                    onClick={() => handleDeleteUser(user.id)}
                    className="flex items-center gap-2 px-4 py-2 bg-error-100 text-error-700 rounded-lg hover:bg-error-200 transition-colors text-sm font-medium"
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

      {/* Active Users List */}
      <h2 className="text-xl font-bold text-neutral-900 mb-4">
        Active Users ({users.length})
      </h2>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {users.map((user) => (
            <motion.div
              key={user.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-xl border border-neutral-200 p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                    <UserIcon className="w-6 h-6 text-primary-600" />
                  </div>
                  <div>
                    <h3 className="font-bold text-neutral-900 text-lg">{user.full_name}</h3>
                    <p className="text-sm text-neutral-600 flex items-center gap-2">
                      <Mail className="w-4 h-4" />
                      {user.email}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {user.is_active ? (
                    <span className="flex items-center gap-1 px-3 py-1 bg-success-100 text-success-700 rounded-lg text-xs font-semibold">
                      <UserCheck className="w-3 h-3" />
                      Active
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 px-3 py-1 bg-error-100 text-error-700 rounded-lg text-xs font-semibold">
                      <UserX className="w-3 h-3" />
                      Inactive
                    </span>
                  )}
                </div>
              </div>

              <div className="mb-4">
                <select
                  value={user.role}
                  onChange={(e) => handleChangeRole(user.id, e.target.value)}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-semibold cursor-pointer ${
                    ROLE_COLORS[user.role]
                  }`}
                >
                  {ROLES.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.icon} {role.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="text-sm text-neutral-600 mb-4">
                <p>
                  <strong>Created:</strong>{' '}
                  {new Date(user.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </p>
              </div>

              <div className="flex items-center gap-2 pt-4 border-t border-neutral-200">
                <button
                  onClick={() => handleEditUser(user)}
                  className="flex items-center gap-2 px-4 py-2 bg-neutral-100 text-neutral-700 rounded-lg hover:bg-neutral-200 transition-colors text-sm font-medium"
                >
                  <Edit2 className="w-4 h-4" />
                  Edit
                </button>
                <button
                  onClick={() => handleToggleActive(user.id, user.is_active)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors text-sm font-medium ${
                    user.is_active
                      ? 'bg-warning-100 text-warning-700 hover:bg-warning-200'
                      : 'bg-success-100 text-success-700 hover:bg-success-200'
                  }`}
                >
                  {user.is_active ? (
                    <>
                      <UserX className="w-4 h-4" />
                      Deactivate
                    </>
                  ) : (
                    <>
                      <UserCheck className="w-4 h-4" />
                      Activate
                    </>
                  )}
                </button>
                <button
                  onClick={() => handleDeleteUser(user.id)}
                  className="flex items-center gap-2 px-4 py-2 bg-error-100 text-error-700 rounded-lg hover:bg-error-200 transition-colors text-sm font-medium ml-auto"
                >
                  <Trash2 className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Create/Edit User Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <UserFormModal
            user={editingUser}
            onClose={() => setShowCreateModal(false)}
            onSuccess={() => {
              setShowCreateModal(false);
              fetchUsers();
              fetchPendingUsers();
            }}
          />
        )}
        {showApproveModal && approvingUser && (
          <ApproveUserModal
            user={approvingUser}
            onClose={() => setShowApproveModal(false)}
            onApprove={handleApproveSubmit}
          />
        )}
      </AnimatePresence>
    </div>
  );
}

function ApproveUserModal({ user, onClose, onApprove }) {
  const [selectedRole, setSelectedRole] = useState('viewer');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    await onApprove(selectedRole);
    setLoading(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6 border-b border-neutral-200">
          <h2 className="text-2xl font-bold text-neutral-900 flex items-center gap-3">
            <UserCheck className="w-6 h-6 text-success-600" />
            Approve User Access
          </h2>
          <p className="text-neutral-600 mt-1">
            Assign a role to {user.full_name} and activate their account
          </p>
        </div>

        <div className="p-6">
          {/* User Info */}
          <div className="bg-neutral-50 rounded-xl p-4 mb-6">
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <UserIcon className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-bold text-neutral-900">{user.full_name}</h3>
                <p className="text-sm text-neutral-600">{user.email}</p>
              </div>
            </div>
            {user.permissions?.company_role && (
              <p className="text-sm text-neutral-600">
                <strong>Company/Role:</strong> {user.permissions.company_role}
              </p>
            )}
            <p className="text-sm text-neutral-600">
              <strong>Requested:</strong>{' '}
              {new Date(user.created_at).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </p>
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-semibold text-neutral-700 mb-3">
              Assign Role
            </label>
            <div className="grid grid-cols-2 gap-3">
              {ROLES.map((role) => (
                <button
                  key={role.value}
                  type="button"
                  onClick={() => setSelectedRole(role.value)}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${
                    selectedRole === role.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-neutral-200 hover:border-neutral-300'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">{role.icon}</span>
                    <span className="font-bold text-neutral-900">{role.label}</span>
                    {selectedRole === role.value && (
                      <Check className="w-5 h-5 text-primary-600 ml-auto" />
                    )}
                  </div>
                  <p className="text-xs text-neutral-600">{role.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3 pt-6 mt-6 border-t border-neutral-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-neutral-300 text-neutral-700 rounded-xl font-semibold hover:bg-neutral-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1 px-6 py-3 bg-success-600 text-white rounded-xl font-semibold hover:bg-success-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Approving...
                </>
              ) : (
                <>
                  <Check className="w-5 h-5" />
                  Approve & Activate
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

function UserFormModal({ user, onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    email: user?.email || '',
    full_name: user?.full_name || '',
    password: '',
    role: user?.role || 'viewer',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (user) {
        // Update existing user
        const payload = { ...formData };
        if (!payload.password) {
          delete payload.password; // Don't update password if not provided
        }
        await api.patch(`/users/${user.id}`, payload);
      } else {
        // Create new user
        await api.post('/users', formData);
      }
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save user');
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6 border-b border-neutral-200">
          <h2 className="text-2xl font-bold text-neutral-900 flex items-center gap-3">
            <UserIcon className="w-6 h-6 text-primary-600" />
            {user ? 'Edit User' : 'Create New User'}
          </h2>
          <p className="text-neutral-600 mt-1">
            {user ? 'Update user details and permissions' : 'Add a new user account to the platform'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Email */}
          <div>
            <label className="block text-sm font-semibold text-neutral-700 mb-2">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full pl-10 pr-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="user@abbk.tn"
                required
              />
            </div>
          </div>

          {/* Full Name */}
          <div>
            <label className="block text-sm font-semibold text-neutral-700 mb-2">Full Name</label>
            <div className="relative">
              <UserIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
              <input
                type="text"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                className="w-full pl-10 pr-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="John Doe"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-semibold text-neutral-700 mb-2">
              Password {user && <span className="text-neutral-500">(leave blank to keep current)</span>}
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" />
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className="w-full pl-10 pr-4 py-3 border border-neutral-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500"
                placeholder="••••••••"
                required={!user}
              />
            </div>
          </div>

          {/* Role */}
          <div>
            <label className="block text-sm font-semibold text-neutral-700 mb-2">User Role</label>
            <div className="grid grid-cols-2 gap-3">
              {ROLES.map((role) => (
                <button
                  key={role.value}
                  type="button"
                  onClick={() => setFormData({ ...formData, role: role.value })}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${
                    formData.role === role.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-neutral-200 hover:border-neutral-300'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xl">{role.icon}</span>
                    <span className="font-bold text-neutral-900">{role.label}</span>
                    {formData.role === role.value && (
                      <Check className="w-5 h-5 text-primary-600 ml-auto" />
                    )}
                  </div>
                  <p className="text-xs text-neutral-600">{role.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-error-50 border border-error-200 rounded-xl p-4 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-error-600" />
              <p className="text-sm text-error-700 font-medium">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center gap-3 pt-4 border-t border-neutral-200">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-neutral-300 text-neutral-700 rounded-xl font-semibold hover:bg-neutral-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Saving...' : user ? 'Update User' : 'Create User'}
            </button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
}
