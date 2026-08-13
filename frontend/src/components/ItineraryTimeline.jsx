import React, { useState } from 'react';
import { Clock, MapPin, DollarSign, Plus, Trash2, Edit3, Sparkles, CheckCircle2 } from 'lucide-react';

export const ItineraryTimeline = ({ itinerary, onAddItem, onDeleteItem }) => {
  const [activeDay, setActiveDay] = useState(1);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newItem, setNewItem] = useState({
    time: '10:00 AM',
    activity: '',
    location: '',
    duration: '2 hours',
    estimated_cost: 1000,
    travel_time: '15 mins',
    description: ''
  });

  const items = itinerary?.items || [];
  const totalDays = itinerary?.total_days || 3;
  const isAiGenerated = itinerary?.is_ai_generated;
  const statusMessage = itinerary?.ai_status_message;

  const filteredItems = items.filter((item) => item.day_number === activeDay);

  const handleAddSubmit = (e) => {
    e.preventDefault();
    if (!newItem.activity) return;
    if (onAddItem) {
      onAddItem({ ...newItem, day_number: activeDay });
    }
    setShowAddModal(false);
    setNewItem({
      time: '10:00 AM',
      activity: '',
      location: '',
      duration: '2 hours',
      estimated_cost: 1000,
      travel_time: '15 mins',
      description: ''
    });
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-gray-800 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-gray-800 pb-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${
              isAiGenerated
                ? 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20'
                : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
            }`}>
              {isAiGenerated ? 'AI Personalized' : 'Standard Fallback'}
            </span>
            <span className="text-xs text-gray-400">{itinerary?.destination || 'Goa'}</span>
          </div>
          <h3 className="text-xl font-bold text-white">Day-by-Day Timeline Itinerary</h3>
          {statusMessage && (
            <p className="text-xs text-cyan-300 mt-1 italic flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> {statusMessage}
            </p>
          )}
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-3.5 py-2 rounded-xl bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500 hover:text-white text-xs font-semibold flex items-center gap-1.5 transition-all self-start sm:self-auto border border-cyan-500/30"
        >
          <Plus className="w-4 h-4" /> Add Custom Activity
        </button>
      </div>

      {/* Day Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-gray-800 pb-3 overflow-x-auto">
        {Array.from({ length: totalDays }, (_, i) => i + 1).map((dayNum) => (
          <button
            key={dayNum}
            onClick={() => setActiveDay(dayNum)}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
              activeDay === dayNum
                ? 'bg-cyan-500 text-white shadow-lg shadow-cyan-500/20'
                : 'bg-gray-800/60 text-gray-400 hover:bg-gray-800 hover:text-white'
            }`}
          >
            Day {dayNum}
          </button>
        ))}
      </div>

      {/* Timeline Items */}
      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-gradient-to-b before:from-cyan-500 before:via-indigo-500 before:to-gray-800">
        {filteredItems.length === 0 ? (
          <div className="text-center py-8 text-xs text-gray-500">
            No activities scheduled for Day {activeDay}. Click "+ Add Custom Activity" to insert an item.
          </div>
        ) : (
          filteredItems.map((item, idx) => (
            <div key={item.id || idx} className="relative group">
              {/* Timeline Dot */}
              <div className="absolute -left-6 top-1.5 w-5 h-5 rounded-full bg-cyan-950 border-2 border-cyan-400 flex items-center justify-center text-cyan-400">
                <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              </div>

              {/* Item Card */}
              <div className="glass-panel rounded-xl p-4 border border-gray-800/80 hover:border-cyan-500/30 transition-all space-y-2">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 text-xs font-semibold text-cyan-400">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{item.time}</span>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-400">{item.duration}</span>
                  </div>

                  {onDeleteItem && item.id && (
                    <button
                      onClick={() => onDeleteItem(item.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-rose-400 transition-opacity"
                      title="Delete Item"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>

                <h4 className="text-base font-bold text-white">{item.activity}</h4>

                <div className="flex flex-wrap items-center gap-4 text-xs text-gray-400">
                  <span className="flex items-center gap-1 text-gray-300">
                    <MapPin className="w-3.5 h-3.5 text-cyan-400" /> {item.location}
                  </span>
                  <span>Est. Cost: <strong className="text-white">₹{item.estimated_cost ? item.estimated_cost.toLocaleString() : '500'}</strong></span>
                  <span>Travel: {item.travel_time}</span>
                </div>

                {item.description && (
                  <p className="text-xs text-gray-400 pt-1 leading-relaxed border-t border-gray-800/50">
                    {item.description}
                  </p>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Add Item Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel rounded-2xl p-6 max-w-md w-full border border-gray-800 space-y-4">
            <h4 className="text-lg font-bold text-white">Add Activity to Day {activeDay}</h4>
            
            <form onSubmit={handleAddSubmit} className="space-y-3 text-xs">
              <div>
                <label className="block text-gray-300 mb-1">Time</label>
                <input
                  type="text"
                  value={newItem.time}
                  onChange={(e) => setNewItem({ ...newItem, time: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white"
                  placeholder="e.g. 03:00 PM"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-1">Activity Name *</label>
                <input
                  type="text"
                  required
                  value={newItem.activity}
                  onChange={(e) => setNewItem({ ...newItem, activity: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white"
                  placeholder="e.g. Sunset Boat Cruise"
                />
              </div>

              <div>
                <label className="block text-gray-300 mb-1">Location</label>
                <input
                  type="text"
                  value={newItem.location}
                  onChange={(e) => setNewItem({ ...newItem, location: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white"
                  placeholder="e.g. Mandovi River Jetty"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-gray-300 mb-1">Est Cost (₹)</label>
                  <input
                    type="number"
                    value={newItem.estimated_cost}
                    onChange={(e) => setNewItem({ ...newItem, estimated_cost: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-gray-300 mb-1">Duration</label>
                  <input
                    type="text"
                    value={newItem.duration}
                    onChange={(e) => setNewItem({ ...newItem, duration: e.target.value })}
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white"
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-300 mb-1">Description</label>
                <textarea
                  rows={2}
                  value={newItem.description}
                  onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                  className="w-full bg-gray-900 border border-gray-700 rounded-lg p-2.5 text-white"
                  placeholder="Additional details..."
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-lg bg-gray-800 text-gray-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-cyan-500 text-white font-bold"
                >
                  Add Activity
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
