import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { Compass, Calendar, MapPin, DollarSign, Users, Sparkles, ArrowRight, CheckCircle2, Plane, Hotel, Ticket } from 'lucide-react';
import { ItineraryTimeline } from '../components/ItineraryTimeline';
import { BudgetCard } from '../components/BudgetCard';

export const PlanTripPage = () => {
  const navigate = useNavigate();
  const [source, setSource] = useState('Mumbai');
  const [destination, setDestination] = useState('Goa');
  const [startDate, setStartDate] = useState('2026-09-10');
  const [endDate, setEndDate] = useState('2026-09-14');
  const [budget, setBudget] = useState(30000);
  const [travelers, setTravelers] = useState(2);
  const [travelStyle, setTravelStyle] = useState('Balanced');
  const [interests, setInterests] = useState(['Beach', 'Adventure']);
  const [loading, setLoading] = useState(false);
  const [createdTrip, setCreatedTrip] = useState(null);
  const [itinerary, setItinerary] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // 1. Create Trip in Trip Service
      const tripRes = await api.post('/trips', {
        source,
        destination,
        start_date: startDate,
        end_date: endDate,
        budget: parseFloat(budget),
        traveler_count: parseInt(travelers, 10),
        interests,
        travel_style: travelStyle
      });
      setCreatedTrip(tripRes.data);

      // 2. Generate AI / Fallback Itinerary
      const aiRes = await api.post('/ai/itinerary', {
        destination,
        start_date: startDate,
        end_date: endDate,
        budget: parseFloat(budget),
        travel_style: travelStyle,
        interests,
        traveler_count: parseInt(travelers, 10)
      }).catch(() => null);

      if (aiRes && aiRes.data) {
        setItinerary(aiRes.data);
      } else {
        // Fetch trip service generated itinerary
        const itinRes = await api.get(`/trips/${tripRes.data.id}/itinerary`).catch(() => null);
        if (itinRes) setItinerary(itinRes.data);
      }
    } catch (err) {
      console.error("Trip creation failed:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      <div className="text-center space-y-2 max-w-2xl mx-auto">
        <span className="text-xs font-semibold px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 uppercase tracking-wider">
          Intelligent Itinerary Generator
        </span>
        <h1 className="text-3xl font-extrabold text-white">Plan Your Next Trip</h1>
        <p className="text-sm text-gray-400">
          Enter trip details to calculate budget allocations, predictions, and personalized itineraries.
        </p>
      </div>

      {!createdTrip ? (
        <form onSubmit={handleSubmit} className="glass-panel rounded-3xl p-8 border border-gray-800 space-y-6 max-w-3xl mx-auto shadow-2xl">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Source Location</label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-cyan-400 absolute left-3 top-3.5" />
                <input
                  type="text"
                  required
                  value={source}
                  onChange={(e) => setSource(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-xl pl-9 pr-4 py-3 text-sm text-white"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Destination City</label>
              <div className="relative">
                <Compass className="w-4 h-4 text-indigo-400 absolute left-3 top-3.5" />
                <input
                  type="text"
                  required
                  value={destination}
                  onChange={(e) => setDestination(e.target.value)}
                  className="w-full bg-gray-900 border border-gray-700 rounded-xl pl-9 pr-4 py-3 text-sm text-white"
                />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Start Date</label>
              <input
                type="date"
                required
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">End Date</label>
              <input
                type="date"
                required
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Total Budget (₹)</label>
              <input
                type="number"
                required
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Travelers</label>
              <input
                type="number"
                min={1}
                value={travelers}
                onChange={(e) => setTravelers(e.target.value)}
                className="w-full bg-gray-900 border border-gray-700 rounded-xl px-4 py-3 text-sm text-white"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-gray-300 mb-2">Travel Style</label>
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
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-extrabold text-base shadow-xl shadow-cyan-500/25 flex items-center justify-center gap-2 transition-all"
          >
            {loading ? 'Generating Personalized Itinerary...' : 'Generate Trip Plan'} <Sparkles className="w-5 h-5" />
          </button>
        </form>
      ) : (
        /* Detailed Itinerary View */
        <div className="space-y-8">
          <div className="flex items-center justify-between p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs">
            <span className="flex items-center gap-2 font-bold">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" /> Trip to {createdTrip.destination} successfully created & saved!
            </span>
            <button
              onClick={() => setCreatedTrip(null)}
              className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded-lg text-white font-semibold"
            >
              Plan Another
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <ItineraryTimeline itinerary={itinerary} />
            </div>

            <div className="space-y-6">
              <BudgetCard budget={createdTrip.budget} />

              {/* Booking Recommendations Cards (FR-13) */}
              <div className="glass-panel rounded-2xl p-6 border border-gray-800 space-y-4">
                <h4 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Ticket className="w-4 h-4 text-cyan-400" /> Demo Booking Recommendations
                </h4>

                <div className="space-y-3">
                  <div className="p-3 rounded-xl bg-gray-900 border border-gray-800 flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <Plane className="w-4 h-4 text-cyan-400" />
                      <div>
                        <div className="text-xs font-bold text-white">Indigo / Air India Flight</div>
                        <div className="text-[10px] text-gray-400">Direct • 1h 45m</div>
                      </div>
                    </div>
                    <span className="text-xs font-extrabold text-cyan-400">₹4,200</span>
                  </div>

                  <div className="p-3 rounded-xl bg-gray-900 border border-gray-800 flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <Hotel className="w-4 h-4 text-indigo-400" />
                      <div>
                        <div className="text-xs font-bold text-white">Grand Resort & Spa</div>
                        <div className="text-[10px] text-gray-400">4 Star • Ocean View</div>
                      </div>
                    </div>
                    <span className="text-xs font-extrabold text-indigo-400">₹3,500/night</span>
                  </div>
                </div>

                <div className="text-[10px] text-gray-400 text-center italic border-t border-gray-800 pt-2">
                  Demo booking integration — Payments simulated.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
