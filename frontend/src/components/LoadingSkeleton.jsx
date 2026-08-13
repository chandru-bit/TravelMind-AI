import React from 'react';

export const LoadingSkeleton = ({ count = 3 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, idx) => (
        <div key={idx} className="glass-panel rounded-2xl p-6 border border-gray-800 animate-pulse space-y-4">
          <div className="h-4 bg-gray-800 rounded w-1/3" />
          <div className="h-6 bg-gray-800 rounded w-2/3" />
          <div className="space-y-2">
            <div className="h-3 bg-gray-800 rounded w-full" />
            <div className="h-3 bg-gray-800 rounded w-4/5" />
          </div>
          <div className="h-10 bg-gray-800 rounded-xl" />
        </div>
      ))}
    </div>
  );
};
