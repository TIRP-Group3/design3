import React from 'react';
import TopNavbar from './TopNavbar'; // Reusing TopNavbar
// import UserSidebar from './UserSidebar'; // If a user-specific sidebar is needed later
import './AdminLayout.css'; // Can reuse AdminLayout's main content styling for now

const UserLayout = ({ children }) => {
  return (
    <div className="admin-layout"> {/* Reuse class name or create UserLayout.css */}
      <TopNavbar userType="user" /> {/* Pass userType */}
      <div className="admin-layout-main">
        {/* <UserSidebar /> */} {/* Optional: if users have a sidebar */}
        <main className="admin-layout-content" style={{ marginLeft: 0 /* No admin sidebar */ }}>
          {children}
        </main>
      </div>
    </div>
  );
};
export default UserLayout;