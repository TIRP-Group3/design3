import React from 'react';
import { Link } from 'react-router-dom'; // For the "VIEW" button
import { FiDatabase, FiEye, FiTrash2 } from 'react-icons/fi'; // Example icons
import './DatasetCard.css'; // We'll create this CSS file

const DatasetCard = ({ dataset, onDelete }) => {
  const handleDelete = () => {
    if (window.confirm(`Are you sure you want to delete dataset "${dataset.name}"? This action cannot be undone.`)) {
      onDelete(dataset.id);
    }
  };

  return (
    <div className="dataset-card">
      <div className="dataset-card-icon">
        <FiDatabase size={40} />
      </div>
      <div className="dataset-card-content">
        <h4 className="dataset-name">{dataset.name} (ID: {dataset.id})</h4>
        <p className="dataset-description">
          {dataset.description || "No description available."}
        </p>
        <p className="dataset-details">
          Path: {dataset.file_path ? `...${dataset.file_path.slice(-30)}` : 'N/A'} <br />
          Uploaded: {new Date(dataset.upload_date).toLocaleDateString()}
        </p>
      </div>
      <div className="dataset-card-actions">
        <Link to={`/admin/datasets/${dataset.id}`} className="action-button view-button">
          <FiEye /> VIEW
        </Link>
        <button onClick={handleDelete} className="action-button delete-button">
          <FiTrash2 /> REMOVE
        </button>
      </div>
    </div>
  );
};

export default DatasetCard;