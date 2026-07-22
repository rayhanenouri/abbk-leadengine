/**
 * Professional Login Page
 * Modern design with ABBK branding and smooth animations
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, Mail, Lock, AlertCircle, Loader2, TrendingUp } from 'lucide-react';
import { login } from '../services/api';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('admin@abbk.tn');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      onLoginSuccess();
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0">
        {/* Gradient Mesh */}
        <div className="absolute inset-0 bg-gradient-mesh opacity-40" />

        {/* Grid Pattern */}
        <div className="absolute inset-0 grid-pattern opacity-20" />

        {/* Radial Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-primary-600/10 rounded-full blur-3xl" />

        {/* Floating Particles */}
        <motion.div
          className="absolute top-20 left-[10%] w-2 h-2 bg-primary-500 rounded-full"
          animate={{
            y: [0, -30, 0],
            opacity: [0.3, 0.8, 0.3],
          }}
          transition={{
            duration: 6,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.div
          className="absolute top-40 right-[15%] w-3 h-3 bg-accent-500 rounded-full"
          animate={{
            y: [0, -40, 0],
            opacity: [0.3, 0.7, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1,
          }}
        />
      </div>

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        <div className="bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl border border-neutral-200/50 overflow-hidden">
          {/* Header with Gradient */}
          <div className="bg-gradient-to-br from-primary-600 to-primary-700 p-8 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="w-16 h-16 bg-white rounded-2xl mx-auto mb-4 flex items-center justify-center"
            >
              <TrendingUp className="w-8 h-8 text-primary-600" />
            </motion.div>
            <motion.h1
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="text-3xl font-bold text-white mb-2"
            >
              ABBK LeadEngine
            </motion.h1>
            <motion.p
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-primary-100 text-sm"
            >
              B2B Lead Generation & Sales Intelligence
            </motion.p>
          </div>

          {/* Form */}
          <div className="p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Email Input */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
              >
                <label className="block text-sm font-semibold text-neutral-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Mail className="w-5 h-5 text-neutral-400" />
                  </div>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Enter your email"
                    required
                    autoFocus
                  />
                </div>
              </motion.div>

              {/* Password Input */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
              >
                <label className="block text-sm font-semibold text-neutral-700 mb-2">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    <Lock className="w-5 h-5 text-neutral-400" />
                  </div>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Enter your password"
                    required
                  />
                </div>
              </motion.div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-error-50 border border-error-200 rounded-xl p-4"
                >
                  <div className="flex items-center gap-3">
                    <AlertCircle className="w-5 h-5 text-error-600 flex-shrink-0" />
                    <p className="text-sm text-error-700 font-medium">{error}</p>
                  </div>
                </motion.div>
              )}

              {/* Submit Button */}
              <motion.button
                type="submit"
                disabled={loading}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.7 }}
                className={`w-full py-4 rounded-xl font-bold text-base flex items-center justify-center gap-3 transition-all shadow-lg ${
                  loading
                    ? 'bg-neutral-400 cursor-not-allowed'
                    : 'bg-primary-600 hover:bg-primary-700 shadow-primary-600/25 hover:shadow-xl hover:shadow-primary-600/30 hover:-translate-y-0.5 active:translate-y-0'
                } text-white`}
                whileHover={!loading ? { scale: 1.02 } : {}}
                whileTap={!loading ? { scale: 0.98 } : {}}
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Logging in...
                  </>
                ) : (
                  <>
                    <LogIn className="w-5 h-5" />
                    Login to Dashboard
                  </>
                )}
              </motion.button>
            </form>

            {/* Demo Credentials & Account Info */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.8 }}
              className="mt-6 pt-6 border-t border-neutral-200 space-y-3"
            >
              <p className="text-center text-sm text-neutral-500">
                Demo credentials:{' '}
                <span className="font-mono text-neutral-700 font-semibold">
                  admin@abbk.tn
                </span>{' '}
                /{' '}
                <span className="font-mono text-neutral-700 font-semibold">
                  admin123
                </span>
              </p>
              <p className="text-center text-xs text-neutral-400 px-4">
                Don't have an account? Contact your admin to create one for you.
              </p>
            </motion.div>
          </div>
        </div>

        {/* Features Below Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.9 }}
          className="mt-8 grid grid-cols-3 gap-4"
        >
          {[
            { label: '500+ Leads', icon: '🎯' },
            { label: 'AI-Powered', icon: '🤖' },
            { label: '3x Faster', icon: '⚡' },
          ].map((feature, i) => (
            <div
              key={i}
              className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl p-4 text-center"
            >
              <div className="text-2xl mb-1">{feature.icon}</div>
              <div className="text-xs text-white font-semibold">{feature.label}</div>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </div>
  );
}
