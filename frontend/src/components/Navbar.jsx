import { Link, useNavigate } from 'react-router-dom';
import { Home, Settings, Shield, Users, LogOut, Menu, X, List, CheckCircle } from 'lucide-react';
import { useState } from 'react';
import { logout } from '../utils/auth';

export default function Navbar({ user, setUser }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    setUser(null);
    navigate('/login');
  };

  return (
    <nav className="bg-white/80 backdrop-blur-md shadow-lg sticky top-0 z-50 border-b border-gray-200/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white px-4 py-2 rounded-lg font-bold text-xl">
              DropSpot
            </div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-6">
            <Link to="/" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center space-x-1">
              <Home size={18} />
              <span>Ana Sayfa</span>
            </Link>
            
            {user && (
              <>
                <Link to="/my-waitlist" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center space-x-1">
                  <List size={18} />
                  <span>Bekleme Listem</span>
                </Link>
                <Link to="/my-claims" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center space-x-1">
                  <CheckCircle size={18} />
                  <span>Claim'lerim</span>
                </Link>
                {user.is_superuser && (
                  <>
                    <Link to="/admin" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center space-x-1">
                      <Shield size={18} />
                      <span>Admin</span>
                    </Link>
                    <Link to="/superadmin" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center space-x-1">
                      <Users size={18} />
                      <span>Süper Admin</span>
                    </Link>
                  </>
                )}
                <Link to="/settings" className="text-gray-700 hover:text-primary-600 transition-colors flex items-center space-x-1">
                  <Settings size={18} />
                  <span>Ayarlar</span>
                </Link>
                <div className="flex items-center space-x-4">
                  <span className="text-gray-700">Merhaba, {user.username}</span>
                  <button
                    onClick={handleLogout}
                    className="flex items-center space-x-1 text-red-600 hover:text-red-700 transition-colors"
                  >
                    <LogOut size={18} />
                    <span>Çıkış</span>
                  </button>
                </div>
              </>
            )}

            {!user && (
              <div className="flex items-center space-x-4">
                <Link to="/login" className="text-gray-700 hover:text-primary-600 transition-colors">
                  Giriş Yap
                </Link>
                <Link to="/register" className="btn-primary">
                  Kayıt Ol
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-gray-700"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200">
          <div className="px-4 py-4 space-y-4">
            <Link to="/" className="block text-gray-700 hover:text-primary-600">Ana Sayfa</Link>
            {user && (
              <>
                <Link to="/my-waitlist" className="block text-gray-700 hover:text-primary-600">Bekleme Listem</Link>
                <Link to="/my-claims" className="block text-gray-700 hover:text-primary-600">Claim'lerim</Link>
                {user.is_superuser && (
                  <>
                    <Link to="/admin" className="block text-gray-700 hover:text-primary-600">Admin</Link>
                    <Link to="/superadmin" className="block text-gray-700 hover:text-primary-600">Süper Admin</Link>
                  </>
                )}
                <Link to="/settings" className="block text-gray-700 hover:text-primary-600">Ayarlar</Link>
                <div className="pt-4 border-t border-gray-200">
                  <p className="text-gray-700 mb-2">Merhaba, {user.username}</p>
                  <button onClick={handleLogout} className="text-red-600 hover:text-red-700">
                    Çıkış Yap
                  </button>
                </div>
              </>
            )}
            {!user && (
              <div className="space-y-2">
                <Link to="/login" className="block text-gray-700 hover:text-primary-600">Giriş Yap</Link>
                <Link to="/register" className="block btn-primary text-center">Kayıt Ol</Link>
              </div>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}
