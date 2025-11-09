import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import AdminPanel from './pages/AdminPanel';
import SuperAdminPanel from './pages/SuperAdminPanel';
import Settings from './pages/Settings';
import DropDetail from './pages/DropDetail';
import MyWaitlist from './pages/MyWaitlist';
import MyClaims from './pages/MyClaims';
import ChatWidget from './components/ChatWidget';
import Toast from './components/Toast';
import { useToast } from './hooks/useToast';
import { isAuthenticated } from './utils/auth';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          const { authService } = await import('./services/api');
          const response = await authService.me();
          console.log('User data loaded:', response.data);
          setUser(response.data);
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('access_token');
        }
      }
      setLoading(false);
    };
    checkAuth();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navbar user={user} setUser={setUser} />
        {toast.toasts.length > 0 && (
          <Toast toasts={toast.toasts} removeToast={toast.removeToast} />
        )}
        <Routes>
          <Route path="/login" element={!isAuthenticated() ? <Login setUser={setUser} /> : <Navigate to="/" />} />
          <Route path="/register" element={!isAuthenticated() ? <Register /> : <Navigate to="/" />} />
          <Route path="/" element={<Home user={user} />} />
          <Route 
            path="/admin" 
            element={isAuthenticated() && user?.is_superuser ? <AdminPanel /> : <Navigate to="/" />} 
          />
          <Route 
            path="/superadmin" 
            element={
              isAuthenticated() && user?.is_superuser ? (
                <SuperAdminPanel />
              ) : (
                (() => {
                  console.log('SuperAdmin access denied:', { 
                    isAuthenticated: isAuthenticated(), 
                    is_superuser: user?.is_superuser,
                    user: user 
                  });
                  return <Navigate to="/" />;
                })()
              )
            } 
          />
          <Route 
            path="/settings" 
            element={isAuthenticated() ? <Settings user={user} setUser={setUser} /> : <Navigate to="/login" />} 
          />
          <Route path="/drops/:id" element={<DropDetail user={user} />} />
          <Route 
            path="/my-waitlist" 
            element={isAuthenticated() ? <MyWaitlist user={user} /> : <Navigate to="/login" />} 
          />
          <Route 
            path="/my-claims" 
            element={isAuthenticated() ? <MyClaims user={user} /> : <Navigate to="/login" />} 
          />
        </Routes>
        {isAuthenticated() && <ChatWidget />}
      </div>
    </Router>
  );
}

export default App;
