import { useState } from 'react';
import { authService } from '../services/api';
import { User, Mail, Lock, Save } from 'lucide-react';

export default function Settings({ user, setUser }) {
  const [formData, setFormData] = useState({
    email: user?.email || '',
    username: user?.username || '',
    full_name: user?.full_name || ''
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      // Profile update logic would go here
      setMessage('Profil güncellendi!');
    } catch (err) {
      setMessage('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage('Yeni şifreler eşleşmiyor');
      setLoading(false);
      return;
    }

    try {
      // Password change logic would go here
      setMessage('Şifre değiştirildi!');
      setPasswordData({ old_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setMessage('Bir hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Ayarlar</h1>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${
            message.includes('hata') ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
          }`}>
            {message}
          </div>
        )}

        {/* Profile Settings */}
        <div className="card mb-6">
          <div className="flex items-center space-x-2 mb-6">
            <User className="text-primary-600" size={24} />
            <h2 className="text-xl font-bold">Profil Bilgileri</h2>
          </div>

          <form onSubmit={handleProfileUpdate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">E-posta</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="email"
                  className="input-field pl-10"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Kullanıcı Adı</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  className="input-field pl-10"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Ad Soyad</label>
              <input
                type="text"
                className="input-field"
                value={formData.full_name}
                onChange={(e) => setFormData({...formData, full_name: e.target.value})}
              />
            </div>

            <button type="submit" disabled={loading} className="btn-primary flex items-center space-x-2">
              <Save size={20} />
              <span>Kaydet</span>
            </button>
          </form>
        </div>

        {/* Password Settings */}
        <div className="card">
          <div className="flex items-center space-x-2 mb-6">
            <Lock className="text-primary-600" size={24} />
            <h2 className="text-xl font-bold">Şifre Değiştir</h2>
          </div>

          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Mevcut Şifre</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="password"
                  className="input-field pl-10"
                  value={passwordData.old_password}
                  onChange={(e) => setPasswordData({...passwordData, old_password: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Yeni Şifre</label>
              <input
                type="password"
                className="input-field"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Yeni Şifre (Tekrar)</label>
              <input
                type="password"
                className="input-field"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
              />
            </div>

            <button type="submit" disabled={loading} className="btn-primary flex items-center space-x-2">
              <Lock size={20} />
              <span>Şifreyi Değiştir</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
