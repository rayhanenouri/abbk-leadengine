/**
 * useReducedMotion Hook
 * Respects user's motion preferences for accessibility
 */

import { useEffect, useState } from 'react';

export function useReducedMotion() {
  const [shouldReduceMotion, setShouldReduceMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

    setShouldReduceMotion(mediaQuery.matches);

    const handleChange = (event) => {
      setShouldReduceMotion(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);

    return () => {
      mediaQuery.removeEventListener('change', handleChange);
    };
  }, []);

  return shouldReduceMotion;
}
