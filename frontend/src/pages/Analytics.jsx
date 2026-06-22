import { useState, useEffect } from 'react';

const API_BASE_URL = `http://${window.location.hostname}:8000/api`;

const Analytics = ({ onBack }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/analytics/overview`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.reload();
        return;
      }

      if (!response.ok) throw new Error('Failed to fetch analytics');

      const data = await response.json();
      setAnalytics(data);
      setLoading(false);
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-red-600">Error: {error}</div>
      </div>
    );
  }

  if (!analytics) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">📊 Analytics Dashboard</h1>
              <p className="text-sm text-gray-600">ABBK Sales Intelligence Overview</p>
            </div>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
            >
              Back to Leads
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <SummaryCard
            title="Total Leads"
            value={analytics.summary.total_leads}
            icon="🏢"
            color="blue"
          />
          <SummaryCard
            title="High Priority"
            value={analytics.summary.high_priority_leads}
            subtitle="Score ≥ 70"
            icon="🔥"
            color="red"
          />
          <SummaryCard
            title="New This Week"
            value={analytics.summary.new_companies_this_week}
            icon="✨"
            color="green"
          />
          <SummaryCard
            title="Conversion Rate"
            value={`${analytics.summary.conversion_rate}%`}
            subtitle={`${analytics.summary.converted_count}/${analytics.summary.contacted_count} contacted`}
            icon="📈"
            color="purple"
          />
        </div>

        {/* High-Value Leads Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <HighValueCard
            title="Multinationals"
            count={analytics.high_value_leads.multinational}
            description="International companies (best converters)"
            icon="🌍"
          />
          <HighValueCard
            title="Exporters"
            count={analytics.high_value_leads.exporter}
            description="Must pass international audits"
            icon="📦"
          />
          <HighValueCard
            title="Under Audit"
            count={analytics.high_value_leads.under_audit}
            description="Ready to buy NOW (compliance)"
            icon="✅"
          />
        </div>

        {/* Sales Funnel */}
        <ChartCard title="Sales Funnel" subtitle="Lead status progression">
          <div className="space-y-2">
            {analytics.leads_by_status.map((status, index) => {
              const maxCount = Math.max(...analytics.leads_by_status.map(s => s.count));
              const percentage = (status.count / maxCount) * 100;
              const colors = {
                new: 'bg-blue-400',
                qualified: 'bg-green-400',
                contacted: 'bg-yellow-400',
                converted: 'bg-green-600',
                lost: 'bg-red-500'
              };

              return (
                <div key={index} className="flex items-center gap-3">
                  <div className="w-24 text-sm font-medium text-gray-700 capitalize">
                    {status.status || 'new'}
                  </div>
                  <div className="flex-1 bg-gray-200 rounded-full h-8 relative">
                    <div
                      className={`${colors[status.status] || 'bg-gray-500'} h-8 rounded-full flex items-center justify-end px-3 text-white font-bold text-sm transition-all duration-500`}
                      style={{ width: `${percentage}%` }}
                    >
                      {status.count}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </ChartCard>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Top Sectors by Count */}
          <ChartCard title="Top 10 Sectors" subtitle="By number of leads">
            <div className="space-y-2">
              {analytics.leads_by_sector.slice(0, 10).map((sector, index) => {
                const maxCount = Math.max(...analytics.leads_by_sector.map(s => s.count));
                const percentage = (sector.count / maxCount) * 100;
                const colors = ['bg-blue-500', 'bg-blue-400', 'bg-blue-300'];
                const colorClass = colors[Math.min(index, 2)];

                return (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-6 text-xs font-bold text-gray-500">{index + 1}</div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium text-gray-700 truncate">
                          {sector.sector}
                        </div>
                        <div className="text-sm font-bold text-gray-900 ml-2">{sector.count}</div>
                      </div>
                      <div className="bg-gray-200 rounded-full h-2">
                        <div
                          className={`${colorClass} h-2 rounded-full transition-all duration-500`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ChartCard>

          {/* Best Sectors by Score */}
          <ChartCard title="Best Sectors" subtitle="Highest average scores">
            <div className="space-y-2">
              {analytics.top_sectors_by_score.map((sector, index) => {
                const percentage = sector.avg_score;
                const colors = ['bg-green-500', 'bg-green-400', 'bg-green-300'];
                const colorClass = colors[Math.min(index, 2)];

                return (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-6 text-xs font-bold text-gray-500">{index + 1}</div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <div className="text-sm font-medium text-gray-700 truncate">
                          {sector.sector}
                        </div>
                        <div className="text-sm font-bold text-gray-900 ml-2">
                          {sector.avg_score} <span className="text-xs text-gray-500">({sector.lead_count})</span>
                        </div>
                      </div>
                      <div className="bg-gray-200 rounded-full h-2">
                        <div
                          className={`${colorClass} h-2 rounded-full transition-all duration-500`}
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ChartCard>

          {/* Score Distribution */}
          <ChartCard title="Score Distribution" subtitle="Lead quality histogram">
            <div className="flex items-end justify-between h-48 gap-1">
              {analytics.score_distribution.map((bucket, index) => {
                const maxCount = Math.max(...analytics.score_distribution.map(b => b.count));
                const height = maxCount > 0 ? (bucket.count / maxCount) * 100 : 0;

                return (
                  <div key={index} className="flex-1 flex flex-col items-center justify-end">
                    <div className="text-xs font-bold text-gray-700 mb-1">{bucket.count}</div>
                    <div
                      className="w-full bg-purple-500 rounded-t transition-all duration-500 hover:bg-purple-600"
                      style={{ height: `${height}%`, minHeight: bucket.count > 0 ? '8px' : '0' }}
                    />
                    <div className="text-xs text-gray-600 mt-1 transform -rotate-45 origin-top-left">
                      {bucket.range}
                    </div>
                  </div>
                );
              })}
            </div>
          </ChartCard>

          {/* Top Cities */}
          <ChartCard title="Top Cities in Tunisia" subtitle="Lead concentration">
            <div className="space-y-2">
              {analytics.geographic.by_city.slice(0, 10).map((city, index) => {
                const maxCount = Math.max(...analytics.geographic.by_city.map(c => c.count));
                const percentage = (city.count / maxCount) * 100;

                return (
                  <div key={index} className="flex items-center gap-2">
                    <div className="w-20 text-sm font-medium text-gray-700">{city.city}</div>
                    <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                      <div
                        className="bg-orange-500 h-6 rounded-full flex items-center justify-end px-2 text-white font-bold text-xs transition-all duration-500"
                        style={{ width: `${percentage}%`, minWidth: city.count > 0 ? '32px' : '0' }}
                      >
                        {city.count}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </ChartCard>
        </div>

        {/* Countries */}
        <ChartCard title="Geographic Distribution" subtitle="Leads by country">
          <div className="flex flex-wrap gap-3">
            {analytics.geographic.by_country.map((country, index) => {
              const colors = ['bg-indigo-500', 'bg-blue-500', 'bg-cyan-500', 'bg-teal-500', 'bg-green-500'];
              const colorClass = colors[index % colors.length];

              return (
                <div key={index} className={`${colorClass} text-white rounded-lg px-4 py-3 shadow-md`}>
                  <div className="text-2xl font-bold">{country.count}</div>
                  <div className="text-sm opacity-90">{country.country}</div>
                </div>
              );
            })}
          </div>
        </ChartCard>

        {/* Recent Signals */}
        {analytics.recent_signals.length > 0 && (
          <ChartCard
            title="Signals Detected This Week"
            subtitle={`${analytics.summary.total_signals_this_week} total signals`}
          >
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {analytics.recent_signals.map((signal, index) => (
                <SignalBadge key={index} type={signal.signal_type} count={signal.count} />
              ))}
            </div>
          </ChartCard>
        )}
      </div>
    </div>
  );
};

// Summary Card Component
const SummaryCard = ({ title, value, subtitle, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    red: 'bg-red-50 border-red-200',
    green: 'bg-green-50 border-green-200',
    purple: 'bg-purple-50 border-purple-200'
  };

  return (
    <div className={`border-2 rounded-lg p-4 ${colorClasses[color]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-2xl">{icon}</span>
        <span className="text-3xl font-bold text-gray-900">{value}</span>
      </div>
      <div className="text-sm font-semibold text-gray-700">{title}</div>
      {subtitle && <div className="text-xs text-gray-600 mt-1">{subtitle}</div>}
    </div>
  );
};

