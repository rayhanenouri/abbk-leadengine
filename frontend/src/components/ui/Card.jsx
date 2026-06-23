/**
 * Premium Card Component
 * Glass-morphism cards with hover effects
 */

import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import { useReducedMotion } from '../../hooks/useReducedMotion';

const Card = ({
  children,
  variant = 'glass',
  hover = 'lift',
  className,
  ...props
}) => {
  const shouldReduceMotion = useReducedMotion();

  const variants = {
    glass: 'bg-neutral-900/50 backdrop-blur-xl border border-neutral-800/50',
    solid: 'bg-neutral-900 border border-neutral-800',
    outline: 'bg-transparent border-2 border-neutral-700',
    'gradient-border': 'gradient-border',
  };

  const hoverEffects = {
    none: {},
    lift: !shouldReduceMotion ? {
      y: -4,
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
    } : {},
    glow: !shouldReduceMotion ? {
      boxShadow: '0 0 40px rgba(220, 38, 38, 0.3)',
    } : {},
    scale: !shouldReduceMotion ? {
      scale: 1.02,
    } : {},
  };

  const MotionDiv = shouldReduceMotion ? 'div' : motion.div;

  return (
    <MotionDiv
      className={cn(
        'rounded-xl p-6 transition-all duration-300',
        variants[variant],
        className
      )}
      whileHover={hoverEffects[hover]}
      {...props}
    >
      {children}
    </MotionDiv>
  );
};

export default Card;
