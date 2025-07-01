import React from 'react';
import TransportCoSearchbar from '../components/TransportCoSearchbar';
import Dashboard from '../components/Dashboard';

const HomePage = () => {
  return (
    <div className="flex flex-col">
      <TransportCoSearchbar />
      <div className="flex flex-col">
        <Dashboard />
      </div>
    </div>
  );
};

export default HomePage;