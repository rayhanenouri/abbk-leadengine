/**
 * Professional Leads Table
 * Clean, scannable table view like Linear/Notion
 */

import { motion } from 'framer-motion';
import { ChevronRight, Phone, Mail, ExternalLink, TrendingUp, Building2 } from 'lucide-react';

const LeadsTable = ({ leads, onLeadClick }) => {
  const getScoreColor = (score) => {
    if (score >= 70) return 'text-emerald-600 bg-emerald-50';
    if (score >= 50) return 'text-amber-600 bg-amber-50';
    if (score >= 30) return 'text-orange-600 bg-orange-50';
    return 'text-neutral-400 bg-neutral-50';
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
    <div className="bg-white rounded-lg border border-neutral-200 overflow-hidden">
      {/* Table Header */}
      <div className="grid grid-cols-12 gap-4 px-6 py-3 bg-neutral-50 border-b border-neutral-200 text-xs font-semibold text-neutral-600 uppercase tracking-wider">
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
            className="grid grid-cols-12 gap-4 px-6 py-4 hover:bg-neutral-50 transition-colors cursor-pointer group"
            onClick={() => onLeadClick(lead.lead_id)}
          >
            {/* Company */}
            <div className="col-span-3 flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Building2 className="w-5 h-5 text-white" />
              </div>
              <div className="min-w-0">
                <div className="font-semibold text-neutral-900 truncate group-hover:text-primary-600 transition-colors">
                  {lead.company_name}
                </div>
                <div className="text-sm text-neutral-500 truncate">
                  {lead.employee_count ? `${lead.employee_count} employees` : 'Company'}
                </div>
              </div>
            </div>

            {/* Location */}
            <div className="col-span-2 flex flex-col justify-center">
              <div className="text-sm font-medium text-neutral-900">{lead.city || '—'}</div>
              <div className="text-xs text-neutral-500">{lead.country || 'Tunisia'}</div>
            </div>

            {/* Sector */}
            <div className="col-span-2 flex items-center">
              <div className="text-sm text-neutral-700 truncate">{lead.sector || 'General'}</div>
            </div>

            {/* Score */}
            <div className="col-span-1 flex items-center justify-center">
              <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-bold text-sm ${getScoreColor(lead.best_score)}`}>
                <TrendingUp className="w-3.5 h-3.5" />
                {Math.round(lead.best_score)}
              </div>
            </div>

            {/* Best Service */}
            <div className="col-span-2 flex items-center">
              <div className="text-sm text-neutral-700 truncate" title={lead.best_service}>
                {lead.best_service}
              </div>
            </div>

            {/* Status */}
            <div className="col-span-1 flex items-center justify-center">
              <span className={`inline-block px-2.5 py-1 rounded-md text-xs font-semibold border ${getStatusColor(lead.status)}`}>
                {lead.status?.toUpperCase() || 'NEW'}
              </span>
            </div>

            {/* Action */}
            <div className="col-span-1 flex items-center justify-end">
              <motion.div
                className="p-1.5 rounded-lg group-hover:bg-primary-50 transition-colors"
                whileHover={{ x: 3 }}
              >
                <ChevronRight className="w-4 h-4 text-neutral-400 group-hover:text-primary-600" />
              </motion.div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default LeadsTable;
