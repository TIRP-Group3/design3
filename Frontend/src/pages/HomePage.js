import React from 'react';
import { useNavigate } from 'react-router-dom';
import './HomePage.css'; // We'll create this for styling

const HomePage = () => {
  const navigate = useNavigate();

  const goToAdminDashboard = () => {
    navigate('/admin');
  };

  const goToUserDashboard = () => {
    navigate('/user');
  };

  return (
    <div className="home-container">
      <header className="home-header">
        <h1>Welcome to the Security Scan Application</h1>
        <p>Your comprehensive solution for dataset management and threat scanning.</p>
      </header>
      <main className="home-main-content">
        <h2>Choose Your Dashboard</h2>
        <div className="dashboard-options">
          <button onClick={goToAdminDashboard} className="dashboard-button admin-button">
            Admin Dashboard
          </button>
          <button onClick={goToUserDashboard} className="dashboard-button user-button">
            User Dashboard
          </button>
        </div>
      </main>
      <footer className="home-footer">
        <p>&copy; {new Date().getFullYear()} Security Scan App. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default HomePage;