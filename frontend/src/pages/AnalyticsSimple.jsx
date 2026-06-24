import { useState, useEffect } from 'react';
import { ArrowLeft } from 'lucide-react';

const AnalyticsSimple = ({ onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`http://${window.location.hostname}:8000/api/analytics/overview`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        setAnalytics(data);
        setLoading(false);
      } catch (err) {
        console.error(err);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: '#FAFAFA', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#000', fontSize: '18px', fontWeight: 600 }}>Loading...</div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#FAFAFA', padding: '40px' }}>
      <button onClick={onBack} style={{
        padding: '12px 24px',
        backgroundColor: '#000',
        color: '#fff',
        border: 'none',
        borderRadius: '12px',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: 600,
        marginBottom: '32px'
      }}>
        ← Back
      </button>

      <h1 style={{ fontSize: '32px', fontWeight: 800, color: '#000', marginBottom: '32px' }}>
        Analytics Overview
      </h1>

      {analytics && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '24px' }}>
          <div style={{
            backgroundColor: '#fff',
            padding: '24px',
            borderRadius: '16px',
            border: '1px solid #E5E5E5'
          }}>
            <div style={{ fontSize: '36px', fontWeight: 700, color: '#000', marginBottom: '8px' }}>
              {analytics.summary.total_leads}
            </div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#737373' }}>
              Total Leads
            </div>
          </div>

          <div style={{
            backgroundColor: '#fff',
            padding: '24px',
            borderRadius: '16px',
            border: '1px solid #E5E5E5'
          }}>
            <div style={{ fontSize: '36px', fontWeight: 700, color: '#000', marginBottom: '8px' }}>
              {analytics.summary.high_priority_leads}
            </div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#737373' }}>
              High Priority
            </div>
          </div>

          <div style={{
            backgroundColor: '#fff',
            padding: '24px',
            borderRadius: '16px',
            border: '1px solid #E5E5E5'
          }}>
            <div style={{ fontSize: '36px', fontWeight: 700, color: '#000', marginBottom: '8px' }}>
              {analytics.high_value_leads.multinational}
            </div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#737373' }}>
              Multinationals
            </div>
          </div>

          <div style={{
            backgroundColor: '#fff',
            padding: '24px',
            borderRadius: '16px',
            border: '1px solid #E5E5E5'
          }}>
            <div style={{ fontSize: '36px', fontWeight: 700, color: '#000', marginBottom: '8px' }}>
              {analytics.summary.conversion_rate}%
            </div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: '#737373' }}>
              Conversion Rate
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsSimple;
