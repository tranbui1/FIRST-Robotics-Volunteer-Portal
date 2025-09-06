import './App.css';
import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Questionnaire from './pages/Questionnaire';
import Results from './pages/Results';
import Page from './pages/Page';
import AdminUpload from './pages/AdminUpload'; 

/**
 * Main application component that defines all route paths.
 *
 * @component
 * @returns {JSX.Element} The app routes
 */
function App() {
  return (
    <Routes>
      {/* Landing page */}
      <Route path="/" element={<Home />} />

      {/* Questionnaire for matching roles */}
      <Route path="/match" element={<Questionnaire />} />

      {/* Results overview page */}
      <Route path="/results" element={<Results />} />

      {/* Individual role details page */}
      <Route path="/results/:roleName" element={<Page />} />

      {/* Admin upload page for CSVs */}
      <Route path="/admin-upload" element={<AdminUpload />} />
    </Routes>
  );
}

export default App;