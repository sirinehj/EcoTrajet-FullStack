import React from 'react';
import { MapPin, Calendar } from 'lucide-react';

const TransportCoSearchbar = () => {
  return (
    <div className="relative w-full h-[500px] ">
      {/* Full-width background image */}
      <div 
        className="w-screen h-[500px] bg-cover bg-center flex items-center relative left-1/2 right-1/2 -ml-[50vw] -mr-[50vw]"
        style={{
          backgroundImage: 'linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url(photo.webp)'
        }}
      >
        {/* Centered content container */}
        <div className="w-full mx-auto px-4 sm:px-6 lg:px-8 text-center text-white z-1">
          {/* Main Heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 leading-tight">
            Voyagez ensemble, économisez ensemble
          </h1>
          
          {/* Subtitle */}
          <p className="text-xl sm:text-2xl mb-12 font-light opacity-90">
            Rejoignez des communautés locales et partagez vos trajets
          </p>
          
          {/* Search Form */}
          <div className="w-full max-w-5xl mx-auto">
            <div className="bg-white rounded-2xl shadow-2xl p-8">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
                
                {/* Departure Field */}
                <div className="space-y-3">
                  <label className="block text-left text-gray-700 font-semibold text-sm uppercase tracking-wide">
                    Départ
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Ville de départ"
                      className="w-full pl-12 pr-4 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none text-gray-800 placeholder-gray-400 transition-colors"
                    />
                  </div>
                </div>
                
                {/* Arrival Field */}
                <div className="space-y-3">
                  <label className="block text-left text-gray-700 font-semibold text-sm uppercase tracking-wide">
                    Arrivée
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Ville d'arrivée"
                      className="w-full pl-12 pr-4 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none text-gray-800 placeholder-gray-400 transition-colors"
                    />
                  </div>
                </div>
                
                {/* Date Field */}
                <div className="space-y-3">
                  <label className="block text-left text-gray-700 font-semibold text-sm uppercase tracking-wide">
                    Date
                  </label>
                  <div className="relative">
                    <Calendar className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="date"
                      className="w-full pl-12 pr-4 py-4 rounded-xl border-2 border-gray-200 focus:border-blue-500 focus:outline-none text-gray-800 transition-colors"
                    />
                  </div>
                </div>
                
                {/* Search Button */}
                <div className="space-y-3">
                  <div className="h-6"></div>
                  <button className="w-full py-4 px-8 rounded-xl bg-green-500 hover:bg-green-600 text-white font-semibold text-lg transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl">
                    Rechercher
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Other components will go below this one */}
    </div>
  );
};

export default TransportCoSearchbar;