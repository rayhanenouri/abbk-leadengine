/**
 * Professional Analytics Dashboard
 * Enterprise-grade metrics visualization
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users, Target, TrendingUp, Activity, Globe, Package, CheckCircle,
  ArrowUpRight, ArrowDownRight, Building2, DollarSign, Zap, Eye,
  ArrowLeft, Download
} from 'lucide-react';
import Sidebar from '../components/layout/Sidebar';
import { logout } from '../services/api';

const API_BASE_URL = `http://${window.location.hostname}:8000/api`;

const AnalyticsPro = ({ onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/analytics/overview`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.reload();
        return;
      }

      if (!response.ok) throw new Error('Failed to fetch analytics');

      const data = await response.json();
      setAnalytics(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen" style={{ backgroundColor: '#FAFAFA' }}>
        <Sidebar currentView="analytics" onViewChange={() => {}} onLogout={logout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="inline-block w-12 h-12 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-neutral-600 font-semibold" style={{ fontSize: '14px', fontWeight: 600 }}>
              Loading analytics...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen" style={{ backgroundColor: '#FAFAFA' }}>
        <Sidebar currentView="analytics" onViewChange={() => {}} onLogout={logout} />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-600 font-semibold">Error: {error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!analytics) return null;

  const metrics = [
    {
      label: 'Total Leads',
      value: analytics.summary.total_leads,
      change: `+${analytics.summary.new_companies_this_week}`,
      trend: 'up',
      icon: Users,
      color: 'blue',
    },
    {
      label: 'High Priority',
      value: analytics.summary.high_priority_leads,
      subtitle: 'Score ≥ 70',
      change: '+12.5%',
      trend: 'up',
      icon: Target,
      color: 'green',
    },
    {
      label: 'New This Week',
      value: analytics.summary.new_companies_this_week,
      change: '+8.2%',
      trend: 'up',
      icon: TrendingUp,
      color: 'amber',
    },
    {
      label: 'Conversion Rate',
      value: `${analytics.summary.conversion_rate}%`,
      subtitle: `${analytics.summary.converted_count}/${analytics.summary.contacted_count} contacted`,
      change: '+2.3%',
      trend: 'up',
      icon: Activity,
      color: 'purple',
    },
  ];

  const highValueLeads = [
    {
      label: 'Multinationals',
      count: analytics.high_value_leads.multinational,
      description: 'International companies',
      icon: Globe,
      color: 'blue',
    },
    {
      label: 'Exporters',
      count: analytics.high_value_leads.exporter,
      description: 'International audits',
      icon: Package,
      color: 'emerald',
    },
    {
      label: 'Under Audit',
      count: analytics.high_value_leads.under_audit,
      description: 'Compliance pressure',
      icon: CheckCircle,
      color: 'amber',
    },
  ];

  const statusColors = {
    new: { bg: 'bg-blue-500', light: 'bg-blue-50', text: 'text-blue-700' },
    contacted: { bg: 'bg-purple-500', light: 'bg-purple-50', text: 'text-purple-700' },
    qualified: { bg: 'bg-emerald-500', light: 'bg-emerald-50', text: 'text-emerald-700' },
    converted: { bg: 'bg-green-600', light: 'bg-green-50', text: 'text-green-700' },
    lost: { bg: 'bg-neutral-400', light: 'bg-neutral-50', text: 'text-neutral-600' },
  };

  return (
    <div className="flex h-screen" style={{ backgroundColor: '#FAFAFA' }}>
      <Sidebar currentView="analytics" onViewChange={(view) => {
        if (view === 'dashboard') onBack();
      }} onLogout={logout} />

      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className="bg-white border-b border-neutral-200">
          <div className="px-8 py-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold text-neutral-900 tracking-tight mb-1" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  Analytics Overview
                </h1>
                <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                  Sales intelligence metrics and performance insights
                </p>
              </div>

              <div className="flex items-center gap-3">
                <motion.button
                  onClick={onBack}
                  className="flex items-center gap-2 px-4 py-2.5 text-neutral-700 hover:bg-neutral-100 rounded-xl transition-all border border-neutral-200"
                  whileHover={{ y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  <ArrowLeft className="w-4 h-4" strokeWidth={2.5} />
                  Back
                </motion.button>
                <motion.button
                  className="flex items-center gap-2 px-4 py-2.5 text-neutral-700 hover:bg-neutral-100 rounded-xl transition-all border border-neutral-200"
                  whileHover={{ y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  <Download className="w-4 h-4" strokeWidth={2.5} />
                  Export
                </motion.button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-8 space-y-8">
            {/* Main Metrics */}
            <div className="grid grid-cols-4 gap-6">
              {metrics.map((metric, idx) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  whileHover={{ y: -4, transition: { duration: 0.2 } }}
                  className="bg-white rounded-2xl p-6 border border-neutral-200 hover:border-neutral-300 hover:shadow-xl transition-all cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-6">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      metric.color === 'blue' ? 'bg-blue-50' :
                      metric.color === 'green' ? 'bg-emerald-50' :
                      metric.color === 'amber' ? 'bg-amber-50' : 'bg-purple-50'
                    }`}>
                      <metric.icon className={`w-6 h-6 ${
                        metric.color === 'blue' ? 'text-blue-600' :
                        metric.color === 'green' ? 'text-emerald-600' :
                        metric.color === 'amber' ? 'text-amber-600' : 'text-purple-600'
                      }`} strokeWidth={2.5} />
                    </div>
                    {metric.trend && (
                      <div className={`flex items-center gap-1 px-2.5 py-1 rounded-lg ${
                        metric.trend === 'up' ? 'bg-emerald-50' : 'bg-red-50'
                      }`}>
                        {metric.trend === 'up' ? (
                          <ArrowUpRight className="w-3.5 h-3.5 text-emerald-600" strokeWidth={2.5} />
                        ) : (
                          <ArrowDownRight className="w-3.5 h-3.5 text-red-600" strokeWidth={2.5} />
                        )}
                        <span className={`text-xs font-bold ${
                          metric.trend === 'up' ? 'text-emerald-600' : 'text-red-600'
                        }`} style={{ letterSpacing: '-0.01em' }}>
                          {metric.change}
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="space-y-2">
                    <div className="text-3xl font-bold text-neutral-900 tracking-tight" style={{
                      fontWeight: 800,
                      letterSpacing: '-0.04em',
                    }}>
                      {typeof metric.value === 'number' ? metric.value.toLocaleString() : metric.value}
                    </div>
                    <div className="text-sm font-medium text-neutral-900" style={{ fontWeight: 600 }}>
                      {metric.label}
                    </div>
                    {metric.subtitle && (
                      <div className="text-xs text-neutral-500" style={{ fontWeight: 500 }}>
                        {metric.subtitle}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* High-Value Leads */}
            <div>
              <h2 className="text-lg font-bold text-neutral-900 mb-4 tracking-tight" style={{
                fontWeight: 700,
                letterSpacing: '-0.02em',
              }}>
                High-Value Segments
              </h2>
              <div className="grid grid-cols-3 gap-6">
                {highValueLeads.map((segment, idx) => (
                  <motion.div
                    key={segment.label}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4 + idx * 0.1 }}
                    whileHover={{ y: -2 }}
                    className="bg-white rounded-2xl p-6 border border-neutral-200 hover:border-neutral-300 hover:shadow-lg transition-all"
                  >
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${
                      segment.color === 'blue' ? 'bg-blue-50' :
                      segment.color === 'emerald' ? 'bg-emerald-50' : 'bg-amber-50'
                    }`}>
                      <segment.icon className={`w-6 h-6 ${
                        segment.color === 'blue' ? 'text-blue-600' :
                        segment.color === 'emerald' ? 'text-emerald-600' : 'text-amber-600'
                      }`} strokeWidth={2.5} />
                    </div>
                    <div className="text-3xl font-bold text-neutral-900 mb-2 tracking-tight" style={{
                      fontWeight: 800,
                      letterSpacing: '-0.04em',
                    }}>
                      {segment.count}
                    </div>
                    <div className="text-sm font-semibold text-neutral-900 mb-1" style={{ fontWeight: 600 }}>
                      {segment.label}
                    </div>
                    <div className="text-xs text-neutral-500" style={{ fontWeight: 500 }}>
                      {segment.description}
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Sales Funnel */}
            <div className="bg-white rounded-2xl p-8 border border-neutral-200">
              <h2 className="text-lg font-bold text-neutral-900 mb-6 tracking-tight" style={{
                fontWeight: 700,
                letterSpacing: '-0.02em',
              }}>
                Sales Funnel
              </h2>
              <div className="space-y-4">
                {analytics.leads_by_status.map((status, index) => {
                  const maxCount = Math.max(...analytics.leads_by_status.map(s => s.count));
                  const percentage = (status.count / maxCount) * 100;
                  const colors = statusColors[status.status] || statusColors.new;

                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="flex items-center gap-4"
                    >
                      <div className="w-32 text-sm font-semibold text-neutral-900 capitalize" style={{
                        fontSize: '13px',
                        fontWeight: 600,
                      }}>
                        {status.status || 'new'}
                      </div>
                      <div className="flex-1 bg-neutral-100 rounded-xl h-12 relative overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ duration: 1, delay: 0.8 + index * 0.1, ease: 'easeOut' }}
                          className={`${colors.bg} h-12 rounded-xl flex items-center justify-between px-4 relative overflow-hidden group`}
                        >
                          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
                          <span className="text-white font-bold" style={{
                            fontSize: '14px',
                            fontWeight: 700,
                          }}>
                            {status.count}
                          </span>
                          <span className="text-white/80 text-xs font-semibold">
                            {((status.count / analytics.summary.total_leads) * 100).toFixed(1)}%
                          </span>
                        </motion.div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Top Sectors */}
            <div className="grid grid-cols-2 gap-6">
              {/* By Count */}
              <div className="bg-white rounded-2xl p-8 border border-neutral-200">
                <h2 className="text-lg font-bold text-neutral-900 mb-6 tracking-tight" style={{
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                }}>
                  Top Sectors by Volume
                </h2>
                <div className="space-y-3">
                  {analytics.top_sectors_by_count.slice(0, 8).map((sector, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1 + idx * 0.05 }}
                      className="flex items-center justify-between py-2"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-neutral-900 flex items-center justify-center text-white text-xs font-bold">
                          {idx + 1}
                        </div>
                        <span className="text-sm font-medium text-neutral-900" style={{ fontWeight: 600 }}>
                          {sector.sector || 'Unknown'}
                        </span>
                      </div>
                      <span className="text-sm font-bold text-neutral-600" style={{ fontWeight: 700 }}>
                        {sector.count}
                      </span>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* By Score */}
              <div className="bg-white rounded-2xl p-8 border border-neutral-200">
                <h2 className="text-lg font-bold text-neutral-900 mb-6 tracking-tight" style={{
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                }}>
                  Top Sectors by Quality
                </h2>
                <div className="space-y-3">
                  {analytics.top_sectors_by_score.slice(0, 8).map((sector, idx) => (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1 + idx * 0.05 }}
                      className="flex items-center justify-between py-2"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold ${
                          sector.avg_score >= 70 ? 'bg-emerald-500' :
                          sector.avg_score >= 50 ? 'bg-amber-500' : 'bg-neutral-400'
                        }`}>
                          {idx + 1}
                        </div>
                        <span className="text-sm font-medium text-neutral-900" style={{ fontWeight: 600 }}>
                          {sector.sector || 'Unknown'}
                        </span>
                      </div>
                      <span className="text-sm font-bold text-neutral-900" style={{ fontWeight: 700 }}>
                        {sector.avg_score.toFixed(1)}
                      </span>
                    </motion.div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPro;
