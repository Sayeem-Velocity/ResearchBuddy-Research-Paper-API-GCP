import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchPapers = async (query, sources = ['arxiv', 'pubmed', 'google_scholar'], maxResults = 20) => {
  const response = await api.post('/papers/search', {
    query,
    sources,
    max_results: maxResults,
    sort_by: 'relevance',
    generate_analysis: true,
  });
  return response.data;
};

export const getSearchStatus = async (sessionId) => {
  const response = await api.get(`/papers/search/status/${sessionId}`);
  return response.data;
};

export const getSearchResults = async (sessionId, sortBy = 'relevance') => {
  const response = await api.get(`/papers/search/results/${sessionId}`, {
    params: { sort_by: sortBy },
  });
  return response.data;
};

export const chatWithPaper = async (paperId, message, conversationHistory = []) => {
  // URL-encode the paper ID to handle URLs with special characters
  const encodedPaperId = encodeURIComponent(paperId);
  const response = await api.post(`/papers/${encodedPaperId}/chat`, {
    message,
    conversation_history: conversationHistory,
  });
  return response.data;
};

export const getChatHistory = async (paperId) => {
  const encodedPaperId = encodeURIComponent(paperId);
  const response = await api.get(`/papers/${encodedPaperId}/chat/history`);
  return response.data;
};

export default api;
