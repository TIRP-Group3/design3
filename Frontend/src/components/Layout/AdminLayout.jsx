import React from 'react';
import TopNavbar from './TopNavbar';
import Sidebar from './Sidebar';
import './AdminLayout.css';

const AdminLayout = ({ children }) => {
  return (
    <div className="admin-layout">
      <TopNavbar />
      <div className="admin-layout-main">
        <Sidebar />
        <main className="admin-layout-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;