// High Value Card Component
const HighValueCard = ({ title, count, description, icon }) => {
  return (
    <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-lg p-4 shadow-lg">
      <div className="flex items-center justify-between mb-2">
        <span className="text-3xl">{icon}</span>
        <span className="text-4xl font-bold">{count}</span>
      </div>
      <div className="text-lg font-semibold">{title}</div>
      <div className="text-sm opacity-90 mt-1">{description}</div>
    </div>
  );
};

// Chart Card Component
const ChartCard = ({ title, subtitle, children }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="mb-4">
        <h3 className="text-lg font-bold text-gray-900">{title}</h3>
        {subtitle && <p className="text-sm text-gray-600">{subtitle}</p>}
      </div>
      {children}
    </div>
  );
};

// Signal Badge Component
const SignalBadge = ({ type, count }) => {
  const signalIcons = {
    new_hire: '👤',
    funding: '💰',
    news: '📰',
    logo_detected: '🎨',
    role_detected: '💼',
    training_detected: '🎓',
    event_attendance: '🎪',
    tender_detected: '📋',
    audit_signal: '✅',
    export_signal: '📦',
    multinational_signal: '🌍',
    cracked_risk: '⚠️'
  };

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center hover:shadow-md transition">
      <div className="text-2xl mb-1">{signalIcons[type] || '📊'}</div>
      <div className="text-xl font-bold text-gray-900">{count}</div>
      <div className="text-xs text-gray-600 mt-1 capitalize">{type.replace(/_/g, ' ')}</div>
    </div>
  );
};

export default Analytics;
