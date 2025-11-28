import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Loader2, AlertCircle, BookOpen, Database } from 'lucide-react';
import { motion } from 'framer-motion';
import { searchPapers } from '../services/api';

const SearchPage = () => {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [sources, setSources] = useState(['arxiv', 'pubmed', 'google_scholar']);
  const [maxResults, setMaxResults] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const availableSources = [
    { id: 'arxiv', name: 'arXiv', icon: '📚' },
    { id: 'pubmed', name: 'PubMed', icon: '🏥' },
    { id: 'google_scholar', name: 'Google Scholar', icon: '🎓' },
    { id: 'ieee', name: 'IEEE Xplore', icon: '⚡' },
  ];

  const handleSourceToggle = (sourceId) => {
    setSources(prev => 
      prev.includes(sourceId) 
        ? prev.filter(s => s !== sourceId)
        : [...prev, sourceId]
    );
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    if (sources.length === 0) {
      setError('Please select at least one data source');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await searchPapers(query, sources, maxResults);
      navigate(`/results/${response.session_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start search. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl mb-6 shadow-lg">
              <Search className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
              Search Research Papers
            </h1>
            <p className="text-xl text-gray-600">
              Search across multiple academic databases simultaneously
            </p>
          </div>

          {/* Search Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
            <form onSubmit={handleSearch} className="space-y-6">
              {/* Search Input */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Search Query
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., machine learning in healthcare, quantum computing, climate change..."
                    className="input-field pr-12 text-lg"
                    disabled={loading}
                  />
                  <BookOpen className="absolute right-4 top-1/2 transform -translate-y-1/2 w-6 h-6 text-gray-400" />
                </div>
              </div>

              {/* Data Sources */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3 flex items-center">
                  <Database className="w-4 h-4 mr-2" />
                  Select Data Sources
                </label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {availableSources.map(source => (
                    <button
                      key={source.id}
                      type="button"
                      onClick={() => handleSourceToggle(source.id)}
                      disabled={loading}
                      className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                        sources.includes(source.id)
                          ? 'border-primary-500 bg-primary-50 shadow-md'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      } ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:shadow-lg'}`}
                    >
                      <div className="text-2xl mb-2">{source.icon}</div>
                      <div className={`text-sm font-medium ${
                        sources.includes(source.id) ? 'text-primary-700' : 'text-gray-700'
                      }`}>
                        {source.name}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Max Results */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Results per Source: {maxResults}
                </label>
                <input
                  type="range"
                  min="5"
                  max="50"
                  step="5"
                  value={maxResults}
                  onChange={(e) => setMaxResults(Number(e.target.value))}
                  disabled={loading}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-primary-600"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>5</span>
                  <span>25</span>
                  <span>50</span>
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700"
                >
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  <span>{error}</span>
                </motion.div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full btn-primary py-4 text-lg font-bold flex items-center justify-center space-x-3"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-6 h-6 animate-spin" />
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-6 h-6" />
                    <span>Search Papers</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Info Cards */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="text-blue-600 font-semibold mb-1">Multi-Source</div>
              <div className="text-sm text-gray-600">Search multiple databases at once</div>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-xl p-4">
              <div className="text-purple-600 font-semibold mb-1">AI Analysis</div>
              <div className="text-sm text-gray-600">Get intelligent paper summaries</div>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-xl p-4">
              <div className="text-green-600 font-semibold mb-1">Fast Results</div>
              <div className="text-sm text-gray-600">Lightning-fast search results</div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SearchPage;
