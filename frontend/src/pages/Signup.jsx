/**
 * User Self-Registration Page
 * Allows new users to request access to ABBK LeadEngine
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, ArrowRight, Mail, Lock, User, Briefcase, ArrowLeft } from 'lucide-react';

const Signup = ({ onNavigateToLogin }) => {

  const [formData, setFormData] = useState({
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
    company_role: ''
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          full_name: formData.full_name,
          password: formData.password,
          company_role: formData.company_role || null
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      setSuccess(true);
    } catch (err) {
      setError(err.message || 'An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md text-center"
        >
          <div className="mb-8">
            <div className="w-20 h-20 mx-auto rounded-full bg-green-100 flex items-center justify-center mb-6">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-neutral-900 mb-4">Request Submitted!</h2>
            <p className="text-lg text-neutral-600 mb-8">
              Your account request has been submitted successfully. The administrator will review and activate your access shortly.
            </p>
            <p className="text-sm text-neutral-500 mb-8">
              You will receive an email notification once your account is approved.
            </p>
            <motion.button
              onClick={onNavigateToLogin}
              className="inline-flex items-center gap-2 px-6 py-3 bg-neutral-900 text-white rounded-xl font-semibold hover:bg-neutral-800 transition-all"
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.99 }}
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Login
            </motion.button>
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left Side - Branding (same as login) */}
      <div className="hidden lg:flex lg:w-1/2 p-12 flex-col justify-between relative overflow-hidden bg-neutral-900">
        {/* Multiple Moving Gradient Layers */}
        <motion.div
          className="absolute inset-0"
          animate={{ rotate: [0, 360] }}
          transition={{ duration: 30, repeat: Infinity, ease: 'linear' }}
          style={{ background: 'radial-gradient(circle at 30% 50%, rgba(220, 38, 38, 0.15), transparent 50%)' }}
        />

        <motion.div
          className="absolute inset-0"
          animate={{ rotate: [360, 0] }}
          transition={{ duration: 25, repeat: Infinity, ease: 'linear' }}
          style={{ background: 'radial-gradient(circle at 70% 50%, rgba(59, 130, 246, 0.1), transparent 50%)' }}
        />

        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative z-10"
        >
          <div className="mb-16">
            <div className="flex items-center gap-4">
              <div className="relative w-14 h-14 rounded-2xl flex items-center justify-center" style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(220, 38, 38, 0.15))',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
              }}>
                <TrendingUp className="w-7 h-7 text-white" strokeWidth={2.5} />
              </div>

              <div>
                <div className="text-4xl font-bold text-white tracking-tight mb-0.5" style={{
                  letterSpacing: '-0.04em',
                  fontWeight: 700,
                }}>
                  LeadEngine
                </div>
                <div className="text-sm font-medium tracking-wider uppercase" style={{
                  color: 'rgba(255, 255, 255, 0.5)',
                  letterSpacing: '0.2em',
                  fontWeight: 500,
                }}>
                  by ABBK
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="relative z-10 space-y-8"
        >
          <div>
            <h1 className="text-5xl font-bold text-white mb-5 leading-tight" style={{
              letterSpacing: '-0.03em',
              fontWeight: 700,
            }}>
              Join the team
            </h1>
            <p className="text-xl leading-relaxed" style={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontWeight: 400,
            }}>
              Request access to ABBK LeadEngine and start finding qualified leads today.
            </p>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="relative z-10 text-neutral-400 text-sm"
        >
          © 2026 ABBK Physicsworks. All rights reserved.
        </motion.div>
      </div>

      {/* Right Side - Signup Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden mb-10">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(220, 38, 38, 0.1))',
                border: '1px solid rgba(0, 0, 0, 0.06)',
              }}>
                <TrendingUp className="w-6 h-6 text-neutral-900" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-2xl font-bold text-neutral-900 tracking-tight" style={{
                  letterSpacing: '-0.03em',
                  fontWeight: 700,
                }}>
                  LeadEngine
                </div>
                <div className="text-xs font-medium tracking-wider uppercase text-neutral-500" style={{
                  letterSpacing: '0.15em',
                }}>
                  by ABBK
                </div>
              </div>
            </div>
          </div>

          {/* Header */}
          <div className="mb-8">
            <h2 className="text-4xl font-bold text-neutral-900 mb-3 tracking-tight" style={{
              letterSpacing: '-0.03em',
              fontWeight: 700,
            }}>
              Request Access
            </h2>
            <p className="text-lg text-neutral-600" style={{
              fontWeight: 400,
            }}>
              Fill out the form below to request an account
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2" style={{
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}>
                Full Name
              </label>
              <div className="relative group">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-hover:text-neutral-600 transition-colors" />
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{ fontSize: '15px', fontWeight: 500 }}
                  placeholder="John Doe"
                  required
                  autoFocus
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2" style={{
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}>
                Email Address
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-hover:text-neutral-600 transition-colors" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{ fontSize: '15px', fontWeight: 500 }}
                  placeholder="you@company.com"
                  required
                />
              </div>
            </div>

            {/* Company/Role */}
            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2" style={{
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}>
                Company / Role <span className="text-neutral-400 font-normal">(Optional)</span>
              </label>
              <div className="relative group">
                <Briefcase className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-hover:text-neutral-600 transition-colors" />
                <input
                  type="text"
                  name="company_role"
                  value={formData.company_role}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{ fontSize: '15px', fontWeight: 500 }}
                  placeholder="Sales Engineer at ABBK"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2" style={{
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}>
                Password
              </label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-hover:text-neutral-600 transition-colors" />
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{ fontSize: '15px', fontWeight: 500 }}
                  placeholder="At least 8 characters"
                  required
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2" style={{
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}>
                Confirm Password
              </label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-hover:text-neutral-600 transition-colors" />
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{ fontSize: '15px', fontWeight: 500 }}
                  placeholder="Confirm your password"
                  required
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 border border-red-200 rounded-lg p-4"
              >
                <p className="text-sm text-red-700 font-medium">{error}</p>
              </motion.div>
            )}

            {/* Submit */}
            <motion.button
              type="submit"
              disabled={loading}
              className={`w-full py-4 rounded-xl font-semibold flex items-center justify-center gap-2.5 transition-all ${
                loading
                  ? 'bg-neutral-300 cursor-not-allowed'
                  : 'bg-neutral-900 hover:bg-neutral-800 shadow-xl shadow-neutral-900/25 hover:shadow-2xl hover:shadow-neutral-900/40'
              } text-white relative overflow-hidden group`}
              style={{ fontSize: '15px', fontWeight: 600, letterSpacing: '-0.01em' }}
              whileHover={!loading ? { y: -1 } : {}}
              whileTap={!loading ? { scale: 0.99 } : {}}
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Submitting...
                </>
              ) : (
                <>
                  Request Access
                  <ArrowRight className="w-5 h-5" strokeWidth={2.5} />
                </>
              )}
            </motion.button>
          </form>

          {/* Back to Login */}
          <div className="mt-8 text-center">
            <button
              onClick={onNavigateToLogin}
              className="inline-flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-neutral-900 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Login
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Signup;
