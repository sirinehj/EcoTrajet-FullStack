import { Routes, Route } from 'react-router-dom';
import TrajetsDisponibles from './pages/TrajetsDisponibles';
import MonProfil from './pages/MonProfil';
import CommunitiesPage from './pages/CommunitiesPage';
import TransportCoRegistration from './pages/TransportCoRegistration';
import HomePage from './pages/HomePage';
import TransportCoNavbar from './components/TransportCoNavbar';

import './app.css';
function App() {
  return (
    <div>
      <TransportCoNavbar />
      <br />      <br />
      <div className=" m-0 p-0"> {/* This pushes content below the fixed navbar */}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/trajets" element={<TrajetsDisponibles />} />
          <Route path="/profil" element={<MonProfil />} />
          <Route path="/communities" element={<CommunitiesPage />} />
          <Route path="/register" element={<TransportCoRegistration />} />
        </Routes>
      </div>
    </div>
  );
}
export default App;