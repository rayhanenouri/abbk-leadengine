import { useState, useEffect } from 'react';
import { getRankedLeads, logout, getUnreadCount, getNotifications, markNotificationRead } from '../services/api';
import LeadDetail from './LeadDetail';
import SearchBar from '../components/SearchBar';
import FilterPanel from '../components/FilterPanel';

export default function Dashboard({ onNavigateToAnalytics }) {
  const [allLeads, setAllLeads] = useState([]); // All leads from API
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [selectedLeadId, setSelectedLeadId] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [appliedFilters, setAppliedFilters] = useState({});

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const leadsPerPage = 50;

  useEffect(() => {
    loadLeads();
    loadUnreadCount();
    // Refresh notifications every 30 seconds
    const interval = setInterval(loadUnreadCount, 30000);
    return () => clearInterval(interval);
  }, [minScore]);

  // Reset to page 1 when filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [minScore]);

  const loadLeads = async () => {
    setLoading(true);
    setError('');
    try {
      // Use the ranked leads endpoint which now supports all filters
      let effectiveMinScore = minScore;

      // Apply filter min_score if higher than global minScore
      if (appliedFilters.min_score && appliedFilters.min_score > effectiveMinScore) {
        effectiveMinScore = appliedFilters.min_score;
      }

      const data = await getRankedLeads(10000, effectiveMinScore, appliedFilters);
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
    // Mark as read
    if (!notification.is_read) {
      await markNotificationRead(notification.id);
      loadUnreadCount();
    }
    // Navigate to lead if available
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

      // Apply current filters
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

      // Download file
      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
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

  // Reload when filters change
  useEffect(() => {
    loadLeads();
  }, [appliedFilters]);

  // Pagination calculations
  const totalLeads = allLeads.length;
  const totalPages = Math.ceil(totalLeads / leadsPerPage);
  const startIndex = (currentPage - 1) * leadsPerPage;
  const endIndex = startIndex + leadsPerPage;
  const currentLeads = allLeads.slice(startIndex, endIndex);

  // Pagination handlers
  const goToPage = (page) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const nextPage = () => goToPage(currentPage + 1);
  const prevPage = () => goToPage(currentPage - 1);

  const getScoreColor = (score) => {
    if (score >= 70) return '#10b981'; // green
    if (score >= 50) return '#f59e0b'; // orange
    if (score >= 30) return '#ef4444'; // red
    return '#6b7280'; // gray
  };

  const getPriorityBadge = (score) => {
    if (score >= 70) return { text: 'HIGH', color: '#10b981' };
    if (score >= 50) return { text: 'MEDIUM', color: '#f59e0b' };
    if (score >= 30) return { text: 'LOW', color: '#ef4444' };
    return { text: 'RESEARCH', color: '#6b7280' };
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      new: { text: 'NEW', emoji: '🆕', color: '#3b82f6' },
      contacted: { text: 'CONTACTED', emoji: '📞', color: '#8b5cf6' },
      qualified: { text: 'QUALIFIED', emoji: '⭐', color: '#10b981' },
      converted: { text: 'CONVERTED', emoji: '✅', color: '#059669' },
      lost: { text: 'LOST', emoji: '❌', color: '#6b7280' },
    };
    return statusMap[status] || statusMap.new;
  };

  // Show lead detail page if a lead is selected
  if (selectedLeadId) {
    return (
      <LeadDetail
        leadId={selectedLeadId}
        onBack={() => setSelectedLeadId(null)}
      />
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>ABBK LeadEngine</h1>
          <p style={styles.subtitle}>Ranked Leads - Who to Call Today</p>
        </div>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          {/* Analytics Button */}
          <button onClick={onNavigateToAnalytics} style={styles.analyticsButton}>
            📊 Analytics
          </button>
          {/* Notification Bell */}
          <div style={{ position: 'relative' }}>
            <button onClick={toggleNotifications} style={styles.notificationButton}>
              🔔
              {unreadCount > 0 && (
                <span style={styles.notificationBadge}>{unreadCount}</span>
              )}
            </button>
            {showNotifications && (
              <div style={styles.notificationPanel}>
                <div style={styles.notificationHeader}>
                  <h3 style={styles.notificationTitle}>Notifications</h3>
                  <button
                    onClick={() => setShowNotifications(false)}
                    style={styles.closeButton}
                  >
                    ✕
                  </button>
                </div>
                <div style={styles.notificationList}>
                  {notifications.length === 0 ? (
                    <div style={styles.emptyNotifications}>No notifications</div>
                  ) : (
                    notifications.map((notif) => (
                      <div
                        key={notif.id}
                        onClick={() => handleNotificationClick(notif)}
                        style={{
                          ...styles.notificationItem,
                          backgroundColor: notif.is_read ? '#fff' : '#eff6ff',
                        }}
                      >
                        <div style={styles.notificationItemTitle}>{notif.title}</div>
                        <div style={styles.notificationItemMessage}>{notif.message}</div>
                        <div style={styles.notificationItemTime}>
                          {new Date(notif.created_at).toLocaleString()}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
          <button onClick={logout} style={styles.logoutButton}>
            Logout
          </button>
        </div>
      </header>

      {/* Search and Filters */}
      <div style={styles.searchSection}>
        <div style={styles.searchRow}>
          <SearchBar onSelectLead={handleSearchSelect} />
          <div style={styles.exportButtons}>
            <button onClick={() => handleExport('csv')} style={styles.exportButton}>
              📊 Export CSV
            </button>
            <button onClick={() => handleExport('excel')} style={styles.exportButton}>
              📈 Export Excel
            </button>
          </div>
        </div>
        <FilterPanel onFilterChange={handleFilterChange} />
      </div>

      {/* Stats Bar */}
      <div style={styles.statsBar}>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>{totalLeads}</div>
          <div style={styles.statLabel}>Total Leads</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>
            {allLeads.filter(l => l.best_score >= 70).length}
          </div>
          <div style={styles.statLabel}>High Priority</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>
            {allLeads.filter(l => l.best_score >= 50 && l.best_score < 70).length}
          </div>
          <div style={styles.statLabel}>Medium Priority</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>
            Page {currentPage} of {totalPages || 1}
          </div>
          <div style={styles.statLabel}>Viewing {currentLeads.length} leads</div>
        </div>
        <div style={styles.filterCard}>
          <label style={styles.filterLabel}>Min Score:</label>
          <select
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            style={styles.filterSelect}
          >
            <option value={0}>All Leads</option>
            <option value={30}>30+</option>
            <option value={50}>50+</option>
            <option value={70}>70+ (High Priority)</option>
          </select>
        </div>
      </div>

      {/* Main Content */}
      <main style={styles.main}>
        {loading && (
          <div style={styles.loading}>Loading leads...</div>
        )}

        {error && (
          <div style={styles.error}>{error}</div>
        )}

        {!loading && !error && totalLeads === 0 && (
          <div style={styles.empty}>
            No leads found. Try lowering the minimum score filter.
          </div>
        )}

        {!loading && !error && totalLeads > 0 && (
          <>
            <div style={styles.leadsGrid}>
              {currentLeads.map((lead) => {
              const badge = getPriorityBadge(lead.best_score);
              const statusBadge = getStatusBadge(lead.status);
              return (
                <div key={lead.lead_id} style={styles.leadCard}>
                  {/* Header */}
                  <div style={styles.leadHeader}>
                    <div>
                      <h3 style={styles.leadName}>{lead.company_name}</h3>
                      <p style={styles.leadLocation}>
                        {lead.city} {lead.city && lead.sector && '•'} {lead.sector}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <div style={{
                        ...styles.statusBadge,
                        backgroundColor: `${statusBadge.color}20`,
                        color: statusBadge.color,
                      }}>
                        {statusBadge.emoji} {statusBadge.text}
                      </div>
                      <div style={{
                        ...styles.priorityBadge,
                        backgroundColor: `${badge.color}20`,
                        color: badge.color,
                      }}>
                        {badge.text}
                      </div>
                    </div>
                  </div>

                  {/* Score */}
                  <div style={styles.scoreSection}>
                    <div style={styles.scoreCircle}>
                      <div
                        style={{
                          ...styles.scoreNumber,
                          color: getScoreColor(lead.best_score),
                        }}
                      >
                        {Math.round(lead.best_score)}
                      </div>
                      <div style={styles.scoreLabel}>Score</div>
                    </div>
                    <div style={styles.scoreDetails}>
                      <div style={styles.scoreDetailItem}>
                        <span style={styles.scoreDetailLabel}>Best Service:</span>
                        <span style={styles.scoreDetailValue}>
                          {lead.best_service}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Reasoning */}
                  <div style={styles.reasoning}>
                    <p style={styles.reasoningText}>{lead.best_reasoning}</p>
                  </div>

                  {/* Actions */}
                  <div style={styles.actions}>
                    <button style={styles.actionButton}>
                      📞 Call Now
                    </button>
                    <button
                      style={styles.actionButtonSecondary}
                      onClick={() => setSelectedLeadId(lead.lead_id)}
                    >
                      View Details
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div style={styles.pagination}>
              <button
                onClick={prevPage}
                disabled={currentPage === 1}
                style={{
                  ...styles.paginationButton,
                  ...(currentPage === 1 ? styles.paginationButtonDisabled : {}),
                }}
              >
                ← Previous
              </button>

              <div style={styles.paginationInfo}>
                <span style={styles.paginationText}>
                  Showing {startIndex + 1}-{Math.min(endIndex, totalLeads)} of {totalLeads} leads
                </span>
                <div style={styles.pageNumbers}>
                  {/* Show page numbers with ellipsis for large page counts */}
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
                      <button
                        key={pageNum}
                        onClick={() => goToPage(pageNum)}
                        style={{
                          ...styles.pageButton,
                          ...(currentPage === pageNum ? styles.pageButtonActive : {}),
                        }}
                      >
                        {pageNum}
                      </button>
                    );
                  })}
                </div>
              </div>

              <button
                onClick={nextPage}
                disabled={currentPage === totalPages}
                style={{
                  ...styles.paginationButton,
                  ...(currentPage === totalPages ? styles.paginationButtonDisabled : {}),
                }}
              >
                Next →
              </button>
            </div>
          )}
        </>
        )}
      </main>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f3f4f6',
  },
  header: {
    backgroundColor: 'white',
    padding: '20px 40px',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1a202c',
    margin: 0,
  },
  subtitle: {
    color: '#718096',
    fontSize: '14px',
    margin: '4px 0 0 0',
  },
  logoutButton: {
    padding: '8px 16px',
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  analyticsButton: {
    padding: '8px 16px',
    backgroundColor: '#8b5cf6',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
    fontWeight: '600',
  },
  statsBar: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '20px',
    padding: '20px 40px',
    backgroundColor: 'white',
    borderBottom: '1px solid #e5e7eb',
  },
  statCard: {
    textAlign: 'center',
  },
  statNumber: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1a202c',
  },
  statLabel: {
    fontSize: '14px',
    color: '#718096',
    marginTop: '4px',
  },
  filterCard: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    justifyContent: 'center',
  },
  filterLabel: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
  },
  filterSelect: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
  },
  main: {
    padding: '40px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  loading: {
    textAlign: 'center',
    padding: '60px',
    fontSize: '18px',
    color: '#718096',
  },
  error: {
    backgroundColor: '#fee2e2',
    color: '#dc2626',
    padding: '16px',
    borderRadius: '8px',
    marginBottom: '20px',
  },
  empty: {
    textAlign: 'center',
    padding: '60px',
    fontSize: '16px',
    color: '#718096',
  },
  leadsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
    gap: '20px',
  },
  leadCard: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    transition: 'transform 0.2s, box-shadow 0.2s',
    cursor: 'pointer',
    ':hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    },
  },
  leadHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '16px',
  },
  leadName: {
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#1a202c',
    margin: '0 0 4px 0',
  },
  leadLocation: {
    fontSize: '14px',
    color: '#718096',
    margin: 0,
  },
  priorityBadge: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 'bold',
  },
  statusBadge: {
    padding: '4px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '600',
    whiteSpace: 'nowrap',
  },
  scoreSection: {
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
    marginBottom: '16px',
    paddingBottom: '16px',
    borderBottom: '1px solid #e5e7eb',
  },
  scoreCircle: {
    textAlign: 'center',
  },
  scoreNumber: {
    fontSize: '36px',
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: '12px',
    color: '#718096',
    marginTop: '4px',
  },
  scoreDetails: {
    flex: 1,
  },
  scoreDetailItem: {
    marginBottom: '8px',
  },
  scoreDetailLabel: {
    fontSize: '12px',
    color: '#718096',
    display: 'block',
  },
  scoreDetailValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#1a202c',
  },
  reasoning: {
    marginBottom: '16px',
  },
  reasoningText: {
    fontSize: '14px',
    color: '#374151',
    lineHeight: '1.5',
    margin: 0,
  },
  actions: {
    display: 'flex',
    gap: '10px',
  },
  actionButton: {
    flex: 1,
    padding: '10px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  actionButtonSecondary: {
    flex: 1,
    padding: '10px',
    backgroundColor: 'transparent',
    color: '#667eea',
    border: '1px solid #667eea',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  // Pagination styles
  pagination: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '40px',
    padding: '20px',
    backgroundColor: 'white',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    gap: '20px',
    flexWrap: 'wrap',
  },
  paginationButton: {
    padding: '10px 20px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    minWidth: '120px',
  },
  paginationButtonDisabled: {
    backgroundColor: '#d1d5db',
    cursor: 'not-allowed',
    opacity: 0.6,
  },
  paginationInfo: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '10px',
    flex: 1,
  },
  paginationText: {
    fontSize: '14px',
    color: '#374151',
    fontWeight: '500',
  },
  pageNumbers: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  pageButton: {
    padding: '8px 12px',
    backgroundColor: 'white',
    color: '#374151',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    minWidth: '40px',
    transition: 'all 0.2s',
  },
  pageButtonActive: {
    backgroundColor: '#667eea',
    color: 'white',
    borderColor: '#667eea',
    fontWeight: '600',
  },
  // Notification styles
  notificationButton: {
    position: 'relative',
    padding: '10px 16px',
    backgroundColor: 'white',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '20px',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  notificationBadge: {
    position: 'absolute',
    top: '4px',
    right: '4px',
    backgroundColor: '#ef4444',
    color: 'white',
    fontSize: '11px',
    fontWeight: 'bold',
    padding: '2px 6px',
    borderRadius: '10px',
    minWidth: '18px',
    textAlign: 'center',
  },
  notificationPanel: {
    position: 'absolute',
    top: '50px',
    right: 0,
    width: '400px',
    maxHeight: '500px',
    backgroundColor: 'white',
    border: '1px solid #d1d5db',
    borderRadius: '12px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.15)',
    zIndex: 1000,
    overflow: 'hidden',
  },
  notificationHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px',
    borderBottom: '1px solid #e5e7eb',
  },
  notificationTitle: {
    fontSize: '18px',
    fontWeight: 'bold',
    margin: 0,
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '20px',
    cursor: 'pointer',
    color: '#6b7280',
  },
  notificationList: {
    maxHeight: '440px',
    overflowY: 'auto',
  },
  notificationItem: {
    padding: '16px',
    borderBottom: '1px solid #f3f4f6',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  notificationItemTitle: {
    fontSize: '14px',
    fontWeight: '600',
    marginBottom: '4px',
    color: '#1a202c',
  },
  notificationItemMessage: {
    fontSize: '13px',
    color: '#4b5563',
    marginBottom: '8px',
    lineHeight: '1.4',
  },
  notificationItemTime: {
    fontSize: '12px',
    color: '#9ca3af',
  },
  emptyNotifications: {
    padding: '40px',
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: '14px',
  },
  searchSection: {
    padding: '20px 40px',
    backgroundColor: 'white',
    borderBottom: '1px solid #e5e7eb',
  },
  searchRow: {
    display: 'flex',
    gap: '20px',
    alignItems: 'center',
    marginBottom: '20px',
  },
  exportButtons: {
    display: 'flex',
    gap: '12px',
  },
  exportButton: {
    padding: '12px 20px',
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    whiteSpace: 'nowrap',
    transition: 'background-color 0.2s',
  },
};
