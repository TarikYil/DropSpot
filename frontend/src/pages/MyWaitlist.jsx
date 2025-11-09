import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { waitlistService, dropsService } from '../services/api';
import { List, MapPin, Clock, Package, Users, ArrowRight, X } from 'lucide-react';
import { motion } from 'framer-motion';

export default function MyWaitlist({ user }) {
  const navigate = useNavigate();
  const [waitlist, setWaitlist] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loadingDropId, setLoadingDropId] = useState(null);

  useEffect(() => {
    if (user) {
      loadWaitlist();
    }
  }, [user]);

  const loadWaitlist = async () => {
    try {
      const response = await waitlistService.getMyWaitlist();
      const waitlistData = response.data;

      // Get drop details for each waitlist entry
      const dropsWithDetails = await Promise.all(
        waitlistData.map(async (entry) => {
          try {
            const dropRes = await dropsService.getById(entry.drop_id);
            const positionRes = await waitlistService.getPosition(entry.drop_id);
            return {
              ...entry,
              drop: dropRes.data,
              position: positionRes.data.position
            };
          } catch (err) {
            return { ...entry, drop: null, position: null };
          }
        })
      );

      setWaitlist(dropsWithDetails);
    } catch (err) {
      setError('Bekleme listesi yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const handleLeaveWaitlist = async (dropId) => {
    setLoadingDropId(dropId);
    setError('');
    setSuccessMessage('');

    try {
      await waitlistService.leave(dropId);
      setSuccessMessage('Bekleme listesinden çıkarıldınız');
      setTimeout(() => setSuccessMessage(''), 5000);
      loadWaitlist();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      setError(errorMessage);
      setTimeout(() => setError(''), 5000);
    } finally {
      setLoadingDropId(null);
    }
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600 text-lg mb-4">Giriş yapmanız gerekiyor</p>
          <button onClick={() => navigate('/login')} className="btn-primary">
            Giriş Yap
          </button>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-3">
            <List size={32} className="text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Bekleme Listem</h1>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-6">
            {successMessage}
          </div>
        )}

        {waitlist.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg">
            <List size={64} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 text-lg">Bekleme listesinde drop bulunmuyor</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 btn-primary"
            >
              Drop'ları Keşfet
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {waitlist.map((entry, index) => (
              <motion.div
                key={entry.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card hover:shadow-xl transition-all duration-300 flex flex-col h-full"
              >
                {entry.drop ? (
                  <>
                    {/* Image */}
                    <div className="relative h-48 w-full mb-4 rounded-lg overflow-hidden bg-gradient-to-br from-primary-100 to-secondary-100">
                      {entry.drop.image_url ? (
                        <img
                          src={entry.drop.image_url}
                          alt={entry.drop.title}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div className={`w-full h-full flex items-center justify-center ${entry.drop.image_url ? 'hidden' : ''}`}>
                        <Package size={64} className="text-primary-600" />
                      </div>
                      {entry.position && (
                        <div className="absolute top-2 left-2 bg-primary-600 text-white px-3 py-1 rounded-full text-sm font-semibold">
                          Sıra: {entry.position}
                        </div>
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 flex flex-col">
                      <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-1">
                        {entry.drop.title}
                      </h3>
                      <p className="text-gray-600 mb-4 line-clamp-2 text-sm flex-1">
                        {entry.drop.description || 'Açıklama yok'}
                      </p>

                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <Package size={16} className="mr-2 flex-shrink-0" />
                          <span className="truncate">
                            Stok: {entry.drop.remaining_quantity}/{entry.drop.total_quantity}
                          </span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <MapPin size={16} className="mr-2 flex-shrink-0" />
                          <span className="truncate">
                            {entry.drop.address || 'Konum belirtilmemiş'}
                          </span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock size={16} className="mr-2 flex-shrink-0" />
                          <span className="truncate">
                            {new Date(entry.drop.end_time).toLocaleDateString('tr-TR')}
                          </span>
                        </div>
                      </div>

                      <div className="flex gap-2 mt-auto">
                        <button
                          onClick={() => navigate(`/drops/${entry.drop.id}`)}
                          className="flex-1 btn-primary text-sm flex items-center justify-center space-x-2"
                        >
                          <span>Detay</span>
                          <ArrowRight size={16} />
                        </button>
                        <button
                          onClick={() => handleLeaveWaitlist(entry.drop_id)}
                          disabled={loadingDropId === entry.drop_id}
                          className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          title="Bekleme listesinden çık"
                        >
                          <X size={18} />
                        </button>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600">Drop bilgileri yüklenemedi</p>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

