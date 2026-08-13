import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Compass, Sparkles, MapPin, DollarSign, Users, Check, ArrowRight } from 'lucide-react';

const TRAVEL_STYLES = ['Budget', 'Balanced', 'Premium', 'Luxury'];
const INTERESTS = [
  'Beach', 'Mountains', 'Adventure', 'Nature', 'Culture',
  'History', 'Food', 'Shopping', 'Nightlife', 'Photography',
  'Spiritual', 'Luxury'
];

export const OnboardingPage = () => {
  const navigate = useNavigate();
  const [homeLocation, setHomeLocation] = useState('Mumbai');
  const [budget, setBudget] = useState(25000);
  const [travelStyle, setTravelStyle] = useState('Balanced');
  const [selectedInterests, setSelectedInterests] = useState(['Beach', 'Adventure', 'Food']);
  const [travelerCount, setTravelerCount] = useState(2);
  const [foodPreference, setFoodPreference] = useState('No Restrictions');
  const [loading, setLoading] = useState(false);

  const toggleInterest = (interest) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter((i) => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const handleSavePreferences = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await api.put('/users/me/preferences', {
        home_location: homeLocation,
        budget: parseFloat(budget),
        travel_style: travelStyle,
        interests: selectedInterests,
        food_preference: foodPreference,
        traveler_count: parseInt(travelerCount, 10),
        preferred_destinations: ['Goa', 'Kodaikanal']
      });
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to save preferences:', err);
      // Navigate anyway for demo UX
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="glass-panel rounded-3xl p-8 sm:p-12 border border-gray-800 space-y-8 shadow-2xl">
        <div className="text-center space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase">
            <Sparkles className="w-3.5 h-3.5" /> Personalized Engine Setup
          </div>
          <h2 className="text-3xl font-extrabold text-white">Customize Your Travel Profile</h2>
          <p className="text-sm text-gray-400">
            Tell us your travel preferences so TravelMind AI can tailor predictions & recommendations.
          </p>
        </div>

        <form onSubmit={handleSavePreferences} className="space-y-8">
          {/* Home Location & Travelers */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Home Location</label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-cyan-400 absolute left-3 top-3.5" />
                <input
                  type="text"
                  required
                  value={homeLocation}
                  onChange={(e) => setHomeLocation(e.target.value)}
                  placeholder="e.g. Mumbai, Bengaluru"
                  className="w-full bg-gray-900 border border-gray-700 focus:border-cyan-500 rounded-xl pl-9 pr-4 py-3 text-sm text-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Standard Budget (₹)</label>
              <div className="relative">
                <DollarSign className="w-4 h-4 text-emerald-400 absolute left-3 top-3.5" />
                <input
                  type="number"
                  required
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 focus:border-cyan-500 rounded-xl pl-9 pr-4 py-3 text-sm text-white"
                />
              </div>
            </div>
          </div>

          {/* Travel Style Selector */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-3">Travel Style</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {TRAVEL_STYLES.map((style) => (
                <button
                  type="button"
                  key={style}
                  onClick={() => setTravelStyle(style)}
                  className={`p-3.5 rounded-xl border text-xs font-bold text-center transition-all ${
                    travelStyle === style
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-lg shadow-cyan-500/10'
                      : 'bg-gray-900/60 text-gray-400 border-gray-800 hover:border-gray-700'
                  }`}
                >
                  {style}
                </button>
              ))}
            </div>
          </div>

          {/* Interests Grid */}
          <div>
            <label className="block text-xs font-semibold text-gray-300 mb-3">
              Select Your Interests (Multi-select)
            </label>
            <div className="flex flex-wrap gap-2">
              {INTERESTS.map((interest) => {
                const isSelected = selectedInterests.includes(interest);
                return (
                  <button
                    type="button"
                    key={interest}
                    onClick={() => toggleInterest(interest)}
                    className={`px-3.5 py-2 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all ${
                      isSelected
                        ? 'bg-gradient-to-r from-cyan-500 to-indigo-600 text-white shadow-md'
                        : 'bg-gray-900 border border-gray-800 text-gray-400 hover:text-white'
                    }`}
                  >
                    {isSelected && <Check className="w-3.5 h-3.5" />}
                    {interest}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Food & Group Size */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Food Preference</label>
              <select
                value={foodPreference}
                onChange={(e) => setFoodPreference(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm text-white"
              >
                <option value="No Restrictions">No Restrictions</option>
                <option value="Vegetarian">Vegetarian</option>
                <option value="Vegan">Vegan</option>
                <option value="Seafood Specialist">Seafood Specialist</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Default Traveler Count</label>
              <input
                type="number"
                min={1}
                max={20}
                value={travelerCount}
                onChange={(e) => setTravelerCount(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 focus:border-cyan-500 rounded-xl px-4 py-3 text-sm text-white"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-extrabold text-base shadow-xl shadow-cyan-500/25 flex items-center justify-center gap-2 transition-all transform hover:-translate-y-0.5"
          >
            {loading ? 'Saving Preferences...' : 'Save & Enter Dashboard'} <ArrowRight className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
};
