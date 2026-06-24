/**
 * Live Signals Feed
 * Real-time buying signals detection and monitoring
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Zap, Users, Globe, CheckCircle2, TrendingUp, Target,
  ExternalLink, Building2, Clock, Filter, RefreshCw,
  Bell, Eye, ArrowUpRight, Newspaper, Briefcase, Award
} from 'lucide-react';
import { getRankedLeads } from '../services/api';

export default function LiveSignals({ onViewLead }) {
  const [leads, setLeads] = useState([]);
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadData, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadData = async () => {
    try {
      const data = await getRankedLeads(10000, 0, {});
      setLeads(data);
      generateSignals(data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateSignals = (leadsData) => {
    const allSignals = [];
    const now = new Date();

    leadsData.forEach(lead => {
      // Multinational signal
      if (lead.is_multinational) {
        allSignals.push({
          id: `multi-${lead.lead_id}`,
          type: 'multinational',
          icon: Globe,
          color: 'blue',
          strength: 'high',
          company: lead.company_name,
          leadId: lead.lead_id,
          title: 'Multinational Company Detected',
          description: 'International clients require licensed software',
          score: lead.best_score,
          timestamp: lead.updated_at || lead.created_at,
        });
      }

      // Exporter signal
      if (lead.is_exporter) {
        allSignals.push({
          id: `export-${lead.lead_id}`,
          type: 'export',
          icon: Target,
          color: 'emerald',
          strength: 'high',
          company: lead.company_name,
          leadId: lead.lead_id,
          title: 'Export Activity Detected',
          description: 'International trade requires compliance',
          score: lead.best_score,
          timestamp: lead.updated_at || lead.created_at,
        });
      }

      // Audit signal
      if (lead.under_audit) {
        allSignals.push({
          id: `audit-${lead.lead_id}`,
          type: 'audit',
          icon: CheckCircle2,
          color: 'amber',
          strength: 'critical',
          company: lead.company_name,
          leadId: lead.lead_id,
          title: 'Audit Pressure Detected',
          description: 'Cannot use unlicensed software during audit',
          score: lead.best_score,
          timestamp: lead.updated_at || lead.created_at,
        });
      }

      // High score signal
      if (lead.best_score >= 60) {
        allSignals.push({
          id: `score-${lead.lead_id}`,
          type: 'high_score',
          icon: TrendingUp,
          color: 'purple',
          strength: 'high',
          company: lead.company_name,
          leadId: lead.lead_id,
          title: 'High Match Score',
          description: `Score ${Math.round(lead.best_score)} - ${lead.best_service}`,
          score: lead.best_score,
          timestamp: lead.updated_at || lead.created_at,
        });
      }
    });

    setSignals(allSignals.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)));
  };

  const filters = [
    { id: 'all', label: 'All Signals', count: signals.length },
    { id: 'multinational', label: 'Multinational', count: signals.filter(s => s.type === 'multinational').length },
    { id: 'export', label: 'Export', count: signals.filter(s => s.type === 'export').length },
    { id: 'audit', label: 'Audit', count: signals.filter(s => s.type === 'audit').length },
    { id: 'high_score', label: 'High Score', count: signals.filter(s => s.type === 'high_score').length },
  ];

  const filteredSignals = selectedFilter === 'all'
    ? signals
    : signals.filter(s => s.type === selectedFilter);

  const criticalCount = signals.filter(s => s.strength === 'critical').length;
  const highCount = signals.filter(s => s.strength === 'high').length;
  const todayCount = signals.filter(s => {
    const sigDate = new Date(s.timestamp);
    const today = new Date();
    return sigDate.toDateString() === today.toDateString();
  }).length;

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return 'Just now';
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
  };

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-emerald-100 flex items-center justify-center">
                <Zap className="w-6 h-6 text-emerald-600 animate-pulse" strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-neutral-900 mb-0.5" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  Live Signals
                </h1>
                <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                  Real-time buying intent detection
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <motion.button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border transition-all ${
                  autoRefresh
                    ? 'bg-emerald-600 text-white border-emerald-600'
                    : 'bg-white text-neutral-700 border-neutral-200 hover:bg-neutral-50'
                }`}
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontSize: '14px', fontWeight: 600 }}
              >
                <Bell className={`w-4 h-4 ${autoRefresh ? 'animate-pulse' : ''}`} strokeWidth={2.5} />
                {autoRefresh ? 'Live' : 'Paused'}
              </motion.button>

              <motion.button
                onClick={loadData}
                className="flex items-center gap-2 px-4 py-2.5 text-neutral-700 hover:bg-neutral-100 rounded-xl transition-all border border-neutral-200"
                whileHover={{ y: -1, rotate: 180 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontSize: '14px', fontWeight: 600 }}
              >
                <RefreshCw className="w-4 h-4" strokeWidth={2.5} />
                Refresh
              </motion.button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200">
              <div className="text-3xl font-bold text-emerald-900 mb-1" style={{ fontWeight: 800 }}>
                {signals.length}
              </div>
              <div className="text-xs text-emerald-700 font-semibold">Total Signals</div>
            </div>

            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4 border border-red-200">
              <div className="text-3xl font-bold text-red-900 mb-1" style={{ fontWeight: 800 }}>
                {criticalCount}
              </div>
              <div className="text-xs text-red-700 font-semibold">Critical</div>
            </div>

            <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 border border-amber-200">
              <div className="text-3xl font-bold text-amber-900 mb-1" style={{ fontWeight: 800 }}>
                {highCount}
              </div>
              <div className="text-xs text-amber-700 font-semibold">High Priority</div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200">
              <div className="text-3xl font-bold text-blue-900 mb-1" style={{ fontWeight: 800 }}>
                {todayCount}
              </div>
              <div className="text-xs text-blue-700 font-semibold">Today</div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            {filters.map(filter => (
              <button
                key={filter.id}
                onClick={() => setSelectedFilter(filter.id)}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                  selectedFilter === filter.id
                    ? 'bg-neutral-900 text-white'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                }`}
              >
                {filter.label}
                <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${
                  selectedFilter === filter.id
                    ? 'bg-white/20 text-white'
                    : 'bg-neutral-100 text-neutral-600'
                }`}>
                  {filter.count}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Signals Feed */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-5xl mx-auto p-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="w-8 h-8 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : filteredSignals.length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center border border-neutral-200">
              <Zap className="w-16 h-16 text-neutral-300 mx-auto mb-4" strokeWidth={2} />
              <p className="text-neutral-500 font-medium">No signals detected</p>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence>
                {filteredSignals.map((signal, idx) => {
                  const Icon = signal.icon;
                  return (
                    <motion.div
                      key={signal.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: idx * 0.02 }}
                      className={`bg-white rounded-xl p-5 border-2 hover:shadow-2xl transition-all cursor-pointer group ${
                        signal.strength === 'critical' ? 'border-red-300 bg-red-50/30' :
                        signal.strength === 'high' ? 'border-amber-300 bg-amber-50/30' :
                        'border-neutral-200'
                      }`}
                      onClick={() => onViewLead(signal.leadId)}
                    >
                      <div className="flex items-start gap-4">
                        {/* Icon */}
                        <div className={`w-14 h-14 rounded-xl bg-${signal.color}-100 flex items-center justify-center flex-shrink-0 border-2 border-${signal.color}-200`}>
                          <Icon className={`w-6 h-6 text-${signal.color}-600`} strokeWidth={2.5} />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                <span className={`inline-flex px-2 py-0.5 rounded text-xs font-bold uppercase ${
                                  signal.strength === 'critical' ? 'bg-red-600 text-white' :
                                  signal.strength === 'high' ? 'bg-amber-600 text-white' :
                                  'bg-neutral-600 text-white'
                                }`}>
                                  {signal.strength}
                                </span>
                                <span className="text-xs text-neutral-500 font-medium">
                                  {formatTimestamp(signal.timestamp)}
                                </span>
                              </div>
                              <div className="font-bold text-neutral-900 mb-1 group-hover:text-emerald-600 transition-colors" style={{ fontSize: '16px', fontWeight: 700 }}>
                                {signal.title}
                              </div>
                              <div className="text-sm text-neutral-600" style={{ fontWeight: 500 }}>
                                {signal.description}
                              </div>
                            </div>
                            <div className="text-right flex-shrink-0 ml-4">
                              <div className="text-3xl font-bold text-neutral-900 mb-1" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                                {Math.round(signal.score)}
                              </div>
                              <div className="text-xs text-neutral-500 font-semibold">Match</div>
                            </div>
                          </div>

                          <div className="flex items-center justify-between mt-3 pt-3 border-t border-neutral-100">
                            <div className="flex items-center gap-2">
                              <Building2 className="w-4 h-4 text-neutral-400" strokeWidth={2} />
                              <span className="text-sm font-bold text-neutral-900">{signal.company}</span>
                            </div>
                            <motion.button
                              className="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-900 text-white rounded-lg text-xs font-bold hover:bg-neutral-800"
                              whileHover={{ scale: 1.05, x: 2 }}
                              whileTap={{ scale: 0.95 }}
                            >
                              View Lead
                              <ArrowUpRight className="w-3.5 h-3.5" strokeWidth={2.5} />
                            </motion.button>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
