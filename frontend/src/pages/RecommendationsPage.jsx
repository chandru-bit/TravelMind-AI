import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Compass, Sparkles, Filter, Search } from 'lucide-react';
import { RecommendationCard } from '../components/RecommendationCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const RecommendationsPage = () => {
  const navigate = useNavigate();
  const [budget, setBudget] = useState(25000);
  const [travelStyle, setTravelStyle] = useState('Balanced');
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const res = await api.post('/recommendations', {
        budget: parseFloat(budget),
        travel_style: travelStyle,
        interests: ['Beach', 'Adventure', 'Culture']
      });
      if (res.data?.recommended_destinations) {
        setRecommendations(res.data.recommended_destinations);
      }
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 uppercase tracking-wider">
            Deterministic Weighted Engine
          </span>
          <h1 className="text-3xl font-extrabold text-white mt-1">Destination Explorer</h1>
          <p className="text-sm text-gray-400">
            Weighted match formula: Budget (25%) + Interest (30%) + Weather (15%) + Activity (15%) + Distance (15%)
          </p>
        </div>

        {/* Filter Controls */}
        <div className="glass-panel rounded-2xl p-3 border border-gray-800 flex items-center gap-3">
          <Filter className="w-4 h-4 text-cyan-400 ml-2" />
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-400">Budget:</span>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-24 bg-gray-900 border border-gray-700 rounded-lg px-2 py-1 text-xs text-white"
            />
          </div>
          <button
            onClick={fetchRecommendations}
            className="px-3 py-1 bg-cyan-500 hover:bg-cyan-400 text-white rounded-lg text-xs font-bold transition-all"
          >
            Calculate Scores
          </button>
        </div>
      </div>

      {loading ? (
        <LoadingSkeleton count={4} />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommendations.map((rec, i) => (
            <RecommendationCard
              key={i}
              recommendation={rec}
              onSelect={(item) => navigate('/plan', { state: { destination: item.destination || item.name, budget: item.estimated_cost || item.avg_cost } })}
            />
          ))}
        </div>
      )}
    </div>
  );
};
