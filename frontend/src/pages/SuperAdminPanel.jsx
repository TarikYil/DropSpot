import { useState, useEffect } from 'react';
import { superAdminService } from '../services/api';
import { Users, Shield, Trash2, UserPlus, UserMinus, Plus, X } from 'lucide-react';

export default function SuperAdminPanel() {
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [roleFormData, setRoleFormData] = useState({
    name: '',
    display_name: '',
    description: ''
  });
  const [activeTab, setActiveTab] = useState('users'); // 'users' or 'roles'
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [usersRes, rolesRes, statsRes] = await Promise.all([
        superAdminService.getUsers(),
        superAdminService.getRoles(),
        superAdminService.getStats()
      ]);
      setUsers(usersRes.data);
      setRoles(rolesRes.data);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Error loading data:', err);
      console.error('Error response:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const handleAssignRole = async (userId, roleId) => {
    try {
      await superAdminService.assignRole(userId, roleId);
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Bir hata oluştu');
    }
  };

  const handleRemoveRole = async (userId, roleId) => {
    try {
      await superAdminService.removeRole(userId, roleId);
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Bir hata oluştu');
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm('Bu kullanıcıyı silmek istediğinize emin misiniz?')) return;
    try {
      await superAdminService.deleteUser(userId);
      loadData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Bir hata oluştu');
    }
  };

  const handleCreateRole = async (e) => {
    e.preventDefault();
    try {
      await superAdminService.createRole(roleFormData);
      setShowRoleModal(false);
      setRoleFormData({ name: '', display_name: '', description: '' });
      loadData();
      alert('Rol başarıyla oluşturuldu!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Bir hata oluştu');
    }
  };

  const handleDeleteRole = async (roleId, roleName) => {
    if (!confirm(`"${roleName}" rolünü silmek istediğinize emin misiniz?`)) return;
    try {
      await superAdminService.deleteRole(roleId);
      loadData();
      alert('Rol başarıyla silindi!');
    } catch (err) {
      alert(err.response?.data?.detail || 'Bir hata oluştu');
    }
  };

  const loadUserDetails = async (userId) => {
    try {
      const response = await superAdminService.getUser(userId);
      setSelectedUser(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Yükleniyor...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Süper Admin Paneli</h1>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Toplam Kullanıcı</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_users}</p>
                </div>
                <Users className="text-primary-600" size={32} />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Aktif Kullanıcı</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.active_users}</p>
                </div>
                <Shield className="text-green-600" size={32} />
              </div>
            </div>
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Toplam Rol</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_roles}</p>
                </div>
                <Shield className="text-purple-600" size={32} />
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-4 mb-6 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 font-semibold transition-colors ${
              activeTab === 'users'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Kullanıcılar
          </button>
          <button
            onClick={() => setActiveTab('roles')}
            className={`px-4 py-2 font-semibold transition-colors ${
              activeTab === 'roles'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Roller
          </button>
        </div>

        {/* Users Table */}
        {activeTab === 'users' && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Kullanıcılar</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4">Kullanıcı Adı</th>
                  <th className="text-left py-3 px-4">E-posta</th>
                  <th className="text-left py-3 px-4">Durum</th>
                  <th className="text-left py-3 px-4">İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4">{user.username}</td>
                    <td className="py-3 px-4">{user.email}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {user.is_active ? 'Aktif' : 'Pasif'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => loadUserDetails(user.id)}
                          className="text-blue-600 hover:text-blue-700"
                        >
                          Detay
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:text-red-700"
                        >
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

        {/* Roles Table */}
        {activeTab === 'roles' && (
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold">Roller</h2>
            <button
              onClick={() => setShowRoleModal(true)}
              className="btn-primary flex items-center space-x-2"
            >
              <Plus size={20} />
              <span>Yeni Rol</span>
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4">Rol Adı</th>
                  <th className="text-left py-3 px-4">Görünen Ad</th>
                  <th className="text-left py-3 px-4">Açıklama</th>
                  <th className="text-left py-3 px-4">İşlemler</th>
                </tr>
              </thead>
              <tbody>
                {roles.length === 0 ? (
                  <tr>
                    <td colSpan="4" className="py-8 text-center text-gray-500">
                      Henüz rol yok
                    </td>
                  </tr>
                ) : (
                  roles.map((role) => (
                    <tr key={role.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-mono text-sm">{role.name}</td>
                      <td className="py-3 px-4">{role.display_name}</td>
                      <td className="py-3 px-4 text-gray-600">{role.description || '-'}</td>
                      <td className="py-3 px-4">
                        <button
                          onClick={() => handleDeleteRole(role.id, role.display_name)}
                          className="text-red-600 hover:text-red-700"
                          title="Rolü Sil"
                        >
                          <Trash2 size={18} />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
        )}

        {/* Create Role Modal */}
        {showRoleModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-md w-full">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold">Yeni Rol Oluştur</h2>
                  <button
                    onClick={() => {
                      setShowRoleModal(false);
                      setRoleFormData({ name: '', display_name: '', description: '' });
                    }}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <X size={24} />
                  </button>
                </div>
                <form onSubmit={handleCreateRole} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Rol Adı (Teknik)</label>
                    <input
                      type="text"
                      required
                      className="input-field"
                      value={roleFormData.name}
                      onChange={(e) => setRoleFormData({...roleFormData, name: e.target.value})}
                      placeholder="moderator"
                      pattern="[a-z_]+"
                      title="Küçük harf ve alt çizgi kullanın"
                    />
                    <p className="text-xs text-gray-500 mt-1">Küçük harf ve alt çizgi kullanın (örn: moderator, content_editor)</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Görünen Ad</label>
                    <input
                      type="text"
                      required
                      className="input-field"
                      value={roleFormData.display_name}
                      onChange={(e) => setRoleFormData({...roleFormData, display_name: e.target.value})}
                      placeholder="Moderatör"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Açıklama</label>
                    <textarea
                      className="input-field"
                      rows="3"
                      value={roleFormData.description}
                      onChange={(e) => setRoleFormData({...roleFormData, description: e.target.value})}
                      placeholder="Rolün açıklaması..."
                    />
                  </div>
                  <div className="flex space-x-4 pt-4">
                    <button type="submit" className="btn-primary flex-1">Oluştur</button>
                    <button
                      type="button"
                      onClick={() => {
                        setShowRoleModal(false);
                        setRoleFormData({ name: '', display_name: '', description: '' });
                      }}
                      className="btn-secondary flex-1"
                    >
                      İptal
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* User Details Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <h2 className="text-2xl font-bold mb-4">Kullanıcı Detayları</h2>
                <div className="space-y-4">
                  <div>
                    <p className="text-sm text-gray-600">Kullanıcı Adı</p>
                    <p className="text-lg font-semibold">{selectedUser.username}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">E-posta</p>
                    <p className="text-lg">{selectedUser.email}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Roller</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {selectedUser.roles?.map((role) => (
                        <span key={role.id} className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
                          {role.display_name}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-2">Rol Ata</p>
                    <div className="flex flex-wrap gap-2">
                      {roles.map((role) => {
                        const hasRole = selectedUser.roles?.some(r => r.id === role.id);
                        return (
                          <button
                            key={role.id}
                            onClick={() => hasRole ? handleRemoveRole(selectedUser.id, role.id) : handleAssignRole(selectedUser.id, role.id)}
                            className={`px-3 py-1 rounded-full text-sm flex items-center space-x-1 ${
                              hasRole
                                ? 'bg-red-100 text-red-800 hover:bg-red-200'
                                : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                            }`}
                          >
                            {hasRole ? <UserMinus size={14} /> : <UserPlus size={14} />}
                            <span>{role.display_name}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedUser(null)}
                  className="mt-6 btn-secondary w-full"
                >
                  Kapat
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
