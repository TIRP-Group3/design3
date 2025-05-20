import React, { useState } from 'react';
import { trainModel } from '../../services/api';

const ModelTrainForm = ({ datasets, onModelTrained, isLoadingDatasets }) => {
  const [modelName, setModelName] = useState('');
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  // const [ownerId, setOwnerId] = useState('1'); // REMOVED
  const [targetColumn, setTargetColumn] = useState('');
  const [kmeansParamsStr, setKmeansParamsStr] = useState('{\n  "n_clusters": 3,\n  "n_init": "auto",\n  "max_iter": 300\n}'); // Updated n_init to "auto"
  const [svmParamsStr, setSvmParamsStr] = useState('{\n  "C": 1.0,\n  "kernel": "rbf",\n  "gamma": "scale",\n  "probability": true\n}');
  const [testSize, setTestSize] = useState('0.2');
  const [randomState, setRandomState] = useState('42');

  const [isTraining, setIsTraining] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!modelName.trim() || !selectedDatasetId) { // Owner ID check removed
      setError('Model Name and Dataset are required.');
      return;
    }

    let parsedKmeansParams, parsedSvmParams;
    try {
      parsedKmeansParams = JSON.parse(kmeansParamsStr);
      parsedSvmParams = JSON.parse(svmParamsStr);
    } catch (jsonError) {
      setError('Invalid JSON format for K-Means or SVM parameters. Please check syntax.');
      return;
    }

    const formData = new FormData();
    formData.append('name', modelName);
    formData.append('dataset_id', selectedDatasetId);
    // formData.append('owner_id', parseInt(ownerId, 10)); // REMOVED
    if (targetColumn.trim()) {
      formData.append('target_column_name', targetColumn.trim());
    }
    formData.append('kmeans_params_str', JSON.stringify(parsedKmeansParams));
    formData.append('svm_params_str', JSON.stringify(parsedSvmParams));
    formData.append('test_size', parseFloat(testSize));
    if (randomState.trim()) {
      formData.append('random_state', parseInt(randomState, 10));
    }

    setIsTraining(true);
    setMessage('');
    setError('');

    try {
      const trainedModel = await trainModel(formData);
      setMessage(`Model "${trainedModel.name}" trained successfully! Accuracy: ${trainedModel.accuracy !== null ? (trainedModel.accuracy * 100).toFixed(2) + '%' : 'N/A'}`);
      setModelName('');
      setSelectedDatasetId('');
      setTargetColumn('');
      if (onModelTrained) {
        onModelTrained();
      }
    } catch (err) {
      setError(err.detail || err.message || 'Failed to train model.');
    } finally {
      setIsTraining(false);
    }
  };

  // ... (styles remain the same)
  const formStyle = { /* ... */ };
  const inputStyle = { /* ... */ };
  const textAreaStyle = { /* ... */ };
  const buttonStyle = { /* ... */ };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <div>
        <label htmlFor="modelName">Model Name:</label>
        <input id="modelName" type="text" value={modelName} onChange={(e) => setModelName(e.target.value)} placeholder="Enter a name for your model" required style={inputStyle}/>
      </div>
      <div>
        <label htmlFor="datasetSelect">Select Dataset:</label>
        <select id="datasetSelect" value={selectedDatasetId} onChange={(e) => setSelectedDatasetId(e.target.value)} required disabled={isLoadingDatasets || datasets.length === 0} style={inputStyle}>
          <option value="">{isLoadingDatasets ? "Loading..." : "Select a dataset"}</option>
          {!isLoadingDatasets && datasets.map(d => (<option key={d.id} value={d.id}>{d.name} (ID: {d.id})</option>))}
        </select>
        {datasets.length === 0 && !isLoadingDatasets && <p style={{fontSize: '0.9em', color: 'orange'}}>No datasets available. Please upload one first.</p>}
      </div>
      {/* Owner ID Input REMOVED */}
      <div>
        <label htmlFor="targetColumn">Target Column Name (Optional):</label>
        <input id="targetColumn" type="text" value={targetColumn} onChange={(e) => setTargetColumn(e.target.value)} placeholder="Name of target/label column in CSV (if not last)" style={inputStyle}/>
      </div>
      <div>
        <label htmlFor="kmeansParams">K-Means Parameters (JSON):</label>
        <textarea id="kmeansParams" value={kmeansParamsStr} onChange={(e) => setKmeansParamsStr(e.target.value)} rows="5" style={textAreaStyle}/>
      </div>
      <div>
        <label htmlFor="svmParams">SVM Parameters (JSON):</label>
        <textarea id="svmParams" value={svmParamsStr} onChange={(e) => setSvmParamsStr(e.target.value)} rows="5" style={textAreaStyle}/>
      </div>
      <div>
        <label htmlFor="testSize">Test Split Size (e.g., 0.2 for 20%):</label>
        <input id="testSize" type="number" step="0.01" min="0.1" max="0.5" value={testSize} onChange={(e) => setTestSize(e.target.value)} style={inputStyle}/>
      </div>
      <div>
        <label htmlFor="randomState">Random State (integer, for reproducibility):</label>
        <input id="randomState" type="number" value={randomState} onChange={(e) => setRandomState(e.target.value)} placeholder="e.g., 42" style={inputStyle}/>
      </div>
      <button type="submit" disabled={isTraining || !selectedDatasetId} style={buttonStyle}>
        {isTraining ? 'Training Model...' : 'Train Model'}
      </button>
      {message && <p style={{ color: 'green' }}>{message}</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </form>
  );
};

export default ModelTrainForm;