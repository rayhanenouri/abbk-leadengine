/**
 * Landing Page
 * Complete premium SaaS landing page composition
 */

import Navbar from '../components/layout/Navbar';
import Hero from '../components/landing/Hero';
import ProblemSolution from '../components/landing/ProblemSolution';
import Features from '../components/landing/Features';
import HowItWorks from '../components/landing/HowItWorks';
import Stats from '../components/landing/Stats';
import Footer from '../components/landing/Footer';

const Landing = ({ onGetStarted }) => {
  return (
    <div className="min-h-screen bg-neutral-950 overflow-x-hidden">
      {/* Navigation */}
      <Navbar onGetStarted={onGetStarted} />

      {/* Hero Section */}
      <Hero onGetStarted={onGetStarted} />

      {/* Problem → Solution */}
      <ProblemSolution />

      {/* Features Grid */}
      <Features />

      {/* How It Works */}
      <HowItWorks />

      {/* Statistics */}
      <Stats />

      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Landing;
