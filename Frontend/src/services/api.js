import axios from 'axios';
const API_BASE_URL = 'http://127.0.0.1:8001/api/v1'; // Adjust this to your actual API base URL

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json', },
});

export const uploadDataset = async (formData) => {
  // formData already correctly excludes owner_id from component
  try {
    const response = await apiClient.post('/admin/datasets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data', },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading dataset:', error.response?.data || error.message);
    throw error.response?.data || new Error('Dataset upload failed');
  }
};

export const getDatasets = async () => { /* ... (no change) ... */ 
    try {
        const response = await apiClient.get('/admin/datasets/');
        return response.data;
    } catch (error) {
        console.error('Error fetching datasets:', error.response?.data || error.message);
        throw error.response?.data || new Error('Failed to fetch datasets');
    }
};

export const trainModel = async (trainingData) => {
  // trainingData (FormData) already correctly excludes owner_id from component
  try {
    const response = await apiClient.post('/admin/models/train/', trainingData, {
      headers: { 'Content-Type': 'multipart/form-data', },
    });
    return response.data;
  } catch (error) {
    console.error('Error training model:', error.response?.data || error.message);
    throw error.response?.data || new Error('Model training failed');
  }
};

export const getModels = async () => { /* ... (no change) ... */ 
    try {
        const response = await apiClient.get('/admin/models/');
        return response.data;
    } catch (error) {
        console.error('Error fetching models:', error.response?.data || error.message);
        throw error.response?.data || new Error('Failed to fetch models');
    }
};

export const getNotifications = async (skip = 0, limit = 10) => {
  try {
    // Ensure the URL is a clean template literal with variables correctly interpolated
    const url = `/admin/notifications/?skip=${skip}&limit=${limit}`;
    console.log("Notification Service: Requesting URL:", url); // For debugging
    const response = await apiClient.get(url);
    console.log("Notification Service: Received response:", response.data); // For debugging
    return response.data;
  } catch (error) {
    console.error('Error fetching notifications:', error.response?.data || error.message);
    // It's helpful to log the full error object from Axios for more details
    if (error.response) {
        console.error("Axios error response data:", error.response.data);
        console.error("Axios error response status:", error.response.status);
        console.error("Axios error response headers:", error.response.headers);
    } else if (error.request) {
        console.error("Axios error request (no response received):", error.request);
    } else {
        console.error('Axios error message:', error.message);
    }
    throw error.response?.data || new Error('Failed to fetch notifications');
  }
};

export const getUnreadNotificationCount = async () => {
  try {
    const response = await apiClient.get('/admin/notifications/unread_count/');
    return response.data; // Should be an integer
  } catch (error) {
    console.error('Error fetching unread notification count:', error.response?.data || error.message);
    throw error.response?.data || new Error('Failed to fetch unread count');
  }
};

export const markNotificationsAsRead = async (logIds) => {
  try {
    const response = await apiClient.post('/admin/notifications/mark_read/', { log_ids: logIds });
    return response.data;
  } catch (error) {
    console.error('Error marking notifications as read:', error.response?.data || error.message);
    throw error.response?.data || new Error('Failed to mark notifications as read');
  }
};

export const markAllNotificationsAsRead = async () => {
  try {
    const response = await apiClient.post('/admin/notifications/mark_all_read/');
       return response.data;
} catch (error) {
console.error('Error marking all notifications as read:', error.response?.data || error.message);
throw error.response?.data || new Error('Failed to mark all as read');
}
};

// Function to get models suitable for user scanning (could be same as admin's getModels for now)
export const getModelsForUser = async () => {
  // Assuming general getModels is fine for users to see, or create a specific user endpoint
  return getModels(); 
};

export const scanFile = async (formData) => {
  // formData should include: 'file', 'model_id', 'user_id'
  try {
    const response = await apiClient.post('/user/scan/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data; // This will be the ScanHistory object
  } catch (error) {
    console.error('Error scanning file:', error.response?.data || error.message);
    throw error.response?.data || new Error('File scan failed');
  }
};

export const getScanHistory = async (skip = 0, limit = 7) => { // Fetch latest 7 for sidebar
  try {
    const response = await apiClient.get(`/admin/scan-history/?skip=<span class="math-inline">\{skip\}&limit\=</span>{limit}`);
    return response.data; // This will be a list of ScanHistory objects
  } catch (error) {
    console.error('Error fetching scan history:', error.response?.data || error.message);
    throw error.response?.data || new Error('Failed to fetch scan history');
  }
};


export const deleteDataset = async (datasetId) => {
  try {
    const response = await apiClient.delete(`/admin/datasets/${datasetId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting dataset ${datasetId}:`, error.response?.data || error.message);
    throw error.response?.data || new Error('Failed to delete dataset');
  }
};

export default apiClient;