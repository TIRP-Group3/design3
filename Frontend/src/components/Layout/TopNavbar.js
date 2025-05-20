// frontend_app/src/components/Layout/TopNavbar.js
import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import ProfileDropdown from './ProfileDropdown';
import NotificationPanel from './NotificationPanel';
import { getUnreadNotificationCount } from '../../services/api';
import { FiHome, FiBell } from 'react-icons/fi';
import './TopNavbar.css';

const TopNavbar = ({ userType = "admin" }) => {
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const [notificationPanelOpen, setNotificationPanelOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  const profileTriggerRef = useRef(null); // Ref for the profile icon/trigger area
  const notificationTriggerRef = useRef(null); // Ref for the notification icon/trigger area
  
  // Refs for the dropdown panels themselves (these will be on the root div of those components)
  // For this approach, we don't need to pass refs to children if we use event.target.closest()

  const profileName = userType === "admin" ? "Josh Armstrong" : "Test User"; // Using name from doc
  const profileInitial = profileName.charAt(0).toUpperCase();
  const profileRole = userType === "admin" ? "ADMINISTRATOR" : "USER";

  const fetchAndUpdateUnreadCount = async () => {
    try {
      // TODO: Adapt for user-specific count if userType === "user"
      // For now, admin count is global, user count would need user ID.
      const count = await getUnreadNotificationCount(); 
      setUnreadCount(count);
    } catch (error) {
      console.error("TopNavbar: Failed to fetch unread count", error);
      setUnreadCount(0);
    }
  };
  
  useEffect(() => { 
    fetchAndUpdateUnreadCount(); 
  }, [userType]); // Re-fetch if userType changes (e.g. if app supported login/logout)

  const toggleProfileDropdown = () => {
    setProfileDropdownOpen(prev => !prev);
    if (notificationPanelOpen) setNotificationPanelOpen(false);
  };

  const toggleNotificationPanel = async () => {
    const opening = !notificationPanelOpen;
    setNotificationPanelOpen(opening);
    if (profileDropdownOpen) setProfileDropdownOpen(false);
    if (opening) { 
       await fetchAndUpdateUnreadCount(); // Refresh count when panel is opened
    }
  };
  
  const handleNewUnreadCount = (count) => { 
    setUnreadCount(count); 
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      // Check for Profile Dropdown
      // If the click is NOT on the trigger AND NOT inside an element with class 'profile-dropdown'
      if (profileTriggerRef.current && !profileTriggerRef.current.contains(event.target) &&
          !event.target.closest('.profile-dropdown')) { // Uses class name of the dropdown's root
        setProfileDropdownOpen(false);
      }

      // Check for Notification Panel
      // If the click is NOT on the trigger AND NOT inside an element with class 'notification-panel'
      if (notificationTriggerRef.current && !notificationTriggerRef.current.contains(event.target) &&
          !event.target.closest('.notification-panel')) { // Uses class name of the panel's root
        setNotificationPanelOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []); // Empty dependency array means this effect runs once on mount and cleans up on unmount

  return (
    <nav className="top-navbar">
      <div className="top-navbar-left">
        <Link to="/" className="nav-item" title="Home">
          <FiHome size={20} style={{ verticalAlign: 'middle', marginRight: '5px' }} />
          Home
        </Link>
        <span className="nav-item active">Dashboards</span>
        <span className="nav-item">Default</span>
      </div>
      <div className="top-navbar-center">
        <input type="text" placeholder="Search" className="search-bar" />
      </div>
      <div className="top-navbar-right">
        {/* Notification Section */}
        <div className="notification-icon-wrapper" ref={notificationTriggerRef}> {/* Wrapper for the trigger ref */}
          <div className="notification-icon" onClick={toggleNotificationPanel}>
            <FiBell size={22} />
            {unreadCount > 0 && <span className="indicator">{unreadCount > 9 ? '9+' : unreadCount}</span>}
          </div>
          {notificationPanelOpen && <NotificationPanel onVisibilityChange={setNotificationPanelOpen} onNewUnreadCount={handleNewUnreadCount} userType={userType} />}
        </div>
        
        {/* Profile Section */}
        <div className="profile-section-wrapper" ref={profileTriggerRef}> {/* Wrapper for the trigger ref */}
          <div className="profile-section" onClick={toggleProfileDropdown}>
            <div className="profile-pic" style={{ backgroundColor: userType === "admin" ? '#007bff' : '#28a745' }}>
              {profileInitial}
            </div>
            <span className="profile-name">{profileName}</span>
            <span style={{ marginLeft: '5px', fontSize: '0.8em' }}>▼</span>
          </div>
          {profileDropdownOpen && <ProfileDropdown userName={profileName} userRole={profileRole} userType={userType} />}
        </div>
      </div>
    </nav>
  );
};

export default TopNavbar;