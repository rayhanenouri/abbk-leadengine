/**
 * Enterprise Analytics Dashboard
 * Professional KPI & Metrics Visualization
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Users, Target, TrendingUp, Activity, Globe, Package, CheckCircle,
  ArrowUpRight, ArrowDownRight, BarChart3, PieChart, Map, Award,
  Zap, Eye, DollarSign, Building2, ChevronRight, Download, Calendar
} from 'lucide-react';
import Sidebar from '../components/layout/Sidebar';
import { logout } from '../services/api';

const AnalyticsEnterprise = ({ onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMetric, setSelectedMetric] = useState('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`http://${window.location.hostname}:8000/api/analytics/overview`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setAnalytics(data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center" style={{ backgroundColor: '#FAFAFA' }}>
        <div className="text-center">
          <div className="inline-block w-12 h-12 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-neutral-600 font-semibold" style={{ fontSize: '14px', fontWeight: 600 }}>
            Loading analytics...
          </p>
        </div>
      </div>
    );
  }

  if (!analytics) return null;

  // Calculate derived metrics
  const totalLeads = analytics.summary.total_leads;
  const weekGrowth = ((analytics.summary.new_companies_this_week / totalLeads) * 100).toFixed(1);
  const avgScore = analytics.score_distribution.reduce((acc, bucket, idx) => {
    const midpoint = (idx * 10) + 5;
    return acc + (bucket.count * midpoint);
  }, 0) / totalLeads;

  const heroMetrics = [
    {
      label: 'Total Pipeline',
      value: totalLeads,
      change: `+${weekGrowth}%`,
      trend: 'up',
      subtitle: 'Active leads',
      icon: Users,
      color: 'slate',
      gradient: 'from-slate-700 to-slate-800',
    },
    {
      label: 'High Priority',
      value: analytics.summary.high_priority_leads,
      change: 'Score ≥70',
      trend: 'neutral',
      subtitle: 'Ready to close',
      icon: Target,
      color: 'red',
      gradient: 'from-red-600 to-red-700',
    },
    {
      label: 'Multinationals',
      value: analytics.high_value_leads.multinational,
      change: '+15.3%',
      trend: 'up',
      subtitle: 'Best converters',
      icon: Globe,
      color: 'blue',
      gradient: 'from-blue-700 to-blue-800',
    },
    {
      label: 'Conversion Rate',
      value: `${analytics.summary.conversion_rate}%`,
      change: '+2.1%',
      trend: 'up',
      subtitle: 'Month over month',
      icon: TrendingUp,
      color: 'emerald',
      gradient: 'from-emerald-600 to-emerald-700',
    },
  ];

  const statusData = analytics.leads_by_status;
  const maxStatus = Math.max(...statusData.map(s => s.count));

  const scoreData = analytics.score_distribution.filter(s => s.count > 0);
  const maxScoreCount = Math.max(...scoreData.map(s => s.count));

  return (
    <div className="flex-1 flex flex-col overflow-hidden" style={{ backgroundColor: '#FAFAFA' }}>
        {/* Header */}
        <div className="bg-white border-b border-neutral-200" style={{
          background: 'linear-gradient(to right, #FFFFFF 0%, #FAFAFA 100%)'
        }}>
          <div className="px-8 py-8">
            <div className="flex items-center justify-between mb-6">
              <div>
                <motion.h1
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-3xl font-bold text-neutral-900 tracking-tight mb-2"
                  style={{
                    fontWeight: 800,
                    letterSpacing: '-0.04em',
                  }}
                >
                  Analytics Dashboard
                </motion.h1>
                <motion.p
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-sm text-neutral-500"
                  style={{ fontWeight: 500 }}
                >
                  Real-time insights and performance metrics
                </motion.p>
              </div>

              <div className="flex items-center gap-3">
                <motion.button
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-4 py-2.5 text-neutral-700 bg-white hover:bg-neutral-50 rounded-xl transition-all border border-neutral-200"
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  <Calendar className="w-4 h-4" strokeWidth={2.5} />
                  Last 30 days
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02, y: -1 }}
                  whileTap={{ scale: 0.98 }}
                  className="flex items-center gap-2 px-4 py-2.5 bg-neutral-900 text-white rounded-xl transition-all relative overflow-hidden group"
                  style={{ fontSize: '14px', fontWeight: 600 }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
                  <Download className="w-4 h-4" strokeWidth={2.5} />
                  Export Report
                </motion.button>
              </div>
            </div>

            {/* Quick Stats Bar */}
            <div className="flex items-center gap-8">
              {[
                { label: 'Avg Score', value: avgScore.toFixed(1), icon: BarChart3 },
                { label: 'New This Week', value: analytics.summary.new_companies_this_week, icon: Zap },
                { label: 'Active Signals', value: analytics.summary.total_signals_this_week, icon: Activity },
              ].map((stat, idx) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + idx * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center">
                    <stat.icon className="w-5 h-5 text-neutral-700" strokeWidth={2.5} />
                  </div>
                  <div>
                    <div className="text-xl font-bold text-neutral-900" style={{ fontWeight: 700, letterSpacing: '-0.02em' }}>
                      {stat.value}
                    </div>
                    <div className="text-xs text-neutral-500" style={{ fontWeight: 600 }}>
                      {stat.label}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto">
          <div className="p-8 space-y-8">
            {/* Hero Metrics */}
            <div className="grid grid-cols-4 gap-6">
              {heroMetrics.map((metric, idx) => (
                <motion.div
                  key={metric.label}
                  initial={{ opacity: 0, y: 30 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.15, type: 'spring', stiffness: 100 }}
                  whileHover={{ y: -8, scale: 1.02 }}
                  className="relative overflow-hidden rounded-2xl cursor-pointer group"
                  style={{
                    background: 'white',
                    border: '1px solid #E5E5E5',
                  }}
                >
                  {/* Gradient Background on Hover */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${metric.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-500`} />

                  <div className="relative p-6">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-6">
                      <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${metric.gradient} flex items-center justify-center transform group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
                        <metric.icon className="w-7 h-7 text-white" strokeWidth={2.5} />
                      </div>
                      {metric.trend !== 'neutral' && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ delay: 0.5 + idx * 0.1, type: 'spring' }}
                          className={`flex items-center gap-1 px-3 py-1.5 rounded-xl ${
                            metric.trend === 'up' ? 'bg-emerald-50' : 'bg-red-50'
                          }`}
                        >
                          {metric.trend === 'up' ? (
                            <ArrowUpRight className="w-4 h-4 text-emerald-600" strokeWidth={2.5} />
                          ) : (
                            <ArrowDownRight className="w-4 h-4 text-red-600" strokeWidth={2.5} />
                          )}
                          <span className={`text-xs font-bold ${
                            metric.trend === 'up' ? 'text-emerald-600' : 'text-red-600'
                          }`} style={{ letterSpacing: '-0.01em' }}>
                            {metric.change}
                          </span>
                        </motion.div>
                      )}
                    </div>

                    {/* Value */}
                    <motion.div
                      initial={{ opacity: 0, scale: 0.5 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.3 + idx * 0.1, type: 'spring', stiffness: 200 }}
                      className="text-4xl font-bold text-neutral-900 mb-2 tracking-tight group-hover:text-neutral-900 transition-colors"
                      style={{
                        fontWeight: 800,
                        letterSpacing: '-0.05em',
                      }}
                    >
                      {typeof metric.value === 'number' ? metric.value.toLocaleString() : metric.value}
                    </motion.div>

                    {/* Label */}
                    <div className="text-sm font-semibold text-neutral-900 mb-1" style={{ fontWeight: 700 }}>
                      {metric.label}
                    </div>
                    <div className="text-xs text-neutral-500" style={{ fontWeight: 500 }}>
                      {metric.subtitle}
                    </div>

                    {/* Decorative Element */}
                    <div className="absolute bottom-0 right-0 w-32 h-32 opacity-5 transform translate-x-8 translate-y-8">
                      <metric.icon className="w-full h-full text-neutral-900" strokeWidth={1} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Sales Funnel & Score Distribution */}
            <div className="grid grid-cols-2 gap-6">
              {/* Sales Funnel */}
              <motion.div
                initial={{ opacity: 0, x: -30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 }}
                whileHover={{ y: -4, transition: { duration: 0.3 } }}
                className="bg-white rounded-2xl p-8 border border-neutral-200 hover:shadow-xl transition-shadow cursor-pointer"
              >
                <div className="flex items-center justify-between mb-6">
                  <motion.div whileHover={{ x: 4 }}>
                    <h2 className="text-xl font-bold text-neutral-900 tracking-tight mb-1" style={{
                      fontWeight: 800,
                      letterSpacing: '-0.03em',
                    }}>
                      Sales Pipeline
                    </h2>
                    <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                      Lead status distribution
                    </p>
                  </motion.div>
                  <motion.div
                    className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                  >
                    <BarChart3 className="w-5 h-5 text-neutral-700" strokeWidth={2.5} />
                  </motion.div>
                </div>

                <div className="space-y-4">
                  {statusData.map((status, idx) => {
                    const percentage = (status.count / maxStatus) * 100;
                    const statusColors = {
                      new: { bg: 'bg-neutral-700', light: 'bg-neutral-50', text: 'text-neutral-700' },
                      contacted: { bg: 'bg-orange-600', light: 'bg-orange-50', text: 'text-orange-700' },
                      qualified: { bg: 'bg-red-500', light: 'bg-red-50', text: 'text-red-700' },
                      converted: { bg: 'bg-red-700', light: 'bg-red-50', text: 'text-red-700' },
                      lost: { bg: 'bg-neutral-400', light: 'bg-neutral-50', text: 'text-neutral-600' },
                    };
                    const colors = statusColors[status.status] || statusColors.new;

                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 1 + idx * 0.1 }}
                        className="space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div className={`w-3 h-3 rounded-full ${colors.bg}`} />
                            <span className="text-sm font-semibold text-neutral-900 capitalize" style={{ fontWeight: 600 }}>
                              {status.status || 'new'}
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                              {((status.count / totalLeads) * 100).toFixed(1)}%
                            </span>
                            <span className="text-sm font-bold text-neutral-900" style={{ fontWeight: 700 }}>
                              {status.count}
                            </span>
                          </div>
                        </div>
                        <div className="relative h-3 bg-neutral-100 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ delay: 1.2 + idx * 0.1, duration: 1, ease: 'easeOut' }}
                            className={`absolute inset-y-0 left-0 ${colors.bg} rounded-full`}
                          />
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>

              {/* Score Distribution */}
              <motion.div
                initial={{ opacity: 0, x: 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 }}
                whileHover={{ y: -4, transition: { duration: 0.3 } }}
                className="bg-white rounded-2xl p-8 border border-neutral-200 hover:shadow-xl transition-shadow cursor-pointer"
              >
                <div className="flex items-center justify-between mb-6">
                  <motion.div whileHover={{ x: 4 }}>
                    <h2 className="text-xl font-bold text-neutral-900 tracking-tight mb-1" style={{
                      fontWeight: 800,
                      letterSpacing: '-0.03em',
                    }}>
                      Lead Quality
                    </h2>
                    <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                      Score distribution
                    </p>
                  </motion.div>
                  <motion.div
                    className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                  >
                    <PieChart className="w-5 h-5 text-neutral-700" strokeWidth={2.5} />
                  </motion.div>
                </div>

                <div className="space-y-3">
                  {scoreData.map((bucket, idx) => {
                    const percentage = (bucket.count / maxScoreCount) * 100;
                    const scoreNum = parseInt(bucket.range.split('-')[0]);

                    // Simple 3-tier system: green (high), blue (medium), grey (low)
                    const getColor = (score) => {
                      if (score >= 60) return { bg: 'bg-emerald-600', text: 'text-emerald-700' };
                      if (score >= 30) return { bg: 'bg-blue-600', text: 'text-blue-700' };
                      return { bg: 'bg-neutral-500', text: 'text-neutral-600' };
                    };

                    const color = getColor(scoreNum);

                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: 1.2 + idx * 0.05 }}
                        className="flex items-center gap-4"
                      >
                        <div className="w-16 text-sm font-bold text-neutral-900" style={{ fontWeight: 700 }}>
                          {bucket.range}
                        </div>
                        <div className="flex-1 relative h-10 bg-neutral-100 rounded-xl overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ delay: 1.4 + idx * 0.05, duration: 0.8, ease: 'easeOut' }}
                            className={`absolute inset-y-0 left-0 rounded-xl flex items-center justify-end px-3 ${color.bg}`}
                          >
                            <span className="text-white text-sm font-bold" style={{ fontWeight: 700 }}>
                              {bucket.count}
                            </span>
                          </motion.div>
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            </div>

            {/* Top Sectors - Leaderboard Style */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.5 }}
              className="bg-white rounded-2xl p-8 border border-neutral-200"
            >
              <div className="flex items-center justify-between mb-8">
                <motion.div whileHover={{ x: 4 }}>
                  <h2 className="text-xl font-bold text-neutral-900 tracking-tight mb-1" style={{
                    fontWeight: 800,
                    letterSpacing: '-0.03em',
                  }}>
                    Top Performing Sectors
                  </h2>
                  <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                    Highest volume industries
                  </p>
                </motion.div>
                <motion.div
                  className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <Building2 className="w-5 h-5 text-neutral-700" strokeWidth={2.5} />
                </motion.div>
              </div>

              <div className="space-y-3">
                {analytics.leads_by_sector.slice(0, 8).map((sector, idx) => {
                  const maxCount = analytics.leads_by_sector[0].count;
                  const percentage = (sector.count / maxCount) * 100;
                  const rankColors = [
                    { bg: 'from-red-600 to-red-700', border: 'border-red-500', shadow: 'shadow-red-500/30' },
                    { bg: 'from-red-500 to-red-600', border: 'border-red-400', shadow: 'shadow-red-400/20' },
                    { bg: 'from-neutral-700 to-neutral-800', border: 'border-neutral-600', shadow: 'shadow-neutral-600/20' },
                  ];
                  const isTopThree = idx < 3;

                  return (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, x: -40 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 1.7 + idx * 0.08, duration: 0.4 }}
                      className="relative"
                    >
                      <motion.div
                        className="flex items-center gap-4 cursor-pointer p-3 rounded-xl group"
                        whileHover={{
                          x: 8,
                          y: -2,
                          transition: { duration: 0.2, ease: "easeOut" }
                        }}
                      >
                        {/* Rank Badge */}
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center font-bold text-xl flex-shrink-0 ${
                          isTopThree
                            ? `bg-gradient-to-br ${rankColors[idx].bg} text-white shadow-lg ${rankColors[idx].shadow} border-2 ${rankColors[idx].border}`
                            : 'bg-neutral-100 text-neutral-700 border-2 border-neutral-200'
                        }`} style={{
                          fontWeight: 800,
                          letterSpacing: '-0.02em',
                        }}>
                          {idx + 1}
                        </div>

                        {/* Sector Name */}
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-bold text-neutral-900 mb-2 truncate" style={{ fontWeight: 700 }}>
                            {sector.sector || 'Unknown'}
                          </div>

                          {/* Progress Bar */}
                          <div className="relative h-8 bg-neutral-100 rounded-xl overflow-hidden">
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${percentage}%` }}
                              transition={{ delay: 2 + idx * 0.08, duration: 1, ease: 'easeOut' }}
                              className={`absolute inset-y-0 left-0 rounded-xl flex items-center justify-between px-4 ${
                                isTopThree
                                  ? `bg-gradient-to-r ${rankColors[idx].bg}`
                                  : 'bg-neutral-900'
                              } group-hover:shadow-lg transition-shadow`}
                            >
                              <span className="text-white text-sm font-bold" style={{ fontWeight: 700 }}>
                                {sector.count} leads
                              </span>
                              <span className="text-white/80 text-xs font-semibold">
                                {((sector.count / totalLeads) * 100).toFixed(1)}%
                              </span>
                            </motion.div>
                          </div>
                        </div>

                        {/* Arrow Indicator */}
                        <ChevronRight className="w-5 h-5 text-neutral-300 group-hover:text-neutral-900 transition-colors" strokeWidth={2.5} />
                      </motion.div>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>

            {/* Geographic Distribution - Professional Chart */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 2 }}
              whileHover={{ y: -4, transition: { duration: 0.3 } }}
              className="bg-white rounded-2xl p-8 border border-neutral-200 hover:shadow-xl transition-shadow cursor-pointer"
            >
              <div className="flex items-center justify-between mb-8">
                <motion.div whileHover={{ x: 4 }}>
                  <h2 className="text-xl font-bold text-neutral-900 tracking-tight mb-1" style={{
                    fontWeight: 800,
                    letterSpacing: '-0.03em',
                  }}>
                    Geographic Distribution
                  </h2>
                  <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                    Lead coverage by city
                  </p>
                </motion.div>
                <motion.div
                  className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <Map className="w-5 h-5 text-neutral-700" strokeWidth={2.5} />
                </motion.div>
              </div>

              <div className="flex items-center justify-between gap-12">
                {/* Professional Donut Chart */}
                <div className="flex-shrink-0 relative" style={{ width: '300px', height: '300px' }}>
                  <svg width="300" height="300" viewBox="0 0 300 300" className="transform -rotate-90">
                    {/* Background ring */}
                    <circle
                      cx="150"
                      cy="150"
                      r="110"
                      fill="none"
                      stroke="#F5F5F5"
                      strokeWidth="44"
                    />

                    {/* Data segments */}
                    {analytics.geographic.by_city.slice(0, 8).map((city, idx) => {
                      const total = analytics.geographic.by_city.slice(0, 8).reduce((acc, c) => acc + c.count, 0);
                      const percentage = city.count / total;
                      const colors = [
                        '#2563EB', '#059669', '#EAB308', '#0891B2',
                        '#D97706', '#334155', '#7C3AED', '#EC4899'
                      ];

                      const prevPercentage = analytics.geographic.by_city
                        .slice(0, idx)
                        .reduce((acc, c) => acc + c.count / total, 0);

                      const radius = 110;
                      const circumference = 2 * Math.PI * radius;
                      const strokeDasharray = `${percentage * circumference} ${circumference}`;
                      const strokeDashoffset = -prevPercentage * circumference;

                      return (
                        <motion.circle
                          key={idx}
                          initial={{ strokeDasharray: `0 ${circumference}` }}
                          animate={{ strokeDasharray }}
                          transition={{ delay: 2.2 + idx * 0.08, duration: 0.8, ease: 'easeOut' }}
                          cx="150"
                          cy="150"
                          r={radius}
                          fill="none"
                          stroke={colors[idx]}
                          strokeWidth="44"
                          strokeDashoffset={strokeDashoffset}
                          strokeLinecap="round"
                          style={{
                            cursor: 'pointer',
                            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                          }}
                          onMouseEnter={(e) => {
                            e.target.style.strokeWidth = '52';
                            e.target.style.filter = `drop-shadow(0 0 16px ${colors[idx]})`;
                            e.target.style.opacity = '0.9';
                          }}
                          onMouseLeave={(e) => {
                            e.target.style.strokeWidth = '44';
                            e.target.style.filter = 'none';
                            e.target.style.opacity = '1';
                          }}
                        />
                      );
                    })}
                  </svg>

                  {/* Center stats */}
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: 2.5, type: 'spring', stiffness: 200 }}
                      className="text-center"
                    >
                      <div className="text-5xl font-bold text-neutral-900 mb-1" style={{
                        fontWeight: 800,
                        letterSpacing: '-0.04em'
                      }}>
                        {analytics.geographic.by_city.length}
                      </div>
                      <div className="text-neutral-500 uppercase tracking-wide" style={{
                        fontWeight: 600,
                        letterSpacing: '0.05em',
                        fontSize: '11px'
                      }}>
                        Cities
                      </div>
                    </motion.div>
                  </div>
                </div>

                {/* Legend */}
                <div className="flex-1 grid grid-cols-2 gap-x-8 gap-y-3">
                  {analytics.geographic.by_city.slice(0, 8).map((city, idx) => {
                    const colors = [
                      'bg-blue-600', 'bg-emerald-600', 'bg-yellow-500', 'bg-cyan-700',
                      'bg-amber-600', 'bg-slate-700', 'bg-violet-600', 'bg-pink-600'
                    ];
                    const total = analytics.geographic.by_city.slice(0, 8).reduce((acc, c) => acc + c.count, 0);
                    const percentage = ((city.count / total) * 100).toFixed(1);

                    return (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 2.3 + idx * 0.04 }}
                        whileHover={{ x: 8, y: -2, transition: { duration: 0.2 } }}
                        className="flex items-center gap-3 cursor-pointer group p-2 rounded-lg hover:bg-neutral-50 transition-all"
                      >
                        <motion.div
                          className={`w-3 h-3 rounded-sm ${colors[idx]} flex-shrink-0`}
                          whileHover={{ scale: 1.3, rotate: 12, transition: { duration: 0.2 } }}
                        />
                        <div className="flex-1 min-w-0">
                          <div className="text-neutral-900 truncate group-hover:text-blue-600 transition-colors" style={{
                            fontWeight: 700,
                            fontSize: '13px',
                            letterSpacing: '-0.01em'
                          }}>
                            {city.city}
                          </div>
                          <div className="text-neutral-500" style={{
                            fontWeight: 500,
                            fontSize: '11px'
                          }}>
                            {percentage}%
                          </div>
                        </div>
                        <div className="text-neutral-900" style={{
                          fontWeight: 700,
                          fontSize: '14px',
                          letterSpacing: '-0.01em'
                        }}>
                          {city.count}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
  );
};

export default AnalyticsEnterprise;
