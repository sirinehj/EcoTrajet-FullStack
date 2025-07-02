import React, { useState } from 'react';
import { Plus, Search, Filter, Building2, GraduationCap, Mountain, Users, Car, X, MapPin, Star } from 'lucide-react';
import TransportCoNavbar from '../components/TransportCoNavbar';

const CommunitiesPage = () => {
  const [selectedCommunity, setSelectedCommunity] = useState(null);
  const [activeTab, setActiveTab] = useState('apercu');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newCommunity, setNewCommunity] = useState({
    name: '',
    type: '',
    location: '',
    description: ''
  });
  const [joinedCommunities, setJoinedCommunities] = useState([
    {
      id: 1,
      title: "Trajets Entreprise Paris",
      description: "Communauté pour les trajets domicile-travail dans la région parisienne. Partagez vos trajets quotidiens et économisez sur vos frais de transport.",
      members: 47,
      activeTrips: 12,
      icon: Building2,
      bgColor: "bg-blue-500",
      iconColor: "text-white",
      avatars: [{ id: 1, name: "A" }, { id: 2, name: "A" }],
      additionalMembers: 44,
      location: "Paris, Île-de-France",
      createdDate: "15 janvier 2024",
      membersList: [
        { id: 1, name: "Amed Ben Said", username: "@test123", avatar: "AB", rating: 4.8, trips: 23 },
        { id: 2, name: "Amed Ben Said", username: "@test", avatar: "AB", rating: 4.8, trips: 23 }
      ],
      tripsList: [
        { 
          id: 1, 
          user: "Amed Ben Said", 
          date: "30 juin 2024", 
          from: "Boulogne-Billancourt", 
          to: "La Défense", 
          price: "5,50 €", 
          availableSeats: 3 
        }
      ]
    }
  ]);

  const [availableCommunities, setAvailableCommunities] = useState([
    {
      id: 2,
      title: "Étudiants Université Lyon",
      description: "Groupe d'étudiants de l'Université de Lyon pour partager les trajets vers le campus et les sorties étudiantes.",
      members: 78,
      activeTrips: 8,
      icon: GraduationCap,
      bgColor: "bg-green-500",
      iconColor: "text-white"
    },
    {
      id: 3,
      title: "Week-end Montagne",
      description: "Pour tous les amoureux de la montagne ! Organisez vos trajets vers les stations de ski et les randonnées en groupe.",
      members: 23,
      activeTrips: 6,
      icon: Mountain,
      bgColor: "bg-orange-500",
      iconColor: "text-white"
    },
    {
      id: 4,
      title: "Covoiturage Toulouse-Bordeaux",
      description: "Trajets réguliers entre Toulouse et Bordeaux pour les professionnels et particuliers.",
      members: 34,
      activeTrips: 15,
      icon: Building2,
      bgColor: "bg-blue-600",
      iconColor: "text-white"
    }
  ]);

  const handleLogout = () => {
    // Handle logout logic here
    console.log('Logout clicked');
  };

  const handleJoinCommunity = (community) => {
    // Add to joined communities
    const newJoinedCommunity = {
      ...community,
      avatars: [{ id: 1, name: "A" }, { id: 2, name: "A" }],
      additionalMembers: community.members - 1,
      location: "Paris, Île-de-France",
      createdDate: "15 janvier 2024",
      membersList: [
        { id: 1, name: "Amed Ben Said", username: "@test", avatar: "AB", rating: 4.8, trips: 23 },
        { id: 2, name: "Amed Ben Said", username: "@test", avatar: "AB", rating: 4.8, trips: 23 }
      ],
      tripsList: [
        { 
          id: 1, 
          user: "Amed Ben Said", 
          date: "30 juin 2024", 
          from: "Boulogne-Billancourt", 
          to: "La Défense", 
          price: "5,50 €", 
          availableSeats: 3 
        }
      ]
    };
    
    setJoinedCommunities(prev => [...prev, newJoinedCommunity]);
    
    // Remove from available communities
    setAvailableCommunities(prev => prev.filter(c => c.id !== community.id));
  };

  const handleLeaveCommunity = (communityId) => {
    const communityToMove = joinedCommunities.find(c => c.id === communityId);
    if (communityToMove) {
      // Remove from joined
      setJoinedCommunities(prev => prev.filter(c => c.id !== communityId));
      
      // Add back to available (without the joined-specific properties)
      const { avatars, additionalMembers, location, createdDate, membersList, tripsList, ...originalCommunity } = communityToMove;
      setAvailableCommunities(prev => [...prev, originalCommunity]);
      
      // Close modal if it's open for this community
      if (selectedCommunity && selectedCommunity.id === communityId) {
        setSelectedCommunity(null);
      }
    }
  };

  const handleViewCommunity = (community) => {
    setSelectedCommunity(community);
    setActiveTab('apercu');
  };

  const handleCloseCommunity = () => {
    setSelectedCommunity(null);
  };

  const handleCreateCommunity = () => {
    if (newCommunity.name && newCommunity.type && newCommunity.location && newCommunity.description) {
      const communityIcons = {
        'Entreprise': Building2,
        'Étudiants': GraduationCap,
        'Loisirs': Mountain,
        'Général': Users
      };

      const communityColors = {
        'Entreprise': 'bg-blue-500',
        'Étudiants': 'bg-green-500',
        'Loisirs': 'bg-orange-500',
        'Général': 'bg-purple-500'
      };

      const createdCommunity = {
        id: Date.now(),
        title: newCommunity.name,
        description: newCommunity.description,
        members: 1,
        activeTrips: 0,
        icon: communityIcons[newCommunity.type] || Building2,
        bgColor: communityColors[newCommunity.type] || 'bg-blue-500',
        iconColor: 'text-white',
        avatars: [{ id: 1, name: "A" }],
        additionalMembers: 0,
        location: newCommunity.location,
        createdDate: new Date().toLocaleDateString('fr-FR', { 
          day: 'numeric', 
          month: 'long', 
          year: 'numeric' 
        }),
        membersList: [
          { id: 1, name: "Amed Ben Said", username: "@test123", avatar: "AB", rating: 4.8, trips: 0 }
        ],
        tripsList: []
      };

      setJoinedCommunities(prev => [...prev, createdCommunity]);
      setShowCreateModal(false);
      setNewCommunity({ name: '', type: '', location: '', description: '' });
    }
  };

  const handleCloseCreateModal = () => {
    setShowCreateModal(false);
    setNewCommunity({ name: '', type: '', location: '', description: '' });
  };
  return (
    <div>
            <TransportCoNavbar onLogout={handleLogout} />
          


    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div>
              <br />  <br />  <br />
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Communautés</h1>
            <p className="text-gray-600">Découvrez et rejoignez des groupes de transport</p>
          </div>
          <button 
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
          >
            <Plus size={20} />
            Nouvelle communauté
          </button>
        </div>

        {/* Search and Filter */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="flex gap-4 items-center">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Rechercher une communauté..."
                className="w-full pl-10 pr-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div className="flex items-center gap-2 px-4 py-3 border border-gray-200 rounded-lg cursor-pointer hover:bg-gray-50">
              <Filter size={16} className="text-gray-400" />
              <span className="text-gray-700">Tous les types</span>
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </div>
        </div>

        {/* Mes Communautés Section */}
        {joinedCommunities.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Mes Communautés</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {joinedCommunities.map((community) => {
                const IconComponent = community.icon;
                return (
                  <div key={community.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                    {/* Icon Section with Member Badge */}
                    <div className={`${community.bgColor} h-32 flex items-center justify-center relative`}>
                      <IconComponent size={48} className={community.iconColor} />
                      <div className="absolute top-3 right-3 bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                        Membre
                      </div>
                    </div>
                    
                    {/* Content Section */}
                    <div className="p-6">
                      <h3 className="text-xl font-semibold text-gray-900 mb-3">{community.title}</h3>
                      <p className="text-gray-600 text-sm mb-4 leading-relaxed">{community.description}</p>
                      
                      {/* Stats */}
                      <div className="flex justify-between items-center mb-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Users size={16} />
                          <span>{community.members} membres</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Car size={16} />
                          <span>{community.activeTrips} trajets actifs</span>
                        </div>
                      </div>

                      {/* Member Avatars */}
                      <div className="flex items-center gap-2 mb-4">
                        <div className="flex -space-x-2">
                          {community.avatars.map((avatar, index) => (
                            <div 
                              key={avatar.id} 
                              className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium border-2 border-white"
                            >
                              {avatar.name}
                            </div>
                          ))}
                        </div>
                        <span className="text-sm text-gray-500">+{community.additionalMembers} autres</span>
                      </div>
                      
                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleViewCommunity(community)}
                          className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium transition-colors"
                        >
                          Voir la communauté
                        </button>
                        <button 
                          onClick={() => handleLeaveCommunity(community.id)}
                          className="bg-red-100 hover:bg-red-200 text-red-700 py-2 px-4 rounded-lg font-medium transition-colors"
                        >
                          Quitter
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Available Communities Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Découvrir des Communautés</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {availableCommunities.map((community) => {
              const IconComponent = community.icon;
              return (
                <div key={community.id} className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                  {/* Icon Section */}
                  <div className={`${community.bgColor} h-32 flex items-center justify-center`}>
                    <IconComponent size={48} className={community.iconColor} />
                  </div>
                  
                  {/* Content Section */}
                  <div className="p-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">{community.title}</h3>
                    <p className="text-gray-600 text-sm mb-6 leading-relaxed">{community.description}</p>
                    
                    {/* Stats */}
                    <div className="flex justify-between items-center mb-6 text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Users size={16} />
                        <span>{community.members} membres</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Car size={16} />
                        <span>{community.activeTrips} trajets actifs</span>
                      </div>
                    </div>
                    
                    {/* Join Button */}
                    <button 
                      onClick={() => handleJoinCommunity(community)}
                      className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg font-medium transition-colors"
                    >
                      Rejoindre
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Create Community Modal */}
        {showCreateModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-md w-full">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b">
                <h2 className="text-xl font-bold text-gray-900">Créer une communauté</h2>
                <button 
                  onClick={handleCloseCreateModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6 space-y-4">
                {/* Name Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nom de la communauté
                  </label>
                  <input
                    type="text"
                    value={newCommunity.name}
                    onChange={(e) => setNewCommunity(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Ex: Trajets Entreprise"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Type Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Type
                  </label>
                  <select
                    value={newCommunity.type}
                    onChange={(e) => setNewCommunity(prev => ({ ...prev, type: e.target.value }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Sélectionner un type</option>
                    <option value="Entreprise">Entreprise</option>
                    <option value="Étudiants">Étudiants</option>
                    <option value="Loisirs">Loisirs</option>
                    <option value="Général">Général</option>
                  </select>
                </div>

                {/* Location Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Localisation
                  </label>
                  <input
                    type="text"
                    value={newCommunity.location}
                    onChange={(e) => setNewCommunity(prev => ({ ...prev, location: e.target.value }))}
                    placeholder="Ex: Paris, Lyon..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Description Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  <textarea
                    value={newCommunity.description}
                    onChange={(e) => setNewCommunity(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Décrivez votre communauté..."
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  />
                </div>
              </div>

              {/* Modal Footer */}
              <div className="flex justify-end gap-3 p-6 border-t bg-gray-50">
                <button 
                  onClick={handleCloseCreateModal}
                  className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  Annuler
                </button>
                <button 
                  onClick={handleCreateCommunity}
                  disabled={!newCommunity.name || !newCommunity.type || !newCommunity.location || !newCommunity.description}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                >
                  Créer
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Community Modal */}
        {selectedCommunity && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-6 border-b">
                <div className="flex items-center gap-4">
                  <div className={`${selectedCommunity.bgColor} p-3 rounded-lg`}>
                    <selectedCommunity.icon size={24} className={selectedCommunity.iconColor} />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">{selectedCommunity.title}</h2>
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                      Membre
                    </span>
                  </div>
                </div>
                <button 
                  onClick={handleCloseCommunity}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>

              {/* Modal Tabs */}
              <div className="flex border-b">
                <button
                  onClick={() => setActiveTab('apercu')}
                  className={`px-6 py-3 font-medium ${
                    activeTab === 'apercu' 
                      ? 'border-b-2 border-blue-500 text-blue-600' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Aperçu
                </button>
                <button
                  onClick={() => setActiveTab('membres')}
                  className={`px-6 py-3 font-medium ${
                    activeTab === 'membres' 
                      ? 'border-b-2 border-blue-500 text-blue-600' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Membres ({selectedCommunity.members})
                </button>
                <button
                  onClick={() => setActiveTab('trajets')}
                  className={`px-6 py-3 font-medium ${
                    activeTab === 'trajets' 
                      ? 'border-b-2 border-blue-500 text-blue-600' 
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Trajets ({selectedCommunity.activeTrips})
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6 max-h-[60vh] overflow-y-auto">
                {activeTab === 'apercu' && (
                  <div className="space-y-6">
                    {/* Stats Cards */}
                    <div className="grid grid-cols-3 gap-4">
                      <div className="bg-gray-50 p-4 rounded-lg text-center">
                        <Users className="mx-auto mb-2 text-blue-500" size={24} />
                        <div className="text-lg font-bold text-gray-900">Membres</div>
                        <div className="text-2xl font-bold text-blue-600">{selectedCommunity.members}</div>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg text-center">
                        <Car className="mx-auto mb-2 text-green-500" size={24} />
                        <div className="text-lg font-bold text-gray-900">Trajets actifs</div>
                        <div className="text-2xl font-bold text-green-600">{selectedCommunity.activeTrips}</div>
                      </div>
                      <div className="bg-gray-50 p-4 rounded-lg text-center">
                        <div className="text-lg font-bold text-gray-900">Créée le</div>
                        <div className="text-lg font-bold text-gray-900">{selectedCommunity.createdDate}</div>
                      </div>
                    </div>

                    {/* Description */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Description</h3>
                      <p className="text-gray-600 leading-relaxed">{selectedCommunity.description}</p>
                    </div>

                    {/* Location */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Localisation</h3>
                      <div className="flex items-center gap-2 text-gray-600">
                        <MapPin size={16} />
                        <span>{selectedCommunity.location}</span>
                      </div>
                    </div>

                    {/* Recent Members */}
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-3">Membres récents</h3>
                      <div className="flex items-center gap-4">
                        {selectedCommunity.membersList?.slice(0, 2).map((member) => (
                          <div key={member.id} className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center font-medium">
                              {member.avatar}
                            </div>
                            <div>
                              <div className="font-medium text-gray-900">{member.name}</div>
                              <div className="text-sm text-gray-500">membre</div>
                            </div>
                          </div>
                        ))}
                        <span className="text-sm text-gray-500">+{selectedCommunity.additionalMembers} autres</span>
                      </div>
                    </div>
                  </div>
                )}

                {activeTab === 'membres' && (
                  <div className="space-y-4">
                    {selectedCommunity.membersList?.map((member) => (
                      <div key={member.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 bg-blue-500 text-white rounded-full flex items-center justify-center font-medium text-lg">
                            {member.avatar}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{member.name}</div>
                            <div className="text-sm text-gray-500">{member.username}</div>
                            <div className="flex items-center gap-2 text-sm">
                              <Star className="text-yellow-400" size={14} fill="currentColor" />
                              <span>{member.rating}</span>
                              <span className="text-gray-500">• {member.trips} trajets</span>
                            </div>
                          </div>
                        </div>
                        <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs font-medium">
                          Membre
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {activeTab === 'trajets' && (
                  <div className="space-y-4">
                    {selectedCommunity.tripsList?.length > 0 ? (
                      selectedCommunity.tripsList.map((trip) => (
                        <div key={trip.id} className="p-4 border border-gray-200 rounded-lg">
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center font-medium">
                                AB
                              </div>
                              <div>
                                <div className="font-medium text-gray-900">{trip.user}</div>
                                <div className="text-sm text-gray-500">{trip.date}</div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-lg font-bold text-blue-600">{trip.price}</div>
                              <div className="text-sm text-gray-500">{trip.availableSeats} places disponibles</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 text-gray-600">
                            <MapPin size={16} />
                            <span>{trip.from}</span>
                            <span className="mx-2">→</span>
                            <MapPin size={16} />
                            <span>{trip.to}</span>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-8 text-gray-500">
                        Aucun trajet actif pour le moment
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Modal Footer */}
              <div className="flex justify-between p-6 border-t bg-gray-50">
                <button 
                  onClick={handleCloseCommunity}
                  className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  Fermer
                </button>
                <button 
                  onClick={() => handleLeaveCommunity(selectedCommunity.id)}
                  className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Quitter la communauté
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
        </div>
  );
};

export default CommunitiesPage;