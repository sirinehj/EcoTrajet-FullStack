import React from 'react';
import TransportCoNavbar from '../components/TransportCoNavbar';
import TransportCoSearchbar from '../components/TransportCoSearchbar';
import Dashboard from '../components/Dashboard';

const HomePage = () => {
  const handleLogout = () => {
    // Handle logout logic here
    // You might want to redirect to login page or clear user data
    console.log('Logout clicked');
  };

  return (
    <div className="flex flex-col">
      <TransportCoNavbar onLogout={handleLogout} />
      <div className="pt-16"> {/* Add padding-top to account for fixed navbar */}
        <TransportCoSearchbar />
        <div className="flex flex-col">
          <Dashboard />
        </div>
      </div>
    </div>
  );
};

export default HomePage;