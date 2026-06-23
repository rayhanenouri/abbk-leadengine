/**
 * Professional Leads Table
 * Clean, scannable table view like Linear/Notion
 */

import { motion } from 'framer-motion';
import { ChevronRight, Phone, Mail, ExternalLink, TrendingUp, Building2 } from 'lucide-react';

const LeadsTable = ({ leads, onLeadClick }) => {
  const getScoreColor = (score) => {
    if (score >= 60) return 'text-emerald-600 bg-emerald-50';
    if (score >= 30) return 'text-blue-600 bg-blue-50';
    return 'text-neutral-500 bg-neutral-50';
  };

  const getPriorityText = (score) => {
    if (score >= 70) return 'High';
    if (score >= 50) return 'Medium';
    if (score >= 30) return 'Low';
    return 'Research';
  };

  const getStatusColor = (status) => {
    const colors = {
      new: 'bg-blue-50 text-blue-700 border-blue-200',
      contacted: 'bg-purple-50 text-purple-700 border-purple-200',
      qualified: 'bg-emerald-50 text-emerald-700 border-emerald-200',
      converted: 'bg-green-50 text-green-700 border-green-200',
      lost: 'bg-neutral-50 text-neutral-500 border-neutral-200',
    };
    return colors[status] || colors.new;
  };

  return (
    <div className="bg-white rounded-xl border border-neutral-200 overflow-hidden shadow-sm">
      {/* Table Header */}
      <div className="grid grid-cols-12 gap-4 px-8 py-4 bg-neutral-50 border-b border-neutral-200 uppercase tracking-wider" style={{
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.1em',
        color: '#737373',
      }}>
        <div className="col-span-3">Company</div>
        <div className="col-span-2">Location</div>
        <div className="col-span-2">Sector</div>
        <div className="col-span-1 text-center">Score</div>
        <div className="col-span-2">Best Service</div>
        <div className="col-span-1 text-center">Status</div>
        <div className="col-span-1"></div>
      </div>

      {/* Table Body */}
      <div className="divide-y divide-neutral-200">
        {leads.map((lead, index) => (
          <motion.div
            key={lead.lead_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.02 }}
            whileHover={{ backgroundColor: 'rgba(250, 250, 250, 1)' }}
            className="grid grid-cols-12 gap-4 px-8 py-5 border-b border-neutral-100 hover:border-neutral-200 cursor-pointer group transition-all"
            onClick={() => onLeadClick(lead.lead_id)}
          >
            {/* Company */}
            <div className="col-span-3 flex items-center gap-3">
              <div className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0" style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(220, 38, 38, 0.1))',
                border: '1px solid rgba(0, 0, 0, 0.06)',
              }}>
                <Building2 className="w-5 h-5 text-neutral-700" strokeWidth={2} />
              </div>
              <div className="min-w-0">
                <div className="font-semibold text-neutral-900 truncate group-hover:text-neutral-900 transition-colors" style={{
                  fontSize: '14px',
                  fontWeight: 600,
                  letterSpacing: '-0.01em',
                }}>
                  {lead.company_name}
                </div>
                <div className="text-sm text-neutral-500 truncate" style={{
                  fontSize: '13px',
                  fontWeight: 500,
                }}>
                  {lead.employee_count ? `${lead.employee_count} employees` : 'Company'}
                </div>
              </div>
            </div>

            {/* Location */}
            <div className="col-span-2 flex flex-col justify-center">
              <div className="text-sm font-medium text-neutral-900" style={{
                fontSize: '14px',
                fontWeight: 600,
              }}>
                {lead.city || '—'}
              </div>
              <div className="text-xs text-neutral-500" style={{
                fontSize: '12px',
                fontWeight: 500,
              }}>
                {lead.country || 'Tunisia'}
              </div>
            </div>

            {/* Sector */}
            <div className="col-span-2 flex items-center">
              <div className="text-sm text-neutral-700 truncate" style={{
                fontSize: '14px',
                fontWeight: 500,
              }}>
                {lead.sector || 'General'}
              </div>
            </div>

            {/* Score */}
            <div className="col-span-1 flex items-center justify-center">
              <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold ${getScoreColor(lead.best_score)}`} style={{
                fontSize: '14px',
                fontWeight: 700,
                letterSpacing: '-0.01em',
              }}>
                <TrendingUp className="w-3.5 h-3.5" strokeWidth={2.5} />
                {Math.round(lead.best_score)}
              </div>
            </div>

            {/* Best Service */}
            <div className="col-span-2 flex items-center">
              <div className="text-sm text-neutral-700 truncate" title={lead.best_service} style={{
                fontSize: '13px',
                fontWeight: 500,
              }}>
                {lead.best_service}
              </div>
            </div>

            {/* Status */}
            <div className="col-span-1 flex items-center justify-center">
              <span className={`inline-block px-2.5 py-1 rounded-lg border ${getStatusColor(lead.status)}`} style={{
                fontSize: '11px',
                fontWeight: 600,
                letterSpacing: '0.05em',
              }}>
                {lead.status?.toUpperCase() || 'NEW'}
              </span>
            </div>

            {/* Action */}
            <div className="col-span-1 flex items-center justify-end">
              <motion.div
                className="p-2 rounded-lg group-hover:bg-neutral-100 transition-colors"
                whileHover={{ x: 3 }}
              >
                <ChevronRight className="w-4 h-4 text-neutral-400 group-hover:text-neutral-900" strokeWidth={2.5} />
              </motion.div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default LeadsTable;
