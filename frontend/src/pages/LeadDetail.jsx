import { useState, useEffect } from 'react';
import { getLeadDetail } from '../services/api';

export default function LeadDetail({ leadId, onBack }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadLeadDetail();
  }, [leadId]);

  const loadLeadDetail = async () => {
    setLoading(true);
    setError('');
    try {
      const result = await getLeadDetail(leadId);
      setData(result);
    } catch (err) {
      setError(err.message || 'Failed to load lead details');
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

  const getSignalIcon = (signalType) => {
    const icons = {
      new_hire: '👤',
      funding: '💰',
      news: '📰',
      logo_detected: '🔍',
      role_detected: '💼',
      training_detected: '🎓',
      event_attendance: '🎪',
      tender_detected: '📋',
      audit_signal: '✅',
      export_signal: '🌍',
      multinational_signal: '🏢',
      cracked_risk: '⚠️',
    };
    return icons[signalType] || '📌';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading lead details...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>{error}</div>
        <button onClick={onBack} style={styles.backButton}>← Back to Dashboard</button>
      </div>
    );
  }

  if (!data) return null;

  const { lead, scores, signals } = data;
  const bestScore = scores.scores[0]; // Already sorted by score DESC

  return (
    <div style={styles.container}>
      {/* Header with Back Button */}
      <header style={styles.header}>
        <button onClick={onBack} style={styles.backButton}>
          ← Back to Dashboard
        </button>
        <div style={styles.headerTitle}>
          <h1 style={styles.title}>Lead Detail</h1>
        </div>
      </header>

      {/* Company Header Card */}
      <div style={styles.companyHeader}>
        <div style={styles.companyInfo}>
          <h2 style={styles.companyName}>{lead.company_name}</h2>
          <div style={styles.companyMeta}>
            {lead.sector && <span style={styles.metaItem}>🏭 {lead.sector}</span>}
            {lead.city && <span style={styles.metaItem}>📍 {lead.city}, {lead.country || 'Tunisia'}</span>}
          </div>
          <div style={styles.companyLinks}>
            {lead.website && (
              <a href={lead.website} target="_blank" rel="noopener noreferrer" style={styles.link}>
                🌐 Website
              </a>
            )}
            {lead.linkedin_url && (
              <a href={lead.linkedin_url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                💼 LinkedIn
              </a>
            )}
            {lead.scraped_data?.csv_import?.phone && (
              <span style={styles.phone}>📞 {lead.scraped_data.csv_import.phone}</span>
            )}
          </div>
        </div>
        <div style={styles.companyBadges}>
          {lead.is_multinational && (
            <span style={styles.badge}>🏢 Multinational</span>
          )}
          {lead.is_exporter && (
            <span style={styles.badge}>🌍 Exporter</span>
          )}
          {lead.under_audit && (
            <span style={styles.badge}>✅ Under Audit</span>
          )}
          {lead.employee_count && (
            <span style={styles.badge}>👥 {lead.employee_count} employees</span>
          )}
        </div>
      </div>

      {/* Best Deal Recommendation */}
      <div style={styles.bestDeal}>
        <div style={styles.bestDealHeader}>
          <span style={styles.bestDealIcon}>⭐</span>
          <h3 style={styles.bestDealTitle}>Best Deal Recommendation</h3>
        </div>
        <div style={styles.bestDealContent}>
          <div style={styles.bestDealScore}>
            <div style={{
              ...styles.bigScore,
              color: getScoreColor(bestScore.score),
            }}>
              {Math.round(bestScore.score)}
            </div>
            <div style={styles.scoreLabel}>Score</div>
          </div>
          <div style={styles.bestDealInfo}>
            <div style={styles.bestDealService}>{bestScore.service_name}</div>
            <div style={styles.bestDealReasoning}>{bestScore.reasoning}</div>
            <button style={styles.callButton}>
              📞 Call Now - Pitch {bestScore.service_name}
            </button>
          </div>
        </div>
      </div>

      {/* Score Cards Grid */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>All ABBK Services - Score Breakdown</h3>
        <div style={styles.scoresGrid}>
          {scores.scores.map((score) => (
            <div key={score.id} style={styles.scoreCard}>
              <div style={styles.scoreCardHeader}>
                <div style={styles.scoreCardTitle}>{score.service_name}</div>
                <div style={{
                  ...styles.scoreCardScore,
                  color: getScoreColor(score.score),
                }}>
                  {Math.round(score.score)}
                </div>
              </div>
              <div style={styles.scoreCardType}>{score.service_type.replace('_', ' ')}</div>
              <div style={styles.scoreCardReasoning}>{score.reasoning}</div>
              <div style={styles.scoreProgress}>
                <div
                  style={{
                    ...styles.scoreProgressBar,
                    width: `${score.score}%`,
                    backgroundColor: getScoreColor(score.score),
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Signals Timeline */}
      <div style={styles.section}>
        <h3 style={styles.sectionTitle}>
          Signals Timeline ({signals.length} detected)
        </h3>
        {signals.length === 0 ? (
          <div style={styles.emptySignals}>
            No signals detected yet. Run scrapers to collect signals.
          </div>
        ) : (
          <div style={styles.timeline}>
            {signals.map((signal) => (
              <div key={signal.id} style={styles.timelineItem}>
                <div style={styles.timelineIcon}>
                  {getSignalIcon(signal.signal_type)}
                </div>
                <div style={styles.timelineContent}>
                  <div style={styles.timelineHeader}>
                    <div style={styles.timelineTitle}>{signal.title}</div>
                    <div style={styles.timelineDate}>{formatDate(signal.detected_at)}</div>
                  </div>
                  <div style={styles.timelineType}>
                    {signal.signal_type.replace('_', ' ').toUpperCase()}
                  </div>
                  {signal.detail && (
                    <div style={styles.timelineDetail}>{signal.detail}</div>
                  )}
                  {signal.source_url && (
                    <a
                      href={signal.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={styles.timelineSource}
                    >
                      🔗 View Source
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f3f4f6',
    paddingBottom: '40px',
  },
  header: {
    backgroundColor: 'white',
    padding: '20px 40px',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    alignItems: 'center',
    gap: '20px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  backButton: {
    padding: '10px 20px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  headerTitle: {
    flex: 1,
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1a202c',
    margin: 0,
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
    margin: '20px',
  },
  companyHeader: {
    backgroundColor: 'white',
    margin: '20px 40px',
    padding: '30px',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  companyInfo: {
    marginBottom: '20px',
  },
  companyName: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1a202c',
    margin: '0 0 12px 0',
  },
  companyMeta: {
    display: 'flex',
    gap: '20px',
    marginBottom: '12px',
  },
  metaItem: {
    fontSize: '16px',
    color: '#718096',
  },
  companyLinks: {
    display: 'flex',
    gap: '16px',
    flexWrap: 'wrap',
  },
  link: {
    color: '#667eea',
    textDecoration: 'none',
    fontSize: '14px',
    fontWeight: '500',
  },
  phone: {
    color: '#374151',
    fontSize: '14px',
    fontWeight: '500',
  },
  companyBadges: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap',
  },
  badge: {
    padding: '6px 12px',
    backgroundColor: '#f3f4f6',
    color: '#374151',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
  },
  bestDeal: {
    backgroundColor: '#fef3c7',
    border: '2px solid #f59e0b',
    margin: '0 40px 20px 40px',
    padding: '30px',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(245, 158, 11, 0.15)',
  },
  bestDealHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '20px',
  },
  bestDealIcon: {
    fontSize: '32px',
  },
  bestDealTitle: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#92400e',
    margin: 0,
  },
  bestDealContent: {
    display: 'flex',
    gap: '30px',
    alignItems: 'center',
  },
  bestDealScore: {
    textAlign: 'center',
    minWidth: '100px',
  },
  bigScore: {
    fontSize: '56px',
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: '14px',
    color: '#78716c',
    marginTop: '4px',
  },
  bestDealInfo: {
    flex: 1,
  },
  bestDealService: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1a202c',
    marginBottom: '12px',
  },
  bestDealReasoning: {
    fontSize: '16px',
    color: '#374151',
    lineHeight: '1.6',
    marginBottom: '20px',
  },
  callButton: {
    padding: '14px 28px',
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '600',
    cursor: 'pointer',
    boxShadow: '0 2px 8px rgba(16, 185, 129, 0.3)',
  },
  section: {
    margin: '0 40px 20px 40px',
  },
  sectionTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1a202c',
    marginBottom: '16px',
  },
  scoresGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '16px',
  },
  scoreCard: {
    backgroundColor: 'white',
    padding: '20px',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  scoreCardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '8px',
  },
  scoreCardTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#1a202c',
    flex: 1,
  },
  scoreCardScore: {
    fontSize: '28px',
    fontWeight: 'bold',
  },
  scoreCardType: {
    fontSize: '12px',
    color: '#718096',
    textTransform: 'uppercase',
    marginBottom: '12px',
  },
  scoreCardReasoning: {
    fontSize: '14px',
    color: '#374151',
    lineHeight: '1.5',
    marginBottom: '12px',
  },
  scoreProgress: {
    height: '6px',
    backgroundColor: '#e5e7eb',
    borderRadius: '3px',
    overflow: 'hidden',
  },
  scoreProgressBar: {
    height: '100%',
    transition: 'width 0.3s ease',
  },
  timeline: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
  },
  timelineItem: {
    display: 'flex',
    gap: '16px',
    paddingBottom: '20px',
    marginBottom: '20px',
    borderBottom: '1px solid #e5e7eb',
  },
  timelineIcon: {
    fontSize: '32px',
    flexShrink: 0,
  },
  timelineContent: {
    flex: 1,
  },
  timelineHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '8px',
  },
  timelineTitle: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#1a202c',
  },
  timelineDate: {
    fontSize: '14px',
    color: '#718096',
  },
  timelineType: {
    fontSize: '12px',
    color: '#667eea',
    fontWeight: '600',
    marginBottom: '8px',
  },
  timelineDetail: {
    fontSize: '14px',
    color: '#374151',
    lineHeight: '1.5',
    marginBottom: '8px',
  },
  timelineSource: {
    fontSize: '14px',
    color: '#667eea',
    textDecoration: 'none',
    fontWeight: '500',
  },
  emptySignals: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '12px',
    textAlign: 'center',
    color: '#718096',
    fontSize: '16px',
  },
};
