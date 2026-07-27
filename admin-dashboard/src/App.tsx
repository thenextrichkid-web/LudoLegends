import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Users from './pages/Users';
import Tournaments from './pages/Tournaments';
import Matches from './pages/Matches';
import Wallet from './pages/Wallet';
import AutoMoveSettings from './pages/AutoMoveSettings';
import Layout from './components/Layout';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('admin_token');
  if (!token) return <Navigate to="/login" />;
  return <>{children}</>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" toastOptions={{ style: { background: '#1A1A25', color: '#fff', border: '1px solid #2A2A3A' } }} />
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="users" element={<Users />} />
          <Route path="tournaments" element={<Tournaments />} />
          <Route path="matches" element={<Matches />} />
          <Route path="wallet" element={<Wallet />} />
          <Route path="settings/auto-move" element={<AutoMoveSettings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
