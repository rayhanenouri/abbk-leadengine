/**
 * Empty State Component
 * Beautiful empty states for better UX
 */

import { motion } from 'framer-motion';

const EmptyState = ({
  icon: Icon,
  title,
  description,
  action,
  actionLabel,
  illustration
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="flex flex-col items-center justify-center py-24 px-6 bg-white rounded-3xl border border-neutral-200"
    >
      {/* Icon or Illustration */}
      {Icon && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
          className="mb-6"
        >
          <div className="p-6 bg-neutral-100 rounded-full">
            <Icon className="w-12 h-12 text-neutral-400" />
          </div>
        </motion.div>
      )}

      {/* Title */}
      <motion.h3
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-2xl font-bold text-neutral-900 mb-3 text-center"
      >
        {title}
      </motion.h3>

      {/* Description */}
      <motion.p
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="text-neutral-500 text-center max-w-md mb-6"
      >
        {description}
      </motion.p>

      {/* Action Button */}
      {action && actionLabel && (
        <motion.button
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          onClick={action}
          className="px-6 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition-all shadow-lg shadow-primary-600/25 hover:shadow-xl hover:shadow-primary-600/30"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {actionLabel}
        </motion.button>
      )}
    </motion.div>
  );
};

export default EmptyState;
