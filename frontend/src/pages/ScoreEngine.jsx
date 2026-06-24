/**
 * Score Engine - AI Scoring System Dashboard
 * Monitor and manage the scoring algorithm
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Target, Zap, TrendingUp, Activity, BarChart3, Settings,
  RefreshCw, CheckCircle2, Clock, Users, Globe, Award,
  AlertCircle, Database, Cpu, Sliders, Eye, ChevronRight
} from 'lucide-react';
import { getRankedLeads } from '../services/api';

export default function ScoreEngine({ onViewLead }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [recalculating, setRecalculating] = useState(false);
  const [selectedTab, setSelectedTab] = useState('overview');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const data = await getRankedLeads(10000, 0, {});
      setLeads(data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecalculate = async () => {
    setRecalculating(true);
    setTimeout(() => {
      loadData();
      setRecalculating(false);
    }, 3000);
  };

  // BUSINESS MANAGER PRIORITY WEIGHTS - EXACT MATCH
  const signals = [
    // 1️⃣ HIGHEST PRIORITY - Training
    { id: 'training', name: '🎯 Training History/Potential', weight: 40, icon: Database, color: 'red', detected: 0, priority: 1 },

    // 2️⃣ HIGH PRIORITY - New Machines & Hiring
    { id: 'tender', name: 'New Machine Purchase (Tender)', weight: 30, icon: Award, color: 'emerald', detected: 0, priority: 2 },
    { id: 'news', name: 'New Project/Machine (News)', weight: 25, icon: Activity, color: 'orange', detected: 0, priority: 2 },
    { id: 'new_hire', name: 'Hiring Engineers', weight: 20, icon: Users, color: 'blue', detected: leads.filter(l => l.best_score > 40).length, priority: 2 },
    { id: 'role_detected', name: 'Engineering Roles Detected', weight: 20, icon: Users, color: 'indigo', detected: 0, priority: 2 },

    // 3️⃣ MEDIUM PRIORITY - Multinational & Audit
    { id: 'multinational', name: 'Multinational Company', weight: 15, icon: Globe, color: 'purple', detected: leads.filter(l => l.is_multinational).length, priority: 3 },
    { id: 'audit', name: 'Under Audit/ISO', weight: 15, icon: CheckCircle2, color: 'amber', detected: leads.filter(l => l.under_audit).length, priority: 3 },
    { id: 'export', name: 'Export Activity', weight: 15, icon: Target, color: 'cyan', detected: leads.filter(l => l.is_exporter).length, priority: 3 },
    { id: 'funding', name: 'International Funding', weight: 15, icon: TrendingUp, color: 'violet', detected: 0, priority: 3 },

    // 4️⃣ SUPPORTING SIGNALS
    { id: 'event', name: 'Event Attendance', weight: 10, icon: Activity, color: 'pink', detected: 0, priority: 4 },
    { id: 'logo', name: 'SOLIDWORKS Logo Detected', weight: 10, icon: Eye, color: 'teal', detected: 0, priority: 4 },
  ];

  // Score distribution
  const scoreRanges = [
    { range: '90-100', count: leads.filter(l => l.best_score >= 90).length, color: 'emerald', label: 'Excellent' },
    { range: '70-89', count: leads.filter(l => l.best_score >= 70 && l.best_score < 90).length, color: 'green', label: 'High' },
    { range: '50-69', count: leads.filter(l => l.best_score >= 50 && l.best_score < 70).length, color: 'blue', label: 'Medium' },
    { range: '30-49', count: leads.filter(l => l.best_score >= 30 && l.best_score < 50).length, color: 'amber', label: 'Low' },
    { range: '0-29', count: leads.filter(l => l.best_score < 30).length, color: 'neutral', label: 'Research' },
  ];

  const avgScore = leads.length > 0 ? leads.reduce((sum, l) => sum + l.best_score, 0) / leads.length : 0;
  const totalDetectedSignals = signals.reduce((sum, s) => sum + s.detected, 0);
  const maxPossibleWeight = signals.reduce((sum, s) => sum + s.weight, 0);
  const activeSignals = signals.filter(s => s.detected > 0).length;

  const stats = [
    { label: 'Total Leads Scored', value: leads.length, icon: Database, color: 'blue', change: '121 companies' },
    { label: 'Average Score', value: Math.round(avgScore), icon: Target, color: 'emerald', change: `${Math.round(avgScore)}/100` },
    { label: 'Active Signals', value: `${activeSignals}/11`, icon: Zap, color: 'amber', change: 'Live detection' },
    { label: 'Hot Leads (60+)', value: leads.filter(l => l.best_score >= 60).length, icon: TrendingUp, color: 'red', change: 'Ready to call' },
  ];

  const tabs = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'signals', label: 'Signal Weights', icon: Sliders },
    { id: 'distribution', label: 'Score Distribution', icon: Activity },
    { id: 'methodology', label: 'Methodology', icon: Cpu },
  ];

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-purple-100 flex items-center justify-center">
                <Cpu className="w-6 h-6 text-purple-600" strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-neutral-900 mb-0.5" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  Score Engine
                </h1>
                <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                  AI-powered lead scoring system
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-4 py-2 bg-emerald-50 rounded-xl border border-emerald-200">
                <div className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
                <span className="text-sm font-bold text-emerald-700">Engine Active</span>
              </div>

              <motion.button
                onClick={handleRecalculate}
                disabled={recalculating}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold transition-all ${
                  recalculating
                    ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                    : 'bg-neutral-900 text-white hover:bg-neutral-800'
                }`}
                whileHover={!recalculating ? { y: -1, rotate: 180 } : {}}
                whileTap={!recalculating ? { scale: 0.98 } : {}}
                style={{ fontSize: '14px' }}
              >
                <RefreshCw className={`w-4 h-4 ${recalculating ? 'animate-spin' : ''}`} strokeWidth={2.5} />
                {recalculating ? 'Recalculating...' : 'Recalculate All'}
              </motion.button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {stats.map((stat, idx) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-neutral-50 rounded-xl p-4 border border-neutral-200"
                >
                  <div className="flex items-center gap-3 mb-2">
                    <div className={`w-10 h-10 rounded-lg bg-${stat.color}-100 flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 text-${stat.color}-600`} strokeWidth={2.5} />
                    </div>
                    <div className="flex-1">
                      <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                        {stat.value}
                      </div>
                      <div className="text-xs text-neutral-600 font-semibold">{stat.label}</div>
                    </div>
                  </div>
                  <div className="text-xs font-semibold text-neutral-500">{stat.change}</div>
                </motion.div>
              );
            })}
          </div>

          {/* Tabs */}
          <div className="flex items-center gap-2">
            {tabs.map(tab => {
              const Icon = tab.icon;
              const isActive = selectedTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setSelectedTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold transition-all ${
                    isActive
                      ? 'bg-neutral-900 text-white'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                  }`}
                  style={{ fontSize: '14px' }}
                >
                  <Icon className="w-4 h-4" strokeWidth={2.5} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-8">
          <AnimatePresence mode="wait">
            {selectedTab === 'overview' && (
              <motion.div
                key="overview"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                {/* Algorithm Status */}
                <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-8 text-white">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="text-sm font-bold uppercase tracking-wider mb-2">Scoring Algorithm</div>
                      <h2 className="text-3xl font-bold mb-3" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                        Claude Sonnet 4.5 AI Engine
                      </h2>
                      <p className="text-purple-100 mb-4 max-w-2xl">
                        Analyzes 11 buying signals across {leads.length} companies using business manager's priority weighting.
                        Training signals (40pts) are HIGHEST priority, followed by new machines (30pts) and hiring (20pts).
                      </p>
                      <div className="flex items-center gap-4">
                        <div className="px-4 py-2 bg-white/20 rounded-lg backdrop-blur-sm border border-white/30">
                          <div className="text-2xl font-bold">{maxPossibleWeight}</div>
                          <div className="text-xs text-purple-100">Max Points</div>
                        </div>
                        <div className="px-4 py-2 bg-white/20 rounded-lg backdrop-blur-sm border border-white/30">
                          <div className="text-2xl font-bold">{totalDetectedSignals}</div>
                          <div className="text-xs text-purple-100">Signals Detected</div>
                        </div>
                        <div className="px-4 py-2 bg-white/20 rounded-lg backdrop-blur-sm border border-white/30">
                          <div className="text-2xl font-bold">{activeSignals}</div>
                          <div className="text-xs text-purple-100">Active Signals</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Top Scoring Companies */}
                <div className="bg-white rounded-2xl border border-neutral-200 p-6">
                  <h3 className="text-lg font-bold text-neutral-900 mb-4" style={{ fontWeight: 700 }}>
                    Highest Scoring Leads
                  </h3>
                  <div className="space-y-3">
                    {leads.slice(0, 5).map((lead, idx) => (
                      <div
                        key={lead.lead_id}
                        className="flex items-center justify-between p-4 bg-neutral-50 rounded-xl hover:bg-neutral-100 transition-colors cursor-pointer"
                        onClick={() => onViewLead(lead.lead_id)}
                      >
                        <div className="flex items-center gap-4">
                          <div className="text-2xl font-bold text-neutral-400" style={{ fontWeight: 800 }}>
                            #{idx + 1}
                          </div>
                          <div>
                            <div className="font-bold text-neutral-900" style={{ fontSize: '15px', fontWeight: 700 }}>
                              {lead.company_name}
                            </div>
                            <div className="text-sm text-neutral-500">{lead.best_service}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <div className="text-3xl font-bold text-emerald-600" style={{ fontWeight: 800 }}>
                              {Math.round(lead.best_score)}
                            </div>
                            <div className="text-xs text-neutral-500">Score</div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-neutral-400" strokeWidth={2} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {selectedTab === 'signals' && (
              <motion.div
                key="signals"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid grid-cols-2 gap-4"
              >
                {signals.map((signal, idx) => {
                  const Icon = signal.icon;
                  const detectionRate = leads.length > 0 ? ((signal.detected / leads.length) * 100).toFixed(1) : 0;
                  return (
                    <motion.div
                      key={signal.id}
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.05 }}
                      className="bg-white rounded-xl p-6 border border-neutral-200 hover:shadow-lg transition-all"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-12 h-12 rounded-xl bg-${signal.color}-100 flex items-center justify-center`}>
                            <Icon className={`w-6 h-6 text-${signal.color}-600`} strokeWidth={2.5} />
                          </div>
                          <div>
                            <div className="font-bold text-neutral-900 mb-1" style={{ fontSize: '15px', fontWeight: 700 }}>
                              {signal.name}
                            </div>
                            <div className="flex items-center gap-2">
                              <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                signal.priority === 1 ? 'bg-red-100 text-red-700' :
                                signal.priority === 2 ? 'bg-emerald-100 text-emerald-700' :
                                signal.priority === 3 ? 'bg-blue-100 text-blue-700' :
                                'bg-neutral-100 text-neutral-600'
                              }`}>
                                Priority {signal.priority}
                              </span>
                              <span className="text-xs text-neutral-500">{signal.id}</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800 }}>
                            +{signal.weight}
                          </div>
                          <div className="text-xs text-neutral-500">Points</div>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-neutral-600 font-medium">Detected</span>
                          <span className="font-bold text-neutral-900">{signal.detected} companies</span>
                        </div>
                        <div className="h-2 bg-neutral-100 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${detectionRate}%` }}
                            transition={{ delay: 0.3 + idx * 0.05, duration: 0.6 }}
                            className={`h-full bg-${signal.color}-600`}
                          />
                        </div>
                        <div className="text-xs text-neutral-500 text-right">
                          {detectionRate}% detection rate
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </motion.div>
            )}

            {selectedTab === 'distribution' && (
              <motion.div
                key="distribution"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-2xl border border-neutral-200 p-8"
              >
                <h3 className="text-xl font-bold text-neutral-900 mb-6" style={{ fontWeight: 800 }}>
                  Score Distribution
                </h3>
                <div className="space-y-4">
                  {scoreRanges.map((range, idx) => {
                    const percentage = leads.length > 0 ? ((range.count / leads.length) * 100).toFixed(1) : 0;
                    return (
                      <div key={range.range} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <span className="text-sm font-bold text-neutral-900 w-20">{range.range}</span>
                            <span className={`px-3 py-1 rounded-lg text-xs font-bold bg-${range.color}-100 text-${range.color}-700`}>
                              {range.label}
                            </span>
                          </div>
                          <div className="flex items-center gap-4">
                            <span className="text-sm text-neutral-600">{percentage}%</span>
                            <span className="text-lg font-bold text-neutral-900 w-16 text-right">{range.count}</span>
                          </div>
                        </div>
                        <div className="h-8 bg-neutral-100 rounded-lg overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${percentage}%` }}
                            transition={{ delay: idx * 0.1, duration: 0.8 }}
                            className={`h-full bg-${range.color}-600 flex items-center justify-center`}
                          >
                            {percentage > 10 && (
                              <span className="text-white text-sm font-bold">{percentage}%</span>
                            )}
                          </motion.div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {selectedTab === 'methodology' && (
              <motion.div
                key="methodology"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-2xl border border-neutral-200 p-8"
              >
                <h3 className="text-xl font-bold text-neutral-900 mb-6" style={{ fontWeight: 800 }}>
                  How It Works
                </h3>
                <div className="space-y-4">
                  <div className="p-6 bg-gradient-to-br from-red-50 to-red-100 rounded-xl border-2 border-red-200">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg bg-red-600 flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-lg">1</span>
                      </div>
                      <div>
                        <h4 className="font-bold text-neutral-900 mb-2" style={{ fontSize: '16px', fontWeight: 700 }}>
                          Business Manager's Priority Weights
                        </h4>
                        <p className="text-sm text-neutral-700 font-medium">
                          Training (40pts) → New Machines (30pts) → Hiring (20pts) → Multinational+Audit (15pts each) → Events+Logo (10pts each)
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border-2 border-blue-200">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-lg">2</span>
                      </div>
                      <div>
                        <h4 className="font-bold text-neutral-900 mb-2" style={{ fontSize: '16px', fontWeight: 700 }}>
                          AI Detects Signals (Claude Sonnet 4.5)
                        </h4>
                        <p className="text-sm text-neutral-700 font-medium">
                          Scrapes data from LinkedIn, news, tenders, job boards → AI extracts signals → Cached to avoid re-processing same text
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl border-2 border-emerald-200">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg bg-emerald-600 flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-lg">3</span>
                      </div>
                      <div>
                        <h4 className="font-bold text-neutral-900 mb-2" style={{ fontSize: '16px', fontWeight: 700 }}>
                          Calculate Score (0-100)
                        </h4>
                        <p className="text-sm text-neutral-700 font-medium">
                          Sum detected signal weights → Divide by max possible (215pts) → Multiply by 100 = Final Score
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="p-6 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl border-2 border-purple-200">
                    <div className="flex items-start gap-3">
                      <div className="w-10 h-10 rounded-lg bg-purple-600 flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-lg">4</span>
                      </div>
                      <div>
                        <h4 className="font-bold text-neutral-900 mb-2" style={{ fontSize: '16px', fontWeight: 700 }}>
                          Classify & Recommend Action
                        </h4>
                        <p className="text-sm text-neutral-700 font-medium">
                          HOT (70+): Call today • WARM (60-69): Call this week • POTENTIAL (30-59): Pipeline • RESEARCH (&lt;30): Gather more data
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
