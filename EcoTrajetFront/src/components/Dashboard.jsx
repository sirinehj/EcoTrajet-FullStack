import React from 'react';
import { 
  Car, 
  Users, 
  Star, 
  Recycle, 
  Plus, 
  Search, 
  UserPlus, 
  User,
  TrendingUp
} from 'lucide-react';

const Dashboard = () => {
  // Sample data - replace with your actual data structure
  const stats = {
    tripsCompleted: 0,
    activeCommunities: 0,
    averageRating: 0,
    totalReviews: 0,
    savingsAmount: 342,
    co2Saved: 127
  };

  const recentTrips = [
    {
      id: 1,
      from: "Boulogne-Billancourt",
      to: "La Défense",
      date: "30/06/2024",
      status: "Confirmé",
      seats: "3/3 places"
    },
    {
      id: 2,
      from: "Campus LyonTech",
      to: "Part-Dieu",
      date: "30/06/2024",
      status: "Confirmé",
      seats: "2/4 places"
    }
  ];

  const StatCard = ({ title, value, subtitle, icon: Icon, color, trend }) => (
    <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-2">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mb-1">{value}</p>
          {subtitle && (
            <p className="text-xs text-gray-500">{subtitle}</p>
          )}
          {trend && (
            <div className="flex items-center mt-2">
              <TrendingUp className="w-3 h-3 text-green-500 mr-1" />
              <span className="text-xs text-green-600">{trend}</span>
            </div>
          )}
        </div>
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );

  const TripCard = ({ trip }) => (
    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg mb-3 last:mb-0">
      <div className="flex items-center space-x-4">
        <div className="p-2 bg-blue-100 rounded-lg">
          <Car className="w-5 h-5 text-blue-600" />
        </div>
        <div>
          <p className="font-medium text-gray-900">
            {trip.from} → {trip.to}
          </p>
          <p className="text-sm text-gray-500">{trip.date}</p>
        </div>
      </div>
      <div className="text-right">
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
          {trip.status}
        </span>
        <p className="text-xs text-gray-500 mt-1">{trip.seats}</p>
      </div>
    </div>
  );

  const QuickAction = ({ icon: Icon, label, primary = false }) => (
    <button 
      className={`flex items-center justify-center space-x-2 px-4 py-3 rounded-lg transition-colors w-full ${
        primary 
          ? 'bg-blue-600 text-white hover:bg-blue-700' 
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
    >
      <Icon className="w-4 h-4" />
      <span className="text-sm font-medium">{label}</span>
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Tableau de bord</h1>
          <p className="text-gray-600">Aperçu de votre activité et de vos communautés</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Trajets effectués"
            value={stats.tripsCompleted}
            trend="+12% ce mois"
            icon={Car}
            color="bg-blue-100 text-blue-600"
          />
          <StatCard
            title="Communautés actives"
            value={stats.activeCommunities}
            trend="+2 nouvelles"
            icon={Users}
            color="bg-green-100 text-green-600"
          />
          <StatCard
            title="Note moyenne"
            value={stats.averageRating}
            subtitle={`(${stats.totalReviews} avis)`}
            icon={Star}
            color="bg-yellow-100 text-yellow-600"
          />
    
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Trips */}
          <div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Trajets récents</h2>
              <div className="space-y-3">
                {recentTrips.map((trip) => (
                  <TripCard key={trip.id} trip={trip} />
                ))}
              </div>
              {recentTrips.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Car className="w-12 h-12 mx-auto mb-3 text-gray-300" />
                  <p>Aucun trajet récent</p>
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Actions rapides</h2>
              <div className="space-y-3">
                <QuickAction
                  icon={Plus}
                  label="Publier un trajet"
                  primary={true}
                />
                <QuickAction
                  icon={Search}
                  label="Rechercher un trajet"
                />
                <QuickAction
                  icon={UserPlus}
                  label="Créer une communauté"
                />
                <QuickAction
                  icon={User}
                  label="Modifier le profil"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;