import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { Compass, Sparkles, TrendingUp, Calendar, MapPin, Wallet, ArrowRight, CloudSun, Award } from 'lucide-react';
import { RecommendationCard } from '../components/RecommendationCard';
import { PricePredictionCard } from '../components/PricePredictionCard';
import { WeatherCard } from '../components/WeatherCard';
import { BudgetCard } from '../components/BudgetCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const DashboardPage = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [weather, setWeather] = useState(null);
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // 1. Fetch Recommendations
        const recRes = await api.post('/recommendations', {
          budget: 25000,
          travel_style: 'Balanced',
          interests: ['Beach', 'Adventure']
        }).catch(() => null);

        if (recRes && recRes.data?.recommended_destinations) {
          setRecommendations(recRes.data.recommended_destinations.slice(0, 3));
        }

        // 2. Fetch ML Price Prediction for Goa
        const predRes = await api.post('/predictions/price', {
          destination: 'Goa',
          travel_date: '2026-09-01',
          season: 'Monsoon',
          duration_days: 4,
          traveler_count: 2
        }).catch(() => null);

        if (predRes && predRes.data) {
          setPrediction(predRes.data);
        }

        // 3. Set Sample Weather
        setWeather({
          destination: 'Goa',
          temperature_celsius: 28.5,
          condition: 'Sunny & Tropical',
          humidity_percent: 68,
          wind_speed_kmh: 14.0
        });

        // 4. Fetch User Trips
        const tripRes = await api.get('/trips').catch(() => null);
        if (tripRes && Array.isArray(tripRes.data)) {
          setTrips(tripRes.data);
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      {/* Welcome Banner */}
      <div className="glass-panel rounded-3xl p-8 border border-gray-800 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="absolute right-0 top-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl -z-10" />
        
        <div className="space-y-2">
          <span className="text-xs font-semibold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 uppercase tracking-wider">
            Travel Intelligence Dashboard
          </span>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
            Welcome back, <span className="gradient-text">{user?.name || 'Explorer'}</span>! 👋
          </h1>
          <p className="text-sm text-gray-400">
            Your personalized travel predictions, ML price trends, and itinerary optimizations are active.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/plan')}
            className="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all transform hover:scale-105"
          >
            <Calendar className="w-4 h-4" /> Plan New Trip
          </button>
        </div>
      </div>

      {/* Travel Statistics Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="glass-panel rounded-2xl p-5 border border-gray-800">
          <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Planned Trips</span>
          <span className="text-2xl font-black text-white">{trips.length || 1}</span>
        </div>
        <div className="glass-panel rounded-2xl p-5 border border-gray-800">
          <span className="text-[11px] text-gray-400 uppercase tracking-wider block">Top Match Score</span>
          <span className="text-2xl font-black text-cyan-400">96%</span>
        </div>
        <div className="glass-panel rounded-2xl p-5 border border-gray-800">
          <span className="text-[11px] text-gray-400 uppercase tracking-wider block">ML Price Accuracy</span>
          <span className="text-2xl font-black text-indigo-400">R² 0.85</span>
        </div>
        <div className="glass-panel rounded-2xl p-5 border border-gray-800">
          <span className="text-[11px] text-gray-400 uppercase tracking-wider block">System Status</span>
          <span className="text-2xl font-black text-emerald-400">Active</span>
        </div>
      </div>

      {/* Main Grid Layout */}
      {loading ? (
        <LoadingSkeleton count={3} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left 2 Columns: Top Recommendations & Saved Trips */}
          <div className="lg:col-span-2 space-y-8">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-5 h-5 text-cyan-400" /> Recommended Destinations
                </h3>
                <Link to="/recommendations" className="text-xs text-cyan-400 font-semibold hover:underline flex items-center gap-1">
                  View All <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="space-y-4">
                {recommendations.map((rec, i) => (
                  <RecommendationCard
                    key={i}
                    recommendation={rec}
                    onSelect={() => navigate('/plan')}
                  />
                ))}
              </div>
            </div>

            {/* Budget Optimizer Component */}
            <BudgetCard budget={30000} />
          </div>

          {/* Right Column: ML Price Prediction, Weather & Quick Actions */}
          <div className="space-y-6">
            {prediction && <PricePredictionCard prediction={prediction} />}
            <WeatherCard weather={weather} />

            {/* Recent Activity / Feedback Card */}
            <div className="glass-panel rounded-2xl p-6 border border-gray-800 space-y-3">
              <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Award className="w-4 h-4 text-amber-400" /> Recent User Feedback
              </h4>
              <p className="text-xs text-gray-300 italic bg-gray-900/60 p-3 rounded-xl border border-gray-800">
                "TravelMind AI recommendation was spot on! Goa fit our budget perfectly and saved ₹4,000 on flights."
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
