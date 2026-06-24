/**
 * How It Works Section
 * Step-by-step process with animated connectors
 */

import { motion } from 'framer-motion';
import { Search, Brain, Target, Rocket } from 'lucide-react';
import SectionWrapper from '../ui/SectionWrapper';
import Card from '../ui/Card';
import { staggerContainer, staggerItem } from '../../utils/animations';

const HowItWorks = () => {
  const steps = [
    {
      number: '01',
      icon: Search,
      title: 'AI Discovers',
      description: 'Scans LinkedIn, databases, and news. Finds 500+ qualified leads in your market.',
      color: 'primary',
    },
    {
      number: '02',
      icon: Brain,
      title: 'Smart Scoring',
      description: 'Each lead scored 0-100 by buying signals, size, industry, and hiring.',
      color: 'accent',
    },
    {
      number: '03',
      icon: Target,
      title: 'Deal Intel',
      description: 'AI tells you what to pitch, why they need it, when to call.',
      color: 'primary',
    },
    {
      number: '04',
      icon: Rocket,
      title: 'Close Deals',
      description: 'Call pre-qualified leads with perfect intel. They say yes.',
      color: 'accent',
    },
  ];

  return (
    <SectionWrapper id="how-it-works">
      <div className="text-center mb-16">
        <motion.h2
          className="text-4xl lg:text-6xl font-bold text-white mb-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          How It <span className="text-gradient">Actually Works</span>
        </motion.h2>
        <motion.p
          className="text-xl text-neutral-400 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Zero to 500 leads in 4 steps
        </motion.p>
      </div>

      <motion.div
        className="max-w-5xl mx-auto"
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
      >
        {steps.map((step, index) => (
          <motion.div
            key={index}
            variants={staggerItem}
            className="relative"
          >
            <div className="grid lg:grid-cols-12 gap-8 items-center mb-16 last:mb-0">
              {/* Number Badge */}
              <div className="lg:col-span-2 flex justify-center lg:justify-end">
                <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${
                  step.color === 'primary'
                    ? 'from-primary-500 to-primary-700'
                    : 'from-accent-500 to-accent-700'
                } flex items-center justify-center shadow-glow-red-sm`}>
                  <span className="text-3xl font-bold text-white">{step.number}</span>
                </div>
              </div>

              {/* Content Card */}
              <div className="lg:col-span-10">
                <Card hover="lift">
                  <div className="flex items-start gap-6">
                    <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${
                      step.color === 'primary'
                        ? 'from-primary-500/20 to-primary-700/20'
                        : 'from-accent-500/20 to-accent-700/20'
                    } border ${
                      step.color === 'primary'
                        ? 'border-primary-500/30'
                        : 'border-accent-500/30'
                    } flex items-center justify-center flex-shrink-0`}>
                      <step.icon className={`w-7 h-7 ${
                        step.color === 'primary' ? 'text-primary-500' : 'text-accent-500'
                      }`} />
                    </div>

                    <div>
                      <h3 className="text-2xl font-bold text-white mb-2">{step.title}</h3>
                      <p className="text-lg text-neutral-400 leading-relaxed">{step.description}</p>
                    </div>
                  </div>
                </Card>
              </div>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <motion.div
                className="hidden lg:block absolute left-[10%] top-20 w-0.5 h-16 bg-gradient-to-b from-primary-600 to-accent-600"
                initial={{ scaleY: 0 }}
                whileInView={{ scaleY: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: 0.3 }}
              />
            )}
          </motion.div>
        ))}
      </motion.div>

      {/* CTA */}
      <motion.div
        className="text-center mt-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay: 0.4 }}
      >
        <p className="text-neutral-400 mb-4">Sounds too good to be true?</p>
        <button className="text-primary-500 hover:text-primary-400 font-semibold text-lg underline underline-offset-4 transition-colors">
          Watch a 2-minute demo →
        </button>
      </motion.div>
    </SectionWrapper>
  );
};

export default HowItWorks;
