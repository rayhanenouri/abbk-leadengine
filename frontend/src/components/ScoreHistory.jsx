import { useState, useEffect } from 'react';

export default function ScoreHistory({ leadId }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedService, setSelectedService] = useState('all');

  useEffect(() => {
    loadHistory();
  }, [leadId, selectedService]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const params = new URLSearchParams();
      if (selectedService !== 'all') {
        params.append('service_name', selectedService);
      }

      const response = await fetch(
        `http://${window.location.hostname}:8000/api/scores/${leadId}/history?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      const data = await response.json();
      setHistory(data);
    } catch (err) {
      console.error('Failed to load score history:', err);
    } finally {
      setLoading(false);
    }
  };

  const getChangeIcon = (change) => {
    if (change > 0) return '📈';
    if (change < 0) return '📉';
    return '➡️';
  };

  const getChangeColor = (change) => {
    if (change > 0) return '#10b981';
    if (change < 0) return '#ef4444';
    return '#6b7280';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get unique services
  const services = ['all', ...new Set(history.map(h => h.service_name))];

  if (loading) {
    return <div style={styles.loading}>Loading score history...</div>;
  }

  if (history.length === 0) {
    return (
      <div style={styles.empty}>
        No score changes recorded yet. Scores will be tracked as new signals are detected.
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Score History</h3>
        <select
          value={selectedService}
          onChange={(e) => setSelectedService(e.target.value)}
          style={styles.select}
        >
          <option value="all">All Services</option>
          {services.slice(1).map((service) => (
            <option key={service} value={service}>
              {service}
            </option>
          ))}
        </select>
      </div>

      <div style={styles.timeline}>
        {history.map((record, index) => (
          <div key={record.id} style={styles.timelineItem}>
            <div style={styles.timelineDot}></div>
            {index < history.length - 1 && <div style={styles.timelineLine}></div>}

            <div style={styles.card}>
              <div style={styles.cardHeader}>
                <div style={styles.serviceName}>{record.service_name}</div>
                <div style={styles.date}>{formatDate(record.recorded_at)}</div>
              </div>

              <div style={styles.scoreChange}>
                <span style={styles.scoreLabel}>Score:</span>
                <span style={styles.oldScore}>{record.old_score.toFixed(1)}</span>
                <span style={{ ...styles.arrow, color: getChangeColor(record.change) }}>
                  {getChangeIcon(record.change)}
                </span>
                <span style={styles.newScore}>{record.new_score.toFixed(1)}</span>
                <span style={{ ...styles.change, color: getChangeColor(record.change) }}>
                  ({record.change > 0 ? '+' : ''}{record.change.toFixed(1)})
                </span>
              </div>

              {record.reason && (
                <div style={styles.reason}>{record.reason}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    marginTop: '20px',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    margin: 0,
    color: '#1a202c',
  },
  select: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: 'white',
    cursor: 'pointer',
  },
  timeline: {
    position: 'relative',
  },
  timelineItem: {
    position: 'relative',
    paddingLeft: '40px',
    marginBottom: '24px',
  },
  timelineDot: {
    position: 'absolute',
    left: '0',
    top: '8px',
    width: '12px',
    height: '12px',
    backgroundColor: '#667eea',
    borderRadius: '50%',
    border: '3px solid #e0e7ff',
  },
  timelineLine: {
    position: 'absolute',
    left: '5px',
    top: '20px',
    bottom: '-24px',
    width: '2px',
    backgroundColor: '#e5e7eb',
  },
  card: {
    backgroundColor: '#f9fafb',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '16px',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
  },
  serviceName: {
    fontSize: '15px',
    fontWeight: '600',
    color: '#374151',
  },
  date: {
    fontSize: '13px',
    color: '#6b7280',
  },
  scoreChange: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '16px',
  },
  scoreLabel: {
    fontSize: '14px',
    color: '#6b7280',
  },
  oldScore: {
    fontWeight: '600',
    color: '#6b7280',
  },
  arrow: {
    fontSize: '20px',
  },
  newScore: {
    fontWeight: 'bold',
    color: '#1a202c',
    fontSize: '18px',
  },
  change: {
    fontWeight: '600',
    fontSize: '14px',
  },
  reason: {
    fontSize: '13px',
    color: '#6b7280',
    marginTop: '8px',
    fontStyle: 'italic',
  },
  loading: {
    padding: '40px',
    textAlign: 'center',
    color: '#6b7280',
  },
  empty: {
    padding: '40px',
    textAlign: 'center',
    color: '#9ca3af',
    backgroundColor: '#f9fafb',
    borderRadius: '12px',
    fontSize: '14px',
  },
};
