/**
 * Professional B2B SaaS Dashboard
 * Enterprise-grade design like Stripe, Linear, Vercel
 * Mobile responsive with hamburger menu
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Target, TrendingUp, Activity, ArrowUpRight, ArrowDownRight,
  Search, Filter, Download, Plus, MoreVertical, ChevronRight,
  Calendar, DollarSign, Zap, Eye, Menu, CheckCircle2
} from 'lucide-react';
import { getLeads, getRankedLeads, logout, getUnreadCount } from '../services/api';
import Sidebar from '../components/layout/Sidebar';
import LeadDetail from './LeadDetail';

const DashboardPro = ({ onNavigate, onLogout, sidebarOpen, setSidebarOpen, currentUser }) => {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    setLoading(true);
    try {
      // Get leads with scores attached
      const data = await getLeads(0, 1000, 'created_at', 'desc');
      console.log('Loaded leads:', data.length, data.slice(0, 2)); // Debug

      // Calculate best_score from lead_scores if available
      const leadsWithScore = data.map(lead => {
        let bestScore = 0;

        // If lead has scores array, find the highest
        if (lead.lead_scores && lead.lead_scores.length > 0) {
          bestScore = Math.max(...lead.lead_scores.map(s => s.score || 0));
        }

        return {
          ...lead,
          lead_id: lead.id,
          best_score: bestScore,
          company_name: lead.company_name || 'Unknown Company',
          sector: lead.sector || 'Unknown',
          city: lead.city || 'Unknown',
        };
      });

      console.log('Processed leads:', leadsWithScore.slice(0, 2)); // Debug
      setLeads(leadsWithScore);
    } catch (err) {
      console.error('Failed to load leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredLeads = leads
    .filter(lead => {
      const companyName = lead.company_name || '';
      const matchesSearch = companyName.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter =
        selectedFilter === 'all' ? true :
        selectedFilter === 'hot' ? (lead.best_score >= 60 || (lead.is_multinational && lead.under_audit)) :
        selectedFilter === 'high' ? lead.best_score >= 70 :
        selectedFilter === 'medium' ? lead.best_score >= 50 && lead.best_score < 70 :
        selectedFilter === 'new' ? lead.status === 'new' : true;
      return matchesSearch && matchesFilter;
    })
    .slice(0, 20);

  // Metrics
  const totalLeads = leads.length;
  const highPriority = leads.filter(l => l.best_score >= 70).length;
  const mediumPriority = leads.filter(l => l.best_score >= 50 && l.best_score < 70).length;
  const newThisWeek = 12; // Mock data
  const conversionRate = ((highPriority / totalLeads) * 100).toFixed(1);

  // HOT LEAD CRITERIA from business manager:
  // 1. Training history/potential (HIGHEST)
  // 2. New machine purchase
  // 3. Hiring engineers
  // 4. Multinational + audit
  const hotLeads = leads.filter(l =>
    l.best_score >= 60 || // Training signal or multiple priority signals
    (l.is_multinational && l.under_audit) // Multinational under audit
  ).length;

  const metrics = [
    {
      label: 'Total Leads',
      value: totalLeads,
      change: `+${newThisWeek}`,
      trend: 'up',
      icon: Users,
      color: 'blue',
    },
    {
      label: 'Hot Leads',
      value: hotLeads,
      change: 'Training/Machine/Hiring',
      trend: 'up',
      icon: Zap,
      color: 'red',
    },
    {
      label: 'High Priority',
      value: highPriority,
      change: `${conversionRate}%`,
      trend: 'up',
      icon: Target,
      color: 'green',
    },
    {
      label: 'Active Pipeline',
      value: filteredLeads.length,
      change: 'Live',
      trend: 'neutral',
      icon: Activity,
      color: 'purple',
    },
  ];

  const filters = [
    { id: 'all', label: 'All Leads', count: totalLeads },
    { id: 'hot', label: 'Hot Leads', count: hotLeads },
    { id: 'high', label: 'High Priority', count: highPriority },
    { id: 'medium', label: 'Medium Priority', count: mediumPriority },
    { id: 'new', label: 'New', count: leads.filter(l => l.status === 'new').length },
  ];

  if (selectedLeadId) {
    return (
      <div className="flex h-screen bg-neutral-50 overflow-hidden">
        <Sidebar
          currentView="dashboard"
          onViewChange={onNavigate}
          onLogout={onLogout}
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          user={currentUser}
        />
        <div className="flex-1 overflow-auto w-full">
          <LeadDetail
            leadId={selectedLeadId}
            onBack={() => setSelectedLeadId(null)}
            onMenuClick={() => setSidebarOpen(!sidebarOpen)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-neutral-50 overflow-hidden">
      <Sidebar
        currentView="dashboard"
        onViewChange={onNavigate}
        onLogout={onLogout}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        user={currentUser}
      />

      <div className="flex-1 flex flex-col overflow-hidden w-full">
        {/* Header */}
        <div className="bg-white border-b border-neutral-200">
          <div className="px-4 md:px-8 py-4 md:py-6">
            {/* Mobile hamburger */}
            <div className="flex items-center gap-4 mb-4 md:hidden">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-neutral-100 rounded-lg"
              >
                <Menu className="w-6 h-6 text-neutral-900" />
              </button>
              <h1 className="text-lg font-bold text-neutral-900">Dashboard</h1>
            </div>

            <div className="flex items-center justify-between">
              <div className="hidden md:block">
                <h1 className="text-2xl font-bold text-neutral-900 tracking-tight mb-1" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  Dashboard
                </h1>
                <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                  Overview of your sales pipeline and leads performance
                </p>
              </div>

              <div className="flex items-center gap-3">
                <motion.button
                  className="flex items-center gap-2 px-4 py-2.5 text-neutral-700 hover:bg-neutral-100 rounded-xl transition-all border border-neutral-200"
                  whileHover={{ y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  <Download className="w-4 h-4" strokeWidth={2.5} />
                  Export
                </motion.button>
                <motion.button
                  className="flex items-center gap-2 px-4 py-2.5 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 shadow-lg transition-all relative overflow-hidden group"
                  whileHover={{ y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
                  <Plus className="w-4 h-4" strokeWidth={2.5} />
                  New Lead
                </motion.button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-8 space-y-8">
            {/* Metrics Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
              {metrics.map((metric, idx) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  whileHover={{ y: -4, transition: { duration: 0.2 } }}
                  className="bg-white rounded-2xl p-6 border border-neutral-200 hover:border-neutral-300 hover:shadow-xl transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-6">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      metric.color === 'blue' ? 'bg-blue-50' :
                      metric.color === 'red' ? 'bg-red-50' :
                      metric.color === 'green' ? 'bg-emerald-50' :
                      metric.color === 'amber' ? 'bg-amber-50' : 'bg-purple-50'
                    }`}>
                      <metric.icon className={`w-6 h-6 ${
                        metric.color === 'blue' ? 'text-blue-600' :
                        metric.color === 'red' ? 'text-red-600' :
                        metric.color === 'green' ? 'text-emerald-600' :
                        metric.color === 'amber' ? 'text-amber-600' : 'text-purple-600'
                      }`} strokeWidth={2.5} />
                    </div>
                    <div className={`flex items-center gap-1 px-2.5 py-1 rounded-lg ${
                      metric.trend === 'up' ? 'bg-emerald-50' : 'bg-neutral-100'
                    }`}>
                      {metric.trend === 'up' && <ArrowUpRight className="w-3.5 h-3.5 text-emerald-600" strokeWidth={2.5} />}
                      <span className={`text-xs font-bold ${
                        metric.trend === 'up' ? 'text-emerald-600' : 'text-neutral-600'
                      }`} style={{ letterSpacing: '-0.01em' }}>
                        {metric.change}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-3xl font-bold text-neutral-900 tracking-tight group-hover:text-neutral-900 transition-colors" style={{
                      fontWeight: 800,
                      letterSpacing: '-0.04em',
                    }}>
                      {metric.value.toLocaleString()}
                    </div>
                    <div className="text-sm font-medium text-neutral-500" style={{ fontWeight: 600 }}>
                      {metric.label}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Filters & Search */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {filters.map(filter => (
                  <motion.button
                    key={filter.id}
                    onClick={() => setSelectedFilter(filter.id)}
                    className={`px-4 py-2.5 rounded-xl transition-all ${
                      selectedFilter === filter.id
                        ? 'bg-neutral-900 text-white shadow-lg'
                        : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                    }`}
                    whileHover={{ y: -1 }}
                    whileTap={{ scale: 0.98 }}
                    style={{ fontSize: '14px', fontWeight: 600 }}
                  >
                    {filter.label}
                    <span className={`ml-2 px-2 py-0.5 rounded-lg text-xs font-bold ${
                      selectedFilter === filter.id
                        ? 'bg-white/20 text-white'
                        : 'bg-neutral-100 text-neutral-600'
                    }`}>
                      {filter.count}
                    </span>
                  </motion.button>
                ))}
              </div>

              <div className="relative group">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 group-hover:text-neutral-600 transition-colors" strokeWidth={2.5} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search companies..."
                  className="pl-12 pr-4 py-3 w-80 bg-white border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{ fontSize: '14px', fontWeight: 500 }}
                />
              </div>
            </div>

            {/* Leads Table */}
            <div className="bg-white rounded-2xl border border-neutral-200 shadow-sm overflow-hidden">
              {/* Table Header - hide on mobile */}
              <div className="hidden md:block px-8 py-4 border-b border-neutral-200 bg-neutral-50">
                <div className="grid grid-cols-12 gap-4 uppercase text-neutral-600" style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  letterSpacing: '0.1em',
                }}>
                  <div className="col-span-4">Company</div>
                  <div className="col-span-2">Location</div>
                  <div className="col-span-2">Industry</div>
                  <div className="col-span-1 text-center">Data</div>
                  <div className="col-span-1 text-center">Score</div>
                  <div className="col-span-2">Top Product</div>
                  <div className="col-span-1 text-right">Action</div>
                </div>
              </div>

              {/* Table Body */}
              <div className="divide-y divide-neutral-100">
                {loading ? (
                  <div className="px-8 py-32 text-center">
                    <div className="inline-block w-8 h-8 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin mb-4" />
                    <p className="text-neutral-500 font-medium">Loading leads...</p>
                  </div>
                ) : (
                  <AnimatePresence mode="wait">
                    {filteredLeads.map((lead, idx) => (
                      <motion.div
                        key={lead.lead_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        transition={{ delay: idx * 0.03 }}
                        whileHover={{ backgroundColor: '#FAFAFA' }}
                        onClick={() => setSelectedLeadId(lead.lead_id)}
                        className="px-3 md:px-8 py-3 md:py-5 cursor-pointer group transition-all"
                      >
                        {/* MOBILE LAYOUT */}
                        <div className="md:hidden flex items-center gap-3">
                          {/* Avatar */}
                          <div className="w-10 h-10 rounded-lg flex items-center justify-center font-bold text-white text-xs flex-shrink-0" style={{
                            background: `linear-gradient(135deg, ${
                              lead.best_score >= 70 ? '#10B981, #059669' :
                              lead.best_score >= 50 ? '#F59E0B, #D97706' : '#6B7280, #4B5563'
                            })`,
                          }}>
                            {(lead.company_name || 'UK').substring(0, 2).toUpperCase()}
                          </div>

                          {/* Company info */}
                          <div className="flex-1 min-w-0">
                            <div className="font-bold text-neutral-900 text-sm truncate">
                              {lead.company_name || 'Unknown Company'}
                            </div>
                            <div className="text-xs text-neutral-500">
                              {lead.city || 'Tunisia'} • {lead.sector || 'General'}
                            </div>
                          </div>

                          {/* Score badge */}
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold text-sm flex-shrink-0 ${
                            lead.best_score >= 70 ? 'bg-emerald-100 text-emerald-700' :
                            lead.best_score >= 50 ? 'bg-amber-100 text-amber-700' :
                            'bg-neutral-100 text-neutral-600'
                          }`}>
                            {lead.best_score}
                          </div>

                          {/* Arrow */}
                          <ChevronRight className="w-5 h-5 text-neutral-400 flex-shrink-0" />
                        </div>

                        {/* DESKTOP LAYOUT */}
                        <div className="hidden md:grid grid-cols-12 gap-4 items-center">
                          {/* Company */}
                          <div className="col-span-4 flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl flex items-center justify-center font-bold text-white text-sm" style={{
                              background: `linear-gradient(135deg, ${
                                lead.best_score >= 70 ? '#10B981, #059669' :
                                lead.best_score >= 50 ? '#F59E0B, #D97706' : '#6B7280, #4B5563'
                              })`,
                            }}>
                              {(lead.company_name || 'UK').substring(0, 2).toUpperCase()}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="font-semibold text-neutral-900 truncate group-hover:text-neutral-900 transition-colors" style={{
                                fontSize: '14px',
                                fontWeight: 700,
                                letterSpacing: '-0.01em',
                              }}>
                                {lead.company_name || 'Unknown Company'}
                              </div>
                              <div className="text-sm text-neutral-500 truncate" style={{
                                fontSize: '12px',
                                fontWeight: 500,
                              }}>
                                {lead.employee_count || '—'} employees
                              </div>
                            </div>
                          </div>

                          {/* Location */}
                          <div className="col-span-2">
                            <div className="font-medium text-neutral-900" style={{ fontSize: '13px', fontWeight: 600 }}>
                              {lead.city || '—'}
                            </div>
                            <div className="text-xs text-neutral-500" style={{ fontWeight: 500 }}>
                              {lead.country || 'Tunisia'}
                            </div>
                          </div>

                          {/* Industry */}
                          <div className="col-span-2">
                            <span className="inline-flex px-3 py-1 rounded-lg bg-neutral-100 text-neutral-700 text-xs font-semibold" style={{
                              fontSize: '12px',
                              fontWeight: 600,
                            }}>
                              {lead.sector || 'General'}
                            </span>
                          </div>

                          {/* Data Status - NEW COLUMN */}
                          <div className="col-span-1 text-center">
                            {lead.best_score > 0 ? (
                              <CheckCircle2 className="w-5 h-5 text-emerald-600 mx-auto" strokeWidth={2.5} />
                            ) : (
                              <span className="text-neutral-300 font-bold">—</span>
                            )}
                          </div>

                          {/* Score */}
                          <div className="col-span-1 flex justify-center">
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-sm ${
                              lead.best_score >= 70 ? 'bg-emerald-50 text-emerald-700' :
                              lead.best_score >= 50 ? 'bg-amber-50 text-amber-700' : 'bg-neutral-100 text-neutral-600'
                            }`} style={{
                              fontWeight: 800,
                              letterSpacing: '-0.02em',
                            }}>
                              {Math.round(lead.best_score)}
                            </div>
                          </div>

                          {/* Top Product */}
                          <div className="col-span-2">
                            <div className="text-sm text-neutral-700 truncate" style={{
                              fontSize: '13px',
                              fontWeight: 600,
                            }}>
                              {lead.best_service}
                            </div>
                          </div>

                          {/* Action */}
                          <div className="col-span-1 flex justify-end">
                            <motion.div
                              className="w-8 h-8 rounded-lg bg-neutral-100 group-hover:bg-neutral-900 flex items-center justify-center transition-all"
                              whileHover={{ scale: 1.1 }}
                            >
                              <ChevronRight className="w-4 h-4 text-neutral-600 group-hover:text-white transition-colors" strokeWidth={2.5} />
                            </motion.div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPro;
