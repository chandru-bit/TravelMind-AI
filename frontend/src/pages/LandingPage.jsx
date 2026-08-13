import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Sparkles, TrendingUp, ShieldCheck, Zap, Layers, MapPin, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export const LandingPage = () => {
  return (
    <div className="space-y-24 py-12">
      {/* Hero Section */}
      <section className="relative text-center max-w-5xl mx-auto px-4 pt-10">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/15 rounded-full blur-3xl -z-10" />
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold uppercase tracking-wider mb-6"
        >
          <Sparkles className="w-4 h-4 text-cyan-400" /> AI-Powered Travel Intelligence Platform
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white leading-tight"
        >
          Predict. Personalize. <span className="gradient-text">Plan.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 text-lg sm:text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed"
        >
          Revolutionizing travel planning with predictive price analytics, weighted destination scoring algorithms, and intelligent day-by-day itinerary generation.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link
            to="/register"
            className="w-full sm:w-auto px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-base shadow-xl shadow-cyan-500/25 flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5"
          >
            Start Planning Now <ArrowRight className="w-5 h-5" />
          </Link>
          <Link
            to="/recommendations"
            className="w-full sm:w-auto px-8 py-4 rounded-xl glass-panel text-gray-200 hover:text-white font-semibold text-base border border-gray-700 hover:border-cyan-500/50 flex items-center justify-center gap-2 transition-all"
          >
            Explore Destinations
          </Link>
        </motion.div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-extrabold text-white">Engineered for Travel Intelligence</h2>
          <p className="text-gray-400 text-sm mt-2">Comprehensive microservice architecture solving complex trip planning friction</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="glass-panel glass-panel-hover rounded-2xl p-8 border border-gray-800 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center">
              <Compass className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Weighted Recommendation Engine</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Deterministic matching algorithm combining budget (25%), interest overlap (30%), weather (15%), activity score (15%), and distance (15%).
            </p>
          </div>

          <div className="glass-panel glass-panel-hover rounded-2xl p-8 border border-gray-800 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">Scikit-Learn ML Price Predictor</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Predictive analytics forecasting flight and hotel price trends using Linear Regression trained on seasonal demand metrics.
            </p>
          </div>

          <div className="glass-panel glass-panel-hover rounded-2xl p-8 border border-gray-800 space-y-4">
            <div className="w-12 h-12 rounded-xl bg-purple-500/20 text-purple-400 flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-bold text-white">AI Itinerary & Fallback Generator</h3>
            <p className="text-sm text-gray-400 leading-relaxed">
              Configurable LLM integration backed by deterministic rule-based itinerary fallback logic ensuring 100% availability.
            </p>
          </div>
        </div>
      </section>

      {/* Tech Stack Banner */}
      <section className="max-w-7xl mx-auto px-4">
        <div className="glass-panel rounded-3xl p-8 sm:p-12 border border-gray-800 text-center relative overflow-hidden">
          <h3 className="text-2xl font-bold text-white mb-6">Production Ready Microservices Architecture</h3>
          <div className="flex flex-wrap justify-center items-center gap-6 text-sm text-gray-300">
            <span className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-900 border border-gray-800"><Layers className="w-4 h-4 text-cyan-400" /> Nginx Load Balancer</span>
            <span className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-900 border border-gray-800"><Zap className="w-4 h-4 text-amber-400" /> API Gateway Rate Limiter</span>
            <span className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-900 border border-gray-800"><ShieldCheck className="w-4 h-4 text-emerald-400" /> Stateless JWT Auth</span>
            <span className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gray-900 border border-gray-800"><MapPin className="w-4 h-4 text-purple-400" /> Redis Cache & PostgreSQL</span>
          </div>
        </div>
      </section>
    </div>
  );
};
