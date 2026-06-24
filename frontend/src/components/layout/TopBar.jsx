/**
 * Clean TopBar with Search and Actions
 * Minimal, professional design
 */

import { motion } from 'framer-motion';
import { Search, Bell, FileDown, Plus } from 'lucide-react';
import { useState } from 'react';

const TopBar = ({
  title,
  subtitle,
  onSearch,
  showExport = false,
  onExport,
  unreadCount = 0,
  onNotificationClick
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    if (onSearch) {
      onSearch(value);
    }
  };

  return (
    <div className="h-16 bg-white border-b border-neutral-200 flex items-center justify-between px-8">
      {/* Left: Title */}
      <div>
        <h1 className="text-xl font-bold text-neutral-900 tracking-tight" style={{
          fontWeight: 700,
          letterSpacing: '-0.02em',
        }}>
          {title}
        </h1>
        {subtitle && (
          <p className="text-sm text-neutral-500 mt-0.5" style={{
            fontWeight: 500,
          }}>
            {subtitle}
          </p>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative group">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400 group-hover:text-neutral-600 transition-colors" strokeWidth={2.5} />
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearch}
            placeholder="Search leads..."
            className="pl-11 pr-4 py-2.5 w-96 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
            style={{
              fontSize: '14px',
              fontWeight: 500,
            }}
          />
        </div>

        {/* Export */}
        {showExport && (
          <>
            <motion.button
              onClick={() => onExport('csv')}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-neutral-200 text-neutral-700 rounded-xl hover:bg-neutral-50 hover:border-neutral-300 transition-all"
              style={{
                fontSize: '14px',
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.98 }}
            >
              <FileDown className="w-4 h-4" strokeWidth={2.5} />
              CSV
            </motion.button>
            <motion.button
              onClick={() => onExport('excel')}
              className="flex items-center gap-2 px-4 py-2.5 bg-white border border-neutral-200 text-neutral-700 rounded-xl hover:bg-neutral-50 hover:border-neutral-300 transition-all"
              style={{
                fontSize: '14px',
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.98 }}
            >
              <FileDown className="w-4 h-4" strokeWidth={2.5} />
              Excel
            </motion.button>
          </>
        )}

        {/* Notifications */}
        <motion.button
          onClick={onNotificationClick}
          className="relative p-2 hover:bg-neutral-50 rounded-lg transition-colors"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Bell className="w-5 h-5 text-neutral-600" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-primary-600 rounded-full"></span>
          )}
        </motion.button>

        {/* Add Lead Button */}
        <motion.button
          className="flex items-center gap-2 px-5 py-2.5 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 shadow-lg shadow-neutral-900/20 hover:shadow-xl transition-all relative overflow-hidden group"
          style={{
            fontSize: '14px',
            fontWeight: 600,
            letterSpacing: '-0.01em',
          }}
          whileHover={{ y: -1 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
          <Plus className="w-4 h-4" strokeWidth={2.5} />
          Add Lead
        </motion.button>
      </div>
    </div>
  );
};

export default TopBar;
