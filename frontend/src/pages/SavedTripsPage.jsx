import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { billingApi } from '../api/client';
import { Calendar, MapPin, Trash2, ArrowRight, Compass, FileText, Download } from 'lucide-react';
import { LoadingSkeleton } from '../components/LoadingSkeleton';

export const SavedTripsPage = () => {
  const navigate = useNavigate();
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTrips = async () => {
    setLoading(true);
    try {
      const res = await api.get('/trips');
      if (Array.isArray(res.data)) {
        setTrips(res.data);
      }
    } catch (err) {
      console.error("Failed to fetch trips:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (tripId) => {
    try {
      await api.delete(`/trips/${tripId}`);
      setTrips(trips.filter((t) => t.id !== tripId));
    } catch (err) {
      console.error("Failed to delete trip:", err);
    }
  };

  const handleDownloadInvoice = async (tripId) => {
    try {
      const res = await billingApi.downloadInvoicePdf(tripId);
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `invoice-${tripId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Download failed:", err);
      navigate(`/billing/booking/${tripId}`);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold text-white">Your Saved Trips & Bookings</h1>
          <p className="text-sm text-gray-400">View itineraries, room bookings, invoices, and billing history</p>
        </div>
        <button
          onClick={() => navigate('/plan')}
          className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-cyan-500/20"
        >
          <Compass className="w-4 h-4" /> Plan New Trip
        </button>
      </div>

      {loading ? (
        <LoadingSkeleton count={3} />
      ) : trips.length === 0 ? (
        <div className="glass-panel rounded-3xl p-12 text-center border border-gray-800 space-y-4">
          <Calendar className="w-12 h-12 text-cyan-400 mx-auto" />
          <h3 className="text-xl font-bold text-white">No Saved Trips Yet</h3>
          <p className="text-sm text-gray-400 max-w-md mx-auto">
            You haven't saved any trips. Use the trip planner to generate personalized itineraries.
          </p>
          <button
            onClick={() => navigate('/plan')}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 text-white font-bold text-xs"
          >
            Create Your First Trip
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trips.map((trip) => (
            <div key={trip.id} className="glass-panel glass-panel-hover rounded-2xl p-6 border border-gray-800 flex flex-col justify-between space-y-4">
              <div>
                <div className="flex items-center justify-between text-xs text-cyan-400 mb-2">
                  <span className="flex items-center gap-1 font-semibold">
                    <MapPin className="w-3.5 h-3.5" /> {trip.source} → {trip.destination}
                  </span>
                  <span className="uppercase font-bold px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                    {trip.status}
                  </span>
                </div>
                <h3 className="text-2xl font-black text-white">{trip.destination}</h3>
                <p className="text-xs text-gray-400 mt-1">
                  Dates: {trip.start_date} to {trip.end_date}
                </p>
                <div className="mt-3 flex items-center justify-between">
                  <div className="text-sm font-extrabold text-emerald-400">
                    Budget: ₹{trip.budget ? trip.budget.toLocaleString() : '25,000'}
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                    Invoice Ready
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-800 flex items-center justify-between gap-2">
                <button
                  onClick={() => handleDelete(trip.id)}
                  className="p-2 rounded-lg text-gray-400 hover:text-rose-400 hover:bg-rose-500/10"
                  title="Delete Trip"
                >
                  <Trash2 className="w-4 h-4" />
                </button>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => navigate(`/billing/booking/${trip.id}`)}
                    className="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500 hover:text-white text-xs font-semibold flex items-center gap-1"
                    title="View Billing & Invoice"
                  >
                    <FileText className="w-3.5 h-3.5" /> View Bill
                  </button>

                  <button
                    onClick={() => handleDownloadInvoice(trip.id)}
                    className="p-2 rounded-lg bg-gray-800 text-gray-300 hover:text-white hover:bg-gray-700"
                    title="Download PDF Invoice"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
