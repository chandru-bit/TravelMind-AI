import React from 'react';
import { Info, Cpu } from 'lucide-react';

export const DemoBanner = () => {
  return (
    <div className="bg-gradient-to-r from-cyan-900/60 via-indigo-900/60 to-purple-900/60 border-b border-cyan-500/20 px-4 py-2 text-xs sm:text-sm text-cyan-200 backdrop-blur-md flex items-center justify-between shadow-lg">
      <div className="flex items-center gap-2 max-w-7xl mx-auto w-full justify-center text-center">
        <Cpu className="w-4 h-4 text-cyan-400 animate-pulse" />
        <span className="font-semibold text-white bg-cyan-500/20 px-2 py-0.5 rounded border border-cyan-400/30 uppercase tracking-wider">
          Demo Mode Active
        </span>
        <span className="hidden md:inline">
          Running with 15 pre-seeded destinations, Scikit-Learn price prediction ML model, and AI fallback logic.
        </span>
      </div>
    </div>
  );
};
