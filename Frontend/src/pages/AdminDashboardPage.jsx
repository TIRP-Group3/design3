import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/Layout/AdminLayout';
import DatasetUploadForm from '../components/Admin/DatasetUploadForm';
import ModelTrainForm from '../components/Admin/ModelTrainForm';
import DatasetCard from '../components/Admin/DatasetCard'; // Import DatasetCard
import { getDatasets, getModels, deleteDataset as deleteDatasetAPI } from '../services/api'; // Import deleteDataset API
import { FiPlusCircle } from 'react-icons/fi'; // Icon for Add Dataset

const AdminDashboardPage = () => {
  const [datasets, setDatasets] = useState([]);
  const [models, setModels] = useState([]);
  const [isLoadingDatasets, setIsLoadingDatasets] = useState(false);
  const [isLoadingModels, setIsLoadingModels] = useState(false);
  const [error, setError] = useState('');
  const [showDatasetUploadForm, setShowDatasetUploadForm] = useState(false); // State for form visibility

  const fetchDatasets = async () => {
    setIsLoadingDatasets(true);
    setError('');
    try {
      const data = await getDatasets();
      
      console.log('Fetched datasets:', data); // Add this line
      setDatasets(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch datasets');
      setDatasets([]);
    } finally {
      setIsLoadingDatasets(false);
    }
  };

  const fetchModels = async () => {
    setIsLoadingModels(true);
    setError('');
    try {
      const data = await getModels();
      setModels(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch models');
      setModels([]);
    } finally {
      setIsLoadingModels(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
    fetchModels();
  }, []);

  const handleDatasetUploaded = () => {
    fetchDatasets(); // Refresh the list of datasets
    setShowDatasetUploadForm(false); // Optionally hide form after upload
  };

  const handleModelTrained = () => {
    fetchModels(); // Refresh the list of models
  };

  const handleDeleteDataset = async (datasetId) => {
    try {
      await deleteDatasetAPI(datasetId); // Call API to delete
      fetchDatasets(); // Refresh dataset list
      // Also refresh models if they might be dependent on this dataset and should be re-evaluated
      fetchModels();
    } catch (err) {
      setError(err.message || `Failed to delete dataset ID ${datasetId}`);
    }
  };

  const pageSectionStyle = { // Renamed from sectionStyle to avoid conflict if AdminLayout has it
    border: '1px solid #e0e0e0', // Lighter border
    padding: '25px', // More padding
    marginBottom: '25px',
    borderRadius: '8px',
    backgroundColor: '#ffffff',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  };

  const datasetsGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', // Responsive grid
    gap: '20px',
    marginBottom: '25px',
  };

  const addDatasetButtonStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 15px',
    backgroundColor: '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontSize: '1em',
    marginBottom: '20px',
  };

  return (
    <AdminLayout>
      {/* The H1 from AdminLayout might be enough, or keep this for specific page title */}
      {/* <h1>Admin Dashboard</h1> */}
      {error && <p style={{ color: 'red', padding: '10px', backgroundColor: '#ffebee', border: '1px solid red', borderRadius: '4px' }}>Error: {error}</p>}

      {/* Section for Uploading and Training Forms */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px', marginBottom: '25px' }}>
        <div style={pageSectionStyle}>
          <h2>Upload New Dataset</h2>
          <p>Provide a CSV file containing your data for training security models.</p>
          {/* Toggle visibility of the form */}
          {!showDatasetUploadForm && (
            <button 
              onClick={() => setShowDatasetUploadForm(true)} 
              style={addDatasetButtonStyle}
            >
              <FiPlusCircle /> Add New Dataset
            </button>
          )}
          {showDatasetUploadForm && (
            <>
              <DatasetUploadForm onDatasetUploaded={handleDatasetUploaded} />
              <button 
                onClick={() => setShowDatasetUploadForm(false)} 
                style={{...addDatasetButtonStyle, backgroundColor: '#6c757d', marginTop: '10px'}}
              >
                Cancel Upload
              </button>
            </>
          )}
        </div>

        <div style={pageSectionStyle}>
          <h2>Train New Model</h2>
          <p>Select an uploaded dataset and configure parameters to train a K-Means+SVM model.</p>
          <ModelTrainForm datasets={datasets} onModelTrained={handleModelTrained} isLoadingDatasets={isLoadingDatasets} />
        </div>
      </div>
      
      {/* Datasets Display Section */}
      <div style={pageSectionStyle}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
            <h2>Available Datasets</h2>
            {/* Add filter/sort options here in future if needed */}
        </div>
        {isLoadingDatasets ? <p>Loading datasets...</p> : (
          datasets.length > 0 ? (
            <div style={datasetsGridStyle}>
              {datasets.map(dataset => (
                <DatasetCard key={dataset.id} dataset={dataset} onDelete={handleDeleteDataset} />
              ))}
            </div>
          ) : <p>No datasets available. Click "Add New Dataset" to upload one.</p>
        )}
      </div>

      {/* Trained Models List (can also be converted to cards later if desired) */}
      <div style={pageSectionStyle}>
        <h2>Trained Models</h2>
        {isLoadingModels ? <p>Loading models...</p> : (
          models.length > 0 ? (
            <ul style={{ listStyleType: 'none', paddingLeft: 0 }}>
              {models.map(model => (
                <li key={model.id} style={{ padding: '10px', borderBottom: '1px solid #eee', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{model.name}</strong> (ID: {model.id}) <br />
                    <span style={{ fontSize: '0.9em', color: '#555' }}>Dataset ID: {model.dataset_id} | </span>
                    <span style={{ fontSize: '0.9em', color: model.accuracy > 0.7 ? 'green' : 'orange' }}>
                        Accuracy: {model.accuracy !== null ? `${(model.accuracy * 100).toFixed(2)}%` : 'N/A'}
                    </span>
                  </div>
                  {/* <Link to={`/admin/models/${model.id}`} className="action-button view-button" style={{fontSize: '0.8em'}}>VIEW</Link> */}
                </li>
              ))}
            </ul>
          ) : <p>No models trained yet.</p>
        )}
      </div>
    </AdminLayout>
  );
};

export default AdminDashboardPage;