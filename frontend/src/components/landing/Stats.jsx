/**
 * Stats Section
 * Animated statistics with impressive numbers
 */

import { motion } from 'framer-motion';
import { TrendingUp, Users, Clock, DollarSign } from 'lucide-react';
import SectionWrapper from '../ui/SectionWrapper';
import AnimatedCounter from '../ui/AnimatedCounter';
import Card from '../ui/Card';
import { staggerContainer, staggerItem } from '../../utils/animations';

const Stats = () => {
  const stats = [
    {
      icon: Users,
      value: 500,
      suffix: '+',
      label: 'Qualified Leads',
      subLabel: 'Discovered automatically every week',
      color: 'primary',
    },
    {
      icon: TrendingUp,
      value: 3,
      suffix: 'x',
      label: 'Faster Pipeline',
      subLabel: 'Compared to manual prospecting',
      color: 'accent',
    },
    {
      icon: Clock,
      value: 20,
      suffix: 'hrs',
      label: 'Time Saved',
      subLabel: 'Per week on research and qualifying',
      color: 'primary',
    },
    {
      icon: DollarSign,
      value: 85,
      suffix: '%',
      label: 'Higher Conversion',
      subLabel: 'With pre-qualified, scored leads',
      color: 'accent',
    },
  ];

  return (
    <SectionWrapper className="bg-gradient-to-b from-neutral-950 via-neutral-900 to-neutral-950">
      <div className="text-center mb-16">
        <motion.h2
          className="text-4xl lg:text-6xl font-bold text-white mb-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          Results That{' '}
          <span className="text-gradient">Speak for Themselves</span>
        </motion.h2>
        <motion.p
          className="text-xl text-neutral-400 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Real metrics from sales teams using LeadEngine
        </motion.p>
      </div>

      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto"
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
      >
        {stats.map((stat, index) => (
          <motion.div key={index} variants={staggerItem}>
            <Card hover="lift" className="text-center">
              <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${
                stat.color === 'primary'
                  ? 'from-primary-500 to-primary-700'
                  : 'from-accent-500 to-accent-700'
              } flex items-center justify-center mx-auto mb-4`}>
                <stat.icon className="w-7 h-7 text-white" />
              </div>

              <div className="mb-2">
                <AnimatedCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  className="text-5xl font-bold text-white"
                />
              </div>

              <h3 className="text-lg font-semibold text-white mb-1">{stat.label}</h3>
              <p className="text-sm text-neutral-400">{stat.subLabel}</p>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </SectionWrapper>
  );
};

export default Stats;
