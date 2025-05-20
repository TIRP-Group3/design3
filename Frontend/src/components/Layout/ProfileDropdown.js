import React, { useState } from 'react';
import './ProfileDropdown.css'; // Make sure you have this CSS file from the previous step

const ProfileDropdown = ({ 
    userName = "User",         // Default if not provided
    userRole = "USER",         // Default if not provided
    userType = "user"          // "admin" or "user", controls admin-specific sections
}) => {
  // Show admin privileges section by default if userType is admin
  const [showAdminPrivileges, setShowAdminPrivileges] = useState(userType === "admin");
  const [allowNotifications, setAllowNotifications] = useState(true); // Default to true

  const userInitial = userName ? userName.charAt(0).toUpperCase() : 'U';

  // Placeholder functions for admin actions - these would navigate or open modals/forms
  const handleAdminAction = (action) => {
    alert(`${action} clicked. Functionality not yet implemented.`);
    // Examples:
    // if (action === 'Add User') navigate('/admin/users/add');
    // if (action === 'Read Users List') navigate('/admin/users');
  };

  return (
    <div className="profile-dropdown">
      <div className="dropdown-header">
        <div className="profile-pic">{userInitial}</div>
        <div className="dropdown-header-info">
          <div className="name">{userName}</div>
          <div className="role">{userRole}</div>
        </div>
      </div>

      <div className="dropdown-section">
        <div className="dropdown-section-title">Account</div>
        {userType === "admin" && ( // Only show Admin Privileges toggle for admin userType
          <div className="toggle-item">
            <label htmlFor="admin-privileges-toggle">Show Admin Privileges</label>
            <label className="switch">
              <input 
                type="checkbox" 
                id="admin-privileges-toggle"
                checked={showAdminPrivileges} 
                onChange={() => setShowAdminPrivileges(!showAdminPrivileges)} 
              />
              <span className="slider round"></span>
            </label>
          </div>
        )}
        <div className="toggle-item">
          <label htmlFor="notifications-toggle">Allow notification</label>
          <label className="switch">
            <input 
              type="checkbox" 
              id="notifications-toggle"
              checked={allowNotifications} 
              onChange={() => setAllowNotifications(!allowNotifications)} 
            />
            <span className="slider round"></span>
          </label>
        </div>
      </div>

      {userType === "admin" && showAdminPrivileges && ( // Only show Admin Privileges section if toggle is on AND user is admin
        <div className="dropdown-section privileges-list">
          <div className="dropdown-section-title">Admin Privileges</div>
          <ul>
            <li><span>Add User</span> <a href="#!" onClick={(e) => { e.preventDefault(); handleAdminAction('Add User'); }}>ADD</a></li>
            <li><span>Delete User</span> <a href="#!" onClick={(e) => { e.preventDefault(); handleAdminAction('Delete User'); }}>DEL</a></li>
            <li><span>Update User</span> <a href="#!" onClick={(e) => { e.preventDefault(); handleAdminAction('Update User'); }}>UPDATE</a></li>
            <li><span>Read Users List</span> <a href="#!" onClick={(e) => { e.preventDefault(); handleAdminAction('Read Users List'); }}>READ</a></li>
          </ul>
        </div>
      )}
      
      {/* You can add other sections for general users or specific to userType === "user" here */}
      {/* For example:
      {userType === "user" && (
        <div className="dropdown-section">
          <div className="dropdown-section-title">My Profile</div>
          // ... user profile links ...
        </div>
      )}
      */}
    </div>
  );
};

export default ProfileDropdown;