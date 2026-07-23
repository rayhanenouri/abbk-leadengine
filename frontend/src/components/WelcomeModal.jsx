/**
 * Welcome Modal for First-Time Users
 * Shows role permissions and gets started info
 */

import { motion } from 'framer-motion';
import { TrendingUp, X, Shield, Eye, Briefcase, Crown } from 'lucide-react';

const ROLE_INFO = {
  viewer: {
    icon: Eye,
    color: 'gray',
    title: 'Viewer',
    description: 'Read-only access to the platform',
    permissions: [
      'View dashboard and lead lists',
      'See company information',
      'Cannot see scores or signal details',
      'Cannot modify any data'
    ]
  },
  sales: {
    icon: Briefcase,
    color: 'green',
    title: 'Sales',
    description: 'Access to assigned leads with scores',
    permissions: [
      'View your assigned leads with scores',
      'See lead details and signals',
      'Update lead status and notes',
      'Cannot see other sales reps leads'
    ]
  },
  manager: {
    icon: Shield,
    color: 'blue',
    title: 'Manager',
    description: 'Full access to all leads and analytics',
    permissions: [
      'View all leads with scores and signals',
      'Access all analytics and reports',
      'Manage sales pipeline',
      'Export data and reports',
      'Cannot manage users'
    ]
  },
  admin: {
    icon: Crown,
    color: 'purple',
    title: 'Administrator',
    description: 'Complete platform control',
    permissions: [
      'Full access to all features',
      'Manage user accounts and roles',
      'Configure system settings',
      'Access all data and reports'
    ]
  }
};

const WelcomeModal = ({ user, onClose }) => {
  if (!user) return null;

  const roleInfo = ROLE_INFO[user.role] || ROLE_INFO.viewer;
  const Icon = roleInfo.icon;

  const colorClasses = {
    gray: {
      bg: 'bg-gray-100',
      text: 'text-gray-700',
      border: 'border-gray-300',
      gradient: 'from-gray-600 to-gray-400'
    },
    green: {
      bg: 'bg-green-100',
      text: 'text-green-700',
      border: 'border-green-300',
      gradient: 'from-green-600 to-green-400'
    },
    blue: {
      bg: 'bg-blue-100',
      text: 'text-blue-700',
      border: 'border-blue-300',
      gradient: 'from-blue-600 to-blue-400'
    },
    purple: {
      bg: 'bg-purple-100',
      text: 'text-purple-700',
      border: 'border-purple-300',
      gradient: 'from-purple-600 to-purple-400'
    }
  };

  const colors = colorClasses[roleInfo.color];

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
        {/* Header */}
        <div className="p-8 pb-6 border-b border-neutral-200">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-4">
              {/* Logo */}
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center" style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(220, 38, 38, 0.1))',
                border: '1px solid rgba(0, 0, 0, 0.06)',
              }}>
                <TrendingUp className="w-8 h-8 text-neutral-900" strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-neutral-900 tracking-tight" style={{
                  letterSpacing: '-0.03em',
                  fontWeight: 700,
                }}>
                  Welcome to LeadEngine
                </h1>
                <p className="text-neutral-600 mt-1">Your account has been activated</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              <X className="w-6 h-6 text-neutral-600" />
            </button>
          </div>
        </div>

        {/* User Info */}
        <div className="p-8 space-y-6">
          <div className="bg-neutral-50 rounded-xl p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${colors.gradient} flex items-center justify-center text-white font-bold text-xl`}>
                {user.full_name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div>
                <h2 className="text-xl font-bold text-neutral-900">{user.full_name}</h2>
                <p className="text-sm text-neutral-600">{user.email}</p>
              </div>
            </div>

            {/* Role Badge */}
            <div className={`inline-flex items-center gap-3 px-5 py-3 rounded-xl border-2 ${colors.bg} ${colors.text} ${colors.border}`}>
              <Icon className="w-6 h-6" strokeWidth={2.5} />
              <div>
                <div className="font-bold text-sm uppercase tracking-wider">Your Access Level</div>
                <div className="text-lg font-bold">{roleInfo.title}</div>
              </div>
            </div>
          </div>

          {/* Role Description */}
          <div>
            <h3 className="text-lg font-bold text-neutral-900 mb-2">{roleInfo.description}</h3>
            <p className="text-neutral-600 mb-4">
              As a <strong>{roleInfo.title}</strong>, you have the following permissions:
            </p>

            {/* Permissions List */}
            <div className="space-y-3">
              {roleInfo.permissions.map((permission, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="flex items-start gap-3"
                >
                  <div className={`w-6 h-6 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 ${colors.bg}`}>
                    <div className={`w-2 h-2 rounded-full ${colors.gradient} bg-gradient-to-br`} />
                  </div>
                  <p className="text-neutral-700">{permission}</p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Get Started */}
          <div className="bg-gradient-to-br from-neutral-900 to-neutral-700 rounded-xl p-6 text-white">
            <h3 className="text-lg font-bold mb-2">Ready to get started?</h3>
            <p className="text-neutral-200 mb-4">
              Your dashboard shows a complete overview of qualified leads ready for contact. Start exploring now!
            </p>
            <motion.button
              onClick={onClose}
              className="w-full px-6 py-3 bg-white text-neutral-900 rounded-xl font-semibold hover:bg-neutral-100 transition-colors"
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.99 }}
            >
              Go to Dashboard
            </motion.button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
};

export default WelcomeModal;
