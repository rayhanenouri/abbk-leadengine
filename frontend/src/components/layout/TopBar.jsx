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
    <div className="h-16 bg-white border-b border-neutral-200 flex items-center justify-between px-6">
      {/* Left: Title */}
      <div>
        <h1 className="text-lg font-semibold text-neutral-900">{title}</h1>
        {subtitle && (
          <p className="text-sm text-neutral-500">{subtitle}</p>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearch}
            placeholder="Search leads..."
            className="pl-10 pr-4 py-2 w-80 bg-neutral-50 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
          />
        </div>

        {/* Export */}
        {showExport && (
          <>
            <motion.button
              onClick={() => onExport('csv')}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-neutral-200 text-neutral-700 rounded-lg text-sm font-medium hover:bg-neutral-50 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <FileDown className="w-4 h-4" />
              CSV
            </motion.button>
            <motion.button
              onClick={() => onExport('excel')}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-neutral-200 text-neutral-700 rounded-lg text-sm font-medium hover:bg-neutral-50 transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <FileDown className="w-4 h-4" />
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
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Plus className="w-4 h-4" />
          Add Lead
        </motion.button>
      </div>
    </div>
  );
};

export default TopBar;
