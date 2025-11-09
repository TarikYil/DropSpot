import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { claimsService, dropsService } from '../services/api';
import { CheckCircle, XCircle, Clock, Package, MapPin, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function MyClaims({ user }) {
  const navigate = useNavigate();
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      loadClaims();
    }
  }, [user]);

  const loadClaims = async () => {
    try {
      const response = await claimsService.getMyClaims();
      const claimsData = response.data;

      // Get drop details for each claim
      const claimsWithDetails = await Promise.all(
        claimsData.map(async (claim) => {
          try {
            const dropRes = await dropsService.getById(claim.drop_id);
            return {
              ...claim,
              drop: dropRes.data
            };
          } catch (err) {
            return { ...claim, drop: null };
          }
        })
      );

      setClaims(claimsWithDetails);
    } catch (err) {
      setError('Claim\'ler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return (
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold flex items-center space-x-1">
            <CheckCircle size={14} />
            <span>Onaylandı</span>
          </span>
        );
      case 'rejected':
        return (
          <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold flex items-center space-x-1">
            <XCircle size={14} />
            <span>Reddedildi</span>
          </span>
        );
      case 'pending':
      default:
        return (
          <span className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold flex items-center space-x-1">
            <Clock size={14} />
            <span>Beklemede</span>
          </span>
        );
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
            <CheckCircle size={32} className="text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Claim'lerim</h1>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {claims.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg">
            <CheckCircle size={64} className="mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 text-lg">Henüz claim yapmadınız</p>
            <button
              onClick={() => navigate('/')}
              className="mt-4 btn-primary"
            >
              Drop'ları Keşfet
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {claims.map((claim, index) => (
              <motion.div
                key={claim.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="card hover:shadow-xl transition-all duration-300 flex flex-col h-full"
              >
                {claim.drop ? (
                  <>
                    {/* Image */}
                    <div className="relative h-48 w-full mb-4 rounded-lg overflow-hidden bg-gradient-to-br from-primary-100 to-secondary-100">
                      {claim.drop.image_url ? (
                        <img
                          src={claim.drop.image_url}
                          alt={claim.drop.title}
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            e.target.style.display = 'none';
                            e.target.nextSibling.style.display = 'flex';
                          }}
                        />
                      ) : null}
                      <div className={`w-full h-full flex items-center justify-center ${claim.drop.image_url ? 'hidden' : ''}`}>
                        <Package size={64} className="text-primary-600" />
                      </div>
                      <div className="absolute top-2 right-2">
                        {getStatusBadge(claim.status)}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 flex flex-col">
                      <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-1">
                        {claim.drop.title}
                      </h3>
                      <p className="text-gray-600 mb-4 line-clamp-2 text-sm flex-1">
                        {claim.drop.description || 'Açıklama yok'}
                      </p>

                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <Package size={16} className="mr-2 flex-shrink-0" />
                          <span className="truncate">Miktar: {claim.quantity}</span>
                        </div>
                        {claim.verification_code && (
                          <div className="flex items-center text-sm text-gray-600">
                            <CheckCircle size={16} className="mr-2 flex-shrink-0" />
                            <span className="truncate font-mono">Kod: {claim.verification_code}</span>
                          </div>
                        )}
                        <div className="flex items-center text-sm text-gray-600">
                          <Clock size={16} className="mr-2 flex-shrink-0" />
                          <span className="truncate">
                            {new Date(claim.created_at).toLocaleDateString('tr-TR')}
                          </span>
                        </div>
                      </div>

                      <button
                        onClick={() => navigate(`/drops/${claim.drop.id}`)}
                        className="w-full btn-primary text-sm flex items-center justify-center space-x-2 mt-auto"
                      >
                        <span>Drop Detayı</span>
                        <ArrowRight size={16} />
                      </button>
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

