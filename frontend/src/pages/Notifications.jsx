/**
 * Notifications Center
 * All alerts and system notifications
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bell, TrendingUp, Zap, Users, CheckCircle2, X,
  Settings, Filter, Trash2, Check, Eye, ArrowUpRight,
  Globe, Target, AlertCircle, Clock, Building2
} from 'lucide-react';
import { getRankedLeads } from '../services/api';

export default function Notifications({ onViewLead }) {
  const [notifications, setNotifications] = useState([]);
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await getRankedLeads(10000, 0, {});
      setLeads(data);
      generateNotifications(data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const generateNotifications = (leadsData) => {
    const allNotifications = [];
    const now = new Date();

    // Hot leads notifications
    leadsData.filter(l => l.best_score >= 70).forEach(lead => {
      allNotifications.push({
        id: `hot-${lead.lead_id}`,
        type: 'hot_lead',
        icon: TrendingUp,
        color: 'emerald',
        priority: 'high',
        title: 'Hot Lead Alert',
        message: `${lead.company_name} scored ${Math.round(lead.best_score)} - immediate action recommended`,
        leadId: lead.lead_id,
        leadName: lead.company_name,
        timestamp: new Date(now - Math.random() * 86400000 * 2),
        read: Math.random() > 0.5,
      });
    });

    // Signal detected notifications
    leadsData.filter(l => l.is_multinational).forEach(lead => {
      allNotifications.push({
        id: `signal-multi-${lead.lead_id}`,
        type: 'signal',
        icon: Globe,
        color: 'blue',
        priority: 'high',
        title: 'Multinational Signal Detected',
        message: `${lead.company_name} flagged as multinational - high conversion probability`,
        leadId: lead.lead_id,
        leadName: lead.company_name,
        timestamp: new Date(now - Math.random() * 86400000 * 3),
        read: Math.random() > 0.6,
      });
    });

    leadsData.filter(l => l.under_audit).forEach(lead => {
      allNotifications.push({
        id: `signal-audit-${lead.lead_id}`,
        type: 'signal',
        icon: CheckCircle2,
        color: 'amber',
        priority: 'critical',
        title: 'Audit Pressure Detected',
        message: `${lead.company_name} under audit - cannot use unlicensed software`,
        leadId: lead.lead_id,
        leadName: lead.company_name,
        timestamp: new Date(now - Math.random() * 86400000),
        read: false,
      });
    });

    // Status change notifications
    leadsData.filter(l => l.status && l.status !== 'new').slice(0, 5).forEach(lead => {
      allNotifications.push({
        id: `status-${lead.lead_id}`,
        type: 'status_change',
        icon: CheckCircle2,
        color: 'purple',
        priority: 'medium',
        title: 'Status Updated',
        message: `${lead.company_name} moved to ${lead.status}`,
        leadId: lead.lead_id,
        leadName: lead.company_name,
        timestamp: new Date(now - Math.random() * 86400000 * 5),
        read: Math.random() > 0.4,
      });
    });

    // New companies
    leadsData.slice(0, 8).forEach(lead => {
      allNotifications.push({
        id: `new-${lead.lead_id}`,
        type: 'new_lead',
        icon: Building2,
        color: 'indigo',
        priority: 'low',
        title: 'New Company Added',
        message: `${lead.company_name} added to database - ${lead.city || 'Tunisia'}`,
        leadId: lead.lead_id,
        leadName: lead.company_name,
        timestamp: new Date(now - Math.random() * 86400000 * 7),
        read: Math.random() > 0.3,
      });
    });

    // System notifications
    allNotifications.push({
      id: 'sys-1',
      type: 'system',
      icon: Settings,
      color: 'neutral',
      priority: 'low',
      title: 'System Update',
      message: 'Score engine recalculation completed - 121 leads updated',
      timestamp: new Date(now - 3600000),
      read: false,
    });

    allNotifications.push({
      id: 'sys-2',
      type: 'system',
      icon: Zap,
      color: 'neutral',
      priority: 'low',
      title: 'Data Source Active',
      message: 'LinkedIn scraper completed - 45 new signals detected',
      timestamp: new Date(now - 7200000),
      read: true,
    });

    setNotifications(allNotifications.sort((a, b) => b.timestamp - a.timestamp));
  };

  const filters = [
    { id: 'all', label: 'All', count: notifications.length },
    { id: 'unread', label: 'Unread', count: notifications.filter(n => !n.read).length },
    { id: 'hot_lead', label: 'Hot Leads', count: notifications.filter(n => n.type === 'hot_lead').length },
    { id: 'signal', label: 'Signals', count: notifications.filter(n => n.type === 'signal').length },
    { id: 'status_change', label: 'Status', count: notifications.filter(n => n.type === 'status_change').length },
  ];

  const filteredNotifications = notifications.filter(n => {
    if (selectedFilter === 'all') return true;
    if (selectedFilter === 'unread') return !n.read;
    return n.type === selectedFilter;
  });

  const markAsRead = (id) => {
    setNotifications(notifications.map(n =>
      n.id === id ? { ...n, read: true } : n
    ));
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })));
  };

  const deleteNotification = (id) => {
    setNotifications(notifications.filter(n => n.id !== id));
  };

  const deleteAll = () => {
    setNotifications([]);
  };

  const formatTimestamp = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return timestamp.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
  };

  const unreadCount = notifications.filter(n => !n.read).length;
  const criticalCount = notifications.filter(n => n.priority === 'critical' && !n.read).length;
  const highCount = notifications.filter(n => n.priority === 'high' && !n.read).length;

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center relative">
                <Bell className="w-6 h-6 text-blue-600" strokeWidth={2.5} />
                {unreadCount > 0 && (
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-red-600 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-white">{unreadCount}</span>
                  </div>
                )}
              </div>
              <div>
                <h1 className="text-2xl font-bold text-neutral-900 mb-0.5" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  Notifications
                </h1>
                <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                  Stay updated on leads and system activity
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <motion.button
                onClick={markAllAsRead}
                disabled={unreadCount === 0}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-semibold transition-all ${
                  unreadCount > 0
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                }`}
                whileHover={unreadCount > 0 ? { y: -1 } : {}}
                whileTap={unreadCount > 0 ? { scale: 0.98 } : {}}
                style={{ fontSize: '14px' }}
              >
                <Check className="w-4 h-4" strokeWidth={2.5} />
                Mark All Read
              </motion.button>

              <motion.button
                onClick={deleteAll}
                disabled={notifications.length === 0}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl border font-semibold transition-all ${
                  notifications.length > 0
                    ? 'border-neutral-200 text-neutral-700 hover:bg-neutral-100'
                    : 'border-neutral-200 text-neutral-400 cursor-not-allowed'
                }`}
                whileHover={notifications.length > 0 ? { y: -1 } : {}}
                whileTap={notifications.length > 0 ? { scale: 0.98 } : {}}
                style={{ fontSize: '14px' }}
              >
                <Trash2 className="w-4 h-4" strokeWidth={2.5} />
                Clear All
              </motion.button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200">
              <div className="text-3xl font-bold text-blue-900 mb-1" style={{ fontWeight: 800 }}>
                {notifications.length}
              </div>
              <div className="text-xs text-blue-700 font-semibold">Total</div>
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

            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200">
              <div className="text-3xl font-bold text-emerald-900 mb-1" style={{ fontWeight: 800 }}>
                {unreadCount}
              </div>
              <div className="text-xs text-emerald-700 font-semibold">Unread</div>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2">
            {filters.map(filter => (
              <button
                key={filter.id}
                onClick={() => setSelectedFilter(filter.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
                  selectedFilter === filter.id
                    ? 'bg-neutral-900 text-white'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                }`}
              >
                {filter.label}
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
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

      {/* Notifications List */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-5xl mx-auto p-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="w-8 h-8 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin" />
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="bg-white rounded-xl p-12 text-center border border-neutral-200">
              <Bell className="w-16 h-16 text-neutral-300 mx-auto mb-4" strokeWidth={2} />
              <p className="text-neutral-500 font-medium">No notifications</p>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence>
                {filteredNotifications.map((notification, idx) => {
                  const Icon = notification.icon;
                  return (
                    <motion.div
                      key={notification.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: idx * 0.02 }}
                      className={`bg-white rounded-xl p-5 border-2 hover:shadow-lg transition-all group ${
                        notification.read ? 'border-neutral-200' : 'border-blue-300 bg-blue-50/30'
                      } ${
                        notification.priority === 'critical' ? 'bg-red-50/30 border-red-300' :
                        notification.priority === 'high' ? 'bg-amber-50/30 border-amber-300' : ''
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        {/* Icon */}
                        <div className={`w-12 h-12 rounded-xl bg-${notification.color}-100 flex items-center justify-center flex-shrink-0 border-2 border-${notification.color}-200`}>
                          <Icon className={`w-5 h-5 text-${notification.color}-600`} strokeWidth={2.5} />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <div className="flex items-center gap-2 mb-1">
                                {!notification.read && (
                                  <div className="w-2 h-2 rounded-full bg-blue-600" />
                                )}
                                <div className="font-bold text-neutral-900" style={{ fontSize: '15px', fontWeight: 700 }}>
                                  {notification.title}
                                </div>
                                {notification.priority === 'critical' && (
                                  <span className="px-2 py-0.5 bg-red-600 text-white rounded text-xs font-bold uppercase">
                                    Critical
                                  </span>
                                )}
                                {notification.priority === 'high' && (
                                  <span className="px-2 py-0.5 bg-amber-600 text-white rounded text-xs font-bold uppercase">
                                    High
                                  </span>
                                )}
                              </div>
                              <div className="text-sm text-neutral-600 mb-2" style={{ fontWeight: 500 }}>
                                {notification.message}
                              </div>
                              <div className="flex items-center gap-2 text-xs text-neutral-500">
                                <Clock className="w-3.5 h-3.5" strokeWidth={2} />
                                {formatTimestamp(notification.timestamp)}
                              </div>
                            </div>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-2 mt-3">
                            {notification.leadId && (
                              <motion.button
                                onClick={() => onViewLead(notification.leadId)}
                                className="flex items-center gap-1.5 px-3 py-1.5 bg-neutral-900 text-white rounded-lg text-xs font-bold hover:bg-neutral-800"
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                              >
                                View Lead
                                <ArrowUpRight className="w-3.5 h-3.5" strokeWidth={2.5} />
                              </motion.button>
                            )}
                            {!notification.read && (
                              <button
                                onClick={() => markAsRead(notification.id)}
                                className="px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-xs font-bold hover:bg-blue-200"
                              >
                                Mark Read
                              </button>
                            )}
                            <button
                              onClick={() => deleteNotification(notification.id)}
                              className="ml-auto p-1.5 hover:bg-neutral-100 rounded-lg transition-colors"
                            >
                              <X className="w-4 h-4 text-neutral-500" strokeWidth={2} />
                            </button>
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
