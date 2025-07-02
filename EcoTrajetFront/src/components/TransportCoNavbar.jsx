import React, { useState } from 'react';
import { Bell, User, LogOut } from 'lucide-react';
import { Link } from 'react-router-dom';


const TransportCoNavbar = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  return (
    <nav className="bg-white border-b border-gray-200 w-full fixed top-0 left-0 right-0 z-10">
      <div className="flex items-center justify-between px-6 py-3 w-full">
        {/* Left side - Logo and Navigation */}
        <div className="flex items-center space-x-8">
          {/* Logo */}
          <div className="flex items-center">
            <div className="bg-blue-600 text-white p-1.5 rounded-lg mr-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11C5.84 5 5.28 5.42 5.08 6.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16c-.83 0-1.5-.67-1.5-1.5S5.67 13 6.5 13s1.5.67 1.5 1.5S7.33 16 6.5 16zm11 0c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z"/>
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">EcoTrajet</span>
          </div>

          {/* Navigation Links */}
      <div className="flex items-center space-x-6">
  <Link to="/HomePage" className="text-blue-600 font-medium transition-colors hover:text-blue-600">
    Tableau de bord
  </Link>
  <Link to="/communities" className="text-gray-700 font-medium transition-colors hover:text-blue-600">
    Communautés
  </Link>
  <Link to="/trajets" className="text-gray-700 font-medium transition-colors hover:text-blue-600">
    Trajets
  </Link>
</div>
        </div>

        {/* Right side - Notifications and User Profile */}
        <div className="flex items-center space-x-4">
          {/* Notification Bell */}
          <div className="relative">
            <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-full transition-colors">
              <Bell className="w-5 h-5" />
            </button>
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
              3
            </span>
          </div>

          {/* User Profile Dropdown */}
          <div className="relative">
            <button 
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-3 p-1 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-medium text-sm">
                AB
              </div>
              <span className="text-gray-700 font-medium whitespace-nowrap">Amed Ben Said</span>
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown Menu */}
   {/* Dropdown Menu */}
{isDropdownOpen && (
  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
    <Link to="/profil" className="flex items-center px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors">
      <User className="w-4 h-4 mr-3" />
      Profil
    </Link>
    <hr className="my-1 border-gray-200" />
    <Link to="/logout" className="flex items-center px-4 py-2 text-red-600 hover:bg-red-50 transition-colors">
      <LogOut className="w-4 h-4 mr-3" />
      Déconnexion
    </Link>
  </div>
)}

          </div>
        </div>
      </div>
    </nav>
  );
};

export default TransportCoNavbar;