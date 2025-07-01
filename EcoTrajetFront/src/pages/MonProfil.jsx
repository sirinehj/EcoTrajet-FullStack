import React, { useState } from 'react';
import { User, Mail, Phone, Calendar, Route, CheckCircle, Users, Star, ArrowRight, Car, MapPin, Clock } from 'lucide-react';

export default function MonProfil() {
  const [activeTab, setActiveTab] = useState('informations');

  // User data matching your database schema
  const userData = {
    idUser: 1,
    Nom: 'Ben Said',
    Prenom: 'Amed',
    Email: 'bensaida991@gmail.com',
    Password: '••••••••', // Hidden for security
    Role: 'passager', // passager, conducteur, Admin
    Trajet: [],
    Paiement: 0, // enum value
    Telephone: '22905938',
    isStaff: false
  };

  // User profile data
  const userProfile = {
    isDriver: false,
    Bio: 'Membre depuis juin 2025'
  };

  // Vehicle data (if user is driver)
  const userVehicle = {
    idVehicule: null,
    Owner: null,
    licensePlate: null,
    make: null,
    model: null,
    couleur: null,
    nbrPlaces: null,
    isActive: false
  };

  // Membership data
  const membershipData = {
    idMembership: 1,
    idUser: userData.idUser,
    idCommun: null,
    isAdmin: false,
    Statut: 'en attente' // en attente, accepté, rejeté
  };

  // Sample trips data matching your schema
  const userTrips = [
    {
      idTrip: 1,
      departTime: '09:00',
      arrivalTime: '09:45',
      origin: 'Boulogne-Billancourt',
      Destination: 'La Défense',
      Prix: 5.50,
      nbrPlaces: 3,
      Driver: userData.idUser,
      Statut: 'Actif',
      Communaute: null
    },
    {
      idTrip: 2,
      departTime: '19:30',
      arrivalTime: '20:00',
      origin: 'Campus LyonTech',
      Destination: 'Part-Dieu',
      Prix: 3.00,
      nbrPlaces: 2,
      Driver: userData.idUser,
      Statut: 'Actif',
      Communaute: null
    }
  ];

  // Sample reservations data
  const userReservations = [
    // No reservations yet
  ];

  // Sample ratings data
  const userRatings = [
    // No ratings yet
  ];

  // Sample notifications
  const userNotifications = [
    {
      idNotif: 1,
      Titre: 'Nouveau trajet disponible',
      Message: 'Un trajet correspond à votre recherche',
      Date: '2025-06-30',
      Utilisateur: userData.idUser,
      isRead: false
    }
  ];

  // Calculate statistics
  const stats = {
    trajetsCreated: userTrips.length,
    trajetsCompleted: userTrips.filter(trip => trip.Statut === 'Terminé').length,
    reservations: userReservations.length,
    averageRating: userRatings.length > 0 
      ? (userRatings.reduce((sum, rating) => sum + rating.Score, 0) / userRatings.length).toFixed(1)
      : null
  };

  const tabs = [
    { id: 'informations', label: 'Informations' },
    { id: 'statistiques', label: 'Statistiques' },
    { id: 'activite', label: 'Activité' }
  ];

  const renderInformations = () => (
    <div className="bg-white rounded-lg border p-6 shadow-sm">
      <div className="flex items-start gap-6">
        <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
          {userData.Prenom[0]}{userData.Nom[0]}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-2xl font-bold text-gray-900">
              {userData.Prenom} {userData.Nom}
            </h2>
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
              membershipData.Statut === 'accepté' 
                ? 'bg-green-100 text-green-800' 
                : membershipData.Statut === 'en attente'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}>
              {membershipData.Statut === 'accepté' ? 'Vérifié' : 'Non vérifié'}
            </span>
            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
              userData.Role === 'Admin' 
                ? 'bg-purple-100 text-purple-800' 
                : userData.Role === 'conducteur'
                ? 'bg-blue-100 text-blue-800'
                : 'bg-gray-100 text-gray-800'
            }`}>
              {userData.Role}
            </span>
          </div>
          <p className="text-gray-600 mb-6">@{userData.Prenom.toLowerCase()}{userData.Nom.toLowerCase()}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-center gap-3">
              <Mail className="text-gray-400" size={20} />
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium text-gray-900">{userData.Email}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Phone className="text-gray-400" size={20} />
              <div>
                <p className="text-sm text-gray-600">Téléphone</p>
                <p className="font-medium text-gray-900">{userData.Telephone}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Calendar className="text-gray-400" size={20} />
              <div>
                <p className="text-sm text-gray-600">Membre depuis</p>
                <p className="font-medium text-gray-900">30 juin 2025</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <User className="text-gray-400" size={20} />
              <div>
                <p className="text-sm text-gray-600">Staff</p>
                <p className="font-medium text-gray-900">{userData.isStaff ? 'Oui' : 'Non'}</p>
              </div>
            </div>
          </div>

          {userProfile.Bio && (
            <div className="mt-6">
              <p className="text-sm text-gray-600">Bio</p>
              <p className="font-medium text-gray-900">{userProfile.Bio}</p>
            </div>
          )}

          {userData.Role === 'conducteur' && userVehicle.idVehicule && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
                <Car size={18} />
                Véhicule
              </h4>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-600">Marque/Modèle:</span>
                  <span className="ml-2 font-medium">{userVehicle.make} {userVehicle.model}</span>
                </div>
                <div>
                  <span className="text-gray-600">Couleur:</span>
                  <span className="ml-2 font-medium">{userVehicule.couleur}</span>
                </div>
                <div>
                  <span className="text-gray-600">Plaque:</span>
                  <span className="ml-2 font-medium">{userVehicle.licensePlate}</span>
                </div>
                <div>
                  <span className="text-gray-600">Places:</span>
                  <span className="ml-2 font-medium">{userVehicle.nbrPlaces}</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderStatistiques = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <Route className="text-blue-600" size={24} />
            <span className="text-sm text-gray-600">Trajets créés</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.trajetsCreated}</p>
        </div>
        
        <div className="bg-white rounded-lg border p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className="text-green-500" size={24} />
            <span className="text-sm text-gray-600">Trajets terminés</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.trajetsCompleted}</p>
        </div>
        
        <div className="bg-white rounded-lg border p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <Users className="text-green-600" size={24} />
            <span className="text-sm text-gray-600">Réservations</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats.reservations}</p>
        </div>
        
        <div className="bg-white rounded-lg border p-6 shadow-sm">
          <div className="flex items-center gap-3 mb-2">
            <Star className="text-yellow-500" size={24} />
            <span className="text-sm text-gray-600">Note moyenne</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">
            {stats.averageRating || '—'}
          </p>
        </div>
      </div>
      
      <div className="bg-white rounded-lg border p-6 shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Mes Communautés</h3>
        {membershipData.idCommun ? (
          <div className="p-4 bg-blue-50 rounded-lg">
            <p className="font-medium">Communauté #{membershipData.idCommun}</p>
            <p className="text-sm text-gray-600">
              Statut: {membershipData.Statut} 
              {membershipData.isAdmin && ' (Administrateur)'}
            </p>
          </div>
        ) : (
          <p className="text-gray-600">Vous n'avez pas encore rejoint de communautés.</p>
        )}
      </div>
    </div>
  );

  const renderActivite = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg border p-6 shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Trajets récents</h3>
        {userTrips.length > 0 ? (
          <div className="space-y-4">
            {userTrips.map((trip) => (
              <div key={trip.idTrip} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <MapPin className="text-gray-400" size={16} />
                    <p className="font-medium text-gray-900">
                      {trip.origin} → {trip.Destination}
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-1">
                      <Clock size={14} />
                      <span>{trip.departTime} - {trip.arrivalTime}</span>
                    </div>
                    <span>{trip.Prix}€</span>
                    <span>{trip.nbrPlaces} places</span>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                    trip.Statut === 'Actif' 
                      ? 'bg-blue-100 text-blue-800' 
                      : trip.Statut === 'Terminé'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {trip.Statut}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">Aucun trajet créé pour le moment.</p>
        )}
      </div>
      
      <div className="bg-white rounded-lg border p-6 shadow-sm">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Réservations récentes</h3>
        {userReservations.length > 0 ? (
          <div className="space-y-4">
            {userReservations.map((reservation) => (
              <div key={reservation.idR} className="p-4 bg-gray-50 rounded-lg">
                <p className="font-medium text-gray-900">Réservation #{reservation.idR}</p>
                <p className="text-sm text-gray-600">
                  Places: {reservation.nbrPlaces} - Statut: {reservation.Statut}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">Vous n'avez pas encore fait de réservations.</p>
        )}
      </div>

      {userNotifications.length > 0 && (
        <div className="bg-white rounded-lg border p-6 shadow-sm">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Notifications récentes</h3>
          <div className="space-y-3">
            {userNotifications.slice(0, 3).map((notif) => (
              <div key={notif.idNotif} className={`p-3 rounded-lg ${
                notif.isRead ? 'bg-gray-50' : 'bg-blue-50'
              }`}>
                <h4 className="font-medium text-sm">{notif.Titre}</h4>
                <p className="text-sm text-gray-600">{notif.Message}</p>
                <p className="text-xs text-gray-500 mt-1">{notif.Date}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <h1 className="text-3xl font-bold text-gray-900">Mon Profil</h1>
            <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
              <User size={20} />
              Modifier le profil
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex space-x-0 mb-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-6 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-gray-900 border-b-2 border-blue-600'
                  : 'text-gray-600 hover:text-gray-900 bg-gray-100'
              } ${
                tab.id === 'informations' ? 'rounded-tl-lg' : ''
              } ${
                tab.id === 'activite' ? 'rounded-tr-lg' : ''
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="min-h-96">
          {activeTab === 'informations' && renderInformations()}
          {activeTab === 'statistiques' && renderStatistiques()}
          {activeTab === 'activite' && renderActivite()}
        </div>
      </div>
    </div>
  );
}