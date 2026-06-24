/**
 * Clean Stats Overview
 * Minimal, data-focused cards
 */

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const StatCard = ({ title, value, change, changeType, icon: Icon, color = 'primary' }) => {
  const colorClasses = {
    primary: 'bg-primary-50 text-primary-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    amber: 'bg-amber-50 text-amber-600',
    purple: 'bg-purple-50 text-purple-600',
  };

  const getTrendIcon = () => {
    if (changeType === 'up') return <TrendingUp className="w-3 h-3" />;
    if (changeType === 'down') return <TrendingDown className="w-3 h-3" />;
    return <Minus className="w-3 h-3" />;
  };

  const getTrendColor = () => {
    if (changeType === 'up') return 'text-emerald-600';
    if (changeType === 'down') return 'text-red-600';
    return 'text-neutral-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-xl border border-neutral-200 p-6 hover:shadow-xl hover:border-neutral-300 transition-all cursor-default"
    >
      <div className="flex items-start justify-between mb-5">
        <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
          <Icon className="w-5 h-5" strokeWidth={2.5} />
        </div>
        {change && (
          <div className={`flex items-center gap-1 text-xs font-bold ${getTrendColor()}`} style={{
            letterSpacing: '-0.01em',
          }}>
            {getTrendIcon()}
            {change}
          </div>
        )}
      </div>
      <div className="text-4xl font-bold text-neutral-900 mb-2 tracking-tight" style={{
        fontWeight: 700,
        letterSpacing: '-0.03em',
      }}>
        {value}
      </div>
      <div className="text-sm font-medium text-neutral-500" style={{
        fontWeight: 500,
      }}>
        {title}
      </div>
    </motion.div>
  );
};

const StatsOverview = ({ stats }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <StatCard key={index} {...stat} />
      ))}
    </div>
  );
};

export default StatsOverview;
