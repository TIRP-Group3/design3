import React, { useState } from 'react';
import { uploadDataset } from '../../services/api';

const DatasetUploadForm = ({ onDatasetUploaded }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [file, setFile] = useState(null);
  // const [ownerId, setOwnerId] = useState('1'); // REMOVED
  const [isUploading, setIsUploading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !name.trim()) { // Owner ID check removed
      setError('Name and a dataset file are required.');
      return;
    }

    const formData = new FormData();
       formData.append('name', name);
formData.append('description', description);
// formData.append('owner_id', parseInt(ownerId, 10)); // REMOVED
formData.append('file', file);

    setIsUploading(true);
    setMessage('');
    setError('');

    try {
      await uploadDataset(formData);
      setMessage('Dataset uploaded successfully!');
      setName('');
      setDescription('');
      setFile(null);
      // setOwnerId('1'); // REMOVED
      if (document.getElementById('dataset-file-input')) {
        document.getElementById('dataset-file-input').value = '';
      }
      if (onDatasetUploaded) {
        onDatasetUploaded();
      }
    } catch (err) {
      setError(err.detail || err.message || 'Failed to upload dataset.');
    } finally {
      setIsUploading(false);
    }
  };

  // ... (styles remain the same)
  const formStyle = { /* ... */ };
  const inputStyle = { /* ... */ };
  const buttonStyle = { /* ... */ };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <div>
        <label htmlFor="datasetName">Dataset Name:</label>
        <input
          id="datasetName" type="text" value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter dataset name" required style={inputStyle}
        />
      </div>
      <div>
        <label htmlFor="datasetDescription">Description (Optional):</label>
        <textarea
          id="datasetDescription" value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description of the dataset"
          style={{...inputStyle, height: '60px'}}
        />
      </div>
      {/* Owner ID Input REMOVED */}
      <div>
        <label htmlFor="datasetFile">Dataset File (CSV):</label>
        <input
          id="dataset-file-input" type="file" accept=".csv"
          onChange={(e) => setFile(e.target.files[0])} required style={inputStyle}
        />
      </div>
      <button type="submit" disabled={isUploading} style={buttonStyle}>
        {isUploading ? 'Uploading...' : 'Upload Dataset'}
      </button>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
};

export default DatasetUploadForm;