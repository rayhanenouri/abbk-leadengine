/**
 * Premium Button Component
 * High-converting CTA button with multiple variants and states
 */

import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import { useReducedMotion } from '../../hooks/useReducedMotion';

const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled = false,
  icon: Icon,
  iconPosition = 'left',
  className,
  ...props
}) => {
  const shouldReduceMotion = useReducedMotion();

  const baseStyles = 'inline-flex items-center justify-center font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-neutral-950 disabled:opacity-50 disabled:cursor-not-allowed';

  const variants = {
    primary: 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500 shadow-lg shadow-primary-600/50 hover:shadow-2xl hover:shadow-primary-600/60 btn-shimmer hover:-translate-y-0.5 active:translate-y-0',
    secondary: 'bg-neutral-800 text-white hover:bg-neutral-700 focus:ring-neutral-500 border border-neutral-700 hover:border-neutral-600 hover:-translate-y-0.5 active:translate-y-0',
    ghost: 'bg-transparent text-neutral-200 hover:bg-neutral-800/50 focus:ring-neutral-500 border border-neutral-700 hover:border-neutral-600 hover:-translate-y-0.5 active:translate-y-0',
    outline: 'bg-transparent text-primary-500 hover:bg-primary-600/10 focus:ring-primary-500 border-2 border-primary-600 hover:border-primary-500 hover:-translate-y-0.5 active:translate-y-0',
    danger: 'bg-error-600 text-white hover:bg-error-700 focus:ring-error-500 shadow-lg shadow-error-600/30 hover:-translate-y-0.5 active:translate-y-0',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm rounded-lg gap-1.5',
    md: 'px-6 py-3 text-base rounded-xl gap-2',
    lg: 'px-8 py-4 text-lg rounded-xl gap-2.5',
    xl: 'px-10 py-5 text-xl rounded-2xl gap-3',
  };

  const MotionButton = shouldReduceMotion ? 'button' : motion.button;

  return (
    <MotionButton
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        fullWidth && 'w-full',
        className
      )}
      disabled={disabled || loading}
      whileHover={!shouldReduceMotion ? { scale: 1.05 } : {}}
      whileTap={!shouldReduceMotion ? { scale: 0.95 } : {}}
      {...props}
    >
      {loading && (
        <svg
          className="animate-spin h-5 w-5"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}

      {Icon && iconPosition === 'left' && !loading && <Icon className="w-5 h-5" />}

      {children}

      {Icon && iconPosition === 'right' && !loading && <Icon className="w-5 h-5" />}
    </MotionButton>
  );
};

export default Button;
