import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { dropsService, waitlistService } from '../services/api';
import { ShoppingBag, MapPin, Clock, Users, Package, Search, Filter, Navigation, Calendar, Sparkles, CheckCircle, XCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { SkeletonCard } from '../components/Skeleton';

export default function Home({ user }) {
  const navigate = useNavigate();
  const [drops, setDrops] = useState([]);
  const [allDrops, setAllDrops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [loadingDropId, setLoadingDropId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('active'); // active, upcoming, past, all
  const [userLocation, setUserLocation] = useState(null);
  const [showNearby, setShowNearby] = useState(false);

  useEffect(() => {
    loadDrops();
    getUserLocation();
  }, []);

  useEffect(() => {
    filterDrops();
  }, [searchTerm, filterType, showNearby, userLocation, allDrops]);

  const getUserLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        () => {
          console.log('Konum alınamadı');
        }
      );
    }
  };

  const loadDrops = async () => {
    try {
      const response = await dropsService.getAll({ limit: 100 });
      setAllDrops(response.data);
      setDrops(response.data.filter(drop => {
        const now = new Date();
        const start = new Date(drop.start_time);
        const end = new Date(drop.end_time);
        return drop.is_active && start <= now && end >= now;
      }));
    } catch (err) {
      setError('Drop\'lar yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const filterDrops = () => {
    let filtered = [...allDrops];

    // Filter by type
    const now = new Date();
    if (filterType === 'active') {
      filtered = filtered.filter(drop => {
        const start = new Date(drop.start_time);
        const end = new Date(drop.end_time);
        return drop.is_active && start <= now && end >= now;
      });
    } else if (filterType === 'upcoming') {
      filtered = filtered.filter(drop => {
        const start = new Date(drop.start_time);
        return drop.is_active && start > now;
      });
    } else if (filterType === 'past') {
      filtered = filtered.filter(drop => {
        const end = new Date(drop.end_time);
        return end < now || !drop.is_active;
      });
    }

    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(drop =>
        drop.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        drop.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        drop.address?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Filter by nearby
    if (showNearby && userLocation) {
      filtered = filtered.filter(drop => {
        const distance = calculateDistance(
          userLocation.latitude,
          userLocation.longitude,
          drop.latitude,
          drop.longitude
        );
        return distance <= (drop.radius_meters || 5000);
      });
    }

    setDrops(filtered);
  };

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371000; // Earth radius in meters
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const handleJoinWaitlist = async (dropId) => {
    setLoadingDropId(dropId);
    setError('');
    setSuccessMessage('');
    
    try {
      const response = await waitlistService.join(dropId);
      setSuccessMessage('Bekleme listesine başarıyla eklendiniz!');
      setTimeout(() => setSuccessMessage(''), 5000);
      loadDrops();
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      setError(errorMessage);
      setTimeout(() => setError(''), 5000);
      console.error('Waitlist join error:', err);
    } finally {
      setLoadingDropId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-primary-50/30 to-secondary-50/30">
        <div className="bg-gradient-to-r from-primary-600 via-primary-700 to-secondary-600 text-white py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h1 className="text-5xl font-bold mb-4">DropSpot'a Hoş Geldiniz</h1>
            <p className="text-xl text-primary-100 mb-8">
              Sınırlı sayıdaki özel ürünlere erişim sağlayın
            </p>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {Array.from({ length: 8 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-primary-50/30 to-secondary-50/30">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-primary-600 via-primary-700 to-secondary-600 text-white py-20 overflow-hidden">
        {/* Animated background elements */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-10 left-10 w-72 h-72 bg-white rounded-full blur-3xl animate-pulse-slow"></div>
          <div className="absolute bottom-10 right-10 w-96 h-96 bg-white rounded-full blur-3xl animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center justify-center mb-4">
              <Sparkles className="text-yellow-300 mr-3" size={32} />
              <h1 className="text-5xl md:text-6xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-primary-100">
                DropSpot'a Hoş Geldiniz
              </h1>
              <Sparkles className="text-yellow-300 ml-3" size={32} />
            </div>
            <p className="text-xl md:text-2xl text-primary-100 mb-8 font-light">
              Sınırlı sayıdaki özel ürünlere erişim sağlayın
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm">
              <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                <Package className="inline mr-2" size={16} />
                Özel Ürünler
              </div>
              <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                <Clock className="inline mr-2" size={16} />
                Sınırlı Süre
              </div>
              <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full">
                <Users className="inline mr-2" size={16} />
                Adil Dağıtım
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Drops Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <h2 className="text-3xl font-bold text-gray-900">Drop'lar</h2>
          
          {/* Search and Filters */}
          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-80">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Drop ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all bg-white/80 backdrop-blur-sm shadow-sm"
              />
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setShowNearby(!showNearby)}
              className={`px-5 py-3 rounded-xl flex items-center space-x-2 transition-all font-medium shadow-sm ${
                showNearby
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
              }`}
              disabled={!userLocation}
              title={!userLocation ? 'Konum izni gerekli' : ''}
            >
              <Navigation size={18} />
              <span className="hidden sm:inline">Yakınım</span>
            </motion.button>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="flex flex-wrap gap-3 mb-8">
          {[
            { 
              key: 'active', 
              label: 'Aktif', 
              icon: Clock, 
              activeClass: 'bg-gradient-to-r from-green-500 to-emerald-600 text-white shadow-lg',
              inactiveClass: 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
            },
            { 
              key: 'upcoming', 
              label: 'Yakında', 
              icon: Calendar, 
              activeClass: 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-lg',
              inactiveClass: 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
            },
            { 
              key: 'past', 
              label: 'Geçmiş', 
              icon: Package, 
              activeClass: 'bg-gradient-to-r from-gray-600 to-gray-700 text-white shadow-lg',
              inactiveClass: 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
            },
            { 
              key: 'all', 
              label: 'Tümü', 
              icon: ShoppingBag, 
              activeClass: 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-lg',
              inactiveClass: 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
            }
          ].map(({ key, label, icon: Icon, activeClass, inactiveClass }) => (
            <motion.button
              key={key}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setFilterType(key)}
              className={`px-5 py-2.5 rounded-xl flex items-center space-x-2 transition-all font-medium shadow-sm ${
                filterType === key ? activeClass : inactiveClass
              }`}
            >
              <Icon size={18} />
              <span>{label}</span>
              {filterType === key && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="ml-1 w-2 h-2 bg-white rounded-full"
                />
              )}
            </motion.button>
          ))}
        </div>

        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 border-l-4 border-red-500 text-red-700 px-4 py-3 rounded-lg mb-6 shadow-lg backdrop-blur-sm"
          >
            <div className="flex items-center">
              <XCircle className="mr-2 flex-shrink-0" size={20} />
              <p>{error}</p>
            </div>
          </motion.div>
        )}

        {successMessage && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-lg mb-6 shadow-lg backdrop-blur-sm"
          >
            <div className="flex items-center">
              <CheckCircle className="mr-2 flex-shrink-0" size={20} />
              <p>{successMessage}</p>
            </div>
          </motion.div>
        )}

        {drops.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-16"
          >
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-12 shadow-xl max-w-md mx-auto">
              <Package size={80} className="mx-auto text-gray-300 mb-6" />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Drop Bulunamadı</h3>
              <p className="text-gray-600 mb-6">
                {searchTerm || filterType !== 'all' || showNearby
                  ? 'Arama kriterlerinize uygun drop bulunamadı. Filtreleri değiştirmeyi deneyin.'
                  : 'Henüz hiç drop eklenmemiş. Yakında yeni drop\'lar eklenecek!'}
              </p>
              {(searchTerm || filterType !== 'all' || showNearby) && (
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setFilterType('all');
                    setShowNearby(false);
                  }}
                  className="btn-primary"
                >
                  Filtreleri Temizle
                </button>
              )}
            </div>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {drops.map((drop, index) => (
              <motion.div
                key={drop.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ y: -8, scale: 1.02 }}
                className="group card hover:shadow-2xl transition-all duration-300 flex flex-col h-full cursor-pointer bg-white/90 backdrop-blur-sm border border-gray-100"
                onClick={() => navigate(`/drops/${drop.id}`)}
              >
                {/* Image */}
                <div className="relative h-48 w-full mb-4 rounded-lg overflow-hidden bg-gradient-to-br from-primary-100 to-secondary-100 group-hover:scale-105 transition-transform duration-300">
                  {drop.image_url ? (
                    <img
                      src={drop.image_url}
                      alt={drop.title}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div className={`w-full h-full flex items-center justify-center ${drop.image_url ? 'hidden' : ''}`}>
                    <ShoppingBag size={64} className="text-primary-600" />
                  </div>
                  {drop.status === 'active' && (
                    <motion.span
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="absolute top-3 right-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-3 py-1.5 rounded-full text-xs font-semibold shadow-lg backdrop-blur-sm"
                    >
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
                      </span>
                      <span className="ml-2">Aktif</span>
                    </motion.span>
                  )}
                  {/* Stock indicator */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-3">
                    <div className="flex items-center justify-between text-white text-sm">
                      <span className="font-semibold">Stok</span>
                      <span className="bg-white/20 backdrop-blur-sm px-2 py-1 rounded-full">
                        {drop.remaining_quantity}/{drop.total_quantity}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div className="flex-1 flex flex-col">
                  <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-1 group-hover:text-primary-600 transition-colors">
                    {drop.title}
                  </h3>
                  <p className="text-gray-600 mb-4 line-clamp-2 text-sm flex-1 leading-relaxed">
                    {drop.description || 'Açıklama yok'}
                  </p>

                  <div className="space-y-2.5 mb-4">
                    <div className="flex items-center text-sm text-gray-600 bg-gray-50 rounded-lg p-2">
                      <MapPin size={16} className="mr-2 flex-shrink-0 text-primary-600" />
                      <span className="truncate">{drop.address || 'Konum belirtilmemiş'}</span>
                    </div>
                    <div className="flex items-center text-sm text-gray-600 bg-gray-50 rounded-lg p-2">
                      <Clock size={16} className="mr-2 flex-shrink-0 text-primary-600" />
                      <span className="truncate">{new Date(drop.end_time).toLocaleDateString('tr-TR', { 
                        day: 'numeric', 
                        month: 'long', 
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}</span>
                    </div>
                  </div>

                  {user && (
                    <div className="flex gap-2 mt-auto">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleJoinWaitlist(drop.id);
                        }}
                        disabled={loadingDropId === drop.id}
                        className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed text-sm relative overflow-hidden"
                      >
                        {loadingDropId === drop.id ? (
                          <span className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                            Ekleniyor...
                          </span>
                        ) : (
                          'Katıl'
                        )}
                      </motion.button>
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/drops/${drop.id}`);
                        }}
                        className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium border border-gray-200"
                      >
                        Detay
                      </motion.button>
                    </div>
                  )}

                  {!user && (
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate('/login');
                      }}
                      className="w-full mt-auto btn-secondary text-sm"
                    >
                      Giriş Yap
                    </motion.button>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
