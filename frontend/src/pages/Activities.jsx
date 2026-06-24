/**
 * Activities Timeline
 * Track all interactions and actions with leads
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Phone, Mail, Calendar, Edit3, CheckCircle2, Clock,
  User, Building2, TrendingUp, MessageSquare, FileText,
  Filter, Search, Plus, MoreVertical, Eye
} from 'lucide-react';
import { getRankedLeads } from '../services/api';

export default function Activities({ onViewLead }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [selectedDate, setSelectedDate] = useState('today');

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

  // Generate mock activities from leads data
  const generateActivities = () => {
    const activities = [];
    const now = new Date();

    leads.forEach((lead) => {
      // Status change activity
      if (lead.status && lead.status !== 'new') {
        activities.push({
          id: `status-${lead.lead_id}`,
          type: 'status_change',
          icon: Edit3,
          color: 'blue',
          lead: lead.company_name,
          leadId: lead.lead_id,
          title: 'Status Updated',
          description: `Changed to ${lead.status}`,
          timestamp: lead.updated_at || lead.created_at,
          user: 'Admin',
        });
      }

      // Lead created
      activities.push({
        id: `created-${lead.lead_id}`,
        type: 'lead_created',
        icon: Building2,
        color: 'emerald',
        lead: lead.company_name,
        leadId: lead.lead_id,
        title: 'Lead Added',
        description: `New lead from ${lead.city || 'Tunisia'}`,
        timestamp: lead.created_at,
        user: 'System',
      });

      // Scored activity
      if (lead.best_score > 0) {
        activities.push({
          id: `scored-${lead.lead_id}`,
          type: 'scored',
          icon: TrendingUp,
          color: 'purple',
          lead: lead.company_name,
          leadId: lead.lead_id,
          title: 'AI Scoring Complete',
          description: `Score: ${Math.round(lead.best_score)} - ${lead.best_service}`,
          timestamp: lead.created_at,
          user: 'AI Engine',
        });
      }
    });

    return activities.sort((a, b) =>
      new Date(b.timestamp) - new Date(a.timestamp)
    );
  };

  const activities = generateActivities();

  const todayActivities = activities.filter(a => {
    const actDate = new Date(a.timestamp);
    const today = new Date();
    return actDate.toDateString() === today.toDateString();
  });

  const weekActivities = activities.filter(a => {
    const actDate = new Date(a.timestamp);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return actDate >= weekAgo;
  });

  const stats = [
    { label: 'Today', value: todayActivities.length, icon: Clock, color: 'blue' },
    { label: 'This Week', value: weekActivities.length, icon: Calendar, color: 'purple' },
    { label: 'Total', value: activities.length, icon: FileText, color: 'emerald' },
    { label: 'Active Leads', value: leads.filter(l => l.status === 'contacted' || l.status === 'qualified').length, icon: TrendingUp, color: 'amber' },
  ];

  const filters = [
    { id: 'all', label: 'All Activities' },
    { id: 'calls', label: 'Calls' },
    { id: 'emails', label: 'Emails' },
    { id: 'meetings', label: 'Meetings' },
    { id: 'status', label: 'Status Changes' },
    { id: 'notes', label: 'Notes' },
  ];

  const dateFilters = [
    { id: 'today', label: 'Today' },
    { id: 'week', label: 'This Week' },
    { id: 'month', label: 'This Month' },
    { id: 'all', label: 'All Time' },
  ];

  const getFilteredActivities = () => {
    let filtered = activities;

    if (selectedDate === 'today') {
      filtered = todayActivities;
    } else if (selectedDate === 'week') {
      filtered = weekActivities;
    }

    if (selectedFilter === 'status') {
      filtered = filtered.filter(a => a.type === 'status_change');
    }

    return filtered.slice(0, 100);
  };

  const filteredActivities = getFilteredActivities();

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
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 mb-1" style={{
                fontWeight: 800,
                letterSpacing: '-0.04em',
              }}>
                Activities
              </h1>
              <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                Track all interactions and changes across your pipeline
              </p>
            </div>

            <div className="flex items-center gap-3">
              <motion.button
                className="flex items-center gap-2 px-4 py-2.5 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 transition-colors"
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontSize: '14px', fontWeight: 600 }}
              >
                <Plus className="w-4 h-4" strokeWidth={2.5} />
                Log Activity
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
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-${stat.color}-100 flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 text-${stat.color}-600`} strokeWidth={2.5} />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                        {stat.value}
                      </div>
                      <div className="text-xs text-neutral-600 font-semibold">{stat.label}</div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Filters */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              {dateFilters.map(filter => (
                <button
                  key={filter.id}
                  onClick={() => setSelectedDate(filter.id)}
                  className={`px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    selectedDate === filter.id
                      ? 'bg-neutral-900 text-white'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>

            <div className="h-6 w-px bg-neutral-200" />

            <div className="flex items-center gap-2">
              {filters.map(filter => (
                <button
                  key={filter.id}
                  onClick={() => setSelectedFilter(filter.id)}
                  className={`px-3 py-2 rounded-lg text-xs font-semibold transition-all ${
                    selectedFilter === filter.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                  }`}
                >
                  {filter.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Activities List */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-5xl mx-auto p-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="w-8 h-8 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : filteredActivities.length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center border border-neutral-200">
              <Clock className="w-16 h-16 text-neutral-300 mx-auto mb-4" strokeWidth={2} />
              <p className="text-neutral-500 font-medium">No activities found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredActivities.map((activity, idx) => {
                const Icon = activity.icon;
                return (
                  <motion.div
                    key={activity.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.02 }}
                    className="bg-white rounded-xl p-5 border border-neutral-200 hover:border-neutral-900 hover:shadow-lg transition-all group cursor-pointer"
                    onClick={() => activity.leadId && onViewLead(activity.leadId)}
                  >
                    <div className="flex items-start gap-4">
                      {/* Icon */}
                      <div className={`w-12 h-12 rounded-xl bg-${activity.color}-100 flex items-center justify-center flex-shrink-0`}>
                        <Icon className={`w-5 h-5 text-${activity.color}-600`} strokeWidth={2.5} />
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between mb-1">
                          <div>
                            <div className="font-bold text-neutral-900 mb-0.5 group-hover:text-emerald-600 transition-colors" style={{ fontSize: '15px', fontWeight: 700 }}>
                              {activity.title}
                            </div>
                            <div className="text-sm text-neutral-600" style={{ fontWeight: 500 }}>
                              {activity.description}
                            </div>
                          </div>
                          <div className="text-xs text-neutral-500 font-medium flex-shrink-0 ml-4">
                            {formatTimestamp(activity.timestamp)}
                          </div>
                        </div>

                        <div className="flex items-center gap-4 mt-3">
                          <div className="flex items-center gap-2">
                            <Building2 className="w-3.5 h-3.5 text-neutral-400" strokeWidth={2} />
                            <span className="text-xs font-semibold text-neutral-700">{activity.lead}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <User className="w-3.5 h-3.5 text-neutral-400" strokeWidth={2} />
                            <span className="text-xs text-neutral-500">{activity.user}</span>
                          </div>
                          {activity.leadId && (
                            <motion.button
                              className="ml-auto flex items-center gap-1 text-xs font-bold text-neutral-700 hover:text-emerald-600"
                              whileHover={{ x: 2 }}
                            >
                              <Eye className="w-3.5 h-3.5" strokeWidth={2.5} />
                              View Lead
                            </motion.button>
                          )}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
