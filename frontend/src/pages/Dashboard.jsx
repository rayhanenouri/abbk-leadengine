/**
 * ABBK LeadEngine Dashboard - Professional Design
 * Modern Tailwind-based UI with microinteractions and premium feel
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Bell,
  LogOut,
  BarChart3,
  FileDown,
  Phone,
  Eye,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  Inbox,
  TrendingUp,
  Users,
  Target,
  X
} from 'lucide-react';
import { getLeads, getRankedLeads, logout, getUnreadCount, getNotifications, markNotificationRead } from '../services/api';
import LeadDetail from './LeadDetail';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';

export default function Dashboard({ onNavigateToAnalytics }) {
  const [allLeads, setAllLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [appliedFilters, setAppliedFilters] = useState({});
  const [currentPage, setCurrentPage] = useState(1);
  const leadsPerPage = 50;

  useEffect(() => {
    loadLeads();
    loadUnreadCount();
    const interval = setInterval(loadUnreadCount, 30000);
    return () => clearInterval(interval);
  }, [minScore]);

  useEffect(() => {
    setCurrentPage(1);
  }, [minScore]);

  const loadLeads = async () => {
    setLoading(true);
    setError('');
    try {
      // Use getLeads directly - works even without scores
      const data = await getLeads(0, 1000, 'created_at', 'desc');
      setAllLeads(data);
    } catch (err) {
      setError(err.message || 'Failed to load leads');
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const data = await getUnreadCount();
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.error('Failed to load notification count:', err);
    }
  };

  const loadNotifications = async () => {
    try {
      const data = await getNotifications(false, 20);
      setNotifications(data);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  const handleNotificationClick = async (notification) => {
    if (!notification.is_read) {
      await markNotificationRead(notification.id);
      loadUnreadCount();
    }
    if (notification.lead_id) {
      setSelectedLeadId(notification.lead_id);
      setShowNotifications(false);
    }
  };

  const toggleNotifications = async () => {
    if (!showNotifications) {
      await loadNotifications();
    }
    setShowNotifications(!showNotifications);
  };

  const handleFilterChange = (filters) => {
    setAppliedFilters(filters);
  };

  const handleSearchSelect = (leadId) => {
    setSelectedLeadId(leadId);
  };

  const handleExport = async (format) => {
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (minScore > 0) params.append('min_score', minScore);
      if (appliedFilters.sector) params.append('sector', appliedFilters.sector);
      if (appliedFilters.city) params.append('city', appliedFilters.city);
      if (appliedFilters.country) params.append('country', appliedFilters.country);
      if (appliedFilters.status) params.append('status', appliedFilters.status);
      if (appliedFilters.is_multinational) params.append('is_multinational', 'true');
      if (appliedFilters.is_exporter) params.append('is_exporter', 'true');
      if (appliedFilters.under_audit) params.append('under_audit', 'true');
      if (appliedFilters.min_score && appliedFilters.min_score > 0) {
        params.append('min_score', appliedFilters.min_score);
      }

      const url = `http://${window.location.hostname}:8000/api/leads/export/${format}?${params.toString()}`;
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = downloadUrl;
      a.download = `leads_export_${new Date().toISOString().split('T')[0]}.${format === 'csv' ? 'csv' : 'xlsx'}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(downloadUrl);
      document.body.removeChild(a);
    } catch (err) {
      alert('Export failed: ' + err.message);
    }
  };

  useEffect(() => {
    loadLeads();
  }, [appliedFilters]);

  // Pagination
  const totalLeads = allLeads.length;
  const totalPages = Math.ceil(totalLeads / leadsPerPage);
  const startIndex = (currentPage - 1) * leadsPerPage;
  const endIndex = startIndex + leadsPerPage;
  const currentLeads = allLeads.slice(startIndex, endIndex);

  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const getScoreColor = (score) => {
    if (score >= 70) return 'text-success-600';
    if (score >= 50) return 'text-warning-600';
    if (score >= 30) return 'text-error-600';
    return 'text-neutral-400';
  };

  const getScoreBg = (score) => {
    if (score >= 70) return 'bg-success-500/10';
    if (score >= 50) return 'bg-warning-500/10';
    if (score >= 30) return 'bg-error-500/10';
    return 'bg-neutral-500/10';
  };

  const getPriorityBadge = (score) => {
    if (score >= 70) return { text: 'HIGH', color: 'bg-success-500/10 text-success-600 ring-success-500/20' };
    if (score >= 50) return { text: 'MEDIUM', color: 'bg-warning-500/10 text-warning-600 ring-warning-500/20' };
    if (score >= 30) return { text: 'LOW', color: 'bg-error-500/10 text-error-600 ring-error-500/20' };
    return { text: 'RESEARCH', color: 'bg-neutral-500/10 text-neutral-400 ring-neutral-500/20' };
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      new: { text: 'NEW', emoji: '🆕', color: 'bg-accent-500/10 text-accent-600 ring-accent-500/20' },
      contacted: { text: 'CONTACTED', emoji: '📞', color: 'bg-purple-500/10 text-purple-600 ring-purple-500/20' },
      qualified: { text: 'QUALIFIED', emoji: '⭐', color: 'bg-success-500/10 text-success-600 ring-success-500/20' },
      converted: { text: 'CONVERTED', emoji: '✅', color: 'bg-success-600/10 text-success-700 ring-success-600/20' },
      lost: { text: 'LOST', emoji: '❌', color: 'bg-neutral-500/10 text-neutral-500 ring-neutral-500/20' },
    };
    return statusMap[status] || statusMap.new;
  };

  // Show lead detail
  if (selectedLeadId) {
    return (
      <LeadDetail
        leadId={selectedLeadId}
        onBack={() => setSelectedLeadId(null)}
      />
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-neutral-200 shadow-sm backdrop-blur-xl bg-white/95">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-neutral-900">ABBK LeadEngine</h1>
              <p className="text-sm text-neutral-500 mt-0.5">Ranked Leads • Who to Call Today</p>
            </div>

            <div className="flex items-center gap-3">
              {/* Analytics Button */}
              <motion.button
                onClick={onNavigateToAnalytics}
                className="flex items-center gap-2 px-4 py-2.5 bg-purple-600 text-white rounded-xl font-semibold text-sm hover:bg-purple-700 transition-all shadow-lg shadow-purple-600/25 hover:shadow-xl hover:shadow-purple-600/30 hover:-translate-y-0.5 active:translate-y-0"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <BarChart3 className="w-4 h-4" />
                Analytics
              </motion.button>

              {/* Notification Bell */}
              <div className="relative">
                <motion.button
                  onClick={toggleNotifications}
                  className="relative p-2.5 bg-neutral-100 hover:bg-neutral-200 rounded-xl transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Bell className="w-5 h-5 text-neutral-700" />
                  {unreadCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-primary-600 text-white text-xs font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
                      {unreadCount}
                    </span>
                  )}
                </motion.button>

                {/* Notification Panel */}
                <AnimatePresence>
                  {showNotifications && (
                    <motion.div
                      initial={{ opacity: 0, y: 10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: 10, scale: 0.95 }}
                      transition={{ duration: 0.2 }}
                      className="absolute top-14 right-0 w-[400px] max-h-[500px] bg-white border border-neutral-200 rounded-2xl shadow-2xl overflow-hidden"
                    >
                      <div className="flex items-center justify-between px-6 py-4 border-b border-neutral-200 bg-neutral-50">
                        <h3 className="font-bold text-lg text-neutral-900">Notifications</h3>
                        <button
                          onClick={() => setShowNotifications(false)}
                          className="p-1 hover:bg-neutral-200 rounded-lg transition-colors"
                        >
                          <X className="w-5 h-5 text-neutral-500" />
                        </button>
                      </div>
                      <div className="max-h-[440px] overflow-y-auto">
                        {notifications.length === 0 ? (
                          <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
                            <Inbox className="w-12 h-12 text-neutral-300 mb-3" />
                            <p className="text-neutral-500 text-sm">No notifications yet</p>
                          </div>
                        ) : (
                          notifications.map((notif) => (
                            <motion.div
                              key={notif.id}
                              onClick={() => handleNotificationClick(notif)}
                              className={`px-6 py-4 border-b border-neutral-100 cursor-pointer transition-colors ${
                                notif.is_read ? 'bg-white hover:bg-neutral-50' : 'bg-accent-50/50 hover:bg-accent-50'
                              }`}
                              whileHover={{ x: 4 }}
                            >
                              <div className="font-semibold text-sm text-neutral-900 mb-1">{notif.title}</div>
                              <div className="text-sm text-neutral-600 mb-2 line-clamp-2">{notif.message}</div>
                              <div className="text-xs text-neutral-400">
                                {new Date(notif.created_at).toLocaleString()}
                              </div>
                            </motion.div>
                          ))
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* Logout Button */}
              <motion.button
                onClick={logout}
                className="flex items-center gap-2 px-4 py-2.5 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 rounded-xl font-semibold text-sm transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <LogOut className="w-4 h-4" />
                Logout
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      <div className="bg-white border-b border-neutral-200">
        <div className="max-w-[1600px] mx-auto px-6 py-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Total Leads */}
            <div className="bg-gradient-to-br from-neutral-50 to-white p-5 rounded-2xl border border-neutral-200">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-neutral-900 rounded-xl">
                  <Users className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-neutral-900">{totalLeads}</div>
                  <div className="text-xs text-neutral-500 font-medium">Total Leads</div>
                </div>
              </div>
            </div>

            {/* High Priority */}
            <div className="bg-gradient-to-br from-success-50 to-white p-5 rounded-2xl border border-success-200">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-success-600 rounded-xl">
                  <Target className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-success-700">
                    {allLeads.filter(l => l.best_score >= 70).length}
                  </div>
                  <div className="text-xs text-success-600 font-medium">High Priority</div>
                </div>
              </div>
            </div>

            {/* Medium Priority */}
            <div className="bg-gradient-to-br from-warning-50 to-white p-5 rounded-2xl border border-warning-200">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-warning-600 rounded-xl">
                  <TrendingUp className="w-5 h-5 text-white" />
                </div>
                <div>
                  <div className="text-2xl font-bold text-warning-700">
                    {allLeads.filter(l => l.best_score >= 50 && l.best_score < 70).length}
                  </div>
                  <div className="text-xs text-warning-600 font-medium">Medium Priority</div>
                </div>
              </div>
            </div>

            {/* Pagination Info */}
            <div className="bg-gradient-to-br from-accent-50 to-white p-5 rounded-2xl border border-accent-200">
              <div className="text-sm text-accent-600 font-medium mb-1">Page {currentPage} of {totalPages || 1}</div>
              <div className="text-xs text-accent-500">Viewing {currentLeads.length} leads</div>
            </div>

            {/* Min Score Filter */}
            <div className="bg-gradient-to-br from-purple-50 to-white p-5 rounded-2xl border border-purple-200">
              <label className="block text-xs text-purple-600 font-medium mb-2">Min Score</label>
              <select
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                className="w-full px-3 py-2 bg-white border border-purple-200 rounded-xl text-sm font-medium text-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 cursor-pointer"
              >
                <option value={0}>All Leads</option>
                <option value={30}>30+</option>
                <option value={50}>50+</option>
                <option value={70}>70+ (High)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white border-b border-neutral-200">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex flex-col lg:flex-row gap-4 mb-4">
            <div className="flex-1">
              <SearchBar onSelectLead={handleSearchSelect} />
            </div>
            <div className="flex gap-3">
              <motion.button
                onClick={() => handleExport('csv')}
                className="flex items-center gap-2 px-4 py-2.5 bg-success-600 text-white rounded-xl font-semibold text-sm hover:bg-success-700 transition-all shadow-lg shadow-success-600/25"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <FileDown className="w-4 h-4" />
                CSV
              </motion.button>
              <motion.button
                onClick={() => handleExport('excel')}
                className="flex items-center gap-2 px-4 py-2.5 bg-success-600 text-white rounded-xl font-semibold text-sm hover:bg-success-700 transition-all shadow-lg shadow-success-600/25"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <FileDown className="w-4 h-4" />
                Excel
              </motion.button>
            </div>
          </div>
          <FilterPanel onFilterChange={handleFilterChange} />
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-6 py-8">
        {/* Loading State */}
        {loading && (
          <div className="flex flex-col items-center justify-center py-24">
            <Loader2 className="w-12 h-12 text-primary-600 animate-spin mb-4" />
            <p className="text-neutral-600 font-medium">Loading leads...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-error-50 border border-error-200 rounded-2xl p-6 mb-6"
          >
            <div className="flex items-start gap-3">
              <AlertCircle className="w-6 h-6 text-error-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-bold text-error-900 mb-1">Error Loading Leads</h3>
                <p className="text-error-700">{error}</p>
              </div>
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {!loading && !error && totalLeads === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center py-24 bg-white rounded-3xl border border-neutral-200"
          >
            <Inbox className="w-16 h-16 text-neutral-300 mb-4" />
            <h3 className="text-xl font-bold text-neutral-900 mb-2">No Leads Found</h3>
            <p className="text-neutral-500">Try lowering the minimum score filter</p>
          </motion.div>
        )}

        {/* Leads Grid */}
        {!loading && !error && totalLeads > 0 && (
          <>
            <motion.div
              className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6"
              initial="hidden"
              animate="visible"
              variants={{
                visible: {
                  transition: {
                    staggerChildren: 0.05
                  }
                }
              }}
            >
              {currentLeads.map((lead) => {
                const priorityBadge = getPriorityBadge(lead.best_score);
                const statusBadge = getStatusBadge(lead.status);

                return (
                  <motion.div
                    key={lead.lead_id}
                    variants={{
                      hidden: { opacity: 0, y: 20 },
                      visible: { opacity: 1, y: 0 }
                    }}
                    className="bg-white rounded-2xl border border-neutral-200 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer group"
                  >
                    {/* Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-lg text-neutral-900 mb-1 truncate group-hover:text-primary-600 transition-colors">
                          {lead.company_name}
                        </h3>
                        <p className="text-sm text-neutral-500 truncate">
                          {lead.city} {lead.city && lead.sector && '•'} {lead.sector}
                        </p>
                      </div>
                    </div>

                    {/* Badges */}
                    <div className="flex gap-2 mb-4">
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ring-1 ${statusBadge.color}`}>
                        {statusBadge.emoji} {statusBadge.text}
                      </span>
                      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ring-1 ${priorityBadge.color}`}>
                        {priorityBadge.text}
                      </span>
                    </div>

                    {/* Score */}
                    <div className="flex items-center gap-4 mb-4 pb-4 border-b border-neutral-100">
                      <div className={`flex items-center justify-center w-20 h-20 rounded-2xl ${getScoreBg(lead.best_score)}`}>
                        <div className="text-center">
                          <div className={`text-3xl font-bold ${getScoreColor(lead.best_score)}`}>
                            {Math.round(lead.best_score)}
                          </div>
                          <div className="text-xs text-neutral-400 font-medium">Score</div>
                        </div>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-xs text-neutral-500 mb-1">Best Service</div>
                        <div className="font-semibold text-sm text-neutral-900 truncate">
                          {lead.best_service}
                        </div>
                      </div>
                    </div>

                    {/* Reasoning */}
                    <p className="text-sm text-neutral-600 mb-4 line-clamp-2 leading-relaxed">
                      {lead.best_reasoning}
                    </p>

                    {/* Actions */}
                    <div className="flex gap-3">
                      <motion.button
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-primary-600 text-white rounded-xl font-semibold text-sm hover:bg-primary-700 transition-colors"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Phone className="w-4 h-4" />
                        Call Now
                      </motion.button>
                      <motion.button
                        onClick={() => setSelectedLeadId(lead.lead_id)}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-2.5 bg-neutral-100 text-neutral-700 rounded-xl font-semibold text-sm hover:bg-neutral-200 transition-colors"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                      >
                        <Eye className="w-4 h-4" />
                        Details
                      </motion.button>
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-8 p-6 bg-white rounded-2xl border border-neutral-200">
                <motion.button
                  onClick={() => goToPage(currentPage - 1)}
                  disabled={currentPage === 1}
                  className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all ${
                    currentPage === 1
                      ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                      : 'bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/25'
                  }`}
                  whileHover={currentPage !== 1 ? { scale: 1.02 } : {}}
                  whileTap={currentPage !== 1 ? { scale: 0.98 } : {}}
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </motion.button>

                <div className="flex flex-col items-center gap-2">
                  <span className="text-sm text-neutral-600 font-medium">
                    Showing {startIndex + 1}-{Math.min(endIndex, totalLeads)} of {totalLeads} leads
                  </span>
                  <div className="flex gap-2">
                    {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 7) {
                        pageNum = i + 1;
                      } else if (currentPage <= 4) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 3) {
                        pageNum = totalPages - 6 + i;
                      } else {
                        pageNum = currentPage - 3 + i;
                      }

                      if (pageNum < 1 || pageNum > totalPages) return null;

                      return (
                        <motion.button
                          key={pageNum}
                          onClick={() => goToPage(pageNum)}
                          className={`min-w-[40px] px-3 py-2 rounded-xl font-semibold text-sm transition-all ${
                            currentPage === pageNum
                              ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/25'
                              : 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200'
                          }`}
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          {pageNum}
                        </motion.button>
                      );
                    })}
                  </div>
                </div>

                <motion.button
                  onClick={() => goToPage(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all ${
                    currentPage === totalPages
                      ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                      : 'bg-primary-600 text-white hover:bg-primary-700 shadow-lg shadow-primary-600/25'
                  }`}
                  whileHover={currentPage !== totalPages ? { scale: 1.02 } : {}}
                  whileTap={currentPage !== totalPages ? { scale: 0.98 } : {}}
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </motion.button>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
