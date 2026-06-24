/**
 * Framer Motion Animation Variants
 * Reusable animation configurations for consistent motion design
 */

export const fadeUp = {
  hidden: {
    opacity: 0,
    y: 20
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.25, 0.1, 0.25, 1], // Custom easing
    }
  }
};

export const fadeIn = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.5,
    }
  }
};

export const fadeDown = {
  hidden: {
    opacity: 0,
    y: -20
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: [0.25, 0.1, 0.25, 1],
    }
  }
};

export const scaleIn = {
  hidden: {
    opacity: 0,
    scale: 0.95
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.1, 0.25, 1],
    }
  }
};

export const slideInLeft = {
  hidden: {
    opacity: 0,
    x: -40
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.6,
      ease: [0.25, 0.1, 0.25, 1],
    }
  }
};

export const slideInRight = {
  hidden: {
    opacity: 0,
    x: 40
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.6,
      ease: [0.25, 0.1, 0.25, 1],
    }
  }
};

// Stagger children animations
export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    }
  }
};

export const staggerItem = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.5,
    }
  }
};

// Hover/Tap animations
export const hoverScale = {
  rest: { scale: 1 },
  hover: {
    scale: 1.05,
    transition: {
      duration: 0.2,
      ease: "easeOut",
    }
  },
  tap: { scale: 0.98 }
};

export const hoverLift = {
  rest: { y: 0, boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)" },
  hover: {
    y: -4,
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.2)",
    transition: {
      duration: 0.2,
      ease: "easeOut",
    }
  }
};

export const hoverGlow = {
  rest: {
    boxShadow: "0 0 0 rgba(220, 38, 38, 0)"
  },
  hover: {
    boxShadow: "0 0 40px rgba(220, 38, 38, 0.4)",
    transition: {
      duration: 0.3,
      ease: "easeOut",
    }
  }
};

// Number counter animation
export const counterAnimation = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.3,
    }
  }
};

// Viewport animation settings (for scroll-triggered animations)
export const viewportSettings = {
  once: true, // Animate only once
  margin: "-100px", // Trigger 100px before element enters viewport
  amount: 0.3, // Trigger when 30% of element is visible
};
