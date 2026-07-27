import { useEffect, useState } from 'react';
import api from '../api/client';
import toast from 'react-hot-toast';

interface User {
  id: string;
  phone: string;
  name: string | null;
  role: string;
  vip_level: number;
  total_earnings: number;
  total_wins: number;
  is_active: boolean;
  created_at: string;
}

export default function Users() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const res = await api.get('/api/admin/users');
        setUsers(res.data.users || []);
      } catch (e) {}
      setLoading(false);
    };
    fetchUsers();
  }, []);

  const toggleStatus = async (userId: string) => {
    try {
      const res = await api.put(`/api/admin/users/${userId}/status`);
      setUsers(users.map(u => u.id === userId ? { ...u, is_active: res.data.is_active } : u));
      toast.success(res.data.message);
    } catch (e) {
      toast.error('Failed to update user');
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Users</h2>

      <div className="bg-surface border border-border rounded-xl overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left px-6 py-4 text-sm text-gray-400 font-medium">User</th>
              <th className="text-left px-6 py-4 text-sm text-gray-400 font-medium">Phone</th>
              <th className="text-left px-6 py-4 text-sm text-gray-400 font-medium">Role</th>
              <th className="text-left px-6 py-4 text-sm text-gray-400 font-medium">VIP</th>
              <th className="text-left px-6 py-4 text-sm text-gray-400 font-medium">Earnings</th>
              <th className="text-left px-6 py-4 text-sm text-gray-400 font-medium">Status</th>
              <th className="text-left px-6 py-4 text-sm text-gray-400 font-medium">Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={7} className="text-center py-8 text-gray-500">Loading...</td></tr>
            ) : users.length === 0 ? (
              <tr><td colSpan={7} className="text-center py-8 text-gray-500">No users found</td></tr>
            ) : (
              users.map((user) => (
                <tr key={user.id} className="border-b border-border hover:bg-surfaceLight transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary text-sm font-bold">
                        {(user.name || user.phone).charAt(0).toUpperCase()}
                      </div>
                      <span className="text-white">{user.name || 'Anonymous'}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-400">{user.phone}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      user.role === 'super_admin' ? 'bg-danger/20 text-danger' :
                      user.role === 'admin' ? 'bg-gold/20 text-gold' :
                      'bg-primary/20 text-primary'
                    }`}>{user.role}</span>
                  </td>
                  <td className="px-6 py-4 text-gold">{user.vip_level}</td>
                  <td className="px-6 py-4 text-success">₹{user.total_earnings}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${user.is_active ? 'bg-success/20 text-success' : 'bg-danger/20 text-danger'}`}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <button onClick={() => toggleStatus(user.id)} className={`px-3 py-1 rounded text-xs font-medium ${user.is_active ? 'bg-danger/20 text-danger hover:bg-danger/30' : 'bg-success/20 text-success hover:bg-success/30'} transition-colors`}>
                      {user.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
