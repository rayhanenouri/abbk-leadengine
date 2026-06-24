# 🏗️ ABBK LeadEngine - Component Architecture

## 📁 File Structure

```
frontend/src/
├── components/
│   ├── ui/                          # Reusable UI Primitives
│   │   ├── Button.jsx              # Premium button with variants
│   │   ├── Card.jsx                # Glass-morph card component
│   │   ├── Badge.jsx               # Status/tag badges
│   │   ├── GradientText.jsx        # Animated gradient text
│   │   ├── AnimatedCounter.jsx     # Number count-up animation
│   │   ├── SectionWrapper.jsx      # Scroll-triggered animation wrapper
│   │   └── Icon.jsx                # Lucide icon wrapper
│   │
│   ├── landing/                     # Landing Page Sections
│   │   ├── Hero.jsx                # Hero section with CTA
│   │   ├── ProblemSolution.jsx     # Before/after comparison
│   │   ├── Features.jsx            # Bento grid features
│   │   ├── HowItWorks.jsx          # Step-by-step process
│   │   ├── Stats.jsx               # Animated statistics
│   │   ├── Testimonials.jsx        # Customer quotes carousel
│   │   ├── Pricing.jsx             # Pricing tiers
│   │   ├── FAQ.jsx                 # Accordion FAQ
│   │   ├── FinalCTA.jsx            # Bottom conversion section
│   │   └── Footer.jsx              # Site footer
│   │
│   └── layout/                      # Layout Components
│       ├── Navbar.jsx              # Sticky navigation
│       ├── MobileMenu.jsx          # Mobile hamburger menu
│       └── PageWrapper.jsx         # Main layout wrapper
│
├── hooks/                           # Custom React Hooks
│   ├── useScrollAnimation.js       # IntersectionObserver hook
│   ├── useReducedMotion.js         # Accessibility hook
│   └── useMediaQuery.js            # Responsive breakpoint hook
│
├── utils/                           # Utility Functions
│   ├── cn.js                       # Class name merger (clsx + tw-merge)
│   └── animations.js               # Framer Motion variants
│
├── styles/
│   └── global.css                  # Global styles & design tokens
│
├── pages/
│   ├── Landing.jsx                 # Landing page composition
│   └── Dashboard.jsx               # Internal dashboard (existing)
│
├── App.jsx                          # Root app component
└── main.jsx                         # Entry point
```

## 🎨 Component Specifications

### UI Primitives (`components/ui/`)

**Button.jsx**
- Variants: `primary`, `secondary`, `ghost`, `outline`, `danger`
- Sizes: `sm`, `md`, `lg`, `xl`
- States: default, hover, active, disabled, loading
- Features: shimmer effect, icon support, full-width option

**Card.jsx**
- Variants: `glass`, `solid`, `outline`, `gradient-border`
- Hover effects: lift, glow, scale
- Responsive padding

**Badge.jsx**
- Variants: `default`, `success`, `warning`, `error`, `accent`
- Sizes: `sm`, `md`, `lg`
- Pill vs square corners

**GradientText.jsx**
- Red gradient, blue gradient, custom gradient support
- Animated shimmer option

**AnimatedCounter.jsx**
- Count-up from 0 to target on scroll into view
- Duration, easing, prefix/suffix support

**SectionWrapper.jsx**
- Fade-up animation trigger on scroll
- Configurable delay, threshold
- Optional children stagger

### Landing Sections (`components/landing/`)

**Hero.jsx**
- Animated headline with text reveal
- Dual CTA buttons (primary + ghost)
- Particle/mesh background animation
- Social proof bar (stats or logos)
- Responsive hero image/mockup

**ProblemSolution.jsx**
- Two-column split: old way vs new way
- Animated flip/transition between states
- Icon-driven pain points vs benefits

**Features.jsx**
- Bento grid layout (3x3 on desktop)
- Icon + title + description per card
- Hover glow + scale effect
- Alternating card sizes for visual interest

**HowItWorks.jsx**
- Numbered step cards (1, 2, 3, 4)
- Animated connector lines between steps
- Scroll-triggered progression

**Stats.jsx**
- 4 stat cards: leads generated, conversion rate, time saved, revenue impact
- Animated counters
- Icons + gradient backgrounds

**Testimonials.jsx**
- Auto-scrolling carousel (pause on hover)
- Avatar + name + role + company
- Quote card with gradient border
- 5-star rating display

**Pricing.jsx**
- 3 tiers: Starter, Professional, Enterprise
- Monthly/Annual toggle
- Feature checklist per tier
- Highlighted "Popular" badge on middle tier

**FAQ.jsx**
- Accordion with smooth expand/collapse
- 6-8 common questions
- Search filter (optional)

**FinalCTA.jsx**
- Full-width section with gradient background
- Bold headline + urgency copy
- Single large CTA button
- Background particle effect

**Footer.jsx**
- 4 columns: Company, Product, Resources, Legal
- Logo + social icons
- Copyright + links

### Layout (`components/layout/`)

**Navbar.jsx**
- Logo (left) + Nav links (center) + CTA button (right)
- Sticky with blur background
- Hide-on-scroll-down, show-on-scroll-up
- Mobile hamburger menu trigger

**MobileMenu.jsx**
- Slide-in from right
- Full-screen overlay
- Animated menu items
- Close button

## 🎬 Animation Strategy (Framer Motion)

### Performance Rules:
- ✅ Animate only `transform` and `opacity`
- ✅ Use `layout` animations sparingly
- ✅ Lazy-load below-fold sections
- ✅ Respect `prefers-reduced-motion`

### Common Variants:
```js
fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
}

scale = {
  rest: { scale: 1 },
  hover: { scale: 1.05 }
}

stagger = {
  visible: { transition: { staggerChildren: 0.1 } }
}
```

## 🚀 Implementation Order

1. ✅ Design tokens (tailwind.config.js)
2. ✅ Global styles (global.css)
3. ⏳ Utils & hooks
4. ⏳ UI primitives (Button, Card, Badge, etc.)
5. ⏳ Layout components (Navbar, Footer)
6. ⏳ Landing sections (Hero → Footer)
7. ⏳ Page composition (Landing.jsx)
8. ⏳ Final polish & performance optimization

## 📦 Dependencies

```json
{
  "dependencies": {
    "react": "^19.2.6",
    "react-dom": "^19.2.6",
    "framer-motion": "^11.15.0",
    "lucide-react": "^0.469.0"
  },
  "devDependencies": {
    "tailwindcss": "^4.1.0",
    "postcss": "^9.0.0",
    "autoprefixer": "^11.0.0"
  }
}
```

## 🎯 Target Metrics

- **Performance**: Lighthouse 90+ (desktop)
- **Accessibility**: WCAG AA compliant
- **Bundle Size**: <200KB (gzipped)
- **First Paint**: <1.5s
- **Interactive**: <3s

## 🎨 Visual Language

- **Primary Action**: Red (#DC2626) - CTAs, highlights
- **Secondary Action**: Ghost/outline buttons
- **Background**: Dark (#0A0A0A) with grid pattern
- **Cards**: Glass-morphism with subtle borders
- **Typography**: Bold headlines, clean body text
- **Motion**: Smooth, purposeful, never distracting
