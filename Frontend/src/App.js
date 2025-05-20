import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import UserDashboardPage from './pages/UserDashboardPage';
import AdminScanDetailPage from './pages/AdminScanDetailPage';
import AdminFullHistoryPage from './pages/AdminFullHistoryPage';
import AdminSettingsPage from './pages/AdminSettingsPage'; // Placeholder
import AdminDatasetDetailPage from './pages/AdminDatasetDetailPage';

import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        {/* Admin Routes - AdminDashboardPage can handle its own layout */}
        <Route path="/admin" element={<AdminDashboardPage />} />
        <Route path="/admin/scans/:scanId" element={<AdminScanDetailPage />} />
        <Route path="/admin/history" element={<AdminFullHistoryPage />} />
        <Route path="/admin/settings" element={<AdminSettingsPage />} /> 
        {/* User Routes */}
        <Route path="/user" element={<UserDashboardPage />} />
		<Route path="/admin/datasets/:datasetId" element={<AdminDatasetDetailPage />} />
        <Route path="/logout" element={<div>Logging out... (Placeholder)</div>} />
      </Routes>
    </Router>
  );
}

export default App;