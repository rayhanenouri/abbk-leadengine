/**
 * Export Reports
 * Generate and download business reports
 */

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FileText, Download, Calendar, BarChart3, TrendingUp,
  Users, Target, Zap, Globe, CheckCircle2, Clock,
  FileSpreadsheet, File, Filter, Settings, Play
} from 'lucide-react';
import { getRankedLeads } from '../services/api';

export default function ExportReports() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(null);
  const [recentExports, setRecentExports] = useState([]);

  useEffect(() => {
    loadData();
    loadRecentExports();
  }, []);

  const loadData = async () => {
    try {
      const data = await getRankedLeads(10000, 0, {});
      setLeads(data);
    } catch (err) {
      console.error('Failed to load data:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadRecentExports = () => {
    const recent = JSON.parse(localStorage.getItem('recentExports') || '[]');
    setRecentExports(recent.slice(0, 5));
  };

  const handleExport = (reportType, format) => {
    setGenerating(reportType);

    setTimeout(() => {
      const timestamp = new Date();
      const filename = `${reportType}_${timestamp.toISOString().split('T')[0]}.${format}`;

      const newExport = {
        id: Date.now(),
        reportType,
        format,
        filename,
        recordCount: leads.length,
        timestamp: timestamp.toISOString(),
      };

      const updated = [newExport, ...recentExports].slice(0, 10);
      setRecentExports(updated);
      localStorage.setItem('recentExports', JSON.stringify(updated));

      setGenerating(null);

      // Simulate download
      alert(`Export complete: ${filename}`);
    }, 2000);
  };

  const reportTemplates = [
    {
      id: 'all_leads',
      name: 'All Leads Report',
      description: 'Complete database export with all fields',
      icon: Users,
      color: 'blue',
      records: leads.length,
      fields: 'Company, Sector, City, Score, Status, Flags',
      formats: ['csv', 'xlsx', 'pdf'],
    },
    {
      id: 'high_priority',
      name: 'High Priority Leads',
      description: 'Leads with score 60+ requiring immediate action',
      icon: TrendingUp,
      color: 'emerald',
      records: leads.filter(l => l.best_score >= 60).length,
      fields: 'Company, Score, Best Product, Signals, Contact',
      formats: ['csv', 'xlsx', 'pdf'],
    },
    {
      id: 'multinational',
      name: 'Multinational Companies',
      description: 'International companies with highest conversion rate',
      icon: Globe,
      color: 'indigo',
      records: leads.filter(l => l.is_multinational).length,
      fields: 'Company, Country, Score, Top Product, Employees',
      formats: ['csv', 'xlsx'],
    },
    {
      id: 'pipeline',
      name: 'Sales Pipeline Status',
      description: 'Current status of all leads in pipeline',
      icon: Target,
      color: 'purple',
      records: leads.filter(l => !['converted', 'lost'].includes(l.status || 'new')).length,
      fields: 'Company, Status, Score, Last Contact, Next Action',
      formats: ['csv', 'xlsx', 'pdf'],
    },
    {
      id: 'signals',
      name: 'Active Signals Report',
      description: 'All detected buying signals by company',
      icon: Zap,
      color: 'amber',
      records: leads.filter(l => l.is_multinational || l.is_exporter || l.under_audit).length,
      fields: 'Company, Signal Type, Detection Date, Score Impact',
      formats: ['csv', 'xlsx'],
    },
    {
      id: 'scores',
      name: 'Score Analysis Report',
      description: 'Detailed scoring breakdown by company and product',
      icon: BarChart3,
      color: 'pink',
      records: leads.length,
      fields: 'Company, Product, Score, Signals Detected, Priority',
      formats: ['csv', 'xlsx', 'pdf'],
    },
    {
      id: 'converted',
      name: 'Converted Leads',
      description: 'Successfully converted customers',
      icon: CheckCircle2,
      color: 'green',
      records: leads.filter(l => l.status === 'converted').length,
      fields: 'Company, Product, Conversion Date, Score, Deal Value',
      formats: ['csv', 'xlsx'],
    },
    {
      id: 'contacted',
      name: 'Recently Contacted',
      description: 'Leads contacted in last 30 days',
      icon: Clock,
      color: 'cyan',
      records: leads.filter(l => l.status === 'contacted' || l.status === 'qualified').length,
      fields: 'Company, Contact Date, Status, Follow-up Date',
      formats: ['csv', 'xlsx'],
    },
  ];

  const stats = [
    { label: 'Total Leads', value: leads.length, icon: Users, color: 'blue' },
    { label: 'High Priority', value: leads.filter(l => l.best_score >= 60).length, icon: TrendingUp, color: 'emerald' },
    { label: 'Reports Available', value: reportTemplates.length, icon: FileText, color: 'purple' },
    { label: 'Recent Exports', value: recentExports.length, icon: Download, color: 'amber' },
  ];

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getFormatIcon = (format) => {
    switch (format) {
      case 'xlsx':
        return FileSpreadsheet;
      case 'pdf':
        return File;
      case 'csv':
      default:
        return FileText;
    }
  };

  return (
    <div className="h-screen flex flex-col bg-neutral-50">
      {/* Header */}
      <div className="bg-white border-b border-neutral-200">
        <div className="px-8 py-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center">
                <FileText className="w-6 h-6 text-green-600" strokeWidth={2.5} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-neutral-900 mb-0.5" style={{
                  fontWeight: 800,
                  letterSpacing: '-0.04em',
                }}>
                  Export Reports
                </h1>
                <p className="text-sm text-neutral-500" style={{ fontWeight: 500 }}>
                  Generate and download business intelligence reports
                </p>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-4 gap-4">
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
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-8">
          <div className="grid grid-cols-12 gap-6">
            {/* Report Templates */}
            <div className="col-span-8 space-y-6">
              <div>
                <h2 className="text-lg font-bold text-neutral-900 mb-4" style={{ fontWeight: 700 }}>
                  Available Reports
                </h2>
                <div className="grid grid-cols-2 gap-4">
                  {reportTemplates.map((report, idx) => {
                    const Icon = report.icon;
                    const isGenerating = generating === report.id;

                    return (
                      <motion.div
                        key={report.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="bg-white rounded-2xl p-6 border-2 border-neutral-200 hover:border-neutral-900 hover:shadow-xl transition-all"
                      >
                        <div className="flex items-start gap-4 mb-4">
                          <div className={`w-14 h-14 rounded-xl bg-${report.color}-100 flex items-center justify-center border-2 border-${report.color}-200`}>
                            <Icon className={`w-7 h-7 text-${report.color}-600`} strokeWidth={2.5} />
                          </div>
                          <div className="flex-1">
                            <div className="font-bold text-neutral-900 mb-1" style={{ fontSize: '16px', fontWeight: 700 }}>
                              {report.name}
                            </div>
                            <div className="text-sm text-neutral-600" style={{ fontWeight: 500 }}>
                              {report.description}
                            </div>
                          </div>
                        </div>

                        <div className="space-y-2 mb-4 pb-4 border-b border-neutral-100">
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-neutral-600 font-medium">Records</span>
                            <span className="font-bold text-neutral-900">{report.records}</span>
                          </div>
                          <div className="flex items-center justify-between text-sm">
                            <span className="text-neutral-600 font-medium">Fields</span>
                            <span className="text-xs text-neutral-700 text-right">{report.fields}</span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {report.formats.map(format => {
                            const FormatIcon = getFormatIcon(format);
                            return (
                              <motion.button
                                key={format}
                                onClick={() => handleExport(report.id, format)}
                                disabled={isGenerating}
                                className={`flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg font-semibold transition-all ${
                                  isGenerating
                                    ? 'bg-neutral-200 text-neutral-400 cursor-not-allowed'
                                    : 'bg-neutral-900 text-white hover:bg-neutral-800'
                                }`}
                                whileHover={!isGenerating ? { scale: 1.05 } : {}}
                                whileTap={!isGenerating ? { scale: 0.95 } : {}}
                                style={{ fontSize: '13px' }}
                              >
                                {isGenerating ? (
                                  <>
                                    <Download className="w-4 h-4 animate-bounce" strokeWidth={2.5} />
                                    Generating...
                                  </>
                                ) : (
                                  <>
                                    <FormatIcon className="w-4 h-4" strokeWidth={2.5} />
                                    {format.toUpperCase()}
                                  </>
                                )}
                              </motion.button>
                            );
                          })}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Sidebar */}
            <div className="col-span-4 space-y-4">
              {/* Custom Report Builder */}
              <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl p-6 text-white">
                <div className="flex items-center gap-3 mb-4">
                  <Settings className="w-6 h-6" strokeWidth={2.5} />
                  <div className="text-lg font-bold" style={{ fontWeight: 700 }}>
                    Custom Report
                  </div>
                </div>
                <p className="text-purple-100 mb-4 text-sm">
                  Build your own report with custom fields and filters
                </p>
                <motion.button
                  className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white text-purple-600 rounded-xl font-bold hover:bg-purple-50 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  style={{ fontSize: '14px' }}
                >
                  <Play className="w-4 h-4" strokeWidth={2.5} />
                  Build Custom Report
                </motion.button>
              </div>

              {/* Recent Exports */}
              {recentExports.length > 0 && (
                <div className="bg-white rounded-2xl p-6 border border-neutral-200">
                  <div className="flex items-center gap-2 mb-4">
                    <Clock className="w-5 h-5 text-neutral-500" strokeWidth={2.5} />
                    <div className="text-sm font-bold text-neutral-900">Recent Exports</div>
                  </div>
                  <div className="space-y-3">
                    {recentExports.map((exp) => {
                      const FormatIcon = getFormatIcon(exp.format);
                      return (
                        <div key={exp.id} className="flex items-start gap-3 p-3 bg-neutral-50 rounded-lg hover:bg-neutral-100 transition-colors cursor-pointer">
                          <div className="w-10 h-10 rounded-lg bg-neutral-200 flex items-center justify-center flex-shrink-0">
                            <FormatIcon className="w-5 h-5 text-neutral-600" strokeWidth={2} />
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="text-sm font-semibold text-neutral-900 truncate">
                              {exp.filename}
                            </div>
                            <div className="text-xs text-neutral-500">
                              {exp.recordCount} records • {formatTimestamp(exp.timestamp)}
                            </div>
                          </div>
                          <motion.button
                            className="p-1.5 hover:bg-neutral-200 rounded-lg"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <Download className="w-4 h-4 text-neutral-600" strokeWidth={2} />
                          </motion.button>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Quick Tips */}
              <div className="bg-blue-50 rounded-xl p-6 border border-blue-200">
                <div className="text-sm font-bold text-blue-900 mb-3">Export Tips</div>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600">•</span>
                    <span>CSV for data analysis in Excel</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600">•</span>
                    <span>XLSX for formatted spreadsheets</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-blue-600">•</span>
                    <span>PDF for sharing with stakeholders</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
