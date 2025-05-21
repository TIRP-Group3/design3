import React, { useState, useEffect } from 'react';
import UserLayout from '../components/Layout/UserLayout'; // Import UserLayout
import { getModelsForUser, scanFile } from '../services/api';

const UserDashboardPage = () => {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [fileToScan, setFileToScan] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState('');
  
  // Hardcode user ID for now. In a real app, this would come from auth context.
  const currentUserId = 2; // Example User ID for testing scans

  useEffect(() => {
    const fetchUserModels = async () => {
      setIsLoadingModels(true);
      setError('');
      try {
        const availableModels = await getModelsForUser();
        setModels(availableModels.filter(m => m.model_path && m.accuracy !== null));
      } catch (err) {
        setError('Failed to fetch available models.');
        setModels([]);
      } finally {
        setIsLoadingModels(false);
      }
    };
    fetchUserModels();
  }, []);

  const handleFileChange = (event) => {
    setFileToScan(event.target.files[0]);
    setScanResult(null);
    setError('');
  };

  const handleScanSubmit = async (event) => {
    event.preventDefault();
    if (!fileToScan || !selectedModel) {
      setError('Please select a model and a file to scan.');
      return;
    }
    setIsScanning(true);
    setError('');
    setScanResult(null);
    try {
      const formData = new FormData();
      formData.append('file', fileToScan);
      formData.append('model_id', selectedModel);
      formData.append('user_id', currentUserId); 

      const result = await scanFile(formData);
      setScanResult(result); 
    } catch (err) {
      setError(err.detail || err.message || 'File scan failed.');
      setScanResult(null);
    } finally {
      setIsScanning(false);
    }
  };
  
  const pageStyle = {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  };
  const formStyle = {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
    maxWidth: '500px',
    marginBottom: '30px',
    padding: '20px',
    border: '1px solid #ddd',
    borderRadius: '5px',
    backgroundColor: '#f9f9f9'
  };
  const inputStyle = {
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '4px',
  };
  const buttonStyle = {
    padding: '10px 15px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  };

  return (
    <UserLayout> {/* All content for the page goes INSIDE UserLayout */}
      <div style={pageStyle}> {/* This div is now correctly a child of UserLayout */}
        <h1>User Dashboard</h1>
        <p>Upload your documents (CSV format expected by current models) here to scan them.</p>

        <form onSubmit={handleScanSubmit} style={formStyle}>
          <div>
            <label htmlFor="modelSelectUser">Select Model for Scanning:</label>
            <select
              id="modelSelectUser"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              required
              disabled={isLoadingModels || models.length === 0}
              style={inputStyle}
            >
              <option value="">
                {isLoadingModels ? "Loading models..." : (models.length === 0 ? "No models available" : "Select a model")}
              </option>
              {models.map(model => (
                <option key={model.id} value={model.id}>
                  {model.name} (ID: {model.id}, Acc: {(model.accuracy * 100).toFixed(2)}%)
                </option>
              ))}
            </select>
            {models.length === 0 && !isLoadingModels && <p style={{fontSize: '0.9em', color: 'orange'}}>No models are currently available for scanning.</p>}
          </div>

          <div>
            <label htmlFor="fileUploadUser">Choose File to Scan (CSV):</label>
            <input
              type="file"
              id="fileUploadUser"
              accept=".csv"
              onChange={handleFileChange}
              required
              style={inputStyle}
            />
          </div>

          <button type="submit" disabled={isScanning || !fileToScan || !selectedModel} style={buttonStyle}>
            {isScanning ? 'Scanning...' : 'Scan File'}
          </button>
        </form>

        {error && <p style={{ color: 'red', marginTop: '15px', padding: '10px', border: '1px solid red', borderRadius: '4px' }}>Error: {error}</p>}
        
        {scanResult && (
          <div style={{marginTop: '30px', padding: '15px', border: '1px solid #eee', borderRadius: '5px', backgroundColor: '#f8f9fa'}}>
            <h2>Scan Result (ID: {scanResult.id}):</h2>
            <p><strong>File:</strong> {scanResult.file_name}</p>
            <p><strong>Scan Date:</strong> {new Date(scanResult.scan_date).toLocaleString()}</p>
            <p><strong>Threat Detected:</strong> {scanResult.is_threat_detected ? 'Yes' : 'No'}</p>
            <h4>Details:</h4>
            <pre style={{backgroundColor: '#e9ecef', padding: '10px', borderRadius: '4px', whiteSpace: 'pre-wrap', wordBreak: 'break-all'}}>
              {JSON.stringify(scanResult.results, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </UserLayout> // UserLayout now correctly encloses all page content
  );
};

export default UserDashboardPage;