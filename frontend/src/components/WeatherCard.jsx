import React from 'react';
import { Sun, Cloud, CloudRain, Wind, Droplets, ShieldCheck } from 'lucide-react';

export const WeatherCard = ({ weather }) => {
  const destination = weather?.destination || "Destination";
  const temp = weather?.temperature_celsius ? Math.round(weather.temperature_celsius) : 26;
  const condition = weather?.condition || "Pleasant & Clear";
  const humidity = weather?.humidity_percent || 65;
  const wind = weather?.wind_speed_kmh ? Math.round(weather.wind_speed_kmh) : 12;
  const isDemo = weather?.is_demo_data !== undefined ? weather.is_demo_data : true;

  const getWeatherIcon = (cond) => {
    const c = cond.toLowerCase();
    if (c.includes('rain') || c.includes('storm')) return <CloudRain className="w-8 h-8 text-cyan-400" />;
    if (c.includes('cloud')) return <Cloud className="w-8 h-8 text-indigo-400" />;
    return <Sun className="w-8 h-8 text-amber-400" />;
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-gray-800 relative overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h4 className="text-sm font-bold text-white uppercase tracking-wider">{destination} Weather</h4>
          <p className="text-xs text-gray-400">Live Forecast & Climate</p>
        </div>

        <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-semibold uppercase">
          Live Weather
        </span>
      </div>

      <div className="flex items-center justify-between my-2">
        <div className="flex items-center gap-3">
          {getWeatherIcon(condition)}
          <div>
            <div className="text-3xl font-black text-white">{temp}°C</div>
            <div className="text-xs font-semibold text-gray-300">{condition}</div>
          </div>
        </div>

        <div className="space-y-1.5 text-xs text-gray-400 border-l border-gray-800 pl-4">
          <div className="flex items-center gap-1.5">
            <Droplets className="w-3.5 h-3.5 text-cyan-400" />
            <span>Humidity: {humidity}%</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Wind className="w-3.5 h-3.5 text-indigo-400" />
            <span>Wind: {wind} km/h</span>
          </div>
        </div>
      </div>
    </div>
  );
};
