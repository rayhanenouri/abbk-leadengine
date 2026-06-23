/**
 * Modern B2B Dashboard
 * Clean, professional, data-focused design
 */

import { useState, useEffect } from 'react';
import { Users, Target, TrendingUp, Activity } from 'lucide-react';
import Sidebar from '../components/layout/Sidebar';
import TopBar from '../components/layout/TopBar';
import StatsOverview from '../components/stats/StatsOverview';
import LeadsTable from '../components/leads/LeadsTable';
import { getRankedLeads, logout, getUnreadCount } from '../services/api';
import LeadDetail from './LeadDetail';

const DashboardV2 = ({ onNavigateToAnalytics }) => {
  const [currentView, setCurrentView] = useState('dashboard');
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const leadsPerPage = 20;

  useEffect(() => {
    loadLeads();
    loadUnreadCount();
  }, []);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const data = await getRankedLeads(1000, 0, {});
      setLeads(data);
    } catch (err) {
      console.error('Failed to load leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const data = await getUnreadCount();
      setUnreadCount(data.unread_count);
    } catch (err) {
      console.error('Failed to load notifications:', err);
    }
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  const handleExport = async (format) => {
    try {
      const token = localStorage.getItem('token');
      const url = `http://${window.location.hostname}:8000/api/leads/export/${format}`;
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

  const handleViewChange = (view) => {
    if (view === 'analytics') {
      onNavigateToAnalytics();
    } else {
      setCurrentView(view);
    }
  };

  // Filter and paginate
  const filteredLeads = leads.filter(lead =>
    lead.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lead.sector?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    lead.city?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const totalLeads = filteredLeads.length;
  const totalPages = Math.ceil(totalLeads / leadsPerPage);
  const startIndex = (currentPage - 1) * leadsPerPage;
  const currentLeads = filteredLeads.slice(startIndex, startIndex + leadsPerPage);

  // Calculate stats
  const highPriorityCount = leads.filter(l => l.best_score >= 70).length;
  const mediumPriorityCount = leads.filter(l => l.best_score >= 50 && l.best_score < 70).length;
  const newThisWeek = leads.filter(l => {
    const createdDate = new Date(l.created_at);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return createdDate > weekAgo;
  }).length;

  const stats = [
    {
      title: 'Total Leads',
      value: totalLeads,
      change: `+${newThisWeek} this week`,
      changeType: 'up',
      icon: Users,
      color: 'primary'
    },
    {
      title: 'High Priority',
      value: highPriorityCount,
      change: 'Score ≥ 70',
      changeType: 'neutral',
      icon: Target,
      color: 'emerald'
    },
    {
      title: 'Medium Priority',
      value: mediumPriorityCount,
      change: 'Score 50-69',
      changeType: 'neutral',
      icon: TrendingUp,
      color: 'amber'
    },
    {
      title: 'Active Now',
      value: currentLeads.length,
      change: `of ${totalLeads} total`,
      changeType: 'neutral',
      icon: Activity,
      color: 'purple'
    }
  ];

  // Show lead detail if selected
  if (selectedLeadId) {
    return (
      <div className="flex h-screen bg-neutral-50">
        <Sidebar
          currentView={currentView}
          onViewChange={handleViewChange}
          onLogout={logout}
          unreadCount={unreadCount}
        />
        <div className="flex-1 overflow-auto">
          <LeadDetail
            leadId={selectedLeadId}
            onBack={() => setSelectedLeadId(null)}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-neutral-50">
      {/* Sidebar */}
      <Sidebar
        currentView={currentView}
        onViewChange={handleViewChange}
        onLogout={logout}
        unreadCount={unreadCount}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <TopBar
          title="Dashboard"
          subtitle={`${totalLeads} leads across all priorities`}
          onSearch={handleSearch}
          showExport={true}
          onExport={handleExport}
          unreadCount={unreadCount}
        />

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-6 space-y-6">
          {/* Stats Overview */}
          <StatsOverview stats={stats} />

          {/* Leads Table */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-neutral-900">All Leads</h2>
                <p className="text-sm text-neutral-500">
                  Showing {startIndex + 1}-{Math.min(startIndex + leadsPerPage, totalLeads)} of {totalLeads}
                </p>
              </div>

              {/* Quick Filters */}
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors">
                  All
                </button>
                <button className="px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors">
                  High Priority
                </button>
                <button className="px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors">
                  New
                </button>
                <button className="px-3 py-1.5 text-sm font-medium text-neutral-700 hover:bg-neutral-100 rounded-lg transition-colors">
                  Contacted
                </button>
              </div>
            </div>

            {loading ? (
              <div className="bg-white rounded-lg border border-neutral-200 p-12 text-center">
                <div className="inline-block w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mb-4"></div>
                <p className="text-neutral-500">Loading leads...</p>
              </div>
            ) : (
              <>
                <LeadsTable
                  leads={currentLeads}
                  onLeadClick={setSelectedLeadId}
                />

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between px-6 py-4 bg-white rounded-lg border border-neutral-200">
                    <button
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Previous
                    </button>

                    <div className="flex items-center gap-2">
                      {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => i + 1).map(page => (
                        <button
                          key={page}
                          onClick={() => setCurrentPage(page)}
                          className={`w-8 h-8 text-sm font-medium rounded-lg transition-colors ${
                            currentPage === page
                              ? 'bg-primary-600 text-white'
                              : 'text-neutral-700 hover:bg-neutral-100'
                          }`}
                        >
                          {page}
                        </button>
                      ))}
                    </div>

                    <button
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="px-4 py-2 text-sm font-medium text-neutral-700 hover:bg-neutral-50 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardV2;
