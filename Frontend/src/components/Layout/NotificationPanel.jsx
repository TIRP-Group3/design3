import React, { useState, useEffect } from 'react';
import { getNotifications, markNotificationsAsRead, markAllNotificationsAsRead } from '../../services/api';
import './NotificationPanel.css';

const NotificationPanel = ({ onVisibilityChange, onNewUnreadCount }) => {
  const [notifications, setNotifications] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchNotifs = async () => {
  setIsLoading(true);
  console.log("NotificationPanel: Fetching notifications...");
  try {
    const data = await getNotifications(0, 15); // Fetch latest 15
    console.log("NotificationPanel: Fetched data:", data); // <-- ADD THIS LOG
    setNotifications(data);
    // If data is an empty array, it will show "No new notifications."
  } catch (error) {
    console.error("NotificationPanel: Failed to fetch notifications", error);
    setNotifications([]); // Ensure it's an empty array on error
  } finally {
    setIsLoading(false);
  }
};

  useEffect(() => {
    fetchNotifs();
  }, []);

  const handleMarkAsRead = async (logId) => {
    try {
      await markNotificationsAsRead([logId]);
      setNotifications(prev => 
        prev.map(n => n.id === logId ? { ...n, is_read: true } : n)
      );
      const newUnreadCount = await getUnreadNotificationCount();
      onNewUnreadCount(newUnreadCount); // Update parent
    } catch (error) {
      console.error("Failed to mark notification as read", error);
    }
  };

  const handleMarkAllRead = async () => {
    try {
        await markAllNotificationsAsRead();
        setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
        onNewUnreadCount(0); // Update parent
    } catch (error) {
        console.error("Failed to mark all as read", error);
    }
  };

  // Helper to format date
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className="notification-panel">
      <div className="notification-panel-header">
        <h4>Notifications</h4>
        <button onClick={handleMarkAllRead} className="mark-all-read">Mark all as read</button>
      </div>
      {isLoading ? (
        <p className="no-notifications">Loading...</p>
      ) : notifications.length === 0 ? (
        <p className="no-notifications">No new notifications.</p>
      ) : (
        <ul className="notification-list">
          {notifications.map(notif => (
            <li 
              key={notif.id} 
              className={`notification-item ${!notif.is_read ? 'unread' : ''}`}
              onClick={() => !notif.is_read && handleMarkAsRead(notif.id)} // Mark as read on click if unread
            >
              {notif.username && <span className="username">{notif.username}:</span>}
              <span className="message">{notif.message}</span>
              <span className="timestamp">{formatDate(notif.timestamp)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default NotificationPanel;