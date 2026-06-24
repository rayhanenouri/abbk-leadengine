/**
 * Smart Search - Advanced Lead Search Engine
 * Multi-field search with filters and saved queries
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Filter, Save, History, X, TrendingUp, MapPin,
  Building2, Briefcase, DollarSign, Calendar, Star,
  ChevronRight, Eye, Download, Sparkles, Zap, Clock
} from 'lucide-react';
import { getRankedLeads } from '../services/api';

export default function SmartSearch({ onViewLead }) {
  const [leads, setLeads] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const [savedSearches, setSavedSearches] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const [advancedFilters, setAdvancedFilters] = useState({
    minScore: 0,
    maxScore: 100,
    sectors: [],
    cities: [],
    flags: {
      multinational: false,
      exporter: false,
      audit: false,
    },
    status: [],
  });

  useEffect(() => {
    loadLeads();
    loadSavedData();
  }, []);

  const loadLeads = async () => {
    try {
      const data = await getRankedLeads(10000, 0, {});
      setLeads(data);
      setResults(data.slice(0, 50));
    } catch (err) {
      console.error('Failed to load leads:', err);
    }
  };

  const loadSavedData = () => {
    const recent = JSON.parse(localStorage.getItem('recentSearches') || '[]');
    const saved = JSON.parse(localStorage.getItem('savedSearches') || '[]');
    setRecentSearches(recent.slice(0, 5));
    setSavedSearches(saved);
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
    setLoading(true);

    setTimeout(() => {
      const filtered = leads.filter(lead => {
        const matchesQuery = query === '' ||
          lead.company_name.toLowerCase().includes(query.toLowerCase()) ||
          (lead.sector || '').toLowerCase().includes(query.toLowerCase()) ||
          (lead.city || '').toLowerCase().includes(query.toLowerCase()) ||
          (lead.best_service || '').toLowerCase().includes(query.toLowerCase());

        const matchesScore = lead.best_score >= advancedFilters.minScore &&
                           lead.best_score <= advancedFilters.maxScore;

        const matchesSector = advancedFilters.sectors.length === 0 ||
                            advancedFilters.sectors.includes(lead.sector);

        const matchesCity = advancedFilters.cities.length === 0 ||
                          advancedFilters.cities.includes(lead.city);

        const matchesFlags = (!advancedFilters.flags.multinational || lead.is_multinational) &&
                           (!advancedFilters.flags.exporter || lead.is_exporter) &&
                           (!advancedFilters.flags.audit || lead.under_audit);

        const matchesStatus = advancedFilters.status.length === 0 ||
                            advancedFilters.status.includes(lead.status || 'new');

        return matchesQuery && matchesScore && matchesSector && matchesCity &&
               matchesFlags && matchesStatus;
      });

      setResults(filtered);
      setLoading(false);

      if (query && !recentSearches.includes(query)) {
        const updated = [query, ...recentSearches].slice(0, 5);
        setRecentSearches(updated);
        localStorage.setItem('recentSearches', JSON.stringify(updated));
      }
    }, 300);
  };

  const saveSearch = () => {
    if (!searchQuery) return;
    const newSearch = {
      id: Date.now(),
      query: searchQuery,
      filters: advancedFilters,
      resultCount: results.length,
      timestamp: new Date().toISOString(),
    };
    const updated = [newSearch, ...savedSearches];
    setSavedSearches(updated);
    localStorage.setItem('savedSearches', JSON.stringify(updated));
  };

  const loadSavedSearch = (search) => {
    setSearchQuery(search.query);
    setAdvancedFilters(search.filters);
    handleSearch(search.query);
  };

  const deleteSavedSearch = (id) => {
    const updated = savedSearches.filter(s => s.id !== id);
    setSavedSearches(updated);
    localStorage.setItem('savedSearches', JSON.stringify(updated));
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem('recentSearches');
  };

  const uniqueSectors = [...new Set(leads.map(l => l.sector).filter(Boolean))];
  const uniqueCities = [...new Set(leads.map(l => l.city).filter(Boolean))];

  const suggestions = [
    { icon: TrendingUp, label: 'High Score Companies', query: '', filter: { minScore: 70 } },
    { icon: MapPin, label: 'Tunis Companies', query: 'Tunis', filter: {} },
    { icon: Building2, label: 'Multinationals', query: '', filter: { flags: { multinational: true } } },
    { icon: Briefcase, label: 'Manufacturing Sector', query: 'manufacturing', filter: {} },
  ];

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center">
              <Search className="w-6 h-6 text-blue-600" strokeWidth={2.5} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 mb-0.5" style={{
                fontWeight: 800,
                letterSpacing: '-0.04em',
              }}>
                Smart Search
              </h1>
              <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                Advanced search across all company data
              </p>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative mb-4">
            <Search className="absolute left-5 top-1/2 -translate-y-1/2 w-6 h-6 text-neutral-400" strokeWidth={2.5} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              placeholder="Search companies, sectors, locations, products..."
              className="w-full pl-16 pr-32 py-4 bg-neutral-50 border-2 border-neutral-200 rounded-2xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-blue-600 focus:ring-4 focus:ring-blue-600/10 transition-all text-lg"
              style={{ fontSize: '17px', fontWeight: 500 }}
              autoFocus
            />
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
              {searchQuery && (
                <motion.button
                  onClick={() => handleSearch('')}
                  className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <X className="w-5 h-5 text-neutral-500" strokeWidth={2.5} />
                </motion.button>
              )}
              <motion.button
                onClick={saveSearch}
                disabled={!searchQuery}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                  searchQuery
                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                    : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                }`}
                whileHover={searchQuery ? { scale: 1.05 } : {}}
                whileTap={searchQuery ? { scale: 0.95 } : {}}
                style={{ fontSize: '14px' }}
              >
                <Save className="w-4 h-4" strokeWidth={2.5} />
                Save
              </motion.button>
            </div>
          </div>

          {/* Advanced Filters Toggle */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="flex items-center gap-2 text-sm font-semibold text-neutral-700 hover:text-neutral-900"
            >
              <Filter className="w-4 h-4" strokeWidth={2.5} />
              Advanced Filters
              <motion.div
                animate={{ rotate: showAdvanced ? 90 : 0 }}
                transition={{ duration: 0.2 }}
              >
                <ChevronRight className="w-4 h-4" strokeWidth={2.5} />
              </motion.div>
            </button>

            <div className="text-sm text-neutral-600">
              <span className="font-bold text-neutral-900">{results.length}</span> results
            </div>
          </div>

          {/* Advanced Filters Panel */}
          <AnimatePresence>
            {showAdvanced && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="mt-4 p-4 bg-neutral-50 rounded-xl border border-neutral-200">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-xs font-bold text-neutral-700 mb-2 uppercase tracking-wider">
                        Score Range
                      </label>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          value={advancedFilters.minScore}
                          onChange={(e) => setAdvancedFilters({ ...advancedFilters, minScore: Number(e.target.value) })}
                          className="w-20 px-3 py-2 border border-neutral-200 rounded-lg text-sm"
                          min="0"
                          max="100"
                        />
                        <span className="text-neutral-400">to</span>
                        <input
                          type="number"
                          value={advancedFilters.maxScore}
                          onChange={(e) => setAdvancedFilters({ ...advancedFilters, maxScore: Number(e.target.value) })}
                          className="w-20 px-3 py-2 border border-neutral-200 rounded-lg text-sm"
                          min="0"
                          max="100"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-neutral-700 mb-2 uppercase tracking-wider">
                        Company Flags
                      </label>
                      <div className="space-y-1">
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={advancedFilters.flags.multinational}
                            onChange={(e) => setAdvancedFilters({
                              ...advancedFilters,
                              flags: { ...advancedFilters.flags, multinational: e.target.checked }
                            })}
                            className="rounded"
                          />
                          <span className="text-sm font-semibold text-neutral-700">Multinational</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={advancedFilters.flags.exporter}
                            onChange={(e) => setAdvancedFilters({
                              ...advancedFilters,
                              flags: { ...advancedFilters.flags, exporter: e.target.checked }
                            })}
                            className="rounded"
                          />
                          <span className="text-sm font-semibold text-neutral-700">Exporter</span>
                        </label>
                        <label className="flex items-center gap-2 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={advancedFilters.flags.audit}
                            onChange={(e) => setAdvancedFilters({
                              ...advancedFilters,
                              flags: { ...advancedFilters.flags, audit: e.target.checked }
                            })}
                            className="rounded"
                          />
                          <span className="text-sm font-semibold text-neutral-700">Under Audit</span>
                        </label>
                      </div>
                    </div>

                    <div>
                      <button
                        onClick={() => {
                          setAdvancedFilters({
                            minScore: 0,
                            maxScore: 100,
                            sectors: [],
                            cities: [],
                            flags: { multinational: false, exporter: false, audit: false },
                            status: [],
                          });
                          handleSearch(searchQuery);
                        }}
                        className="text-sm font-semibold text-neutral-600 hover:text-neutral-900"
                      >
                        Clear Filters
                      </button>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-8">
          <div className="grid grid-cols-12 gap-6">
            {/* Sidebar */}
            <div className="col-span-3 space-y-4">
              {/* Quick Suggestions */}
              <div className="bg-white rounded-xl p-4 border border-neutral-200">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-4 h-4 text-purple-600" strokeWidth={2.5} />
                  <div className="text-sm font-bold text-neutral-900">Quick Filters</div>
                </div>
                <div className="space-y-1">
                  {suggestions.map((sug, idx) => {
                    const Icon = sug.icon;
                    return (
                      <button
                        key={idx}
                        onClick={() => {
                          setSearchQuery(sug.query);
                          setAdvancedFilters({ ...advancedFilters, ...sug.filter });
                          handleSearch(sug.query);
                        }}
                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-neutral-50 transition-colors text-left group"
                      >
                        <Icon className="w-4 h-4 text-neutral-400 group-hover:text-blue-600" strokeWidth={2} />
                        <span className="text-sm text-neutral-700 group-hover:text-neutral-900 font-medium">
                          {sug.label}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Recent Searches */}
              {recentSearches.length > 0 && (
                <div className="bg-white rounded-xl p-4 border border-neutral-200">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <History className="w-4 h-4 text-neutral-500" strokeWidth={2.5} />
                      <div className="text-sm font-bold text-neutral-900">Recent</div>
                    </div>
                    <button
                      onClick={clearRecentSearches}
                      className="text-xs font-semibold text-neutral-500 hover:text-neutral-900"
                    >
                      Clear
                    </button>
                  </div>
                  <div className="space-y-1">
                    {recentSearches.map((query, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSearch(query)}
                        className="w-full flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-neutral-50 transition-colors text-left group"
                      >
                        <Clock className="w-3.5 h-3.5 text-neutral-400" strokeWidth={2} />
                        <span className="text-sm text-neutral-700 truncate">{query}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Saved Searches */}
              {savedSearches.length > 0 && (
                <div className="bg-white rounded-xl p-4 border border-neutral-200">
                  <div className="flex items-center gap-2 mb-3">
                    <Star className="w-4 h-4 text-amber-500" strokeWidth={2.5} />
                    <div className="text-sm font-bold text-neutral-900">Saved</div>
                  </div>
                  <div className="space-y-2">
                    {savedSearches.map((search) => (
                      <div
                        key={search.id}
                        className="flex items-center justify-between p-2 rounded-lg hover:bg-neutral-50 transition-colors group"
                      >
                        <button
                          onClick={() => loadSavedSearch(search)}
                          className="flex-1 text-left"
                        >
                          <div className="text-sm font-semibold text-neutral-900 truncate">
                            {search.query || 'Advanced Filter'}
                          </div>
                          <div className="text-xs text-neutral-500">
                            {search.resultCount} results
                          </div>
                        </button>
                        <button
                          onClick={() => deleteSavedSearch(search.id)}
                          className="opacity-0 group-hover:opacity-100 p-1 hover:bg-neutral-100 rounded"
                        >
                          <X className="w-3.5 h-3.5 text-neutral-500" strokeWidth={2} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Results */}
            <div className="col-span-9">
              {loading ? (
                <div className="flex items-center justify-center h-64">
                  <div className="w-8 h-8 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : results.length === 0 ? (
                <div className="bg-white rounded-xl p-12 text-center border border-neutral-200">
                  <Search className="w-16 h-16 text-neutral-300 mx-auto mb-4" strokeWidth={2} />
                  <p className="text-neutral-500 font-medium">No results found</p>
                  <p className="text-sm text-neutral-400 mt-2">Try adjusting your search or filters</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {results.slice(0, 50).map((lead, idx) => (
                    <motion.div
                      key={lead.lead_id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.02 }}
                      className="bg-white rounded-xl p-5 border border-neutral-200 hover:border-neutral-900 hover:shadow-xl transition-all cursor-pointer group"
                      onClick={() => onViewLead(lead.lead_id)}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <div className="font-bold text-neutral-900 text-lg group-hover:text-emerald-600 transition-colors" style={{ fontWeight: 700 }}>
                              {lead.company_name}
                            </div>
                            <div className={`px-2.5 py-1 rounded-lg text-xs font-bold ${
                              lead.best_score >= 60 ? 'bg-emerald-100 text-emerald-700' :
                              lead.best_score >= 30 ? 'bg-blue-100 text-blue-700' :
                              'bg-neutral-100 text-neutral-600'
                            }`}>
                              {Math.round(lead.best_score)}
                            </div>
                          </div>
                          <div className="flex items-center gap-4 text-sm text-neutral-600 mb-3">
                            {lead.sector && (
                              <span className="flex items-center gap-1.5">
                                <Briefcase className="w-4 h-4" strokeWidth={2} />
                                {lead.sector}
                              </span>
                            )}
                            {lead.city && (
                              <span className="flex items-center gap-1.5">
                                <MapPin className="w-4 h-4" strokeWidth={2} />
                                {lead.city}
                              </span>
                            )}
                            {lead.best_service && (
                              <span className="flex items-center gap-1.5">
                                <TrendingUp className="w-4 h-4" strokeWidth={2} />
                                {lead.best_service}
                              </span>
                            )}
                          </div>
                          <div className="flex gap-2">
                            {lead.is_multinational && (
                              <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs font-semibold border border-blue-200">
                                Multinational
                              </span>
                            )}
                            {lead.is_exporter && (
                              <span className="px-2 py-1 bg-emerald-50 text-emerald-700 rounded text-xs font-semibold border border-emerald-200">
                                Exporter
                              </span>
                            )}
                            {lead.under_audit && (
                              <span className="px-2 py-1 bg-amber-50 text-amber-700 rounded text-xs font-semibold border border-amber-200">
                                Under Audit
                              </span>
                            )}
                          </div>
                        </div>
                        <motion.button
                          className="flex items-center gap-2 px-4 py-2 bg-neutral-900 text-white rounded-lg font-semibold hover:bg-neutral-800"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          <Eye className="w-4 h-4" strokeWidth={2.5} />
                          View
                        </motion.button>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
