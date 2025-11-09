import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import { setToken, setUser as setUserLocalStorage } from '../utils/auth';
import { LogIn } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Login({ setUser }) {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('Login attempt:', formData.username);
      const response = await authService.login(formData.username, formData.password);
      console.log('Login response:', response.data);
      
      if (!response.data.access_token) {
        throw new Error('Token alınamadı');
      }
      
      // Token'ı localStorage'a kaydet
      setToken(response.data.access_token);
      
      // Get user info
      const userResponse = await authService.me();
      console.log('User info:', userResponse.data);
      
      // Hem App.jsx state'ini hem de localStorage'ı güncelle
      setUser(userResponse.data);
      setUserLocalStorage(userResponse.data);
      
      navigate('/');
    } catch (err) {
      console.error('Login error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Giriş başarısız. Lütfen tekrar deneyin.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="mx-auto bg-gradient-to-r from-primary-600 to-secondary-600 text-white w-20 h-20 rounded-full flex items-center justify-center mb-4">
            <LogIn size={40} />
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900">Giriş Yap</h2>
          <p className="mt-2 text-gray-600">DropSpot hesabınıza giriş yapın</p>
        </div>

        <form className="mt-8 space-y-6 card" onSubmit={handleSubmit}>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg shadow-lg"
            >
              <div className="flex items-center">
                <span className="font-semibold mr-2">Hata:</span>
                <span>{error}</span>
              </div>
            </motion.div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Kullanıcı Adı veya E-posta
              </label>
              <input
                type="text"
                required
                className="input-field"
                placeholder="kullaniciadi veya email@example.com"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Şifre
              </label>
              <input
                type="password"
                required
                className="input-field"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>
          </div>

          <motion.button
            type="submit"
            disabled={loading}
            whileHover={{ scale: loading ? 1 : 1.02 }}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mr-2"></div>
                <span>Giriş yapılıyor...</span>
              </>
            ) : (
              'Giriş Yap'
            )}
          </motion.button>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Hesabınız yok mu?{' '}
              <Link to="/register" className="text-primary-600 hover:text-primary-700 font-medium">
                Kayıt olun
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
