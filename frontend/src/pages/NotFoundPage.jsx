import React from 'react';
import { Link } from 'react-router-dom';
import { Compass, Home } from 'lucide-react';

export const NotFoundPage = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center px-4 space-y-6">
      <div className="w-16 h-16 rounded-2xl bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
        <Compass className="w-8 h-8 animate-spin-slow" />
      </div>
      <h1 className="text-6xl font-black text-white">404</h1>
      <h2 className="text-2xl font-bold text-gray-200">Destination Not Found</h2>
      <p className="text-sm text-gray-400 max-w-md">
        The travel page or itinerary route you are looking for does not exist or has moved.
      </p>
      <Link
        to="/dashboard"
        className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold text-xs shadow-lg flex items-center gap-2"
      >
        <Home className="w-4 h-4" /> Return to Dashboard
      </Link>
    </div>
  );
};
