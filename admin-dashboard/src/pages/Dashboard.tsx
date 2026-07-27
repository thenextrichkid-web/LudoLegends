import { useEffect, useState } from 'react';
import { Users, Trophy, Swords, Wallet } from 'lucide-react';
import api from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState({ total_users: 0, total_wallet_balance: 0, pending_withdrawals: 0, pending_deposits: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/api/admin/dashboard');
        setStats(res.data);
      } catch (e) {}
    };
    fetchStats();
  }, []);

  const cards = [
    { label: 'Total Users', value: stats.total_users, icon: Users, color: 'text-primary' },
    { label: 'Platform Balance', value: `₹${stats.total_wallet_balance.toLocaleString()}`, icon: Wallet, color: 'text-success' },
    { label: 'Pending Withdrawals', value: stats.pending_withdrawals, icon: Swords, color: 'text-gold' },
    { label: 'Pending Deposits', value: stats.pending_deposits, icon: Trophy, color: 'text-secondary' },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {cards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-surface border border-border rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-400 text-sm">{label}</span>
              <Icon className={color} size={24} />
            </div>
            <div className="text-3xl font-bold">{value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <p className="text-gray-500">No recent activity</p>
        </div>
        <div className="bg-surface border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full text-left px-4 py-3 bg-surfaceLight rounded-lg text-gray-300 hover:text-white transition-colors">Create Tournament</button>
            <button className="w-full text-left px-4 py-3 bg-surfaceLight rounded-lg text-gray-300 hover:text-white transition-colors">Review Matches</button>
            <button className="w-full text-left px-4 py-3 bg-surfaceLight rounded-lg text-gray-300 hover:text-white transition-colors">Manage Users</button>
          </div>
        </div>
      </div>
    </div>
  );
}
