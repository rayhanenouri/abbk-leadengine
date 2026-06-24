/**
 * Clean, Modern Login Page
 * Professional B2B SaaS style
 */

import { useState } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, ArrowRight, Mail, Lock } from 'lucide-react';
import { login } from '../services/api';

const LoginV2 = ({ onLoginSuccess }) => {
  const [email, setEmail] = useState('admin@abbk.tn');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      onLoginSuccess();
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 p-12 flex-col justify-between relative overflow-hidden bg-neutral-900">
        {/* Multiple Moving Gradient Layers */}
        <motion.div
          className="absolute inset-0"
          animate={{
            rotate: [0, 360],
          }}
          transition={{
            duration: 30,
            repeat: Infinity,
            ease: 'linear',
          }}
          style={{
            background: 'radial-gradient(circle at 30% 50%, rgba(220, 38, 38, 0.15), transparent 50%)',
          }}
        />

        <motion.div
          className="absolute inset-0"
          animate={{
            rotate: [360, 0],
          }}
          transition={{
            duration: 25,
            repeat: Infinity,
            ease: 'linear',
          }}
          style={{
            background: 'radial-gradient(circle at 70% 50%, rgba(59, 130, 246, 0.1), transparent 50%)',
          }}
        />

        {/* Fast Moving Grid */}
        <motion.div
          className="absolute inset-0 opacity-20"
          animate={{
            x: [0, 100, 0],
            y: [0, -100, 0],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'linear',
          }}
        >
          <div className="absolute inset-0" style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
            backgroundSize: '50px 50px'
          }}></div>
        </motion.div>

        {/* Diagonal Lines Moving */}
        <motion.div
          className="absolute inset-0 opacity-10"
          animate={{
            x: [0, -200],
          }}
          transition={{
            duration: 12,
            repeat: Infinity,
            ease: 'linear',
          }}
        >
          <div className="absolute inset-0" style={{
            backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 35px, rgba(255,255,255,0.05) 35px, rgba(255,255,255,0.05) 70px)',
          }}></div>
        </motion.div>

        {/* Large Moving Orbs */}
        <motion.div
          className="absolute w-96 h-96 rounded-full blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgba(220, 38, 38, 0.2), transparent)',
          }}
          animate={{
            x: [-100, 400, -100],
            y: [-50, 300, -50],
            scale: [1, 1.5, 1],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />

        <motion.div
          className="absolute w-80 h-80 rounded-full blur-3xl"
          style={{
            background: 'radial-gradient(circle, rgba(59, 130, 246, 0.15), transparent)',
          }}
          animate={{
            x: [600, -100, 600],
            y: [400, -50, 400],
            scale: [1.2, 1, 1.2],
          }}
          transition={{
            duration: 18,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 2,
          }}
        />

        {/* Particles */}
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-white rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [0, -100, 0],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 4,
              repeat: Infinity,
              delay: Math.random() * 5,
              ease: 'easeInOut',
            }}
          />
        ))}

        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="relative z-10"
        >
          <div className="mb-16">
            <div className="flex items-center gap-4">
              {/* Premium Scale Icon */}
              <div className="relative group">
                <motion.div
                  className="absolute -inset-2 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.4), rgba(220, 38, 38, 0.4))',
                    filter: 'blur(16px)',
                  }}
                />

                <div className="relative w-14 h-14 rounded-2xl flex items-center justify-center" style={{
                  background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(220, 38, 38, 0.15))',
                  backdropFilter: 'blur(10px)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
                }}>
                  <TrendingUp className="w-7 h-7 text-white" strokeWidth={2.5} />
                </div>
              </div>

              {/* Brand Name - LeadEngine is the hero */}
              <div>
                <div className="text-4xl font-bold text-white tracking-tight mb-0.5" style={{
                  letterSpacing: '-0.04em',
                  fontWeight: 700,
                }}>
                  LeadEngine
                </div>
                <div className="text-sm font-medium tracking-wider uppercase" style={{
                  color: 'rgba(255, 255, 255, 0.5)',
                  letterSpacing: '0.2em',
                  fontWeight: 500,
                }}>
                  by ABBK
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="relative z-10 space-y-8"
        >
          <div>
            <h1 className="text-5xl font-bold text-white mb-5 leading-tight" style={{
              letterSpacing: '-0.03em',
              fontWeight: 700,
            }}>
              Find your next deal
            </h1>
            <p className="text-xl leading-relaxed" style={{
              color: 'rgba(255, 255, 255, 0.7)',
              fontWeight: 400,
            }}>
              AI-powered lead generation that finds 500+ qualified companies ready to buy.
            </p>
          </div>

          <div className="space-y-4">
            {[
              { title: 'Smart Scoring', desc: '13 AI signals track buying intent' },
              { title: 'Real-time Data', desc: 'Scraped from LinkedIn, news, tenders' },
              { title: 'Priority Alerts', desc: 'Never miss a hot lead' }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 + i * 0.1 }}
                whileHover={{
                  x: 8,
                  transition: { duration: 0.2 }
                }}
                className="flex items-start gap-3 cursor-pointer group"
              >
                <motion.div
                  className="w-6 h-6 bg-primary-600/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 group-hover:bg-primary-600/40 transition-colors"
                  whileHover={{
                    scale: 1.1,
                    rotate: 5,
                  }}
                >
                  <motion.div
                    className="w-2 h-2 bg-primary-500 rounded-full"
                    whileHover={{
                      scale: 1.5,
                      boxShadow: '0 0 12px rgba(220, 38, 38, 0.8)',
                    }}
                  />
                </motion.div>
                <div>
                  <motion.div
                    className="font-semibold text-white mb-1"
                    whileHover={{
                      color: '#FCA5A5',
                      transition: { duration: 0.2 }
                    }}
                  >
                    {feature.title}
                  </motion.div>
                  <div className="text-sm text-neutral-400">{feature.desc}</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="relative z-10 text-neutral-400 text-sm"
        >
          © 2026 ABBK Physicsworks. All rights reserved.
        </motion.div>
      </div>

      {/* Right Side - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="w-full max-w-md"
        >
          {/* Mobile Logo */}
          <div className="lg:hidden mb-10">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(220, 38, 38, 0.1))',
                border: '1px solid rgba(0, 0, 0, 0.06)',
              }}>
                <TrendingUp className="w-6 h-6 text-neutral-900" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-2xl font-bold text-neutral-900 tracking-tight" style={{
                  letterSpacing: '-0.03em',
                  fontWeight: 700,
                }}>
                  LeadEngine
                </div>
                <div className="text-xs font-medium tracking-wider uppercase text-neutral-500" style={{
                  letterSpacing: '0.15em',
                }}>
                  by ABBK
                </div>
              </div>
            </div>
          </div>

          {/* Header */}
          <div className="mb-10">
            <h2 className="text-4xl font-bold text-neutral-900 mb-3 tracking-tight" style={{
              letterSpacing: '-0.03em',
              fontWeight: 700,
            }}>
              Welcome back
            </h2>
            <p className="text-lg text-neutral-600" style={{
              fontWeight: 400,
            }}>
              Sign in to your account to continue
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2.5" style={{
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}>
                Email address
              </label>
              <div className="relative group">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-hover:text-neutral-600 transition-colors" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{
                    fontSize: '15px',
                    fontWeight: 500,
                  }}
                  placeholder="you@company.com"
                  required
                  autoFocus
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2.5" style={{
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}>
                Password
              </label>
              <div className="relative group">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-hover:text-neutral-600 transition-colors" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-12 pr-4 py-3.5 bg-neutral-50 border border-neutral-200 rounded-xl text-neutral-900 placeholder-neutral-400 focus:outline-none focus:bg-white focus:border-neutral-900 focus:ring-4 focus:ring-neutral-900/5 transition-all"
                  style={{
                    fontSize: '15px',
                    fontWeight: 500,
                  }}
                  placeholder="Enter your password"
                  required
                />
              </div>
            </div>

            {/* Error */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-red-50 border border-red-200 rounded-lg p-4"
              >
                <p className="text-sm text-red-700 font-medium">{error}</p>
              </motion.div>
            )}

            {/* Submit */}
            <motion.button
              type="submit"
              disabled={loading}
              className={`w-full py-4 rounded-xl font-semibold flex items-center justify-center gap-2.5 transition-all ${
                loading
                  ? 'bg-neutral-300 cursor-not-allowed'
                  : 'bg-neutral-900 hover:bg-neutral-800 shadow-xl shadow-neutral-900/25 hover:shadow-2xl hover:shadow-neutral-900/40'
              } text-white relative overflow-hidden group`}
              style={{
                fontSize: '15px',
                fontWeight: 600,
                letterSpacing: '-0.01em',
              }}
              whileHover={!loading ? { y: -1 } : {}}
              whileTap={!loading ? { scale: 0.99 } : {}}
            >
              {!loading && (
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
              )}
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Signing in...
                </>
              ) : (
                <>
                  Sign in
                  <ArrowRight className="w-5 h-5" strokeWidth={2.5} />
                </>
              )}
            </motion.button>
          </form>

          {/* Stats */}
          <div className="mt-10 pt-8 border-t border-neutral-200 grid grid-cols-3 gap-6 text-center">
            {[
              { value: '500+', label: 'Leads' },
              { value: '93', label: 'Sectors' },
              { value: 'AI', label: 'Powered' }
            ].map((stat, i) => (
              <div key={i} className="group cursor-default">
                <div className="text-3xl font-bold text-neutral-900 mb-1 group-hover:text-primary-600 transition-colors" style={{
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                }}>
                  {stat.value}
                </div>
                <div className="text-xs font-medium text-neutral-500 uppercase tracking-wider" style={{
                  letterSpacing: '0.1em',
                }}>
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LoginV2;
