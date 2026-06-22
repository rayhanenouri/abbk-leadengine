import { useState, useEffect } from 'react';

export default function FilterPanel({ onFilterChange }) {
  const [filters, setFilters] = useState({
    sector: '',
    city: '',
    country: '',
    status: '',
    is_multinational: null,
    is_exporter: null,
    under_audit: null,
    min_score: 0,
  });

  const [filterOptions, setFilterOptions] = useState({
    sectors: [],
    cities: [],
    countries: [],
    statuses: [],
  });

  const [showPanel, setShowPanel] = useState(false);

  useEffect(() => {
    loadFilterOptions();
  }, []);

  const loadFilterOptions = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `http://${window.location.hostname}:8000/api/leads/filters/options`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );
      const data = await response.json();
      setFilterOptions(data);
    } catch (err) {
      console.error('Failed to load filter options:', err);
    }
  };

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = {
      sector: '',
      city: '',
      country: '',
      status: '',
      is_multinational: null,
      is_exporter: null,
      under_audit: null,
      min_score: 0,
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const activeFilterCount = Object.values(filters).filter(
    (v) => v !== '' && v !== null && v !== 0
  ).length;

  return (
    <div style={styles.container}>
      <button onClick={() => setShowPanel(!showPanel)} style={styles.toggleButton}>
        🔽 Filters {activeFilterCount > 0 && `(${activeFilterCount})`}
      </button>

      {showPanel && (
        <div style={styles.panel}>
          <div style={styles.grid}>
            {/* Sector */}
            <div style={styles.filterGroup}>
              <label style={styles.label}>Sector</label>
              <select
                value={filters.sector}
                onChange={(e) => handleFilterChange('sector', e.target.value)}
                style={styles.select}
              >
                <option value="">All Sectors</option>
                {filterOptions.sectors.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            {/* City */}
            <div style={styles.filterGroup}>
              <label style={styles.label}>City</label>
              <select
                value={filters.city}
                onChange={(e) => handleFilterChange('city', e.target.value)}
                style={styles.select}
              >
                <option value="">All Cities</option>
                {filterOptions.cities.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            {/* Country */}
            <div style={styles.filterGroup}>
              <label style={styles.label}>Country</label>
              <select
                value={filters.country}
                onChange={(e) => handleFilterChange('country', e.target.value)}
                style={styles.select}
              >
                <option value="">All Countries</option>
                {filterOptions.countries.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            {/* Status */}
            <div style={styles.filterGroup}>
              <label style={styles.label}>Status</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                style={styles.select}
              >
                <option value="">All Statuses</option>
                {filterOptions.statuses.map((s) => (
                  <option key={s} value={s}>
                    {s.charAt(0).toUpperCase() + s.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Min Score */}
            <div style={styles.filterGroup}>
              <label style={styles.label}>Min Score: {filters.min_score}</label>
              <input
                type="range"
                min="0"
                max="100"
                step="10"
                value={filters.min_score}
                onChange={(e) => handleFilterChange('min_score', parseInt(e.target.value))}
                style={styles.range}
              />
            </div>

            {/* Checkboxes */}
            <div style={styles.filterGroup}>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.is_multinational === true}
                  onChange={(e) =>
                    handleFilterChange('is_multinational', e.target.checked ? true : null)
                  }
                />
                <span>Multinational only</span>
              </label>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.is_exporter === true}
                  onChange={(e) =>
                    handleFilterChange('is_exporter', e.target.checked ? true : null)
                  }
                />
                <span>Exporters only</span>
              </label>
              <label style={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.under_audit === true}
                  onChange={(e) =>
                    handleFilterChange('under_audit', e.target.checked ? true : null)
                  }
                />
                <span>Under audit only</span>
              </label>
            </div>
          </div>

          <div style={styles.actions}>
            <button onClick={clearFilters} style={styles.clearButton}>
              Clear All Filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    marginBottom: '20px',
  },
  toggleButton: {
    padding: '12px 24px',
    backgroundColor: '#667eea',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  panel: {
    backgroundColor: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    padding: '24px',
    marginTop: '12px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '20px',
  },
  filterGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  label: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
  },
  select: {
    padding: '10px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: 'white',
    cursor: 'pointer',
  },
  range: {
    width: '100%',
  },
  checkboxLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '14px',
    color: '#4b5563',
    cursor: 'pointer',
  },
  actions: {
    display: 'flex',
    justifyContent: 'flex-end',
    paddingTop: '16px',
    borderTop: '1px solid #e5e7eb',
  },
  clearButton: {
    padding: '10px 20px',
    backgroundColor: '#f3f4f6',
    color: '#374151',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
  },
};
