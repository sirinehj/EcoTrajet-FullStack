import React, { useState, useEffect } from 'react';
import { MapPin, Calendar, Filter, Star, Users, Music, Plus } from 'lucide-react';
import { tripService } from '../api/trips';
import TransportCoNavbar from '../components/TransportCoNavbar';

export default function TrajetsDisponibles() {
  const [searchData, setSearchData] = useState({
    depart: '',
    arrivee: '',
    date: ''
  });

  // trips state holds an array of trips
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const tripsData = await tripService.getTrips();
        setTrips(tripsData ?? []);
      } catch (err) {
        setError(err.message || "Erreur lors du chargement des trajets");
      } finally {
        setLoading(false);
      }
    };
    fetchTrips();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const params = {
        departure_city: searchData.depart,
        arrival_city: searchData.arrivee,
        departure_date: searchData.date,  // note changed to departure_date (matches your service)
      };
      const filteredTrips = await tripService.getTrips(params);
      setTrips(filteredTrips ?? []);
    } catch (err) {
      setError(err.message || "Erreur lors de la recherche");
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field, value) => {
    setSearchData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLogout = () => {
    // Handle logout logic here
    // You might want to redirect to login page or clear user data
    console.log('Logout clicked');
  };

  const formatDate = (dateString) => {
    const options = { weekday: 'long', day: 'numeric', month: 'long' };
    return new Date(dateString).toLocaleDateString('fr-FR', options);
  };

  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  if (loading) {
    return (
      <div>
        <TransportCoNavbar onLogout={handleLogout} />
        <div className="min-h-screen bg-gray-50 flex items-center justify-center pt-16">
          Loading...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <TransportCoNavbar onLogout={handleLogout} />
        <div className="min-h-screen bg-gray-50 flex items-center justify-center pt-16">
          <div className="text-center">
            <div className="text-red-500 mb-4">{error}</div>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  const tripsArray = Array.isArray(trips) ? trips : [];

  return (
    <div>
      <TransportCoNavbar onLogout={handleLogout} />
      <div className="min-h-screen bg-gray-50 pt-16">
        {/* Header and Search */}
        <div className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Trajets disponibles</h1>
                <p className="text-gray-600 mt-1">Trouvez votre prochain voyage</p>
              </div>
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
                <Plus size={20} />  Trajet
              </button>
            </div>
            <form onSubmit={handleSearch} className="bg-white border rounded-lg p-6 shadow-sm">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Départ</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <input
                      type="text"
                      placeholder="Ville de départ"
                      value={searchData.depart}
                      onChange={(e) => handleInputChange('depart', e.target.value)}
                      className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Arrivée</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <input
                      type="text"
                      placeholder="Ville d'arrivée"
                      value={searchData.arrivee}
                      onChange={(e) => handleInputChange('arrivee', e.target.value)}
                      className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div className="relative">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <input
                      type="date"
                      value={searchData.date}
                      onChange={(e) => handleInputChange('date', e.target.value)}
                      className="w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div className="flex items-end">
                  <button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-6 rounded-lg font-medium flex items-center justify-center gap-2"
                  >
                    <Filter size={18} /> Rechercher
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>

        {/* Results */}
        <div className="max-w-7xl mx-auto px-4 py-6">
          {tripsArray.length === 0 ? (
            <div className="text-center py-12">
              <h3 className="text-lg font-medium text-gray-900">No trips found</h3>
              <p className="mt-2 text-gray-600">Try adjusting your search criteria</p>
            </div>
          ) : (
            <div className="space-y-4">
              {tripsArray.map((trip) => (
                <div key={trip.id} className="bg-white rounded-lg border shadow-sm hover:shadow-md transition-shadow">
                  <div className="p-6">
                    <div className="flex items-center gap-4 mb-4">
                      <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                        {trip.conducteur?.prenom?.[0]}{trip.conducteur?.nom?.[0]}
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">{trip.conducteur?.prenom} {trip.conducteur?.nom}</h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Star className="text-yellow-400 fill-current" size={16} />
                            <span>{trip.conducteur?.note ?? '4.5'}</span>
                          </div>
                          <span>{trip.conducteur?.trajets_count ?? 0} trajets</span>
                          <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700">Conducteur</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-900">
                          {trip.prix !== undefined && !isNaN(trip.prix) ? Number(trip.prix).toFixed(2) : 'N/A'} €
                        </div>
                        <div className="text-sm text-gray-600">par personne</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                        <div>
                          <div className="font-medium text-gray-900">{trip.origine}</div>
                          <div className="text-sm text-gray-600">{formatTime(trip.temps_depart)}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        <div>
                          <div className="font-medium text-gray-900">{trip.destination}</div>
                          <div className="text-sm text-gray-600">{formatTime(trip.temps_arrive)}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Calendar className="text-gray-400" size={16} />
                        <div>
                          <div className="font-medium text-gray-900">{formatDate(trip.temps_depart)}</div>
                          <div className="text-sm text-gray-600">{new Date(trip.temps_depart).toLocaleDateString('fr-FR')}</div>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6 mt-4 pt-4 border-t">
                      <div className="flex items-center gap-2">
                        <Users className="text-gray-400" size={16} />
                        <span className="text-sm text-gray-600">{trip.places_dispo} places disponibles</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-gray-600">{trip.preferences?.fumeur ? 'Fumeur' : 'Non fumeur'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {trip.preferences?.musique ? (
                          <>
                            <Music className="text-gray-400" size={16} />
                            <span className="text-sm text-gray-600">Musique ok</span>
                          </>
                        ) : (
                          <span className="text-sm text-gray-600">Pas de musique</span>
                        )}
                      </div>
                      {trip.preferences?.discussion && (
                        <div className="flex items-center gap-2">
                          <span className="text-sm text-gray-600">{trip.preferences.discussion}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}