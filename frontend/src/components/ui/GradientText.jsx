/**
 * Gradient Text Component
 * Animated gradient text for headlines and emphasis
 */

import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

const GradientText = ({
  children,
  gradient = 'primary',
  animate = false,
  className,
  ...props
}) => {
  const gradients = {
    primary: 'bg-gradient-to-r from-primary-500 via-primary-600 to-primary-700',
    blue: 'bg-gradient-to-r from-accent-400 via-accent-500 to-accent-600',
    rainbow: 'bg-gradient-to-r from-primary-500 via-accent-500 to-primary-500',
  };

  const baseStyles = 'bg-clip-text text-transparent';

  return (
    <motion.span
      className={cn(
        baseStyles,
        gradients[gradient],
        animate && 'bg-[length:200%_auto] animate-shimmer',
        className
      )}
      {...props}
    >
      {children}
    </motion.span>
  );
};

export default GradientText;
