/**
 * Hero Section
 * Premium hero with animated headline, dual CTAs, and particle background
 */

import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, TrendingUp, Users } from 'lucide-react';
import Button from '../ui/Button';
import GradientText from '../ui/GradientText';
import Badge from '../ui/Badge';
import { fadeUp, staggerContainer, staggerItem } from '../../utils/animations';
import { useReducedMotion } from '../../hooks/useReducedMotion';

const Hero = ({ onGetStarted }) => {
  const shouldReduceMotion = useReducedMotion();

  const stats = [
    { icon: Users, value: '500+', label: 'Companies Discovered' },
    { icon: TrendingUp, value: '3x', label: 'Faster Pipeline' },
    { icon: Sparkles, value: 'AI-Powered', label: 'Intelligence' },
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-neutral-950">
      {/* Animated Background */}
      <div className="absolute inset-0 z-0">
        {/* Gradient Mesh */}
        <div className="absolute inset-0 bg-gradient-mesh opacity-40" />

        {/* Grid Pattern */}
        <div className="absolute inset-0 grid-pattern opacity-30" />

        {/* Radial Glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-primary-600/10 rounded-full blur-3xl" />

        {/* Noise Texture */}
        <div className="absolute inset-0 noise-overlay" />

        {/* Floating Particles */}
        {!shouldReduceMotion && (
          <>
            <motion.div
              className="absolute top-20 left-[10%] w-2 h-2 bg-primary-500 rounded-full"
              animate={{
                y: [0, -30, 0],
                opacity: [0.3, 0.8, 0.3],
              }}
              transition={{
                duration: 6,
                repeat: Infinity,
                ease: 'easeInOut',
              }}
            />
            <motion.div
              className="absolute top-40 right-[15%] w-3 h-3 bg-accent-500 rounded-full"
              animate={{
                y: [0, -40, 0],
                opacity: [0.3, 0.7, 0.3],
              }}
              transition={{
                duration: 8,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: 1,
              }}
            />
            <motion.div
              className="absolute bottom-40 left-[20%] w-2 h-2 bg-primary-500 rounded-full"
              animate={{
                y: [0, -25, 0],
                opacity: [0.3, 0.9, 0.3],
              }}
              transition={{
                duration: 7,
                repeat: Infinity,
                ease: 'easeInOut',
                delay: 2,
              }}
            />
          </>
        )}
      </div>

      {/* Content */}
      <motion.div
        className="relative z-10 section-container py-32 lg:py-40"
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
      >
        <div className="max-w-5xl mx-auto text-center">
          {/* Badge */}
          <motion.div variants={staggerItem} className="mb-8">
            <Badge variant="primary" size="lg" pill className="inline-flex">
              <Sparkles className="w-4 h-4 mr-1.5" />
              AI-Powered Lead Generation
            </Badge>
          </motion.div>

          {/* Headline */}
          <motion.h1
            variants={staggerItem}
            className="text-5xl sm:text-6xl lg:text-8xl font-bold tracking-tight text-white mb-6 text-balance"
          >
            Stop Guessing.{' '}
            <GradientText gradient="primary" animate>
              Start Closing.
            </GradientText>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            variants={staggerItem}
            className="text-xl lg:text-2xl text-neutral-300 mb-12 max-w-3xl mx-auto text-balance leading-relaxed"
          >
            AI finds <strong className="text-white">500+ ready-to-buy leads</strong>. Know who to call, what to pitch, when to strike.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            variants={staggerItem}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16"
          >
            <Button
              variant="primary"
              size="xl"
              icon={ArrowRight}
              iconPosition="right"
              className="group"
              onClick={onGetStarted}
            >
              Get 500 Leads Now
            </Button>
            <Button variant="ghost" size="xl">
              See It Live
            </Button>
          </motion.div>

          {/* Stats Bar */}
          <motion.div
            variants={staggerItem}
            className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl mx-auto"
          >
            {stats.map((stat, index) => (
              <div
                key={index}
                className="flex flex-col items-center p-4 rounded-xl bg-neutral-900/50 backdrop-blur-sm border border-neutral-800/50"
              >
                <stat.icon className="w-6 h-6 text-primary-500 mb-2" />
                <div className="text-2xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-neutral-400">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </motion.div>

      {/* Bottom Fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-neutral-950 to-transparent z-10" />
    </section>
  );
};

export default Hero;
