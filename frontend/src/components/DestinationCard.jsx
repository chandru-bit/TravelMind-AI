import React from 'react';
import { MapPin, Calendar, DollarSign, Star, Compass } from 'lucide-react';

export const DestinationCard = ({ destination, onSelect }) => {
  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-5 flex flex-col justify-between relative overflow-hidden group">
      {/* Background Subtle Gradient Overlay */}
      <div className="absolute -right-10 -top-10 w-32 h-32 bg-cyan-500/10 rounded-full blur-2xl group-hover:bg-cyan-500/20 transition-all"></div>

      <div>
        <div className="flex items-start justify-between gap-2 mb-3">
          <div>
            <span className="inline-flex items-center gap-1 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-1">
              <MapPin className="w-3 h-3" /> {destination.state_country}
            </span>
            <h3 className="text-xl font-bold text-white group-hover:text-cyan-400 transition-colors">
              {destination.name}
            </h3>
          </div>
          <div className="flex items-center gap-1 bg-amber-500/10 text-amber-400 px-2 py-1 rounded-lg text-xs font-bold border border-amber-500/20">
            <Star className="w-3.5 h-3.5 fill-amber-400" />
            {destination.popularity ? destination.popularity : 90}%
          </div>
        </div>

        <p className="text-xs text-gray-400 mb-4 line-clamp-2">
          {destination.weather_summary}
        </p>

        {/* Tags */}
        <div className="flex flex-wrap gap-1.5 mb-4">
          {destination.activities && destination.activities.slice(0, 3).map((act, i) => (
            <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
              {act}
            </span>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t border-gray-800 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Estimated Cost</span>
          <span className="text-lg font-extrabold text-white">₹{destination.avg_cost ? destination.avg_cost.toLocaleString() : '20,000'}</span>
        </div>

        {onSelect && (
          <button
            onClick={() => onSelect(destination)}
            className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500 hover:text-white transition-all flex items-center gap-1"
          >
            <Compass className="w-3.5 h-3.5" /> Plan Trip
          </button>
        )}
      </div>
    </div>
  );
};
