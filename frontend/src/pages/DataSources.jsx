/**
 * Data Sources - Scraping & Enrichment Dashboard
 * Monitor all data collection sources
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Database, Globe, Briefcase, Newspaper, Award, Users,
  RefreshCw, CheckCircle2, XCircle, Clock, AlertCircle,
  TrendingUp, ExternalLink, Play, Pause, Settings,
  BarChart3, Zap, Calendar, DollarSign, FileText
} from 'lucide-react';

export default function DataSources() {
  const [sources, setSources] = useState([]);
  const [selectedTab, setSelectedTab] = useState('all');
  const [running, setRunning] = useState({});

  useEffect(() => {
    loadSources();
  }, []);

  const loadSources = () => {
    const allSources = [
      // Business Directories
      {
        id: 'annuaire-tn',
        name: 'Annuaire.tn',
        type: 'directory',
        icon: Database,
        color: 'blue',
        url: 'https://annuaire.tn',
        status: 'active',
        lastRun: '2 hours ago',
        nextRun: 'In 22 hours',
        leadsFound: 45,
        frequency: 'Daily',
        spider: 'DirectoriesSpider',
        cost: 'Free',
      },
      {
        id: 'pagesjaunes',
        name: 'PagesJaunes.tn',
        type: 'directory',
        icon: Database,
        color: 'blue',
        url: 'https://pagesjaunes.tn',
        status: 'active',
        lastRun: '3 hours ago',
        nextRun: 'In 21 hours',
        leadsFound: 38,
        frequency: 'Daily',
        spider: 'DirectoriesSpider',
        cost: 'Free',
      },
      {
        id: 'kompass',
        name: 'Kompass Tunisia',
        type: 'directory',
        icon: Database,
        color: 'blue',
        url: 'https://tn.kompass.com',
        status: 'inactive',
        lastRun: '7 days ago',
        nextRun: 'Paused',
        leadsFound: 28,
        frequency: 'Daily',
        spider: 'DirectoriesSpider',
        cost: 'Free',
      },

      // Job Boards
      {
        id: 'emploi-tn',
        name: 'Emploi.tn',
        type: 'jobs',
        icon: Briefcase,
        color: 'emerald',
        url: 'https://emploi.tn',
        status: 'active',
        lastRun: '1 hour ago',
        nextRun: 'In 5 hours',
        leadsFound: 67,
        frequency: '6 hours',
        spider: 'JobsSpider',
        cost: 'Free',
      },
      {
        id: 'keejob',
        name: 'Keejob.com',
        type: 'jobs',
        icon: Briefcase,
        color: 'emerald',
        url: 'https://keejob.com',
        status: 'active',
        lastRun: '2 hours ago',
        nextRun: 'In 4 hours',
        leadsFound: 54,
        frequency: '6 hours',
        spider: 'JobsSpider',
        cost: 'Free',
      },

      // News Sources
      {
        id: 'businessnews',
        name: 'BusinessNews.tn',
        type: 'news',
        icon: Newspaper,
        color: 'purple',
        url: 'https://businessnews.com.tn',
        status: 'active',
        lastRun: '30 min ago',
        nextRun: 'In 30 min',
        leadsFound: 23,
        frequency: 'Hourly',
        spider: 'NewsSpider',
        cost: 'Free',
      },
      {
        id: 'managers',
        name: 'Managers.tn',
        type: 'news',
        icon: Newspaper,
        color: 'purple',
        url: 'https://managers.com.tn',
        status: 'active',
        lastRun: '45 min ago',
        nextRun: 'In 15 min',
        leadsFound: 18,
        frequency: 'Hourly',
        spider: 'NewsSpider',
        cost: 'Free',
      },
      {
        id: 'tekiano',
        name: 'Tekiano.com',
        type: 'news',
        icon: Newspaper,
        color: 'purple',
        url: 'https://tekiano.com',
        status: 'active',
        lastRun: '1 hour ago',
        nextRun: 'Now',
        leadsFound: 15,
        frequency: 'Hourly',
        spider: 'NewsSpider',
        cost: 'Free',
      },

      // LinkedIn (Apify)
      {
        id: 'linkedin',
        name: 'LinkedIn via Apify',
        type: 'social',
        icon: Users,
        color: 'indigo',
        url: 'https://linkedin.com',
        status: 'pending',
        lastRun: 'Never',
        nextRun: 'API Key Required',
        leadsFound: 0,
        frequency: 'Daily',
        spider: 'ApifyLinkedIn',
        cost: '$2-5 per run',
      },

      // Training Centers
      {
        id: 'iset',
        name: 'ISET Tunisia',
        type: 'training',
        icon: Award,
        color: 'amber',
        url: 'https://iset.tn',
        status: 'inactive',
        lastRun: '5 days ago',
        nextRun: 'Paused',
        leadsFound: 12,
        frequency: 'Weekly',
        spider: 'TrainingSpider',
        cost: 'Free',
      },

      // Funders
      {
        id: 'worldbank',
        name: 'World Bank Projects',
        type: 'funding',
        icon: DollarSign,
        color: 'green',
        url: 'https://worldbank.org',
        status: 'inactive',
        lastRun: '10 days ago',
        nextRun: 'Paused',
        leadsFound: 8,
        frequency: 'Weekly',
        spider: 'FundersSpider',
        cost: 'Free',
      },
      {
        id: 'afd',
        name: 'AFD Tunisia',
        type: 'funding',
        icon: DollarSign,
        color: 'green',
        url: 'https://afd.fr',
        status: 'inactive',
        lastRun: '10 days ago',
        nextRun: 'Paused',
        leadsFound: 5,
        frequency: 'Weekly',
        spider: 'FundersSpider',
        cost: 'Free',
      },

      // Tenders
      {
        id: 'tuneps',
        name: 'TUNEPS',
        type: 'tenders',
        icon: FileText,
        color: 'orange',
        url: 'https://tuneps.tn',
        status: 'inactive',
        lastRun: '12 days ago',
        nextRun: 'Paused',
        leadsFound: 6,
        frequency: 'Weekly',
        spider: 'TendersSpider',
        cost: 'Free',
      },

      // Events
      {
        id: 'events',
        name: 'Engineering Events',
        type: 'events',
        icon: Calendar,
        color: 'pink',
        url: 'Multiple sources',
        status: 'inactive',
        lastRun: '15 days ago',
        nextRun: 'Paused',
        leadsFound: 4,
        frequency: 'Weekly',
        spider: 'EventsSpider',
        cost: 'Free',
      },
    ];

    setSources(allSources);
  };

  const handleToggleSource = (sourceId) => {
    setRunning({ ...running, [sourceId]: true });
    setTimeout(() => {
      setRunning({ ...running, [sourceId]: false });
      setSources(sources.map(s =>
        s.id === sourceId ? { ...s, status: s.status === 'active' ? 'inactive' : 'active' } : s
      ));
    }, 2000);
  };

  const types = [
    { id: 'all', label: 'All Sources', count: sources.length },
    { id: 'directory', label: 'Directories', count: sources.filter(s => s.type === 'directory').length },
    { id: 'jobs', label: 'Job Boards', count: sources.filter(s => s.type === 'jobs').length },
    { id: 'news', label: 'News', count: sources.filter(s => s.type === 'news').length },
    { id: 'social', label: 'Social', count: sources.filter(s => s.type === 'social').length },
    { id: 'training', label: 'Training', count: sources.filter(s => s.type === 'training').length },
    { id: 'funding', label: 'Funding', count: sources.filter(s => s.type === 'funding').length },
    { id: 'tenders', label: 'Tenders', count: sources.filter(s => s.type === 'tenders').length },
    { id: 'events', label: 'Events', count: sources.filter(s => s.type === 'events').length },
  ];

  const filteredSources = selectedTab === 'all'
    ? sources
    : sources.filter(s => s.type === selectedTab);

  const activeCount = sources.filter(s => s.status === 'active').length;
  const totalLeads = sources.reduce((sum, s) => sum + s.leadsFound, 0);
  const pendingCount = sources.filter(s => s.status === 'pending').length;

  const stats = [
    { label: 'Total Sources', value: sources.length, icon: Database, color: 'blue' },
    { label: 'Active', value: activeCount, icon: CheckCircle2, color: 'emerald' },
    { label: 'Total Leads Found', value: totalLeads, icon: TrendingUp, color: 'purple' },
    { label: 'Pending Setup', value: pendingCount, icon: AlertCircle, color: 'amber' },
  ];

  const getStatusConfig = (status) => {
    switch (status) {
      case 'active':
        return { icon: CheckCircle2, color: 'emerald', label: 'Active', bg: 'bg-emerald-100', text: 'text-emerald-700', border: 'border-emerald-200' };
      case 'inactive':
        return { icon: Pause, color: 'neutral', label: 'Paused', bg: 'bg-neutral-100', text: 'text-neutral-600', border: 'border-neutral-200' };
      case 'pending':
        return { icon: AlertCircle, color: 'amber', label: 'Setup Required', bg: 'bg-amber-100', text: 'text-amber-700', border: 'border-amber-200' };
      case 'error':
        return { icon: XCircle, color: 'red', label: 'Error', bg: 'bg-red-100', text: 'text-red-700', border: 'border-red-200' };
      default:
        return { icon: Clock, color: 'neutral', label: 'Unknown', bg: 'bg-neutral-100', text: 'text-neutral-600', border: 'border-neutral-200' };
    }
  };

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-indigo-100 flex items-center justify-center">
                <Database className="w-6 h-6 text-indigo-600" strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-neutral-900 mb-0.5" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  Data Sources
                </h1>
                <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                  Monitor and manage all data collection sources
                </p>
              </div>
            </div>

            <motion.button
              onClick={loadSources}
              className="flex items-center gap-2 px-4 py-2.5 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 transition-colors"
              whileHover={{ y: -1, rotate: 180 }}
              whileTap={{ scale: 0.98 }}
              style={{ fontSize: '14px', fontWeight: 600 }}
            >
              <RefreshCw className="w-4 h-4" strokeWidth={2.5} />
              Refresh Status
            </motion.button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4 mb-6">
            {stats.map((stat, idx) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-neutral-50 rounded-xl p-4 border border-neutral-200"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-${stat.color}-100 flex items-center justify-center`}>
                      <Icon className={`w-5 h-5 text-${stat.color}-600`} strokeWidth={2.5} />
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800, letterSpacing: '-0.03em' }}>
                        {stat.value}
                      </div>
                      <div className="text-xs text-neutral-600 font-semibold">{stat.label}</div>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {types.map(type => (
              <button
                key={type.id}
                onClick={() => setSelectedTab(type.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold whitespace-nowrap transition-all ${
                  selectedTab === type.id
                    ? 'bg-neutral-900 text-white'
                    : 'bg-white text-neutral-700 hover:bg-neutral-100 border border-neutral-200'
                }`}
              >
                {type.label}
                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                  selectedTab === type.id
                    ? 'bg-white/20 text-white'
                    : 'bg-neutral-100 text-neutral-600'
                }`}>
                  {type.count}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Sources Grid */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-8">
          <div className="grid grid-cols-2 gap-6">
            {filteredSources.map((source, idx) => {
              const Icon = source.icon;
              const statusConfig = getStatusConfig(source.status);
              const StatusIcon = statusConfig.icon;
              const isRunning = running[source.id];

              return (
                <motion.div
                  key={source.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-white rounded-2xl p-6 border-2 border-neutral-200 hover:border-neutral-900 hover:shadow-xl transition-all"
                >
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-14 h-14 rounded-xl bg-${source.color}-100 flex items-center justify-center border-2 border-${source.color}-200`}>
                        <Icon className={`w-7 h-7 text-${source.color}-600`} strokeWidth={2.5} />
                      </div>
                      <div>
                        <div className="font-bold text-neutral-900 mb-1" style={{ fontSize: '16px', fontWeight: 700 }}>
                          {source.name}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`inline-flex px-2.5 py-1 rounded-lg text-xs font-bold ${statusConfig.bg} ${statusConfig.text} border ${statusConfig.border}`}>
                            <StatusIcon className="w-3 h-3 mr-1" strokeWidth={2.5} />
                            {statusConfig.label}
                          </span>
                          <span className="text-xs text-neutral-500 font-medium">{source.spider}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-xs text-neutral-500 mb-1 font-semibold">Leads Found</div>
                      <div className="text-2xl font-bold text-neutral-900" style={{ fontWeight: 800 }}>
                        {source.leadsFound}
                      </div>
                    </div>
                    <div className="p-3 bg-neutral-50 rounded-lg">
                      <div className="text-xs text-neutral-500 mb-1 font-semibold">Frequency</div>
                      <div className="text-lg font-bold text-neutral-900" style={{ fontWeight: 700 }}>
                        {source.frequency}
                      </div>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="space-y-2 mb-4 pb-4 border-b border-neutral-100">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-neutral-600 font-medium">Last Run</span>
                      <span className="text-neutral-900 font-semibold">{source.lastRun}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-neutral-600 font-medium">Next Run</span>
                      <span className="text-neutral-900 font-semibold">{source.nextRun}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-neutral-600 font-medium">Cost</span>
                      <span className="text-neutral-900 font-semibold">{source.cost}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2">
                    <motion.button
                      onClick={() => handleToggleSource(source.id)}
                      disabled={isRunning || source.status === 'pending'}
                      className={`flex-1 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg font-semibold transition-all ${
                        isRunning
                          ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                          : source.status === 'active'
                          ? 'bg-amber-100 text-amber-700 hover:bg-amber-200 border border-amber-200'
                          : source.status === 'pending'
                          ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed border border-neutral-200'
                          : 'bg-emerald-100 text-emerald-700 hover:bg-emerald-200 border border-emerald-200'
                      }`}
                      whileHover={!isRunning && source.status !== 'pending' ? { scale: 1.02 } : {}}
                      whileTap={!isRunning && source.status !== 'pending' ? { scale: 0.98 } : {}}
                      style={{ fontSize: '14px' }}
                    >
                      {isRunning ? (
                        <>
                          <RefreshCw className="w-4 h-4 animate-spin" strokeWidth={2.5} />
                          Running...
                        </>
                      ) : source.status === 'active' ? (
                        <>
                          <Pause className="w-4 h-4" strokeWidth={2.5} />
                          Pause
                        </>
                      ) : source.status === 'pending' ? (
                        <>
                          <Settings className="w-4 h-4" strokeWidth={2.5} />
                          Setup Required
                        </>
                      ) : (
                        <>
                          <Play className="w-4 h-4" strokeWidth={2.5} />
                          Activate
                        </>
                      )}
                    </motion.button>

                    <motion.a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2.5 hover:bg-neutral-100 rounded-lg transition-colors border border-neutral-200"
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                    >
                      <ExternalLink className="w-4 h-4 text-neutral-600" strokeWidth={2.5} />
                    </motion.a>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
