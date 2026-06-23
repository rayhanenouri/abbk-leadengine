/**
 * Premium Navbar Component
 * Sticky navigation with glass-morphism and scroll behavior
 */

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Menu, X } from 'lucide-react';
import Button from '../ui/Button';
import { cn } from '../../utils/cn';
import { useIsMobile } from '../../hooks/useMediaQuery';

const Navbar = ({ onGetStarted }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const isMobile = useIsMobile();

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Features', href: '#features' },
    { name: 'How It Works', href: '#how-it-works' },
    { name: 'Pricing', href: '#pricing' },
    { name: 'FAQ', href: '#faq' },
  ];

  return (
    <motion.nav
      className={cn(
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300',
        isScrolled
          ? 'bg-neutral-950/80 backdrop-blur-xl border-b border-neutral-800/50 shadow-lg'
          : 'bg-transparent'
      )}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="section-container">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <a href="/" className="flex items-center space-x-3 group">
            <div className="bg-white rounded-lg px-2 py-1">
              <img
                src="/logo ABBK.png"
                alt="ABBK LeadEngine"
                className="h-6 lg:h-8 w-auto transition-transform duration-200 group-hover:scale-105"
              />
            </div>
          </a>

          {/* Desktop Navigation */}
          {!isMobile && (
            <div className="hidden lg:flex items-center space-x-8">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  className="text-neutral-300 hover:text-white transition-colors duration-200 font-medium"
                >
                  {link.name}
                </a>
              ))}
            </div>
          )}

          {/* CTA Buttons */}
          <div className="flex items-center space-x-4">
            {!isMobile && (
              <Button variant="ghost" size="sm" onClick={onGetStarted}>
                Sign In
              </Button>
            )}
            <Button variant="primary" size="sm" onClick={onGetStarted}>
              Get Started
            </Button>

            {/* Mobile Menu Toggle */}
            {isMobile && (
              <button
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                className="lg:hidden text-neutral-300 hover:text-white transition-colors"
                aria-label="Toggle menu"
              >
                {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isMobileMenuOpen && isMobile && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="lg:hidden border-t border-neutral-800/50 bg-neutral-950/95 backdrop-blur-xl"
          >
            <div className="section-container py-4 space-y-2">
              {navLinks.map((link) => (
                <a
                  key={link.name}
                  href={link.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="block py-3 px-4 text-neutral-300 hover:text-white hover:bg-neutral-800/50 rounded-lg transition-all"
                >
                  {link.name}
                </a>
              ))}
              <div className="pt-2 border-t border-neutral-800/50">
                <Button variant="ghost" fullWidth className="mb-2" onClick={onGetStarted}>
                  Sign In
                </Button>
                <Button variant="primary" fullWidth onClick={onGetStarted}>
                  Get Started
                </Button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.nav>
  );
};

export default Navbar;
