import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { dropsService, waitlistService, claimsService } from '../services/api';
import { ShoppingBag, MapPin, Clock, Package, Users, ArrowLeft, CheckCircle, XCircle, Navigation, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';

export default function DropDetail({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [drop, setDrop] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [waitlistPosition, setWaitlistPosition] = useState(null);
  const [waitlistCount, setWaitlistCount] = useState(0);
  const [isInWaitlist, setIsInWaitlist] = useState(false);
  const [canClaim, setCanClaim] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [distance, setDistance] = useState(null);
  const [claiming, setClaiming] = useState(false);

  useEffect(() => {
    loadDrop();
    if (user) {
      checkWaitlistStatus();
      getUserLocation();
    }
  }, [id, user]);

  useEffect(() => {
    if (userLocation && drop) {
      const dist = calculateDistance(
        userLocation.latitude,
        userLocation.longitude,
        drop.latitude,
        drop.longitude
      );
      setDistance(dist);
      setCanClaim(dist <= (drop.radius_meters || 5000));
    }
  }, [userLocation, drop]);

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

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371000;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  const loadDrop = async () => {
    try {
      const response = await dropsService.getById(id);
      setDrop(response.data);
    } catch (err) {
      setError('Drop yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const checkWaitlistStatus = async () => {
    try {
      const [positionRes, countRes, myWaitlistRes] = await Promise.all([
        waitlistService.getPosition(id).catch(() => null),
        waitlistService.getCount(id).catch(() => ({ data: { waitlist_count: 0 } })),
        waitlistService.getMyWaitlist().catch(() => ({ data: [] }))
      ]);

      if (positionRes) {
        setWaitlistPosition(positionRes.data.position);
        setIsInWaitlist(true);
      }
      // Backend'den waitlist_count döner, count değil
      setWaitlistCount(countRes.data.waitlist_count || countRes.data.count || 0);

      const inWaitlist = myWaitlistRes.data.some(w => w.drop_id === parseInt(id));
      setIsInWaitlist(inWaitlist);
    } catch (err) {
      console.error('Waitlist status check failed:', err);
    }
  };

  const handleJoinWaitlist = async () => {
    setError('');
    setSuccessMessage('');
    
    try {
      await waitlistService.join(id);
      setSuccessMessage('Bekleme listesine başarıyla eklendiniz!');
      setTimeout(() => setSuccessMessage(''), 5000);
      // Drop bilgilerini ve waitlist durumunu güncelle
      await Promise.all([loadDrop(), checkWaitlistStatus()]);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      setError(errorMessage);
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleLeaveWaitlist = async () => {
    setError('');
    setSuccessMessage('');
    
    try {
      await waitlistService.leave(id);
      setSuccessMessage('Bekleme listesinden çıkarıldınız');
      setTimeout(() => setSuccessMessage(''), 5000);
      // Drop bilgilerini ve waitlist durumunu güncelle
      await Promise.all([loadDrop(), checkWaitlistStatus()]);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      setError(errorMessage);
      setTimeout(() => setError(''), 5000);
    }
  };

  const handleClaim = async () => {
    if (!userLocation) {
      setError('Konum izni gerekli');
      return;
    }

    setClaiming(true);
    setError('');
    setSuccessMessage('');

    try {
      await claimsService.create(parseInt(id), {
        quantity: 1,
        claim_latitude: userLocation.latitude,
        claim_longitude: userLocation.longitude
      });
      setSuccessMessage('Claim başarıyla oluşturuldu!');
      // Drop bilgilerini güncelle (stok azalacak)
      await loadDrop();
      setTimeout(() => {
        setSuccessMessage('');
        navigate('/my-claims');
      }, 3000);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      setError(errorMessage);
      setTimeout(() => setError(''), 5000);
    } finally {
      setClaiming(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!drop) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <XCircle size={64} className="mx-auto text-red-500 mb-4" />
          <p className="text-gray-600 text-lg">Drop bulunamadı</p>
          <button onClick={() => navigate('/')} className="mt-4 btn-primary">
            Ana Sayfaya Dön
          </button>
        </div>
      </div>
    );
  }

  const now = new Date();
  const start = new Date(drop.start_time);
  const end = new Date(drop.end_time);
  const isActive = drop.is_active && start <= now && end >= now;
  const isUpcoming = start > now;
  const isPast = end < now || !drop.is_active;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-primary-50/20 to-secondary-50/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.button
          whileHover={{ x: -5 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/')}
          className="mb-6 flex items-center space-x-2 text-gray-600 hover:text-primary-600 transition-colors font-medium group"
        >
          <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
          <span>Geri Dön</span>
        </motion.button>

        {error && (
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
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
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-green-50 border-l-4 border-green-500 text-green-700 px-4 py-3 rounded-lg mb-6 shadow-lg backdrop-blur-sm"
          >
            <div className="flex items-center">
              <CheckCircle className="mr-2 flex-shrink-0" size={20} />
              <p>{successMessage}</p>
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Image */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="relative group"
          >
            <div className="relative h-96 w-full rounded-2xl overflow-hidden bg-gradient-to-br from-primary-100 to-secondary-100 shadow-2xl">
              {drop.image_url ? (
                <img
                  src={drop.image_url}
                  alt={drop.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div className={`w-full h-full flex items-center justify-center ${drop.image_url ? 'hidden' : ''}`}>
                <ShoppingBag size={128} className="text-primary-600" />
              </div>
              {isActive && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-4 right-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg backdrop-blur-sm flex items-center space-x-2"
                >
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-white opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
                  </span>
                  <span>Aktif</span>
                </motion.span>
              )}
            </div>
          </motion.div>

          {/* Details */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="space-y-6"
          >
            <div>
              <div className="flex items-center mb-4">
                <Sparkles className="text-yellow-400 mr-2" size={24} />
                <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                  {drop.title}
                </h1>
              </div>
              <p className="text-gray-600 text-lg leading-relaxed mb-6">{drop.description || 'Açıklama yok'}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <motion.div
                whileHover={{ scale: 1.05, y: -5 }}
                className="bg-gradient-to-br from-white to-primary-50/50 p-5 rounded-xl border-2 border-primary-100 shadow-lg backdrop-blur-sm"
              >
                <div className="flex items-center space-x-2 mb-3">
                  <div className="p-2 bg-primary-100 rounded-lg">
                    <Package size={20} className="text-primary-600" />
                  </div>
                  <span className="text-sm font-medium text-gray-600">Stok</span>
                </div>
                <p className="text-3xl font-bold text-gray-900">
                  {drop.remaining_quantity}
                  <span className="text-lg text-gray-500 font-normal">/{drop.total_quantity}</span>
                </p>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(drop.remaining_quantity / drop.total_quantity) * 100}%` }}
                    transition={{ duration: 0.5 }}
                    className="bg-gradient-to-r from-primary-600 to-primary-700 h-2 rounded-full"
                  />
                </div>
              </motion.div>

              <motion.div
                whileHover={{ scale: 1.05, y: -5 }}
                className="bg-gradient-to-br from-white to-secondary-50/50 p-5 rounded-xl border-2 border-secondary-100 shadow-lg backdrop-blur-sm"
              >
                <div className="flex items-center space-x-2 mb-3">
                  <div className="p-2 bg-secondary-100 rounded-lg">
                    <Users size={20} className="text-secondary-600" />
                  </div>
                  <span className="text-sm font-medium text-gray-600">Bekleme Listesi</span>
                </div>
                <p className="text-3xl font-bold text-gray-900">{waitlistCount}</p>
                <p className="text-xs text-gray-500 mt-2">kişi bekliyor</p>
              </motion.div>
            </div>

            <div className="space-y-4">
              <motion.div
                whileHover={{ x: 5 }}
                className="flex items-start space-x-3 bg-white/60 backdrop-blur-sm p-4 rounded-xl border border-gray-200"
              >
                <div className="p-2 bg-primary-100 rounded-lg">
                  <MapPin size={20} className="text-primary-600 flex-shrink-0" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 mb-1">Konum</p>
                  <p className="text-gray-900 font-semibold">{drop.address || 'Konum belirtilmemiş'}</p>
                  {distance !== null && (
                    <div className="mt-2 flex items-center space-x-2">
                      <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                        canClaim 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {Math.round(distance)}m uzaklıkta
                      </span>
                      {!canClaim && (
                        <span className="text-xs text-gray-500">
                          ({Math.round(drop.radius_meters || 5000)}m içinde olmalısınız)
                        </span>
                      )}
                    </div>
                  )}
                </div>
              </motion.div>

              <motion.div
                whileHover={{ x: 5 }}
                className="flex items-start space-x-3 bg-white/60 backdrop-blur-sm p-4 rounded-xl border border-gray-200"
              >
                <div className="p-2 bg-primary-100 rounded-lg">
                  <Clock size={20} className="text-primary-600 flex-shrink-0" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 mb-1">Zaman</p>
                  <p className="text-gray-900 font-semibold">
                    {new Date(drop.start_time).toLocaleString('tr-TR', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                  <p className="text-gray-600 text-sm mt-1">
                    Bitiş: {new Date(drop.end_time).toLocaleString('tr-TR', {
                      day: 'numeric',
                      month: 'long',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                </div>
              </motion.div>
            </div>

            {user && (
              <div className="space-y-4 pt-6 border-t-2 border-gray-200">
                {isInWaitlist && waitlistPosition && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-xl p-5 shadow-lg"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-blue-900 font-semibold mb-1">Bekleme listesindesiniz!</p>
                        <p className="text-blue-700 text-sm">Sıranız</p>
                      </div>
                      <div className="text-4xl font-bold text-blue-600">
                        #{waitlistPosition}
                      </div>
                    </div>
                  </motion.div>
                )}

                {isActive && (
                  <div className="flex flex-col sm:flex-row gap-3">
                    {!isInWaitlist ? (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleJoinWaitlist}
                        className="flex-1 btn-primary text-base py-4"
                      >
                        <Users className="inline mr-2" size={20} />
                        Bekleme Listesine Katıl
                      </motion.button>
                    ) : (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleLeaveWaitlist}
                        className="flex-1 btn-secondary text-base py-4"
                      >
                        Bekleme Listesinden Çık
                      </motion.button>
                    )}

                    {isInWaitlist && canClaim && drop.remaining_quantity > 0 && (
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleClaim}
                        disabled={claiming}
                        className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white px-6 py-4 rounded-xl font-semibold transition-all shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                      >
                        {claiming ? (
                          <>
                            <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                            <span>İşleniyor...</span>
                          </>
                        ) : (
                          <>
                            <CheckCircle size={20} />
                            <span>Claim Yap</span>
                          </>
                        )}
                      </motion.button>
                    )}
                  </div>
                )}

                {isUpcoming && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-900">Bu drop henüz başlamadı</p>
                  </div>
                )}

                {isPast && (
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <p className="text-gray-900">Bu drop sona erdi</p>
                  </div>
                )}
              </div>
            )}

            {!user && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
                <p className="text-gray-600">Katılmak için giriş yapın</p>
                <button
                  onClick={() => navigate('/login')}
                  className="mt-3 btn-primary"
                >
                  Giriş Yap
                </button>
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}

