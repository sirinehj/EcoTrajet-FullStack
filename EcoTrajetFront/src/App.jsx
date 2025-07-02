import { Routes, Route } from 'react-router-dom';
import { useState } from 'react';
import TrajetsDisponibles from './pages/TrajetsDisponibles';
import MonProfil from './pages/MonProfil';
import CommunitiesPage from './pages/CommunitiesPage';
import TransportCoRegistration from './pages/TransportCoRegistration';
import HomePage from './pages/HomePage';
import TransportCoNavbar from './components/TransportCoNavbar';
import Footer from './components/Footer'; // ✅ Import the footer
import './app.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <div className="flex flex-col min-h-screen">
      {/* Navbar */}
      {isLoggedIn && <TransportCoNavbar onLogout={handleLogout} />}

      {/* Page content */}
      <div className="flex-grow">
        <Routes>
          {/* Public route as default (e.g., registration/login page) */}
          <Route path="/" element={<TransportCoRegistration onLogin={handleLogin} />} />

          {/* Protected pages (can still be visited via URL, but navbar appears only when logged in) */}
          <Route path="/trajets" element={<TrajetsDisponibles />} />
          <Route path="/profil" element={<MonProfil />} />
          <Route path="/communautes" element={<CommunitiesPage />} />
          <Route path="/accueil" element={<HomePage />} />
        </Routes>
      </div>

      {/* Footer is always visible */}
      <Footer />
    </div>
  );
}

export default App;
