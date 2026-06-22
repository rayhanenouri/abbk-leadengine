import { useState, useEffect, useRef } from 'react';

export default function SearchBar({ onSearch, onSelectLead }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [loading, setLoading] = useState(false);
  const searchRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowResults(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced search
  useEffect(() => {
    if (query.length < 2) {
      setResults([]);
      setShowResults(false);
      return;
    }

    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(
          `http://${window.location.hostname}:8000/api/leads/search/quick?q=${encodeURIComponent(query)}&limit=10`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );
        const data = await response.json();
        setResults(data);
        setShowResults(true);
      } catch (err) {
        console.error('Search failed:', err);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (lead) => {
    setQuery('');
    setShowResults(false);
    onSelectLead(lead.id);
  };

  return (
    <div ref={searchRef} style={styles.container}>
      <div style={styles.searchBox}>
        <span style={styles.icon}>🔍</span>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search companies..."
          style={styles.input}
        />
        {loading && <span style={styles.loader}>⏳</span>}
      </div>

      {showResults && results.length > 0 && (
        <div style={styles.resultsPanel}>
          {results.map((lead) => (
            <div
              key={lead.id}
              onClick={() => handleSelect(lead)}
              style={styles.resultItem}
            >
              <div style={styles.resultName}>{lead.company_name}</div>
              <div style={styles.resultMeta}>
                {lead.city && <span>{lead.city}</span>}
                {lead.city && lead.sector && <span> • </span>}
                {lead.sector && <span>{lead.sector}</span>}
              </div>
            </div>
          ))}
        </div>
      )}

      {showResults && query.length >= 2 && results.length === 0 && !loading && (
        <div style={styles.resultsPanel}>
          <div style={styles.noResults}>No companies found</div>
        </div>
      )}
    </div>
  );
}

const styles = {
  container: {
    position: 'relative',
    width: '100%',
    maxWidth: '500px',
  },
  searchBox: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: 'white',
    border: '2px solid #e5e7eb',
    borderRadius: '12px',
    padding: '0 16px',
    transition: 'border-color 0.2s',
  },
  icon: {
    fontSize: '20px',
    marginRight: '12px',
  },
  input: {
    flex: 1,
    border: 'none',
    outline: 'none',
    padding: '14px 0',
    fontSize: '16px',
    fontFamily: 'inherit',
  },
  loader: {
    fontSize: '16px',
    marginLeft: '8px',
  },
  resultsPanel: {
    position: 'absolute',
    top: '60px',
    left: 0,
    right: 0,
    backgroundColor: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
    maxHeight: '400px',
    overflowY: 'auto',
    zIndex: 1000,
  },
  resultItem: {
    padding: '12px 16px',
    cursor: 'pointer',
    borderBottom: '1px solid #f3f4f6',
    transition: 'background-color 0.2s',
  },
  resultName: {
    fontSize: '15px',
    fontWeight: '600',
    color: '#1a202c',
    marginBottom: '4px',
  },
  resultMeta: {
    fontSize: '13px',
    color: '#6b7280',
  },
  noResults: {
    padding: '20px',
    textAlign: 'center',
    color: '#9ca3af',
    fontSize: '14px',
  },
};
