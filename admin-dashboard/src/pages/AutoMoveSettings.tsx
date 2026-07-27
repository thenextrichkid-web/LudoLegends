import { useEffect, useState } from 'react';
import { Save } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

export default function AutoMoveSettings() {
  const [limit, setLimit] = useState(3);
  const [penaltyAmount, setPenaltyAmount] = useState(20);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const res = await api.get('/api/auto-move/config');
        setLimit(res.data.limit);
        setPenaltyAmount(res.data.penalty_amount);
      } catch (e) {}
      setLoading(false);
    };
    fetchConfig();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.put(`/api/auto-move/config?limit=${limit}&penalty_amount=${penaltyAmount}`);
      toast.success('Auto move penalty config updated');
    } catch (e) {
      toast.error('Failed to update config');
    }
    setSaving(false);
  };

  if (loading) return <div className="text-center py-8 text-gray-500">Loading...</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Auto Move Penalty Settings</h2>

      <div className="bg-surface border border-border rounded-xl p-6 max-w-lg">
        <div className="space-y-6">
          <div>
            <label className="block text-sm text-gray-400 mb-2">Free Auto Move Limit</label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value) || 0)}
              min={0}
              className="w-full px-4 py-3 bg-surfaceLight border border-border rounded-lg text-white focus:outline-none focus:border-primary"
            />
            <p className="text-xs text-gray-500 mt-1">Number of free auto moves allowed per match</p>
          </div>

          <div>
            <label className="block text-sm text-gray-400 mb-2">Penalty Amount (₹)</label>
            <input
              type="number"
              value={penaltyAmount}
              onChange={(e) => setPenaltyAmount(parseFloat(e.target.value) || 0)}
              min={0}
              className="w-full px-4 py-3 bg-surfaceLight border border-border rounded-lg text-white focus:outline-none focus:border-primary"
            />
            <p className="text-xs text-gray-500 mt-1">Amount deducted per extra auto move beyond the limit</p>
          </div>

          <div className="bg-surfaceLight rounded-lg p-4">
            <p className="text-sm text-gray-300">
              Current: First <span className="text-primary font-bold">{limit}</span> auto moves are free. 
              Every additional move costs <span className="text-gold font-bold">₹{penaltyAmount}</span>.
            </p>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 px-6 py-3 bg-primary hover:bg-primaryLight text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
          >
            <Save size={18} />
            {saving ? 'Saving...' : 'Save Configuration'}
          </button>
        </div>
      </div>
    </div>
  );
}
