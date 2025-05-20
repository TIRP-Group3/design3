import React, { useEffect, useState } from 'react';
import AdminLayout from '../components/Layout/AdminLayout';
import { getScanHistory } from '../services/api'; // Reuse existing API
import { Link } from 'react-router-dom';

const AdminFullHistoryPage = () => {
  const [fullHistory, setFullHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  // Add pagination state if needed: const [page, setPage] = useState(0); const limit = 20;

  useEffect(() => {
    const fetchFullHistory = async () => {
      setLoading(true);
      try {
        // Fetch more items for a "full" history page, e.g., 50 or implement pagination
        const historyData = await getScanHistory(0, 50); 
        setFullHistory(historyData);
      } catch (error) {
        console.error("Failed to fetch full scan history:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchFullHistory();
  }, []); // Add page to dependency array if pagination is implemented

  return (
    <AdminLayout>
      <h2>Full Scan History</h2>
      {loading ? <p>Loading history...</p> : (
        fullHistory.length > 0 ? (
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {fullHistory.map(item => (
              <li key={item.id} style={{ padding: '10px', borderBottom: '1px solid #eee' }}>
                <Link to={`/admin/scans/${item.id}`}>
                  <strong>File:</strong> {item.file_name} ({new Date(item.scan_date).toLocaleDateString()})
                </Link>
                <div>User ID: {item.user_id}, Model ID: {item.model_id}</div>
                <div>Summary: {item.results?.summary || "N/A"}</div>
                <div style={{ color: item.is_threat_detected ? 'red' : 'green' }}>
                  Threat Detected: {item.is_threat_detected ? 'Yes' : 'No'}
                </div>
              </li>
            ))}
          </ul>
        ) : <p>No scan history available.</p>
      )}
      {/* Future: Add pagination controls */}
    </AdminLayout>
  );
};

export default AdminFullHistoryPage;