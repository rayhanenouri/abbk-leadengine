/**
 * Section Wrapper Component
 * Handles scroll-triggered animations for sections
 */

import { motion } from 'framer-motion';
import { fadeUp, viewportSettings } from '../../utils/animations';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { cn } from '../../utils/cn';

const SectionWrapper = ({
  children,
  className,
  animation = fadeUp,
  delay = 0,
  ...props
}) => {
  const shouldReduceMotion = useReducedMotion();

  if (shouldReduceMotion) {
    return (
      <section className={cn('section-container py-20 lg:py-32', className)} {...props}>
        {children}
      </section>
    );
  }

  return (
    <motion.section
      className={cn('section-container py-20 lg:py-32', className)}
      initial="hidden"
      whileInView="visible"
      viewport={viewportSettings}
      variants={animation}
      transition={{ delay }}
      {...props}
    >
      {children}
    </motion.section>
  );
};

export default SectionWrapper;
