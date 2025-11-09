import { useState, useEffect } from 'react';
import { dropsService, adminService } from '../services/api';
import { Plus, Edit, Trash2, Package, TrendingUp, Users, ShoppingCart, CheckCircle, XCircle, Clock } from 'lucide-react';

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState('drops'); // drops or claims
  const [drops, setDrops] = useState([]);
  const [claims, setClaims] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingDrop, setEditingDrop] = useState(null);
  const [claimStatusFilter, setClaimStatusFilter] = useState('pending');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    image_url: '',
    total_quantity: 100,
    latitude: 41.0082,
    longitude: 28.9784,
    address: '',
    radius_meters: 1000,
    start_time: '',
    end_time: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dropsRes, statsRes, claimsRes] = await Promise.all([
        dropsService.getAll(),
        adminService.getStats(),
        adminService.getClaims(claimStatusFilter).catch(() => ({ data: [] }))
      ]);
      setDrops(dropsRes.data);
      setStats(statsRes.data);
      setClaims(claimsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadClaims = async () => {
    try {
      const response = await adminService.getClaims(claimStatusFilter);
      setClaims(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (activeTab === 'claims') {
      loadClaims();
    }
  }, [activeTab, claimStatusFilter]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingDrop) {
        await dropsService.update(editingDrop.id, formData);
      } else {
        await dropsService.create(formData);
      }
      setShowModal(false);
      setEditingDrop(null);
      resetForm();
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Bir hata oluştu');
    }
  };

  const handleDelete = async (id) => {
    if (!confirm('Bu drop\'u silmek istediğinize emin misiniz?')) return;
    try {
      await dropsService.delete(id);
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Bir hata oluştu');
    }
  };

  const handleEdit = (drop) => {
    setEditingDrop(drop);
    setFormData({
      title: drop.title,
      description: drop.description || '',
      image_url: drop.image_url || '',
      total_quantity: drop.total_quantity,
      latitude: drop.latitude,
      longitude: drop.longitude,
      address: drop.address || '',
      radius_meters: drop.radius_meters,
      start_time: drop.start_time.split('T')[0],
      end_time: drop.end_time.split('T')[0]
    });
    setShowModal(true);
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      image_url: '',
      total_quantity: 100,
      latitude: 41.0082,
      longitude: 28.9784,
      address: '',
      radius_meters: 1000,
      start_time: '',
      end_time: ''
    });
  };

  const handleApproveClaim = async (id) => {
    if (!confirm('Bu claim\'i onaylamak istediğinize emin misiniz?')) return;
    try {
      await adminService.approveClaim(id);
      alert('Claim başarıyla onaylandı!');
      loadClaims();
      loadData();
    } catch (err) {
      console.error('Approve claim error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      alert(`Hata: ${errorMessage}`);
    }
  };

  const handleRejectClaim = async (id) => {
    if (!confirm('Bu claim\'i reddetmek istediğinize emin misiniz?')) return;
    try {
      await adminService.rejectClaim(id);
      alert('Claim başarıyla reddedildi!');
      loadClaims();
      loadData();
    } catch (err) {
      console.error('Reject claim error:', err);
      const errorMessage = err.response?.data?.detail || err.message || 'Bir hata oluştu';
      alert(`Hata: ${errorMessage}`);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return (
          <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
            Onaylandı
          </span>
        );
      case 'rejected':
        return (
          <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
            Reddedildi
          </span>
        );
      default:
        return (
          <span className="px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold">
            Beklemede
          </span>
        );
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Yükleniyor...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Admin Paneli</h1>
          {activeTab === 'drops' && (
            <button onClick={() => { setShowModal(true); setEditingDrop(null); resetForm(); }} className="btn-primary flex items-center space-x-2">
              <Plus size={20} />
              <span>Yeni Drop</span>
            </button>
          )}
        </div>

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('drops')}
            className={`px-4 py-2 font-semibold transition-colors ${
              activeTab === 'drops'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Drop'lar
          </button>
          <button
            onClick={() => setActiveTab('claims')}
            className={`px-4 py-2 font-semibold transition-colors ${
              activeTab === 'claims'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Claim'ler
          </button>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Toplam Drop</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_drops}</p>
                </div>
                <Package className="text-primary-600" size={32} />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Aktif Drop</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.active_drops}</p>
                </div>
                <TrendingUp className="text-green-600" size={32} />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Toplam Claim</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_claims}</p>
                </div>
                <ShoppingCart className="text-blue-600" size={32} />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Waitlist</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_users_on_waitlist}</p>
                </div>
                <Users className="text-purple-600" size={32} />
              </div>
            </div>
          </div>
        )}

        {/* Drops Table */}
        {activeTab === 'drops' && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Drop'lar</h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4">Başlık</th>
                    <th className="text-left py-3 px-4">Stok</th>
                    <th className="text-left py-3 px-4">Durum</th>
                    <th className="text-left py-3 px-4">İşlemler</th>
                  </tr>
                </thead>
                <tbody>
                  {drops.map((drop) => (
                    <tr key={drop.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">{drop.title}</td>
                      <td className="py-3 px-4">{drop.remaining_quantity}/{drop.total_quantity}</td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          drop.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {drop.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="flex space-x-2">
                          <button onClick={() => handleEdit(drop)} className="text-blue-600 hover:text-blue-700">
                            <Edit size={18} />
                          </button>
                          <button onClick={() => handleDelete(drop.id)} className="text-red-600 hover:text-red-700">
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Claims Table */}
        {activeTab === 'claims' && (
          <div className="space-y-6">
            {/* Status Filter */}
            <div className="flex flex-wrap gap-2">
              {['pending', 'approved', 'rejected'].map((status) => (
                <button
                  key={status}
                  onClick={() => setClaimStatusFilter(status)}
                  className={`px-4 py-2 rounded-lg transition-colors ${
                    claimStatusFilter === status
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  {status === 'pending' ? 'Beklemede' : status === 'approved' ? 'Onaylandı' : 'Reddedildi'}
                </button>
              ))}
            </div>

            <div className="card">
              <h2 className="text-xl font-bold mb-4">Claim'ler</h2>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4">ID</th>
                      <th className="text-left py-3 px-4">Drop ID</th>
                      <th className="text-left py-3 px-4">Kullanıcı ID</th>
                      <th className="text-left py-3 px-4">Miktar</th>
                      <th className="text-left py-3 px-4">Durum</th>
                      <th className="text-left py-3 px-4">Tarih</th>
                      <th className="text-left py-3 px-4">İşlemler</th>
                    </tr>
                  </thead>
                  <tbody>
                    {claims.length === 0 ? (
                      <tr>
                        <td colSpan="7" className="py-8 text-center text-gray-500">
                          Claim bulunamadı
                        </td>
                      </tr>
                    ) : (
                      claims.map((claim) => (
                        <tr key={claim.id} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4">#{claim.id}</td>
                          <td className="py-3 px-4">#{claim.drop_id}</td>
                          <td className="py-3 px-4">#{claim.user_id}</td>
                          <td className="py-3 px-4">{claim.quantity}</td>
                          <td className="py-3 px-4">{getStatusBadge(claim.status)}</td>
                          <td className="py-3 px-4 text-sm text-gray-600">
                            {new Date(claim.created_at).toLocaleDateString('tr-TR')}
                          </td>
                          <td className="py-3 px-4">
                            {claim.status === 'pending' && (
                              <div className="flex space-x-2">
                                <button
                                  onClick={() => handleApproveClaim(claim.id)}
                                  className="text-green-600 hover:text-green-700"
                                  title="Onayla"
                                >
                                  <CheckCircle size={18} />
                                </button>
                                <button
                                  onClick={() => handleRejectClaim(claim.id)}
                                  className="text-red-600 hover:text-red-700"
                                  title="Reddet"
                                >
                                  <XCircle size={18} />
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4">{editingDrop ? 'Drop Düzenle' : 'Yeni Drop'}</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Başlık</label>
                    <input type="text" required className="input-field" value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Açıklama</label>
                    <textarea className="input-field" rows="3" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Görsel URL</label>
                    <input type="url" className="input-field" value={formData.image_url} onChange={(e) => setFormData({...formData, image_url: e.target.value})} placeholder="https://example.com/image.jpg" />
                    {formData.image_url && (
                      <div className="mt-2">
                        <img src={formData.image_url} alt="Preview" className="w-full h-48 object-cover rounded-lg border border-gray-200" onError={(e) => e.target.style.display = 'none'} />
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Toplam Miktar</label>
                      <input type="number" required className="input-field" value={formData.total_quantity} onChange={(e) => setFormData({...formData, total_quantity: parseInt(e.target.value)})} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Yarıçap (m)</label>
                      <input type="number" required className="input-field" value={formData.radius_meters} onChange={(e) => setFormData({...formData, radius_meters: parseInt(e.target.value)})} />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Enlem</label>
                      <input type="number" step="0.0001" required className="input-field" value={formData.latitude} onChange={(e) => setFormData({...formData, latitude: parseFloat(e.target.value)})} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Boylam</label>
                      <input type="number" step="0.0001" required className="input-field" value={formData.longitude} onChange={(e) => setFormData({...formData, longitude: parseFloat(e.target.value)})} />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Adres</label>
                    <input type="text" className="input-field" value={formData.address} onChange={(e) => setFormData({...formData, address: e.target.value})} />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Başlangıç</label>
                      <input type="datetime-local" required className="input-field" value={formData.start_time} onChange={(e) => setFormData({...formData, start_time: e.target.value})} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-2">Bitiş</label>
                      <input type="datetime-local" required className="input-field" value={formData.end_time} onChange={(e) => setFormData({...formData, end_time: e.target.value})} />
                    </div>
                  </div>
                  <div className="flex space-x-4 pt-4">
                    <button type="submit" className="btn-primary flex-1">Kaydet</button>
                    <button type="button" onClick={() => { setShowModal(false); setEditingDrop(null); resetForm(); }} className="btn-secondary flex-1">İptal</button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
