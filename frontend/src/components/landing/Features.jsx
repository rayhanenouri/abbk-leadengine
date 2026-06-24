/**
 * Features Section
 * Bento grid layout showcasing AI capabilities
 */

import { motion } from 'framer-motion';
import {
  Brain,
  Target,
  Zap,
  TrendingUp,
  Users,
  BarChart3,
  Sparkles,
  Shield,
  Clock
} from 'lucide-react';
import SectionWrapper from '../ui/SectionWrapper';
import Card from '../ui/Card';
import Badge from '../ui/Badge';
import { staggerContainer, staggerItem } from '../../utils/animations';

const Features = () => {
  const features = [
    {
      icon: Brain,
      title: 'AI Discovery',
      description: '500+ qualified leads from LinkedIn, news, and databases.',
      gradient: 'from-primary-500 to-primary-700',
      span: 'lg:col-span-2',
    },
    {
      icon: Target,
      title: 'Smart Scoring',
      description: '0-100 score based on buying signals.',
      gradient: 'from-accent-500 to-accent-700',
      span: 'lg:col-span-1',
    },
    {
      icon: Zap,
      title: 'Live Signals',
      description: 'Hiring, funding, expansion detected instantly.',
      gradient: 'from-primary-600 to-accent-600',
      span: 'lg:col-span-1',
    },
    {
      icon: TrendingUp,
      title: 'Deal Intel',
      description: "AI tells you what to pitch and why they'll buy.",
      gradient: 'from-accent-500 to-primary-500',
      span: 'lg:col-span-2',
    },
    {
      icon: Users,
      title: 'Full Profiles',
      description: 'Company data, employees, signals, contacts — one view.',
      gradient: 'from-primary-500 to-primary-700',
      span: 'lg:col-span-1',
    },
    {
      icon: BarChart3,
      title: 'Live Analytics',
      description: 'Track pipeline and conversion in real-time.',
      gradient: 'from-accent-600 to-accent-800',
      span: 'lg:col-span-1',
    },
    {
      icon: Clock,
      title: 'Auto-Refresh',
      description: 'New leads weekly. Pipeline never empty.',
      gradient: 'from-primary-600 to-primary-800',
      span: 'lg:col-span-1',
    },
    {
      icon: Shield,
      title: 'GDPR Safe',
      description: 'Public data only. Fully compliant.',
      gradient: 'from-accent-500 to-accent-700',
      span: 'lg:col-span-1',
    },
  ];

  return (
    <SectionWrapper id="features">
      <div className="text-center mb-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="inline-block mb-4"
        >
          <Badge variant="accent" size="lg" pill>
            <Sparkles className="w-4 h-4 mr-1.5" />
            Powerful Features
          </Badge>
        </motion.div>

        <motion.h2
          className="text-4xl lg:text-6xl font-bold text-white mb-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          Everything You Need to{' '}
          <span className="text-gradient">Crush Your Quota</span>
        </motion.h2>

        <motion.p
          className="text-xl text-neutral-400 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          AI-powered intelligence that turns cold prospects into hot leads
        </motion.p>
      </div>

      <motion.div
        className="grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto"
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
      >
        {features.map((feature, index) => (
          <motion.div
            key={index}
            variants={staggerItem}
            className={feature.span}
          >
            <Card hover="lift" className="h-full group">
              <div className="flex flex-col h-full">
                {/* Icon */}
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-gradient transition-colors">
                  {feature.title}
                </h3>
                <p className="text-neutral-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </SectionWrapper>
  );
};

export default Features;
