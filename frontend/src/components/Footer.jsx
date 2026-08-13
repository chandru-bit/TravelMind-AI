import React from 'react';
import { Compass, Heart, Github, Server, Database, Cpu, Shield } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="border-t border-gray-800 bg-[#070a12] py-12 px-4 sm:px-6 lg:px-8 mt-20 text-gray-400 text-sm">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Compass className="w-5 h-5" />
            </div>
            <span className="font-bold text-white text-lg">TravelMind AI</span>
          </div>
          <p className="text-xs leading-relaxed text-gray-400">
            Next-generation travel intelligence platform powered by microservices, Scikit-Learn machine learning, and AI recommendation engines.
          </p>
          <div className="text-xs text-cyan-400 font-semibold uppercase tracking-wider">
            "Predict. Personalize. Plan."
          </div>
        </div>

        <div>
          <h4 className="text-white font-semibold text-sm mb-3">System Architecture</h4>
          <ul className="space-y-2 text-xs">
            <li className="flex items-center gap-2"><Server className="w-3.5 h-3.5 text-cyan-400" /> FastAPI Microservices</li>
            <li className="flex items-center gap-2"><Cpu className="w-3.5 h-3.5 text-indigo-400" /> Scikit-Learn ML Predictor</li>
            <li className="flex items-center gap-2"><Database className="w-3.5 h-3.5 text-emerald-400" /> PostgreSQL & Redis Cache</li>
            <li className="flex items-center gap-2"><Shield className="w-3.5 h-3.5 text-purple-400" /> Nginx & API Gateway</li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold text-sm mb-3">Core Features</h4>
          <ul className="space-y-2 text-xs">
            <li>Personalized Destination Engine</li>
            <li>ML Flight & Hotel Price Predictions</li>
            <li>Day-by-Day Timeline Itineraries</li>
            <li>Dynamic Budget Optimizer</li>
            <li>Live & Cached Weather Feed</li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold text-sm mb-3">Tech Stack</h4>
          <div className="flex flex-wrap gap-1.5 text-[11px]">
            {['React', 'Vite', 'Tailwind CSS', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker', 'Scikit-Learn', 'Nginx'].map((tech) => (
              <span key={tech} className="px-2 py-1 rounded bg-gray-800/80 text-gray-300 border border-gray-700">
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto pt-6 border-t border-gray-800/60 flex flex-col md:flex-row items-center justify-between text-xs gap-4">
        <div>
          © {new Date().getFullYear()} TravelMind AI Platform. Built for Production & System Design Demonstration.
        </div>
        <div className="flex items-center gap-2 text-gray-400">
          <span>Engineered with precision for Portfolio & College Capstone</span>
        </div>
      </div>
    </footer>
  );
};
