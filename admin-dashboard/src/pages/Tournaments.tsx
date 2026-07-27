import { useEffect, useState } from 'react';
import api from '../api/client';

interface Tournament {
  id: string;
  name: string;
  type: string;
  status: string;
  entry_fee: number;
  prize_pool: number;
  max_participants: number;
  current_participants: number;
  starts_at: string;
}

export default function Tournaments() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTournaments = async () => {
      try {
        const res = await api.get('/api/tournaments');
        setTournaments(res.data.tournaments || []);
      } catch (e) {}
      setLoading(false);
    };
    fetchTournaments();
  }, []);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Tournaments</h2>
        <button className="px-4 py-2 bg-primary hover:bg-primaryLight rounded-lg text-white font-medium transition-colors">+ Create Tournament</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full text-center py-8 text-gray-500">Loading...</div>
        ) : tournaments.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">No tournaments yet</div>
        ) : (
          tournaments.map((t) => (
            <div key={t.id} className="bg-surface border border-border rounded-xl p-6 hover:border-primary/50 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <span className="text-lg font-semibold">{t.name}</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  t.status === 'upcoming' ? 'bg-primary/20 text-primary' :
                  t.status === 'in_progress' ? 'bg-secondary/20 text-secondary' :
                  'bg-gray-500/20 text-gray-400'
                }`}>{t.status}</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-gray-400">Type</span><span>{t.type}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">Entry Fee</span><span className="text-gold">₹{t.entry_fee}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">Prize Pool</span><span className="text-success">₹{t.prize_pool}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">Players</span><span>{t.current_participants}/{t.max_participants}</span></div>
                <div className="flex justify-between"><span className="text-gray-400">Starts</span><span>{new Date(t.starts_at).toLocaleDateString()}</span></div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
