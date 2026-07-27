import { useEffect, useState } from 'react';
import { Check, X } from 'lucide-react';
import api from '../api/client';
import toast from 'react-hot-toast';

interface Withdrawal {
  id: string;
  user_id: string;
  amount: number;
  status: string;
  payment_method: string | null;
  payment_details: string | null;
  rejection_reason: string | null;
  created_at: string;
}

export default function Wallet() {
  const [withdrawals, setWithdrawals] = useState<Withdrawal[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWithdrawals();
  }, []);

  const fetchWithdrawals = async () => {
    try {
      const res = await api.get('/api/admin/withdrawals?status_filter=pending');
      setWithdrawals(res.data.withdrawals || []);
    } catch (e) {}
    setLoading(false);
  };

  const handleApprove = async (id: string) => {
    try {
      await api.post(`/api/admin/withdrawals/${id}/approve`);
      toast.success('Withdrawal approved');
      setWithdrawals(withdrawals.filter(w => w.id !== id));
    } catch (e) {
      toast.error('Failed to approve');
    }
  };

  const handleReject = async (id: string) => {
    try {
      await api.post(`/api/admin/withdrawals/${id}/reject?reason=Rejected by admin`);
      toast.success('Withdrawal rejected');
      setWithdrawals(withdrawals.filter(w => w.id !== id));
    } catch (e) {
      toast.error('Failed to reject');
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Wallet Management</h2>

      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <div className="px-6 py-4 border-b border-border">
          <h3 className="font-semibold">Pending Withdrawals</h3>
        </div>
        {loading ? (
          <div className="text-center py-8 text-gray-500">Loading...</div>
        ) : withdrawals.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No pending withdrawal requests</div>
        ) : (
          <div className="divide-y divide-border">
            {withdrawals.map((w) => (
              <div key={w.id} className="px-6 py-4 flex items-center justify-between">
                <div>
                  <p className="font-medium">₹{w.amount}</p>
                  <p className="text-sm text-gray-400">User: {w.user_id.slice(0, 8)} | Method: {w.payment_method || 'N/A'}</p>
                  <p className="text-xs text-gray-500">{new Date(w.created_at).toLocaleString()}</p>
                </div>
                <div className="flex items-center gap-2">
                  <button onClick={() => handleApprove(w.id)} className="flex items-center gap-1 px-3 py-1.5 bg-success/20 text-success rounded-lg hover:bg-success/30 transition-colors text-sm">
                    <Check size={14} /> Approve
                  </button>
                  <button onClick={() => handleReject(w.id)} className="flex items-center gap-1 px-3 py-1.5 bg-danger/20 text-danger rounded-lg hover:bg-danger/30 transition-colors text-sm">
                    <X size={14} /> Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
