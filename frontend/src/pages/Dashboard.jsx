import { useState, useEffect } from 'react';
import { getRankedLeads, logout } from '../services/api';

export default function Dashboard() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [minScore, setMinScore] = useState(0);

  useEffect(() => {
    loadLeads();
  }, [minScore]);

  const loadLeads = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getRankedLeads(50, minScore);
      // Deduplicate leads by lead_id, keeping highest score
      const uniqueLeads = [];
      const seen = new Set();
      data.forEach(lead => {
        if (!seen.has(lead.lead_id)) {
          uniqueLeads.push(lead);
          seen.add(lead.lead_id);
        }
      });
      setLeads(uniqueLeads);
    } catch (err) {
      setError(err.message || 'Failed to load leads');
    } finally {
      setLoading(false);
    }
  };

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

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>ABBK LeadEngine</h1>
          <p style={styles.subtitle}>Ranked Leads - Who to Call Today</p>
        </div>
        <button onClick={logout} style={styles.logoutButton}>
          Logout
        </button>
      </header>

      {/* Stats Bar */}
      <div style={styles.statsBar}>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>{leads.length}</div>
          <div style={styles.statLabel}>Total Leads</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>
            {leads.filter(l => l.best_score >= 70).length}
          </div>
          <div style={styles.statLabel}>High Priority</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statNumber}>
            {leads.filter(l => l.best_score >= 50 && l.best_score < 70).length}
          </div>
          <div style={styles.statLabel}>Medium Priority</div>
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

        {!loading && !error && leads.length === 0 && (
          <div style={styles.empty}>
            No leads found. Try lowering the minimum score filter.
          </div>
        )}

        {!loading && !error && leads.length > 0 && (
          <div style={styles.leadsGrid}>
            {leads.map((lead) => {
              const badge = getPriorityBadge(lead.best_score);
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
                    <div style={{
                      ...styles.priorityBadge,
                      backgroundColor: `${badge.color}20`,
                      color: badge.color,
                    }}>
                      {badge.text}
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
                    <button style={styles.actionButtonSecondary}>
                      View Details
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
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
};
