import React from 'react';
import { Sparkles, CheckCircle2, CloudSun, DollarSign, Calendar, ArrowRight } from 'lucide-react';

export const RecommendationCard = ({ recommendation, onSelect }) => {
  const {
    destination,
    state_country,
    match_percentage,
    estimated_cost,
    best_season,
    weather_summary,
    recommendation_reasons,
    breakdown_scores
  } = recommendation;

  return (
    <div className="glass-panel glass-panel-hover rounded-2xl p-6 relative overflow-hidden border-l-4 border-l-cyan-500">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-cyan-400 font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/20">
              {state_country}
            </span>
            <span className="text-xs text-gray-400">Best Season: {best_season}</span>
          </div>
          <h3 className="text-2xl font-extrabold text-white tracking-tight">{destination}</h3>
        </div>

        {/* Match Percentage Pill */}
        <div className="flex items-center gap-3 bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 px-4 py-2 rounded-2xl self-start md:self-auto">
          <Sparkles className="w-5 h-5 text-cyan-400 animate-spin-slow" />
          <div>
            <div className="text-2xl font-black text-cyan-400 leading-none">{match_percentage}%</div>
            <div className="text-[10px] uppercase tracking-wider text-cyan-300 font-semibold">Match Score</div>
          </div>
        </div>
      </div>

      {/* Reasons List */}
      <div className="bg-gray-900/60 rounded-xl p-4 mb-4 border border-gray-800 space-y-2">
        <div className="text-xs font-bold text-gray-300 uppercase tracking-wider mb-1 flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Recommendation Reasons
        </div>
        {recommendation_reasons && recommendation_reasons.map((reason, idx) => (
          <p key={idx} className="text-xs text-gray-300 leading-relaxed pl-5 relative before:content-['•'] before:absolute before:left-1.5 before:text-cyan-400 font-medium">
            "{reason}"
          </p>
        ))}
      </div>

      {/* Breakdown Score Bars */}
      {breakdown_scores && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-4 text-center">
          {Object.entries(breakdown_scores).map(([key, val]) => (
            <div key={key} className="bg-gray-800/40 rounded-lg p-2 border border-gray-800">
              <div className="text-[10px] text-gray-400 uppercase tracking-wider">{key}</div>
              <div className="text-sm font-bold text-cyan-400">{Math.round(val * 100)}%</div>
            </div>
          ))}
        </div>
      )}

      {/* Footer Info */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-800">
        <div className="flex items-center gap-4 text-xs text-gray-400">
          <span className="flex items-center gap-1"><CloudSun className="w-3.5 h-3.5 text-cyan-400" /> {weather_summary}</span>
          <span className="font-bold text-white text-sm">Est. ₹{estimated_cost ? estimated_cost.toLocaleString() : '20,000'}</span>
        </div>

        {onSelect && (
          <button
            onClick={() => onSelect(recommendation)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-cyan-500/20 flex items-center gap-1.5 transition-all transform hover:scale-105"
          >
            Plan Trip <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
};
