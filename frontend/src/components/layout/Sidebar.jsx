/**
 * Professional Sidebar Navigation
 * Clean B2B SaaS navigation with all features
 * Mobile responsive: hidden by default on mobile, toggled by hamburger
 */

import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Users,
  BarChart3,
  Target,
  TrendingUp,
  LogOut,
  Bell,
  Search,
  UserCircle,
  Zap,
  Phone,
  FileText,
  Database,
  Calendar,
  X
} from 'lucide-react';

const Sidebar = ({ currentView, onViewChange, onLogout, unreadCount = 0, user, isOpen, onClose }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'leads', label: 'Leads', icon: Users, badge: unreadCount },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'pipeline', label: 'Sales Pipeline', icon: TrendingUp },
    { id: 'activities', label: 'Activities', icon: Calendar },
    { id: 'signals', label: 'Live Signals', icon: Zap, badge: 'LIVE' },
  ];

  const toolsItems = [
    { id: 'search', label: 'Smart Search', icon: Search },
    { id: 'scoring', label: 'Score Engine', icon: Target },
    { id: 'enrichment', label: 'Data Sources', icon: Database },
  ];

  const bottomItems = [
    { id: 'notifications', label: 'Notifications', icon: Bell, badge: 3 },
    { id: 'reports', label: 'Export Reports', icon: FileText },
  ];

  const handleNavClick = (id) => {
    onViewChange(id);
    // Close sidebar on mobile after navigation
    if (window.innerWidth < 768) {
      onClose();
    }
  };

  return (
    <>
      {/* Mobile overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      {/* Sidebar - narrower on mobile */}
      <motion.div
        initial={false}
        animate={{
          x: isOpen ? 0 : -224
        }}
        className="fixed md:static top-0 left-0 h-screen w-56 md:w-64 bg-white border-r border-neutral-200 flex flex-col z-50 md:translate-x-0"
      >
      {/* Logo */}
      <div className="h-14 md:h-16 flex items-center justify-between px-3 md:px-6 border-b border-neutral-200">
        <div className="flex items-center gap-2 md:gap-3">
          <div className="w-8 h-8 md:w-9 md:h-9 rounded-lg flex items-center justify-center" style={{
            background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(220, 38, 38, 0.1))',
            border: '1px solid rgba(0, 0, 0, 0.06)',
          }}>
            <TrendingUp className="w-4 h-4 md:w-5 md:h-5 text-neutral-900" strokeWidth={2.5} />
          </div>
          <div>
            <div className="font-bold text-neutral-900 tracking-tight text-sm md:text-base" style={{
              fontWeight: 700,
              letterSpacing: '-0.02em',
            }}>
              LeadEngine
            </div>
            <div className="text-xs font-medium text-neutral-500 uppercase tracking-wider hidden md:block" style={{
              fontSize: '10px',
              letterSpacing: '0.1em',
            }}>
              by ABBK
            </div>
          </div>
        </div>

        {/* Close button for mobile */}
        <button
          onClick={onClose}
          className="md:hidden p-2 hover:bg-neutral-100 rounded-lg"
        >
          <X className="w-5 h-5 text-neutral-600" />
        </button>
      </div>

      {/* Main Navigation */}
      <nav className="flex-1 px-2 md:px-3 py-3 md:py-4 overflow-y-auto">
        <div className="space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;

            return (
              <motion.button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-2 md:gap-3 px-2 md:px-3 py-2 md:py-2.5 rounded-lg md:rounded-xl transition-all text-sm md:text-base ${
                  isActive
                    ? 'bg-neutral-900 text-white shadow-lg'
                    : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }`}
                style={{
                  fontWeight: isActive ? 600 : 500,
                  letterSpacing: '-0.01em',
                }}
                whileHover={{ x: 2 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon className="w-4 h-4 md:w-5 md:h-5" strokeWidth={2.5} />
                <span className="text-xs md:text-sm">{item.label}</span>
                {item.badge && (
                  <span className={`ml-auto text-xs font-bold px-2 py-0.5 rounded-full ${
                    item.badge === 'LIVE'
                      ? 'bg-emerald-500 text-white animate-pulse'
                      : 'bg-blue-600 text-white'
                  }`} style={{ fontSize: '11px' }}>
                    {item.badge}
                  </span>
                )}
              </motion.button>
            );
          })}
        </div>

        {/* Tools Section */}
        <div className="mt-4 md:mt-6">
          <div className="px-2 md:px-3 mb-1 md:mb-2">
            <span className="text-xs font-semibold text-neutral-400 uppercase tracking-wider" style={{
              fontSize: '10px',
              letterSpacing: '0.1em',
            }}>
              Tools
            </span>
          </div>
          <div className="space-y-1">
            {toolsItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;

              return (
                <motion.button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`w-full flex items-center gap-2 md:gap-3 px-2 md:px-3 py-2 md:py-2.5 rounded-lg md:rounded-xl transition-all text-sm md:text-base ${
                    isActive
                      ? 'bg-neutral-900 text-white shadow-lg'
                      : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                  }`}
                  style={{
                    fontWeight: isActive ? 600 : 500,
                    letterSpacing: '-0.01em',
                  }}
                  whileHover={{ x: 2 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Icon className="w-4 h-4 md:w-5 md:h-5" strokeWidth={2.5} />
                  <span className="text-xs md:text-sm">{item.label}</span>
                </motion.button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Bottom Navigation */}
      <div className="px-2 md:px-3 py-3 md:py-4 border-t border-neutral-200">
        <div className="space-y-1 mb-2 md:mb-4">
          {bottomItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentView === item.id;

            return (
              <motion.button
                key={item.id}
                onClick={() => handleNavClick(item.id)}
                className={`w-full flex items-center gap-2 md:gap-3 px-2 md:px-3 py-2 md:py-2.5 rounded-lg md:rounded-xl transition-all text-sm md:text-base ${
                  isActive
                    ? 'bg-neutral-100 text-neutral-900'
                    : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
                }`}
                style={{
                  fontWeight: isActive ? 600 : 500,
                  letterSpacing: '-0.01em',
                }}
                whileHover={{ x: 2 }}
                whileTap={{ scale: 0.98 }}
              >
                <Icon className="w-4 h-4 md:w-5 md:h-5" strokeWidth={2.5} />
                <span className="text-xs md:text-sm">{item.label}</span>
                {item.badge && (
                  <span className="ml-auto bg-blue-600 text-white text-xs font-bold px-2 py-0.5 rounded-full" style={{ fontSize: '11px' }}>
                    {item.badge}
                  </span>
                )}
              </motion.button>
            );
          })}
        </div>

        {/* User Profile - compact on mobile */}
        <motion.div
          className="p-2 md:p-3 rounded-lg md:rounded-xl bg-neutral-50 border border-neutral-200 cursor-pointer hover:bg-neutral-100 transition-colors"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div className="flex items-center gap-2 md:gap-3">
            <div className="w-8 h-8 md:w-9 md:h-9 rounded-full bg-gradient-to-br from-blue-600 to-emerald-600 flex items-center justify-center text-white font-bold text-xs md:text-sm">
              {user?.email?.[0]?.toUpperCase() || 'A'}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs md:text-sm font-semibold text-neutral-900 truncate" style={{ fontWeight: 600 }}>
                {user?.full_name || 'Admin'}
              </div>
              <div className="text-xs text-neutral-500 truncate hidden md:block" style={{ fontSize: '11px' }}>
                {user?.role || 'Manager'}
              </div>
            </div>
          </div>
        </motion.div>

        <motion.button
          onClick={onLogout}
          className="w-full flex items-center gap-2 md:gap-3 px-2 md:px-3 py-2 md:py-2.5 rounded-lg md:rounded-xl text-neutral-600 hover:bg-red-50 hover:text-red-600 transition-colors mt-2 text-sm md:text-base"
          style={{
            fontWeight: 500,
            letterSpacing: '-0.01em',
          }}
          whileHover={{ x: 2 }}
          whileTap={{ scale: 0.98 }}
        >
          <LogOut className="w-4 h-4 md:w-5 md:h-5" strokeWidth={2.5} />
          <span className="text-xs md:text-sm">Logout</span>
        </motion.button>
      </div>
      </motion.div>
    </>
  );
};

export default Sidebar;
