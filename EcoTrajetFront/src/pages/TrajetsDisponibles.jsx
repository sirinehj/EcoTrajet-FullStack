import React, { useState } from 'react';
import { MapPin, Calendar, Filter, Star, Users, Volume2, VolumeX, Music, Plus } from 'lucide-react';

export default function TrajetsDisponibles() {
  const [searchData, setSearchData] = useState({
    depart: '',
    arrivee: '',
    date: ''
  });

  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  const trips = [
    {
      id: 1,
      driver: {
        name: 'Amed Ben Said',
        initials: 'AB',
        rating: 4.8,
        tripCount: 47,
        badges: ['Trajets Entreprise Paris']
      },
      departure: {
        city: 'Boulogne-Billancourt',
        time: '09:00'
      },
      arrival: {
        city: 'La Défense',
        time: '09:45'
      },
      date: '30 juin 2024',
      dateShort: '30 juin',
      price: 5.50,
      availableSeats: 3,
      totalSeats: 3,
      preferences: {
        smoking: false,
        music: true,
        chat: 'ok'
      }
    },
    {
      id: 2,
      driver: {
        name: 'Amed Ben Said',
        initials: 'AB',
        rating: 4.8,
        tripCount: 47,
        badges: ['Étudiants Université Lyon']
      },
      departure: {
        city: 'Campus LyonTech',
        time: '19:30'
      },
      arrival: {
        city: 'Part-Dieu',
        time: '20:00'
      },
      date: '30 juin 2024',
      dateShort: '30 juin',
      price: 3.00,
      availableSeats: 2,
      totalSeats: 4,
      preferences: {
        smoking: false,
        music: false,
        chat: 'Bavardage'
      }
    }
  ];

  const handleSearch = (e) => {
    e.preventDefault();
    // Handle search logic here
    console.log('Searching with:', searchData);
  };

  const handleInputChange = (field, value) => {
    setSearchData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Trajets disponibles</h1>
              <p className="text-gray-600 mt-1">Trouvez votre prochain voyage</p>
            </div>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
              <Plus size={20} />
              Publier un trajet
            </button>
          </div>

          {/* Search Form */}
          <div className="bg-white border rounded-lg p-6 shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              {/* Departure */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-2">Départ</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    placeholder="Ville de départ"
                    value={searchData.depart}
                    onChange={(e) => handleInputChange('depart', e.target.value)}
                    className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Arrival */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-2">Arrivée</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    placeholder="Ville d'arrivée"
                    value={searchData.arrivee}
                    onChange={(e) => handleInputChange('arrivee', e.target.value)}
                    className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Date */}
              <div className="relative">
                <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                <div className="relative">
                  <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="date"
                    value={searchData.date}
                    onChange={(e) => handleInputChange('date', e.target.value)}
                    className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Search Button */}
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={handleSearch}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-medium transition-colors flex items-center justify-center gap-2"
                >
                  <Filter size={18} />
                  Rechercher
                </button>
              </div>
            </div>

            {/* Advanced Filters Toggle */}
            <button
              type="button"
              onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
              className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
            >
              Afficher les filtres avancés
            </button>
          </div>
        </div>
      </div>

      {/* Trip Results */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="space-y-4">
          {trips.map((trip) => (
            <div key={trip.id} className="bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow">
              <div className="p-6">
                {/* Driver Info */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                    {trip.driver.initials}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{trip.driver.name}</h3>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Star className="text-yellow-400 fill-current" size={16} />
                        <span>{trip.driver.rating}</span>
                      </div>
                      <span>{trip.driver.tripCount} trajets</span>
                      {trip.driver.badges.map((badge, index) => (
                        <span
                          key={index}
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            badge.includes('Entreprise') 
                              ? 'bg-blue-100 text-blue-700' 
                              : 'bg-green-100 text-green-700'
                          }`}
                        >
                          {badge}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">{trip.price.toFixed(2)} €</div>
                    <div className="text-sm text-gray-600">par personne</div>
                  </div>
                </div>

                {/* Trip Details */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Departure */}
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                    <div>
                      <div className="font-medium text-gray-900">{trip.departure.city}</div>
                      <div className="text-sm text-gray-600">{trip.departure.time}</div>
                    </div>
                  </div>

                  {/* Arrival */}
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                    <div>
                      <div className="font-medium text-gray-900">{trip.arrival.city}</div>
                      <div className="text-sm text-gray-600">{trip.arrival.time}</div>
                    </div>
                  </div>

                  {/* Date */}
                  <div className="flex items-center gap-3">
                    <Calendar className="text-gray-400" size={16} />
                    <div>
                      <div className="font-medium text-gray-900">{trip.date}</div>
                      <div className="text-sm text-gray-600">{trip.dateShort}</div>
                    </div>
                  </div>
                </div>

                {/* Trip Preferences */}
                <div className="flex items-center gap-6 mt-4 pt-4 border-t">
                  <div className="flex items-center gap-2">
                    <Users className="text-gray-400" size={16} />
                    <span className="text-sm text-gray-600">
                      {trip.availableSeats}/{trip.totalSeats} places
                    </span>
                  </div>
                  
                  <div className="flex items-center gap-2">
                    {trip.preferences.smoking ? (
                      <span className="text-sm text-gray-600">Fumeur</span>
                    ) : (
                      <span className="text-sm text-gray-600">Non fumeur</span>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    {trip.preferences.music ? (
                      <>
                        <Music className="text-gray-400" size={16} />
                        <span className="text-sm text-gray-600">Musique ok</span>
                      </>
                    ) : (
                      <span className="text-sm text-gray-600">Pas de musique</span>
                    )}
                  </div>

                  {trip.preferences.chat && (
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-600">{trip.preferences.chat}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}