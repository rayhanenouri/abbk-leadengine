/**
 * Enterprise Lead Detail View
 * Clean tabbed interface for lead intelligence
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ArrowLeft, ExternalLink, Phone, Mail, Globe,
  MapPin, Building2, Users, TrendingUp, Zap,
  Target, Award, AlertCircle, CheckCircle2, X, Edit3,
  Download, Share2, MoreVertical, Activity,
  Sparkles, Clock, FileText, BarChart3, Bell
} from 'lucide-react';
import { getLeadDetail, updateLeadStatus } from '../services/api';

export default function LeadDetail({ leadId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [statusNotes, setStatusNotes] = useState('');

  useEffect(() => {
    loadLeadDetail();
  }, [leadId]);

  const loadLeadDetail = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await getLeadDetail(leadId);
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to load lead details');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 60) return { bg: 'bg-emerald-50', text: 'text-emerald-600', border: 'border-emerald-200', solid: 'bg-emerald-600' };
    if (score >= 30) return { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200', solid: 'bg-blue-600' };
    return { bg: 'bg-neutral-50', text: 'text-neutral-500', border: 'border-neutral-200', solid: 'bg-neutral-500' };
  };

  const getStatusConfig = (status) => {
    const configs = {
      new: { label: 'New', color: 'blue', icon: Sparkles },
      contacted: { label: 'Contacted', color: 'purple', icon: Phone },
      qualified: { label: 'Qualified', color: 'emerald', icon: Target },
      converted: { label: 'Converted', color: 'green', icon: CheckCircle2 },
      lost: { label: 'Lost', color: 'neutral', icon: X },
    };
    return configs[status] || configs.new;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  const handleStatusUpdate = async () => {
    if (!newStatus) return;
    try {
      await updateLeadStatus(leadId, newStatus, statusNotes || null);
      setShowStatusModal(false);
      setStatusNotes('');
      await loadLeadDetail();
    } catch (err) {
      alert('Failed to update status: ' + err.message);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-neutral-600 font-semibold" style={{ fontSize: '14px', fontWeight: 600 }}>
            Loading lead intelligence...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-neutral-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 font-semibold mb-4">{error}</p>
          <motion.button
            onClick={onBack}
            className="px-6 py-3 bg-neutral-900 text-white rounded-xl font-semibold"
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            Back to Dashboard
          </motion.button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  const { lead, scores, signals } = data;
  const bestScore = scores.scores[0];
  const statusConfig = getStatusConfig(lead.status);
  const StatusIcon = statusConfig.icon;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Building2 },
    { id: 'scores', label: 'Scores', icon: BarChart3, badge: scores.scores.length },
    { id: 'signals', label: 'Signals', icon: Zap, badge: signals.length },
    { id: 'activity', label: 'Activity', icon: Clock },
  ];

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#FAFAFA' }}>
      {/* Header */}
      <div className="bg-white border-b border-neutral-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <motion.button
                onClick={onBack}
                className="flex items-center gap-2 px-4 py-2.5 text-neutral-700 hover:bg-neutral-100 rounded-xl transition-all border border-neutral-200"
                whileHover={{ x: -2 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontSize: '14px', fontWeight: 600 }}
              >
                <ArrowLeft className="w-4 h-4" strokeWidth={2.5} />
                Back
              </motion.button>
            </div>
            <div className="flex items-center gap-3">
              <motion.button
                onClick={() => {
                  setShowStatusModal(true);
                  setNewStatus(lead.status);
                }}
                className="flex items-center gap-2 px-4 py-2.5 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 transition-colors"
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontSize: '14px', fontWeight: 600 }}
              >
                <Edit3 className="w-4 h-4" strokeWidth={2.5} />
                Update Status
              </motion.button>
              <motion.button
                className="p-2.5 text-neutral-600 hover:bg-neutral-100 rounded-xl transition-all border border-neutral-200"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <Download className="w-5 h-5" strokeWidth={2.5} />
              </motion.button>
            </div>
          </div>

          {/* Company Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-6">
              <div className="w-20 h-20 rounded-2xl flex items-center justify-center flex-shrink-0" style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(16, 185, 129, 0.1))',
                border: '2px solid rgba(0, 0, 0, 0.06)',
              }}>
                <Building2 className="w-10 h-10 text-neutral-700" strokeWidth={2} />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-neutral-900 mb-2" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  {lead.company_name}
                </h1>
                <div className="flex items-center gap-6 text-neutral-600 mb-3">
                  {lead.sector && (
                    <span style={{ fontSize: '14px', fontWeight: 500 }}>{lead.sector}</span>
                  )}
                  {lead.city && (
                    <span className="flex items-center gap-1.5" style={{ fontSize: '14px', fontWeight: 500 }}>
                      <MapPin className="w-4 h-4" strokeWidth={2.5} />
                      {lead.city}, {lead.country || 'Tunisia'}
                    </span>
                  )}
                  {lead.employee_count && (
                    <span className="flex items-center gap-1.5" style={{ fontSize: '14px', fontWeight: 500 }}>
                      <Users className="w-4 h-4" strokeWidth={2.5} />
                      {lead.employee_count} employees
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  {lead.website && (
                    <motion.a
                      href={lead.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 text-blue-600 hover:text-blue-700"
                      whileHover={{ x: 2 }}
                      style={{ fontSize: '14px', fontWeight: 600 }}
                    >
                      <Globe className="w-4 h-4" strokeWidth={2.5} />
                      Website
                    </motion.a>
                  )}
                  {lead.linkedin_url && (
                    <motion.a
                      href={lead.linkedin_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1.5 text-blue-600 hover:text-blue-700"
                      whileHover={{ x: 2 }}
                      style={{ fontSize: '14px', fontWeight: 600 }}
                    >
                      <ExternalLink className="w-4 h-4" strokeWidth={2.5} />
                      LinkedIn
                    </motion.a>
                  )}
                  {lead.scraped_data?.csv_import?.phone && (
                    <motion.a
                      href={`tel:${lead.scraped_data.csv_import.phone}`}
                      className="flex items-center gap-1.5 text-emerald-600 hover:text-emerald-700"
                      whileHover={{ x: 2 }}
                      style={{ fontSize: '14px', fontWeight: 600 }}
                    >
                      <Phone className="w-4 h-4" strokeWidth={2.5} />
                      {lead.scraped_data.csv_import.phone}
                    </motion.a>
                  )}
                </div>
              </div>
            </div>

            <div className="flex flex-col items-end gap-3">
              <motion.div
                whileHover={{ scale: 1.02 }}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 ${
                  statusConfig.color === 'blue' ? 'bg-blue-50 border-blue-200 text-blue-700' :
                  statusConfig.color === 'purple' ? 'bg-purple-50 border-purple-200 text-purple-700' :
                  statusConfig.color === 'emerald' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' :
                  statusConfig.color === 'green' ? 'bg-green-50 border-green-200 text-green-700' :
                  'bg-neutral-50 border-neutral-200 text-neutral-600'
                }`}
                style={{ fontSize: '13px', fontWeight: 700 }}
              >
                <StatusIcon className="w-4 h-4" strokeWidth={2.5} />
                {statusConfig.label}
              </motion.div>
              <div className="flex items-center gap-2 flex-wrap justify-end">
                {lead.is_multinational && (
                  <span className="px-2.5 py-1 bg-blue-50 text-blue-700 rounded-md border border-blue-200" style={{ fontSize: '11px', fontWeight: 600 }}>
                    Multinational
                  </span>
                )}
                {lead.is_exporter && (
                  <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 rounded-md border border-emerald-200" style={{ fontSize: '11px', fontWeight: 600 }}>
                    Exporter
                  </span>
                )}
                {lead.under_audit && (
                  <span className="px-2.5 py-1 bg-amber-50 text-amber-700 rounded-md border border-amber-200" style={{ fontSize: '11px', fontWeight: 600 }}>
                    Under Audit
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex items-center gap-2 border-b border-neutral-200">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <motion.button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-all relative ${
                    isActive
                      ? 'border-neutral-900 text-neutral-900'
                      : 'border-transparent text-neutral-500 hover:text-neutral-900'
                  }`}
                  whileHover={{ y: -1 }}
                  style={{ fontSize: '14px', fontWeight: isActive ? 600 : 500 }}
                >
                  <Icon className="w-4 h-4" strokeWidth={2.5} />
                  {tab.label}
                  {tab.badge !== undefined && (
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      isActive ? 'bg-neutral-900 text-white' : 'bg-neutral-200 text-neutral-600'
                    }`}>
                      {tab.badge}
                    </span>
                  )}
                </motion.button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto p-8">
        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {/* Best Opportunity */}
              <div className="bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-2xl p-8 text-white relative overflow-hidden">
                <div className="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full blur-3xl" />
                <div className="relative">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-3">
                        <Award className="w-6 h-6" strokeWidth={2.5} />
                        <span className="text-sm font-semibold uppercase tracking-wider" style={{ letterSpacing: '0.1em', fontSize: '11px' }}>
                          Best Opportunity
                        </span>
                      </div>
                      <h3 className="text-3xl font-bold mb-3" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                        {bestScore.service_name}
                      </h3>
                      <p className="text-emerald-50 leading-relaxed mb-6 max-w-2xl" style={{ fontSize: '15px', fontWeight: 500 }}>
                        {bestScore.reasoning}
                      </p>
                      <motion.button
                        className="flex items-center gap-2 px-6 py-3.5 bg-white text-emerald-600 rounded-xl font-bold hover:bg-emerald-50 transition-colors"
                        whileHover={{ y: -2, scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        style={{ fontSize: '15px', fontWeight: 700 }}
                      >
                        <Phone className="w-5 h-5" strokeWidth={2.5} />
                        Call Now - Pitch This Deal
                      </motion.button>
                    </div>
                    <div className="text-center">
                      <div className="text-7xl font-bold mb-2" style={{ fontWeight: 800, letterSpacing: '-0.04em' }}>
                        {Math.round(bestScore.score)}
                      </div>
                      <div className="text-sm text-emerald-100 font-semibold uppercase tracking-wide" style={{ letterSpacing: '0.1em', fontSize: '11px' }}>
                        Score
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Quick Stats Grid */}
              <div className="grid grid-cols-3 gap-6">
                <div className="bg-white rounded-2xl p-6 border border-neutral-200">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center">
                      <BarChart3 className="w-6 h-6 text-blue-600" strokeWidth={2.5} />
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-neutral-900" style={{ fontWeight: 800 }}>
                        {scores.scores.length}
                      </div>
                      <div className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                        Services Scored
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-2xl p-6 border border-neutral-200">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center">
                      <Zap className="w-6 h-6 text-emerald-600" strokeWidth={2.5} />
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-neutral-900" style={{ fontWeight: 800 }}>
                        {signals.length}
                      </div>
                      <div className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                        Active Signals
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-white rounded-2xl p-6 border border-neutral-200">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center">
                      <Target className="w-6 h-6 text-amber-600" strokeWidth={2.5} />
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-neutral-900" style={{ fontWeight: 800 }}>
                        {Math.round(bestScore.score)}
                      </div>
                      <div className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                        Best Score
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'scores' && (
            <motion.div
              key="scores"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="grid grid-cols-3 gap-6"
            >
              {scores.scores.map((score, idx) => {
                const colors = getScoreColor(score.score);
                return (
                  <motion.div
                    key={score.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    whileHover={{ y: -4, transition: { duration: 0.2 } }}
                    className={`bg-white rounded-2xl p-6 border-2 ${colors.border} cursor-pointer`}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h4 className="font-bold text-neutral-900 mb-1" style={{ fontSize: '16px', fontWeight: 700 }}>
                          {score.service_name}
                        </h4>
                        <span className="text-xs font-semibold text-neutral-500 uppercase tracking-wider" style={{ letterSpacing: '0.05em', fontSize: '10px' }}>
                          {score.service_type.replace('_', ' ')}
                        </span>
                      </div>
                      <div className={`text-4xl font-bold ${colors.text}`} style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                        {Math.round(score.score)}
                      </div>
                    </div>
                    <p className="text-sm text-neutral-600 mb-4" style={{ fontSize: '14px', fontWeight: 500, lineHeight: '1.5' }}>
                      {score.reasoning}
                    </p>
                    <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${score.score}%` }}
                        transition={{ delay: 0.3 + idx * 0.05, duration: 0.6 }}
                        className={`h-full ${colors.solid}`}
                      />
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>
          )}

          {activeTab === 'signals' && (
            <motion.div
              key="signals"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
            >
              {signals.length === 0 ? (
                <div className="bg-white rounded-2xl p-12 text-center border border-neutral-200">
                  <Zap className="w-16 h-16 text-neutral-300 mx-auto mb-4" strokeWidth={2} />
                  <p className="text-neutral-500" style={{ fontSize: '14px', fontWeight: 500 }}>
                    No signals detected yet
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {signals.map((signal, idx) => (
                    <motion.div
                      key={signal.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      whileHover={{ x: 4, transition: { duration: 0.2 } }}
                      className="bg-white rounded-2xl p-6 border border-neutral-200 hover:border-neutral-300 hover:shadow-lg transition-all cursor-pointer"
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center flex-shrink-0">
                          <Zap className="w-6 h-6 text-blue-600" strokeWidth={2.5} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2">
                            <h4 className="font-bold text-neutral-900" style={{ fontSize: '16px', fontWeight: 700 }}>
                              {signal.title}
                            </h4>
                            <span className="text-sm text-neutral-500 flex-shrink-0 ml-4" style={{ fontSize: '13px', fontWeight: 500 }}>
                              {formatDate(signal.detected_at)}
                            </span>
                          </div>
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-blue-50 text-blue-700 rounded-lg border border-blue-200 mb-3" style={{ fontSize: '11px', fontWeight: 600 }}>
                            {signal.signal_type.replace('_', ' ').toUpperCase()}
                          </span>
                          {signal.detail && (
                            <p className="text-sm text-neutral-600 mb-3" style={{ fontSize: '14px', fontWeight: 500, lineHeight: '1.5' }}>
                              {signal.detail}
                            </p>
                          )}
                          {signal.source_url && (
                            <a
                              href={signal.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-1.5 text-blue-600 hover:text-blue-700 transition-colors"
                              style={{ fontSize: '14px', fontWeight: 600 }}
                            >
                              <ExternalLink className="w-4 h-4" strokeWidth={2.5} />
                              View Source
                            </a>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          )}

          {activeTab === 'activity' && (
            <motion.div
              key="activity"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.2 }}
              className="bg-white rounded-2xl p-8 border border-neutral-200"
            >
              <h3 className="text-xl font-bold text-neutral-900 mb-6" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                Activity Timeline
              </h3>
              {lead.last_contacted ? (
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-200 flex items-center justify-center flex-shrink-0">
                    <Phone className="w-6 h-6 text-emerald-600" strokeWidth={2.5} />
                  </div>
                  <div>
                    <h4 className="font-bold text-neutral-900 mb-1" style={{ fontSize: '16px', fontWeight: 700 }}>
                      Last Contact
                    </h4>
                    <p className="text-sm text-neutral-500" style={{ fontSize: '14px', fontWeight: 500 }}>
                      {formatDate(lead.last_contacted)}
                    </p>
                    {lead.status_notes && (
                      <p className="text-sm text-neutral-600 mt-2 p-3 bg-neutral-50 rounded-lg" style={{ fontSize: '13px', fontWeight: 500 }}>
                        {lead.status_notes}
                      </p>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <Clock className="w-16 h-16 text-neutral-300 mx-auto mb-4" strokeWidth={2} />
                  <p className="text-neutral-500" style={{ fontSize: '14px', fontWeight: 500 }}>
                    No activity recorded yet
                  </p>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Status Update Modal */}
      <AnimatePresence>
        {showStatusModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowStatusModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="bg-white rounded-2xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <h3 className="text-2xl font-bold text-neutral-900 mb-6" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                Update Lead Status
              </h3>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-semibold text-neutral-700 mb-2" style={{ fontSize: '13px', fontWeight: 600 }}>
                    New Status
                  </label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-neutral-200 rounded-xl focus:border-neutral-900 focus:outline-none transition-colors"
                    style={{ fontSize: '14px', fontWeight: 500 }}
                  >
                    <option value="new">New</option>
                    <option value="contacted">Contacted</option>
                    <option value="qualified">Qualified</option>
                    <option value="converted">Converted</option>
                    <option value="lost">Lost</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-neutral-700 mb-2" style={{ fontSize: '13px', fontWeight: 600 }}>
                    Notes (optional)
                  </label>
                  <textarea
                    value={statusNotes}
                    onChange={(e) => setStatusNotes(e.target.value)}
                    placeholder="Add notes about this status change..."
                    className="w-full px-4 py-3 border-2 border-neutral-200 rounded-xl focus:border-neutral-900 focus:outline-none transition-colors resize-none"
                    style={{ fontSize: '14px', fontWeight: 500 }}
                    rows={4}
                  />
                </div>
              </div>

              <div className="flex items-center gap-3">
                <motion.button
                  onClick={() => setShowStatusModal(false)}
                  className="flex-1 px-6 py-3 bg-neutral-100 text-neutral-700 rounded-xl font-semibold hover:bg-neutral-200 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  Cancel
                </motion.button>
                <motion.button
                  onClick={handleStatusUpdate}
                  className="flex-1 px-6 py-3 bg-neutral-900 text-white rounded-xl font-semibold hover:bg-neutral-800 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  Update
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
