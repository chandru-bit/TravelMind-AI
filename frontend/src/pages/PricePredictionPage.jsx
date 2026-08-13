import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { TrendingUp, Sparkles, AlertCircle, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { PricePredictionCard } from '../components/PricePredictionCard';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const PricePredictionPage = () => {
  const [destination, setDestination] = useState('Goa');
  const [season, setSeason] = useState('Monsoon');
  const [duration, setDuration] = useState(4);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchPrediction = async () => {
    setLoading(true);
    try {
      const res = await api.post('/predictions/price', {
        destination,
        travel_date: '2026-09-01',
        season,
        duration_days: parseInt(duration, 10),
        traveler_count: 2
      });
      setPrediction(res.data);
    } catch (err) {
      console.error("Prediction fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrediction();
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 space-y-8">
      <div className="text-center space-y-2">
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 uppercase tracking-wider">
          Machine Learning Forecast
        </span>
        <h1 className="text-3xl font-extrabold text-white">Price Trend Predictor</h1>
        <p className="text-sm text-gray-400">
          Scikit-Learn Linear Regression model analyzing historical demand, season factors, and prices.
        </p>
      </div>

      <div className="glass-panel rounded-3xl p-6 border border-gray-800 space-y-4 max-w-2xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Destination</label>
            <select
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl p-2.5 text-xs text-white"
            >
              <option value="Goa">Goa</option>
              <option value="Manali">Manali</option>
              <option value="Andaman">Andaman</option>
              <option value="Ooty">Ooty</option>
              <option value="Jaipur">Jaipur</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">Season</label>
            <select
              value={season}
              onChange={(e) => setSeason(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl p-2.5 text-xs text-white"
            >
              <option value="Peak">Peak Season</option>
              <option value="Regular">Regular Season</option>
              <option value="Off-Season">Off-Season</option>
              <option value="Monsoon">Monsoon</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-1">Duration (Days)</label>
            <input
              type="number"
              min={1}
              max={30}
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl p-2.5 text-xs text-white"
            />
          </div>
        </div>

        <button
          onClick={fetchPrediction}
          className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all"
        >
          Run ML Prediction Pipeline
        </button>
      </div>

      {loading ? (
        <LoadingSkeleton count={1} />
      ) : (
        prediction && (
          <div className="max-w-2xl mx-auto space-y-6">
            <PricePredictionCard prediction={prediction} />
          </div>
        )
      )}
    </div>
  );
};
