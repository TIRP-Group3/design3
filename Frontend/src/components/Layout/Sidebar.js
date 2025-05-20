import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { getScanHistory } from '../../services/api'; // Import the new API call
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  const [scanHistory, setScanHistory] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  useEffect(() => {
    const fetchHistory = async () => {
      setIsLoadingHistory(true);
      try {
        const historyData = await getScanHistory(0, 7); // Get latest 7 entries for the sidebar
        setScanHistory(historyData);
      } catch (error) {
        console.error("Failed to fetch scan history for sidebar:", error);
        setScanHistory([]); // Clear history on error
      } finally {
        setIsLoadingHistory(false);
      }
    };
    fetchHistory();
  }, []);

  // Helper to format history item text (simple version)
  const formatHistoryText = (item) => {
    const date = new Date(item.scan_date);
    const dateString = `${date.toLocaleString('en-US', { weekday: 'short' }).toUpperCase()} ${date.getDate()} ${date.toLocaleString('en-US', { month: 'short' }).toUpperCase()}`;
    // Example: "SUN 14 FEB File 'report.csv'"
    // You might want to include dataset name or model name if available and relevant
    // This requires fetching related model/dataset data or having it in ScanHistory results.
    // For now, just using file_name.
    let summary = item.results?.summary || "Scan processed";
    if (item.file_name) {
        summary = `File '${item.file_name}' scan`;
    }

    // Truncate if too long for sidebar
    const maxLength = 30;
    const displayText = `${dateString} - ${summary}`;
    return displayText.length > maxLength ? displayText.substring(0, maxLength) + "..." : displayText;
  };

  // Placeholder for user-specific coloring (not implemented yet)
  const getHistoryItemColorClass = (userId) => {
    // if (userId === 1) return "color-admin"; // Example
    // if (userId === 2) return "color-user-type1";
    return ""; // Default no specific color class
  };

  return (
    <aside className="sidebar">
      <nav>
        <Link // Changed to Link for better SPA navigation
          to="/admin" 
          className={`sidebar-nav-item ${location.pathname.startsWith('/admin') || location.pathname === '/' ? 'active' : ''}`}
        >
          DASHBOARD
        </Link>

        <div className="sidebar-header">HISTORY</div>
        {isLoadingHistory ? (
          <p className="sidebar-nav-item" style={{color: '#95a5a6', fontSize: '0.85em'}}>Loading history...</p>
        ) : scanHistory.length > 0 ? (
          <ul className="scan-history-list">
            {scanHistory.map(item => (
              <li key={item.id}>
                {/* Link to a future scan detail page */}
                <Link 
                  to={`/admin/scans/${item.id}`} 
                  className={`sidebar-nav-item ${getHistoryItemColorClass(item.user_id)}`}
                  title={item.results?.summary || `Scan ID: ${item.id}`}
                >
                  {formatHistoryText(item)}
                </Link>
              </li>
            ))}
          </ul>
        ) : (
          <p className="sidebar-nav-item" style={{color: '#95a5a6', fontSize: '0.85em'}}>No scan history yet.</p>
        )}
        {scanHistory.length > 0 && (
            <Link to="/admin/history" className="sidebar-nav-item" style={{textAlign: 'center', fontSize: '0.85em', color: '#7f8c8d'}}>
                View All History
            </Link> // Link to a future full history page
        )}
      </nav>

      <div className="sidebar-footer">
        {/* These can be Link components if they navigate within the app */}
        <Link to="/admin/settings" className="sidebar-footer-item">Settings</Link>
        <Link to="/logout" className="sidebar-footer-item">Logout</Link> 
        {/* Logout would typically not be a simple Link in a real app with auth */}
      </div>
    </aside>
  );
};

export default Sidebar;