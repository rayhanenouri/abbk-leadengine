/**
 * Full Leads Database Management
 * Complete CRM-style lead management with advanced filters and bulk actions
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search, Filter, Download, Upload, RefreshCw, MoreVertical,
  ChevronDown, ChevronUp, Check, X, Edit3, Trash2, Mail,
  Phone, Globe, MapPin, Building2, Users, TrendingUp, Eye,
  CheckSquare, Square, ChevronLeft, ChevronRight, Menu
} from 'lucide-react';
import { getLeads, getRankedLeads } from '../services/api';

export default function Leads({ onViewLead, onLogout, onMenuClick }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLeads, setSelectedLeads] = useState(new Set());
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortField, setSortField] = useState('best_score');
  const [sortDirection, setSortDirection] = useState('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);
  const [trustFilter, setTrustFilter] = useState('all'); // Show all leads by default

  // Filters
  const [filters, setFilters] = useState({
    sector: '',
    city: '',
    country: '',
    status: '',
    minScore: 0,
    maxScore: 100,
    isMultinational: false,
    isExporter: false,
    underAudit: false,
    hideUnverified: false, // NEW: Filter out companies without websites
  });

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    setLoading(true);
    try {
      const data = await getLeads(0, 1000, 'created_at', 'desc');
      console.log('Leads page - raw data:', data);
      console.log('Leads page - data type:', typeof data, Array.isArray(data));
      console.log('Leads page - data length:', data?.length);

      if (!data || !Array.isArray(data) || data.length === 0) {
        console.warn('No leads data received or empty array');
        setLeads([]);
        setLoading(false);
        return;
      }

      // Calculate best_score from lead_scores if available
      const leadsWithScore = data.map(lead => {
        let bestScore = 0;
        if (lead.scores && lead.scores.length > 0) {
          bestScore = Math.max(...lead.scores.map(s => s.score || 0));
        }

        return {
          ...lead,
          lead_id: lead.id,
          best_score: bestScore,
          company_name: lead.company_name || 'Unknown Company',
          sector: lead.sector || 'Unknown',
          city: lead.city || 'Unknown',
        };
      });

      console.log('Processed leads:', leadsWithScore.slice(0, 2)); // Debug
      setLeads(leadsWithScore);
    } catch (err) {
      console.error('Failed to load leads:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const toggleSelectLead = (leadId) => {
    const newSelected = new Set(selectedLeads);
    if (newSelected.has(leadId)) {
      newSelected.delete(leadId);
    } else {
      newSelected.add(leadId);
    }
    setSelectedLeads(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedLeads.size === filteredLeads.length) {
      setSelectedLeads(new Set());
    } else {
      setSelectedLeads(new Set(filteredLeads.map(l => l.lead_id)));
    }
  };

  // Filter and sort logic
  const filteredLeads = leads
    .filter(lead => {
      const matchesSearch = lead.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           (lead.sector || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                           (lead.city || '').toLowerCase().includes(searchQuery.toLowerCase());

      const matchesSector = !filters.sector || lead.sector === filters.sector;
      const matchesCity = !filters.city || lead.city === filters.city;
      const matchesCountry = !filters.country || lead.country === filters.country;
      const matchesStatus = !filters.status || lead.status === filters.status;
      const matchesScore = lead.best_score >= filters.minScore && lead.best_score <= filters.maxScore;
      const matchesMultinational = !filters.isMultinational || lead.is_multinational;
      const matchesExporter = !filters.isExporter || lead.is_exporter;
      const matchesAudit = !filters.underAudit || lead.under_audit;
      const matchesTrust = trustFilter === 'all' || lead.trust_level === trustFilter; // NEW: Trust filter

      return matchesSearch && matchesSector && matchesCity && matchesCountry &&
             matchesStatus && matchesScore && matchesMultinational &&
             matchesExporter && matchesAudit && matchesTrust;
    })
    .sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

  // Pagination
  const totalPages = Math.ceil(filteredLeads.length / pageSize);
  const paginatedLeads = filteredLeads.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const uniqueSectors = [...new Set(leads.map(l => l.sector).filter(Boolean))];
  const uniqueCities = [...new Set(leads.map(l => l.city).filter(Boolean))];
  const uniqueCountries = [...new Set(leads.map(l => l.country).filter(Boolean))];

  // Business manager criteria for HOT LEADS
  const getScoreColor = (score) => {
    if (score >= 70) return 'text-red-600 bg-red-50'; // HOT LEAD
    if (score >= 60) return 'text-emerald-600 bg-emerald-50'; // WARM LEAD
    if (score >= 30) return 'text-blue-600 bg-blue-50'; // POTENTIAL
    return 'text-neutral-500 bg-neutral-50'; // RESEARCH
  };

  const getScoreLabel = (score) => {
    if (score >= 70) return 'HOT';
    if (score >= 60) return 'WARM';
    if (score >= 30) return 'POTENTIAL';
    return 'RESEARCH';
  };

  const SortIcon = ({ field }) => {
    if (sortField !== field) return <ChevronDown className="w-4 h-4 text-neutral-400" />;
    return sortDirection === 'asc' ?
      <ChevronUp className="w-4 h-4 text-neutral-900" /> :
      <ChevronDown className="w-4 h-4 text-neutral-900" />;
  };

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-neutral-900 mb-1" style={{
                fontWeight: 800,
                letterSpacing: '-0.04em',
              }}>
                All Leads
              </h1>
              <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                {filteredLeads.length} companies · {selectedLeads.size} selected
              </p>
            </div>

            <div className="flex items-center gap-2 md:gap-3">
              <motion.button
                onClick={() => setShowFilters(!showFilters)}
                className={`flex items-center gap-1 md:gap-2 px-2 md:px-4 py-1.5 md:py-2.5 rounded-lg md:rounded-xl border transition-all text-xs md:text-sm ${
                  showFilters
                    ? 'bg-neutral-900 text-white border-neutral-900'
                    : 'bg-white text-neutral-700 border-neutral-200 hover:bg-neutral-50'
                }`}
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontWeight: 600 }}
              >
                <Filter className="w-3 h-3 md:w-4 md:h-4" strokeWidth={2.5} />
                <span className="hidden sm:inline">Filters</span>
                {Object.values(filters).some(v => v && v !== 0 && v !== 100) && (
                  <span className="px-2 py-0.5 bg-blue-600 text-white rounded-full text-xs font-bold">
                    {Object.values(filters).filter(v => v && v !== 0 && v !== 100).length}
                  </span>
                )}
              </motion.button>

              <motion.button
                onClick={loadLeads}
                className="flex items-center gap-1 md:gap-2 px-2 md:px-4 py-1.5 md:py-2.5 text-neutral-700 hover:bg-neutral-100 rounded-lg md:rounded-xl transition-all border border-neutral-200 text-xs md:text-sm"
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontWeight: 600 }}
              >
                <RefreshCw className="w-3 h-3 md:w-4 md:h-4" strokeWidth={2.5} />
                <span className="hidden sm:inline">Refresh</span>
              </motion.button>

              <motion.button
                className="hidden md:flex items-center gap-2 px-4 py-2.5 text-neutral-700 hover:bg-neutral-100 rounded-xl transition-all border border-neutral-200"
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.98 }}
                style={{ fontSize: '14px', fontWeight: 600 }}
              >
                <Upload className="w-4 h-4" strokeWidth={2.5} />
                Import CSV
              </motion.button>

              <motion.button
                disabled={selectedLeads.size === 0}
                className={`hidden md:flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all ${
                  selectedLeads.size > 0
                    ? 'bg-emerald-600 text-white hover:bg-emerald-700'
                    : 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                }`}
                whileHover={selectedLeads.size > 0 ? { y: -1 } : {}}
                whileTap={selectedLeads.size > 0 ? { scale: 0.98 } : {}}
                style={{ fontSize: '14px', fontWeight: 600 }}
              >
                <Download className="w-4 h-4" strokeWidth={2.5} />
                Export ({selectedLeads.size})
              </motion.button>
            </div>
          </div>

          {/* Trust Level Filter Tabs */}
          <div className="flex items-center gap-2 mb-6">
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" strokeWidth={2.5} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
              placeholder="Search by company name, sector, or city..."
              className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
              style={{ fontSize: '15px', fontWeight: 500 }}
            />
          </div>
        </div>

        {/* Filters Panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              className="border-t border-neutral-200 overflow-hidden"
            >
              <div className="px-8 py-6 bg-neutral-50">
                <div className="grid grid-cols-4 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-2 uppercase tracking-wider">
                      Sector
                    </label>
                    <select
                      value={filters.sector}
                      onChange={(e) => setFilters({ ...filters, sector: e.target.value })}
                      className="w-full px-3 py-2 border border-neutral-200 rounded-lg bg-white text-sm focus:outline-none focus:border-neutral-900"
                    >
                      <option value="">All Sectors</option>
                      {uniqueSectors.map(s => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-2 uppercase tracking-wider">
                      City
                    </label>
                    <select
                      value={filters.city}
                      onChange={(e) => setFilters({ ...filters, city: e.target.value })}
                      className="w-full px-3 py-2 border border-neutral-200 rounded-lg bg-white text-sm focus:outline-none focus:border-neutral-900"
                    >
                      <option value="">All Cities</option>
                      {uniqueCities.map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-2 uppercase tracking-wider">
                      Status
                    </label>
                    <select
                      value={filters.status}
                      onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                      className="w-full px-3 py-2 border border-neutral-200 rounded-lg bg-white text-sm focus:outline-none focus:border-neutral-900"
                    >
                      <option value="">All Status</option>
                      <option value="new">New</option>
                      <option value="contacted">Contacted</option>
                      <option value="qualified">Qualified</option>
                      <option value="converted">Converted</option>
                      <option value="lost">Lost</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-neutral-700 mb-2 uppercase tracking-wider">
                      Score Range
                    </label>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        value={filters.minScore}
                        onChange={(e) => setFilters({ ...filters, minScore: Number(e.target.value) })}
                        min="0"
                        max="100"
                        className="w-20 px-3 py-2 border border-neutral-200 rounded-lg bg-white text-sm focus:outline-none focus:border-neutral-900"
                      />
                      <span className="text-neutral-400">to</span>
                      <input
                        type="number"
                        value={filters.maxScore}
                        onChange={(e) => setFilters({ ...filters, maxScore: Number(e.target.value) })}
                        min="0"
                        max="100"
                        className="w-20 px-3 py-2 border border-neutral-200 rounded-lg bg-white text-sm focus:outline-none focus:border-neutral-900"
                      />
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 mt-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.isMultinational}
                      onChange={(e) => setFilters({ ...filters, isMultinational: e.target.checked })}
                      className="w-4 h-4 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-900"
                    />
                    <span className="text-sm font-semibold text-neutral-700">Multinational Only</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.isExporter}
                      onChange={(e) => setFilters({ ...filters, isExporter: e.target.checked })}
                      className="w-4 h-4 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-900"
                    />
                    <span className="text-sm font-semibold text-neutral-700">Exporters Only</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.underAudit}
                      onChange={(e) => setFilters({ ...filters, underAudit: e.target.checked })}
                      className="w-4 h-4 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-900"
                    />
                    <span className="text-sm font-semibold text-neutral-700">Under Audit Only</span>
                  </label>

                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filters.hideUnverified}
                      onChange={(e) => setFilters({ ...filters, hideUnverified: e.target.checked })}
                      className="w-4 h-4 rounded border-neutral-300 text-neutral-900 focus:ring-neutral-900"
                    />
                    <span className="text-sm font-semibold text-neutral-700">Hide Unverified</span>
                  </label>

                  <button
                    onClick={() => setFilters({
                      sector: '',
                      city: '',
                      country: '',
                      status: '',
                      minScore: 0,
                      maxScore: 100,
                      isMultinational: false,
                      isExporter: false,
                      underAudit: false,
                      hideUnverified: false,
                    })}
                    className="ml-auto text-sm font-semibold text-neutral-600 hover:text-neutral-900"
                  >
                    Clear All Filters
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <div className="p-6">
          <div className="bg-white rounded-xl border border-neutral-200 overflow-x-auto">
            <table className="w-full" style={{ minWidth: '1800px' }}>
              <thead>
                <tr className="bg-neutral-50 border-b border-neutral-200">
                  <th className="px-4 py-3 text-left w-10 sticky left-0 bg-neutral-50 z-10">
                    <button onClick={toggleSelectAll} className="hover:bg-neutral-200 rounded p-1">
                      {selectedLeads.size === filteredLeads.length && filteredLeads.length > 0 ? (
                        <CheckSquare className="w-4 h-4 text-neutral-900" strokeWidth={2.5} />
                      ) : (
                        <Square className="w-4 h-4 text-neutral-400" strokeWidth={2.5} />
                      )}
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left sticky left-10 bg-neutral-50 z-10" style={{ minWidth: '220px' }}>
                    <button onClick={() => handleSort('company_name')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900">
                      Company <SortIcon field="company_name" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '160px' }}>
                    <button onClick={() => handleSort('sector')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900">
                      Industry <SortIcon field="sector" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '120px' }}>
                    <button onClick={() => handleSort('city')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900">
                      City <SortIcon field="city" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '100px' }}>
                    <button onClick={() => handleSort('country')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900">
                      Country <SortIcon field="country" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-center" style={{ minWidth: '90px' }}>
                    <button onClick={() => handleSort('employee_count')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900 mx-auto">
                      Size <SortIcon field="employee_count" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '180px' }}>
                    <button onClick={() => handleSort('best_service')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900">
                      Top Product <SortIcon field="best_service" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '110px' }}>
                    <button onClick={() => handleSort('status')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900">
                      Status <SortIcon field="status" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '140px' }}>
                    <span className="text-xs font-bold text-neutral-600 uppercase tracking-wider">Contact</span>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '120px' }}>
                    <span className="text-xs font-bold text-neutral-600 uppercase tracking-wider">Website</span>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '100px' }}>
                    <span className="text-xs font-bold text-neutral-600 uppercase tracking-wider">Signals</span>
                  </th>
                  <th className="px-4 py-3 text-left" style={{ minWidth: '120px' }}>
                    <button onClick={() => handleSort('created_at')} className="flex items-center gap-1 text-xs font-bold text-neutral-600 uppercase tracking-wider hover:text-neutral-900">
                      Added <SortIcon field="created_at" />
                    </button>
                  </th>
                  <th className="px-4 py-3 text-right sticky right-0 bg-neutral-50 z-10" style={{ minWidth: '100px' }}>
                    <span className="text-xs font-bold text-neutral-600 uppercase tracking-wider">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {loading ? (
                  <tr>
                    <td colSpan="14" className="px-6 py-20 text-center">
                      <div className="inline-block w-6 h-6 border-4 border-neutral-900 border-t-transparent rounded-full animate-spin mb-3" />
                      <p className="text-neutral-500 text-sm font-medium">Loading database...</p>
                    </td>
                  </tr>
                ) : paginatedLeads.length === 0 ? (
                  <tr>
                    <td colSpan="14" className="px-6 py-20 text-center">
                      <p className="text-neutral-500 text-sm font-medium">No leads found</p>
                    </td>
                  </tr>
                ) : (
                  paginatedLeads.map((lead, idx) => (
                    <motion.tr
                      key={lead.lead_id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: idx * 0.01 }}
                      className="hover:bg-neutral-50 group text-sm"
                    >
                      <td className="px-4 py-2.5 sticky left-0 bg-white group-hover:bg-neutral-50 z-10">
                        <button onClick={(e) => { e.stopPropagation(); toggleSelectLead(lead.lead_id); }} className="hover:bg-neutral-200 rounded p-1">
                          {selectedLeads.has(lead.lead_id) ? (
                            <CheckSquare className="w-4 h-4 text-neutral-900" strokeWidth={2.5} />
                          ) : (
                            <Square className="w-4 h-4 text-neutral-400 group-hover:text-neutral-600" strokeWidth={2.5} />
                          )}
                        </button>
                      </td>
                      <td className="px-4 py-2.5 sticky left-10 bg-white group-hover:bg-neutral-50 z-10">
                        <div className="flex items-center gap-2">
                          <div>
                            <div className="font-semibold text-neutral-900" style={{ fontSize: '13px', fontWeight: 600 }}>
                              {lead.company_name}
                            </div>
                            <div className="text-xs text-neutral-500">ID: {lead.lead_id}</div>
                          </div>
                          {/* Trust Level Badge */}
                          )}
                          {lead.trust_level === 'partial' && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-amber-100 text-amber-700 whitespace-nowrap" title="Partial data - Directory listing">
                              ⚠ Partial
                            </span>
                          )}
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="text-xs text-neutral-700 font-medium">{lead.sector || '—'}</span>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="text-xs text-neutral-900 font-medium">{lead.city || '—'}</span>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="text-xs text-neutral-700">{lead.country || 'Tunisia'}</span>
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        <span className="text-xs font-semibold text-neutral-900">{lead.employee_count || '—'}</span>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="text-xs text-neutral-700 font-medium">{lead.best_service || '—'}</span>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className={`inline-flex px-2 py-1 rounded text-xs font-bold ${
                          lead.status === 'converted' ? 'bg-green-100 text-green-700' :
                          lead.status === 'qualified' ? 'bg-emerald-100 text-emerald-700' :
                          lead.status === 'contacted' ? 'bg-purple-100 text-purple-700' :
                          lead.status === 'lost' ? 'bg-neutral-100 text-neutral-600' :
                          'bg-blue-100 text-blue-700'
                        }`}>
                          {(lead.status || 'new').toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-2.5">
                        {lead.scraped_data?.csv_import?.phone && (
                          <a href={`tel:${lead.scraped_data.csv_import.phone}`} className="text-xs text-blue-600 hover:underline flex items-center gap-1">
                            <Phone className="w-3 h-3" />
                            {lead.scraped_data.csv_import.phone}
                          </a>
                        )}
                        {lead.scraped_data?.csv_import?.email && (
                          <a href={`mailto:${lead.scraped_data.csv_import.email}`} className="text-xs text-blue-600 hover:underline flex items-center gap-1 mt-0.5">
                            <Mail className="w-3 h-3" />
                            {lead.scraped_data.csv_import.email}
                          </a>
                        )}
                      </td>
                      <td className="px-4 py-2.5">
                        {lead.website && (
                          <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-600 hover:underline flex items-center gap-1">
                            <Globe className="w-3 h-3" />
                            Link
                          </a>
                        )}
                      </td>
                      <td className="px-4 py-2.5">
                        <div className="flex flex-wrap gap-1">
                          {lead.is_multinational && <span className="w-2 h-2 rounded-full bg-blue-600" title="Multinational" />}
                          {lead.is_exporter && <span className="w-2 h-2 rounded-full bg-emerald-600" title="Exporter" />}
                          {lead.under_audit && <span className="w-2 h-2 rounded-full bg-amber-600" title="Under Audit" />}
                        </div>
                      </td>
                      <td className="px-4 py-2.5">
                        <span className="text-xs text-neutral-500">
                          {lead.created_at ? new Date(lead.created_at).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }) : '—'}
                        </span>
                      </td>
                      <td className="px-4 py-2.5 text-right sticky right-0 bg-white group-hover:bg-neutral-50 z-10">
                        <motion.button
                          onClick={() => onViewLead(lead.lead_id)}
                          className="px-3 py-1.5 bg-neutral-900 text-white rounded-lg text-xs font-semibold hover:bg-neutral-800"
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                        >
                          View
                        </motion.button>
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between mt-6">
              <div className="text-sm text-neutral-600">
                Showing {((currentPage - 1) * pageSize) + 1} to {Math.min(currentPage * pageSize, filteredLeads.length)} of {filteredLeads.length} leads
              </div>
              <div className="flex items-center gap-2">
                <motion.button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className={`p-2 rounded-lg border transition-colors ${
                    currentPage === 1
                      ? 'border-neutral-200 text-neutral-400 cursor-not-allowed'
                      : 'border-neutral-200 text-neutral-700 hover:bg-neutral-100'
                  }`}
                  whileHover={currentPage > 1 ? { scale: 1.05 } : {}}
                  whileTap={currentPage > 1 ? { scale: 0.95 } : {}}
                >
                  <ChevronLeft className="w-5 h-5" strokeWidth={2.5} />
                </motion.button>

                {[...Array(totalPages)].map((_, i) => {
                  const page = i + 1;
                  if (
                    page === 1 ||
                    page === totalPages ||
                    (page >= currentPage - 1 && page <= currentPage + 1)
                  ) {
                    return (
                      <motion.button
                        key={page}
                        onClick={() => setCurrentPage(page)}
                        className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
                          currentPage === page
                            ? 'bg-neutral-900 text-white'
                            : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                        }`}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        style={{ fontSize: '14px' }}
                      >
                        {page}
                      </motion.button>
                    );
                  } else if (page === currentPage - 2 || page === currentPage + 2) {
                    return <span key={page} className="px-2 text-neutral-400">...</span>;
                  }
                  return null;
                })}

                <motion.button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className={`p-2 rounded-lg border transition-colors ${
                    currentPage === totalPages
                      ? 'border-neutral-200 text-neutral-400 cursor-not-allowed'
                      : 'border-neutral-200 text-neutral-700 hover:bg-neutral-100'
                  }`}
                  whileHover={currentPage < totalPages ? { scale: 1.05 } : {}}
                  whileTap={currentPage < totalPages ? { scale: 0.95 } : {}}
                >
                  <ChevronRight className="w-5 h-5" strokeWidth={2.5} />
                </motion.button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
