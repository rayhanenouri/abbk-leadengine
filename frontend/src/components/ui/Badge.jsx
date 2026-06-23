/**
 * Badge Component
 * Status and tag badges
 */

import { cn } from '../../utils/cn';

const Badge = ({
  children,
  variant = 'default',
  size = 'md',
  pill = false,
  className,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center font-semibold';

  const variants = {
    default: 'bg-neutral-800 text-neutral-200 border border-neutral-700',
    success: 'bg-success-600/10 text-success-500 border border-success-600/20',
    warning: 'bg-warning-600/10 text-warning-500 border border-warning-600/20',
    error: 'bg-error-600/10 text-error-500 border border-error-600/20',
    accent: 'bg-accent-600/10 text-accent-500 border border-accent-600/20',
    primary: 'bg-primary-600/10 text-primary-500 border border-primary-600/20',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };

  return (
    <span
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        pill ? 'rounded-full' : 'rounded-md',
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;
