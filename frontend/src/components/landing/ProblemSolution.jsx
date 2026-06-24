/**
 * Problem → Solution Section
 * Before/After comparison showing the old manual way vs AI-powered way
 */

import { motion } from 'framer-motion';
import { X, Check, Clock, Search, Phone, Brain, Target, Zap } from 'lucide-react';
import SectionWrapper from '../ui/SectionWrapper';
import Card from '../ui/Card';
import { fadeUp } from '../../utils/animations';

const ProblemSolution = () => {
  const problems = [
    { icon: Search, text: 'Hours Googling for prospects' },
    { icon: Phone, text: 'Cold calls to wrong companies' },
    { icon: Clock, text: 'Days wasted on dead leads' },
    { icon: X, text: 'Zero intel on buying readiness' },
  ];

  const solutions = [
    { icon: Brain, text: '500+ qualified leads in 30 min' },
    { icon: Target, text: 'Exact pitch for each prospect' },
    { icon: Zap, text: 'Complete intel instantly' },
    { icon: Check, text: 'Scored by buying signals' },
  ];

  return (
    <SectionWrapper id="problem-solution">
      <div className="text-center mb-16">
        <motion.h2
          className="text-4xl lg:text-6xl font-bold text-white mb-4"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          The Old Way vs{' '}
          <span className="text-gradient">The Smart Way</span>
        </motion.h2>
        <motion.p
          className="text-xl text-neutral-400 max-w-2xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.1 }}
        >
          Manual prospecting wastes weeks. AI does it in minutes.
        </motion.p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
        {/* Problem Card */}
        <motion.div
          initial={{ opacity: 0, x: -40 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <Card variant="solid" hover="none" className="h-full border-2 border-error-600/20">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-error-600/10 flex items-center justify-center">
                <X className="w-6 h-6 text-error-500" />
              </div>
              <h3 className="text-2xl font-bold text-white">Manual Prospecting</h3>
            </div>

            <div className="space-y-4">
              {problems.map((problem, index) => (
                <motion.div
                  key={index}
                  className="flex items-start gap-3 p-3 rounded-lg bg-neutral-800/30"
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.1 * index }}
                >
                  <X className="w-5 h-5 text-error-500 flex-shrink-0 mt-0.5" />
                  <p className="text-neutral-300">{problem.text}</p>
                </motion.div>
              ))}
            </div>

            <div className="mt-8 p-4 rounded-lg bg-error-600/5 border border-error-600/20">
              <p className="text-sm text-neutral-400">
                <strong className="text-error-500">Result:</strong> Wasted time, low conversion, missed opportunities
              </p>
            </div>
          </Card>
        </motion.div>

        {/* Solution Card */}
        <motion.div
          initial={{ opacity: 0, x: 40 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <Card variant="glass" hover="glow" className="h-full border-2 border-primary-600/30 shadow-glow-red-sm">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 rounded-lg bg-primary-600 flex items-center justify-center">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-white">AI-Powered LeadEngine</h3>
            </div>

            <div className="space-y-4">
              {solutions.map((solution, index) => (
                <motion.div
                  key={index}
                  className="flex items-start gap-3 p-3 rounded-lg bg-primary-600/5 border border-primary-600/20"
                  initial={{ opacity: 0, x: 20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.1 * index }}
                >
                  <Check className="w-5 h-5 text-success-500 flex-shrink-0 mt-0.5" />
                  <p className="text-white font-medium">{solution.text}</p>
                </motion.div>
              ))}
            </div>

            <div className="mt-8 p-4 rounded-lg bg-gradient-primary text-white">
              <p className="text-sm">
                <strong>Result:</strong> 3x faster pipeline, higher conversion, predictable revenue
              </p>
            </div>
          </Card>
        </motion.div>
      </div>
    </SectionWrapper>
  );
};

export default ProblemSolution;
