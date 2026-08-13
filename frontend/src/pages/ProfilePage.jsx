import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';
import { User, Mail, MapPin, DollarSign, Sparkles, Check, Save } from 'lucide-react';

export const ProfilePage = () => {
  const { user, setUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [homeLocation, setHomeLocation] = useState('Mumbai');
  const [budget, setBudget] = useState(25000);
  const [travelStyle, setTravelStyle] = useState('Balanced');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        const res = await api.get('/users/me');
        if (res.data) {
          setName(res.data.name);
          if (res.data.preferences) {
            setHomeLocation(res.data.preferences.home_location || 'Mumbai');
            setBudget(res.data.preferences.budget || 25000);
            setTravelStyle(res.data.preferences.travel_style || 'Balanced');
          }
        }
      } catch (err) {
        console.error("Profile fetch error:", err);
      }
    };
    fetchProfileData();
  }, []);

  const handleUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      // 1. Update Name
      const userRes = await api.put(`/users/me?name=${encodeURIComponent(name)}`);
      if (userRes.data) setUser(userRes.data);

      // 2. Update Preferences
      await api.put('/users/me/preferences', {
        home_location: homeLocation,
        budget: parseFloat(budget),
        travel_style: travelStyle,
        interests: ['Beach', 'Adventure'],
        food_preference: 'No Restrictions',
        traveler_count: 2,
        preferred_destinations: ['Goa', 'Kodaikanal']
      });

      setMessage('Profile and preferences updated successfully!');
    } catch (err) {
      setMessage('Failed to update profile.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 space-y-8">
      <div className="text-center space-y-2">
        <div className="w-16 h-16 rounded-full bg-cyan-500/20 text-cyan-400 font-extrabold text-2xl flex items-center justify-center mx-auto mb-2 border border-cyan-500/30">
          {name ? name[0].toUpperCase() : 'U'}
        </div>
        <h1 className="text-3xl font-extrabold text-white">User Profile & Preferences</h1>
        <p className="text-sm text-gray-400">{user?.email}</p>
      </div>

      {message && (
        <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs text-center font-bold">
          {message}
        </div>
      )}

      <form onSubmit={handleUpdate} className="glass-panel rounded-3xl p-8 border border-gray-800 space-y-6">
        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1.5">Full Name</label>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Home Location</label>
            <input
              type="text"
              value={homeLocation}
              onChange={(e) => setHomeLocation(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-1.5">Standard Budget (₹)</label>
            <input
              type="number"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-gray-300 mb-1.5">Travel Style</label>
          <select
            value={travelStyle}
            onChange={(e) => setTravelStyle(e.target.value)}
            className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
          >
            <option value="Budget">Budget</option>
            <option value="Balanced">Balanced</option>
            <option value="Premium">Premium</option>
            <option value="Luxury">Luxury</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold text-sm shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2"
        >
          <Save className="w-4 h-4" /> Save Profile & Preferences
        </button>
      </form>
    </div>
  );
};
