import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { AlertTriangle, CheckCircle, DollarSign, Wallet } from 'lucide-react';

export const BudgetCard = ({ budget = 30000 }) => {
  // Budget Breakdown Calculations
  const transport = Math.round(budget * 0.25);
  const accommodation = Math.round(budget * 0.35);
  const food = Math.round(budget * 0.20);
  const activities = Math.round(budget * 0.12);
  const shopping = Math.round(budget * 0.05);
  const emergency = Math.round(budget * 0.03);

  const totalEstimated = transport + accommodation + food + activities + shopping + emergency;
  const remaining = budget - totalEstimated;
  const isOver = totalEstimated > budget;

  const chartData = [
    { name: 'Accommodation', value: accommodation, color: '#0284c7' },
    { name: 'Transportation', value: transport, color: '#06b6d4' },
    { name: 'Food & Dining', value: food, color: '#10b981' },
    { name: 'Activities', value: activities, color: '#a855f7' },
    { name: 'Shopping', value: shopping, color: '#f59e0b' },
    { name: 'Emergency Fund', value: emergency, color: '#64748b' },
  ];

  return (
    <div className="glass-panel rounded-2xl p-6 border border-gray-800">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Wallet className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Budget Optimizer</h4>
            <p className="text-xs text-gray-400">Smart Allocation Engine</p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs text-gray-400 block">Total Allocated</span>
          <span className="text-xl font-extrabold text-white">₹{budget.toLocaleString()}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center my-4">
        {/* Donut Chart */}
        <div className="h-48 relative flex items-center justify-center">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={75}
                paddingAngle={4}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`₹${value.toLocaleString()}`, 'Amount']}
                contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute text-center">
            <span className="text-[10px] text-gray-400 uppercase tracking-wider block">Remaining</span>
            <span className={`text-base font-extrabold ${isOver ? 'text-rose-400' : 'text-emerald-400'}`}>
              ₹{remaining.toLocaleString()}
            </span>
          </div>
        </div>

        {/* Breakdown Items */}
        <div className="space-y-2 text-xs">
          {chartData.map((item) => (
            <div key={item.name} className="flex items-center justify-between p-2 rounded-lg bg-gray-900/50 border border-gray-800">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-gray-300 font-medium">{item.name}</span>
              </div>
              <span className="font-bold text-white">₹{item.value.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Warning or Success Banner */}
      <div className={`p-3 rounded-xl text-xs flex items-center gap-2.5 border ${
        isOver
          ? 'bg-rose-500/10 text-rose-300 border-rose-500/30'
          : 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30'
      }`}>
        {isOver ? (
          <>
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>Over-budget warning: Consider reducing shopping or premium hotel selections.</span>
          </>
        ) : (
          <>
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Optimal Budget Match! Emergency reserve of 3% is maintained.</span>
          </>
        )}
      </div>
    </div>
  );
};
