import { useEffect, useState } from 'react';
import { Check, X } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

interface Match {
  id: string;
  tournament_id: string;
  user_id: string;
  status: string;
  screenshot_url: string | null;
  result_notes: string | null;
  submitted_at: string;
}

export default function Matches() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const res = await api.get('/api/matches/pending');
        setMatches(res.data);
      } catch (e) {}
      setLoading(false);
    };
    fetchMatches();
  }, []);

  const handleVerify = async (matchId: string, action: 'approve' | 'reject') => {
    try {
      await api.post(`/api/matches/${matchId}/verify`, {
        action,
        prize_awarded: action === 'approve' ? 100 : 0,
      });
      toast.success(`Match ${action === 'approve' ? 'approved' : 'rejected'}`);
      setMatches(matches.filter((m) => m.id !== matchId));
    } catch (e) {
      toast.error('Failed to update match');
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Pending Matches</h2>

      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : matches.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No pending matches</div>
        ) : (
          matches.map((match) => (
            <div key={match.id} className="bg-surface border border-border rounded-xl p-6">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-semibold">Match {match.id.slice(0, 8)}</span>
                    <span className="px-2 py-1 rounded text-xs bg-gold/20 text-gold">{match.status}</span>
                  </div>
                  <p className="text-sm text-gray-400">Tournament: {match.tournament_id.slice(0, 8)}</p>
                  <p className="text-sm text-gray-400">Submitted: {match.submitted_at ? new Date(match.submitted_at).toLocaleString() : 'N/A'}</p>
                  {match.result_notes && <p className="text-sm text-gray-400 mt-1">Notes: {match.result_notes}</p>}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleVerify(match.id, 'approve')}
                    className="flex items-center gap-1 px-4 py-2 bg-success/20 text-success rounded-lg hover:bg-success/30 transition-colors"
                  >
                    <Check size={16} /> Approve
                  </button>
                  <button
                    onClick={() => handleVerify(match.id, 'reject')}
                    className="flex items-center gap-1 px-4 py-2 bg-danger/20 text-danger rounded-lg hover:bg-danger/30 transition-colors"
                  >
                    <X size={16} /> Reject
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
