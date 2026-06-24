/**
 * Class Name Utility
 * Merges Tailwind classes intelligently without conflicts
 */

export function cn(...inputs) {
  return inputs
    .flat()
    .filter(Boolean)
    .join(' ')
    .trim();
}
