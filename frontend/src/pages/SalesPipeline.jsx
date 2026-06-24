/**
 * Sales Pipeline - Kanban Board
 * Visual pipeline management for lead progression
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Users, TrendingUp, Target, CheckCircle2, XCircle,
  Clock, DollarSign, Percent, ArrowRight, Eye, Phone,
  Mail, Calendar, BarChart3
} from 'lucide-react';
import { getRankedLeads } from '../services/api';

export default function SalesPipeline({ onViewLead }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const data = await getRankedLeads(10000, 0, {});
      setLeads(data);
    } catch (err) {
      console.error('Failed to load leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const stages = [
    { id: 'new', label: 'New Leads', icon: Users, color: 'blue', status: 'new' },
    { id: 'contacted', label: 'Contacted', icon: Phone, color: 'purple', status: 'contacted' },
    { id: 'qualified', label: 'Qualified', icon: Target, color: 'emerald', status: 'qualified' },
    { id: 'converted', label: 'Converted', icon: CheckCircle2, color: 'green', status: 'converted' },
    { id: 'lost', label: 'Lost', icon: XCircle, color: 'neutral', status: 'lost' },
  ];

  const getLeadsByStage = (status) => {
    return leads.filter(l => (l.status || 'new') === status);
  };

  const getTotalValue = (leadsInStage) => {
    return leadsInStage.reduce((sum, lead) => sum + (lead.best_score || 0), 0);
  };

  const avgScore = leads.length > 0 ? leads.reduce((sum, l) => sum + l.best_score, 0) / leads.length : 0;
  const conversionRate = leads.length > 0 ? (getLeadsByStage('converted').length / leads.length * 100).toFixed(1) : 0;
  const totalPipeline = leads.filter(l => !['converted', 'lost'].includes(l.status || 'new')).length;

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 mb-1" style={{
                fontWeight: 800,
                letterSpacing: '-0.04em',
              }}>
                Sales Pipeline
              </h1>
              <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                Track and manage leads through the sales process
              </p>
            </div>
          </div>

          {/* Metrics */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-neutral-50 rounded-xl p-4 border border-neutral-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-blue-600" strokeWidth={2.5} />
                </div>
                <div>
                  <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                    {totalPipeline}
                  </div>
                  <div className="text-xs text-neutral-600 font-semibold">Active Pipeline</div>
                </div>
              </div>
            </div>

            <div className="bg-neutral-50 rounded-xl p-4 border border-neutral-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-emerald-100 flex items-center justify-center">
                  <Target className="w-5 h-5 text-emerald-600" strokeWidth={2.5} />
                </div>
                <div>
                  <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                    {Math.round(avgScore)}
                  </div>
                  <div className="text-xs text-neutral-600 font-semibold">Avg Score</div>
                </div>
              </div>
            </div>

            <div className="bg-neutral-50 rounded-xl p-4 border border-neutral-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-green-600" strokeWidth={2.5} />
                </div>
                <div>
                  <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                    {getLeadsByStage('converted').length}
                  </div>
                  <div className="text-xs text-neutral-600 font-semibold">Converted</div>
                </div>
              </div>
            </div>

            <div className="bg-neutral-50 rounded-xl p-4 border border-neutral-200">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                  <Percent className="w-5 h-5 text-purple-600" strokeWidth={2.5} />
                </div>
                <div>
                  <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                    {conversionRate}%
                  </div>
                  <div className="text-xs text-neutral-600 font-semibold">Win Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Pipeline Board */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden">
        <div className="p-6 h-full">
          <div className="flex gap-4 h-full" style={{ minWidth: 'max-content' }}>
            {stages.map((stage) => {
              const stageLeads = getLeadsByStage(stage.status);
              const StageIcon = stage.icon;
              const stageValue = getTotalValue(stageLeads);

              return (
                <div key={stage.id} className="flex-shrink-0 flex flex-col" style={{ width: '320px' }}>
                  {/* Column Header */}
                  <div className={`bg-${stage.color}-50 rounded-xl p-4 mb-4 border-2 border-${stage.color}-200`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <div className={`w-8 h-8 rounded-lg bg-${stage.color}-600 flex items-center justify-center`}>
                          <StageIcon className="w-4 h-4 text-white" strokeWidth={2.5} />
                        </div>
                        <div>
                          <div className="font-bold text-neutral-900" style={{ fontSize: '14px', fontWeight: 700 }}>
                            {stage.label}
                          </div>
                          <div className="text-xs text-neutral-600 font-semibold">
                            {stageLeads.length} leads
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-lg font-bold text-neutral-900" style={{ fontWeight: 800 }}>
                          {Math.round(stageValue / (stageLeads.length || 1))}
                        </div>
                        <div className="text-xs text-neutral-500">Avg Score</div>
                      </div>
                    </div>
                  </div>

                  {/* Cards Container */}
                  <div className="flex-1 overflow-y-auto space-y-3 pr-2">
                    {loading ? (
                      <div className="flex items-center justify-center h-40">
                        <div className="w-6 h-6 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin" />
                      </div>
                    ) : stageLeads.length === 0 ? (
                      <div className="bg-white rounded-xl p-6 border-2 border-dashed border-neutral-200 text-center">
                        <div className="text-sm text-neutral-400 font-medium">No leads</div>
                      </div>
                    ) : (
                      stageLeads.map((lead, idx) => (
                        <motion.div
                          key={lead.lead_id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.05 }}
                          className="bg-white rounded-xl p-4 border border-neutral-200 hover:border-neutral-900 hover:shadow-xl transition-all cursor-pointer group"
                          onClick={() => onViewLead(lead.lead_id)}
                        >
                          {/* Score Badge */}
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1 min-w-0">
                              <div className="font-bold text-neutral-900 truncate mb-1 group-hover:text-emerald-600 transition-colors" style={{ fontSize: '14px', fontWeight: 700 }}>
                                {lead.company_name}
                              </div>
                              <div className="text-xs text-neutral-500 truncate">{lead.sector || 'N/A'}</div>
                            </div>
                            <div className={`w-12 h-12 rounded-lg flex items-center justify-center font-bold flex-shrink-0 ml-2 ${
                              lead.best_score >= 60 ? 'bg-emerald-100 text-emerald-700' :
                              lead.best_score >= 30 ? 'bg-blue-100 text-blue-700' :
                              'bg-neutral-100 text-neutral-600'
                            }`} style={{ fontSize: '16px', fontWeight: 800 }}>
                              {Math.round(lead.best_score)}
                            </div>
                          </div>

                          {/* Product */}
                          <div className="mb-3">
                            <div className="text-xs text-neutral-500 mb-1 font-semibold uppercase tracking-wider">Top Product</div>
                            <div className="text-xs text-neutral-900 font-semibold truncate">{lead.best_service || 'N/A'}</div>
                          </div>

                          {/* Location */}
                          <div className="flex items-center gap-2 text-xs text-neutral-600 mb-3">
                            <Users className="w-3 h-3" />
                            <span>{lead.city || 'Tunisia'}</span>
                          </div>

                          {/* Flags */}
                          {(lead.is_multinational || lead.is_exporter || lead.under_audit) && (
                            <div className="flex gap-1.5 mb-3 flex-wrap">
                              {lead.is_multinational && (
                                <span className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs font-semibold border border-blue-200">
                                  Multi
                                </span>
                              )}
                              {lead.is_exporter && (
                                <span className="px-2 py-0.5 bg-emerald-50 text-emerald-700 rounded text-xs font-semibold border border-emerald-200">
                                  Export
                                </span>
                              )}
                              {lead.under_audit && (
                                <span className="px-2 py-0.5 bg-amber-50 text-amber-700 rounded text-xs font-semibold border border-amber-200">
                                  Audit
                                </span>
                              )}
                            </div>
                          )}

                          {/* Action */}
                          <div className="flex items-center justify-between pt-3 border-t border-neutral-100">
                            <div className="flex items-center gap-1 text-xs text-neutral-500">
                              <Clock className="w-3 h-3" />
                              <span>
                                {lead.created_at ?
                                  new Date(lead.created_at).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) :
                                  'Today'
                                }
                              </span>
                            </div>
                            <motion.button
                              className="text-xs font-bold text-neutral-900 hover:text-emerald-600 flex items-center gap-1"
                              whileHover={{ x: 2 }}
                            >
                              View
                              <ArrowRight className="w-3 h-3" strokeWidth={2.5} />
                            </motion.button>
                          </div>
                        </motion.div>
                      ))
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
