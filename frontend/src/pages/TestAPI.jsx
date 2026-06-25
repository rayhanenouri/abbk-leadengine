/**
 * API Test Page - Debug why leads aren't showing
 */
import { useState } from 'react';

export default function TestAPI() {
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    setResult('Testing...');

    try {
      // Get token
      const loginRes = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'admin@abbk.tn', password: 'admin123' })
      });
      const loginData = await loginRes.json();
      const token = loginData.access_token;

      setResult(prev => prev + `\n✓ Token: ${token.substring(0, 20)}...`);

      // Test leads endpoint
      const leadsRes = await fetch('http://localhost:8000/api/leads/?skip=0&limit=5&sort_by=created_at&sort_order=desc', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const leadsData = await leadsRes.json();

      setResult(prev => prev + `\n✓ Total leads: ${leadsData.total}`);
      setResult(prev => prev + `\n✓ Leads array length: ${leadsData.leads?.length || 0}`);
      setResult(prev => prev + `\n✓ First lead: ${leadsData.leads?.[0]?.company_name || 'NONE'}`);
      setResult(prev => prev + `\n\nFull response:\n${JSON.stringify(leadsData, null, 2)}`);

    } catch (err) {
      setResult(prev => prev + `\n❌ ERROR: ${err.message}\n${err.stack}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'monospace' }}>
      <h1>API Test Page</h1>
      <button
        onClick={testAPI}
        disabled={loading}
        style={{
          padding: '10px 20px',
          background: '#4F46E5',
          color: 'white',
          border: 'none',
          borderRadius: '4px',
          cursor: loading ? 'wait' : 'pointer'
        }}
      >
        {loading ? 'Testing...' : 'Test API'}
      </button>

      <pre style={{
        marginTop: '20px',
        padding: '20px',
        background: '#1e1e1e',
        color: '#00ff00',
        borderRadius: '8px',
        overflow: 'auto',
        maxHeight: '600px'
      }}>
        {result || 'Click button to test API'}
      </pre>
    </div>
  );
}
