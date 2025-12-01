import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Loader2, CheckCircle2, AlertCircle, ExternalLink, Calendar, User, FileText, ArrowLeft, TrendingUp, Clock, Download, Bookmark, BookmarkCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { getSearchStatus, getSearchResults } from '../services/api';
import { addBookmark, removeBookmark, isBookmarked } from '../services/bookmarkService';

const ResultsPage = () => {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [bookmarkedPapers, setBookmarkedPapers] = useState({});

  useEffect(() => {
    let interval;

    const checkStatus = async () => {
      try {
        const statusData = await getSearchStatus(sessionId);
        setStatus(statusData);

        if (statusData.status === 'completed') {
          const resultsData = await getSearchResults(sessionId, sortBy);
          
          // Flatten the paper structure: backend returns {paper: {...}, analysis: {...}}
          // but frontend expects just the paper fields at top level
          if (resultsData && resultsData.papers) {
            const flattenedPapers = resultsData.papers.map(item => {
              // For arXiv papers, the id is the full URL, so extract just the URL
              let sourceUrl = item.paper.id;
              
              // If it's an arXiv paper and id looks like a URL, use it as source
              if (item.paper.source === 'arxiv' && item.paper.id.startsWith('http')) {
                sourceUrl = item.paper.id;
              }
              
              return {
                ...item.paper,
                published_date: item.paper.published, // Map 'published' to 'published_date'
                citations: item.paper.citation_count, // Map 'citation_count' to 'citations'
                url: sourceUrl, // Use paper id as source URL (arXiv entry_id is a URL)
                analysis: item.analysis
              };
            });
            setResults({ ...resultsData, papers: flattenedPapers });
            
            // Check bookmark status for all papers
            const bookmarkStatus = {};
            flattenedPapers.forEach(paper => {
              bookmarkStatus[paper.id] = isBookmarked(paper.id);
            });
            setBookmarkedPapers(bookmarkStatus);
          } else {
            setResults(resultsData);
          }
          
          setLoading(false);
          clearInterval(interval);
        } else if (statusData.status === 'failed') {
          setError('Search failed. Please try again.');
          setLoading(false);
          clearInterval(interval);
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to fetch results');
        setLoading(false);
        clearInterval(interval);
      }
    };

    checkStatus();
    interval = setInterval(checkStatus, 2000);

    return () => clearInterval(interval);
  }, [sessionId, sortBy]);

  const getSourceBadgeColor = (source) => {
    const colors = {
      arxiv: 'bg-blue-100 text-blue-700 border-blue-300',
      pubmed: 'bg-green-100 text-green-700 border-green-300',
      google_scholar: 'bg-teal-100 text-teal-700 border-teal-300',
      ieee: 'bg-yellow-100 text-yellow-700 border-yellow-300',
    };
    return colors[source] || 'bg-gray-100 text-gray-700 border-gray-300';
  };

  const handleBookmarkToggle = (paper) => {
    const isCurrentlyBookmarked = bookmarkedPapers[paper.id];
    if (isCurrentlyBookmarked) {
      removeBookmark(paper.id);
    } else {
      addBookmark(paper);
    }
    setBookmarkedPapers(prev => ({
      ...prev,
      [paper.id]: !isCurrentlyBookmarked
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <div className="relative mb-8">
            <div className="w-24 h-24 bg-gradient-to-r from-primary-500 to-teal-600 rounded-full flex items-center justify-center mx-auto">
              <Loader2 className="w-12 h-12 text-white animate-spin" />
            </div>
            <div className="absolute inset-0 bg-gradient-to-r from-primary-500 to-teal-600 rounded-full blur-xl opacity-30 animate-pulse"></div>
          </div>
          <h2 className="text-3xl font-bold mb-4 text-gray-900">Searching Papers...</h2>
          <p className="text-gray-600 mb-6">This may take a few moments</p>
          {status && (
            <div className="bg-white rounded-xl shadow-lg p-6 max-w-md mx-auto">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Query:</span>
                  <span className="text-sm font-semibold text-gray-900">{status.query}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Sources:</span>
                  <span className="text-sm font-semibold text-gray-900">{status.sources?.join(', ')}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Status:</span>
                  <span className="badge bg-primary-100 text-primary-700">{status.status}</span>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md"
        >
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <AlertCircle className="w-10 h-10 text-red-600" />
          </div>
          <h2 className="text-2xl font-bold mb-4 text-gray-900">Something went wrong</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => navigate('/search')}
            className="btn-primary"
          >
            Try Again
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <button
            onClick={() => navigate('/search')}
            className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 mb-6 transition-colors duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">New Search</span>
          </button>

          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <CheckCircle2 className="w-8 h-8 text-green-500" />
                <h1 className="text-3xl font-bold text-gray-900">Search Results</h1>
              </div>
              <p className="text-gray-600">
                Found <span className="font-semibold text-primary-600">{results?.papers?.length || 0}</span> papers for "{status?.query}"
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="relevance">Relevance</option>
                <option value="date">Date</option>
                <option value="citations">Citations</option>
              </select>
            </div>
          </div>
        </motion.div>

        {/* Results Grid */}
        <AnimatePresence>
          {results?.papers && results.papers.length > 0 ? (
            <div className="grid gap-6">
              {results.papers.map((paper, index) => (
                <motion.div
                  key={paper.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.4, delay: index * 0.05 }}
                  className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 p-6 border border-gray-100"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2 flex-wrap">
                        <span className={`badge border ${getSourceBadgeColor(paper.source)}`}>
                          {paper.source}
                        </span>
                        {paper.citations !== undefined && paper.citations > 0 && (
                          <span className="badge bg-gray-100 text-gray-700 border border-gray-300">
                            <TrendingUp className="w-3 h-3 mr-1" />
                            {paper.citations} citations
                          </span>
                        )}
                      </div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2 hover:text-primary-600 transition-colors">
                        <Link to={`/paper/${encodeURIComponent(paper.id)}`} state={{ paper }}>{paper.title}</Link>
                      </h3>
                      {paper.authors && paper.authors.length > 0 && (
                        <div className="flex items-center text-gray-600 mb-2">
                          <User className="w-4 h-4 mr-2" />
                          <span className="text-sm">{paper.authors.slice(0, 3).join(', ')}{paper.authors.length > 3 && ' et al.'}</span>
                        </div>
                      )}
                      {paper.published_date && (
                        <div className="flex items-center text-gray-500 text-sm mb-3">
                          <Calendar className="w-4 h-4 mr-2" />
                          <span>{new Date(paper.published_date).toLocaleDateString()}</span>
                        </div>
                      )}
                      {paper.abstract && (
                        <p className="text-gray-700 line-clamp-3 mb-4">{paper.abstract}</p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center space-x-4">
                      <Link
                        to={`/paper/${encodeURIComponent(paper.id)}`}
                        state={{ paper }}
                        className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium transition-colors"
                      >
                        <FileText className="w-4 h-4" />
                        <span>View Details & Chat</span>
                      </Link>
                      <button
                        onClick={() => handleBookmarkToggle(paper)}
                        className={`flex items-center space-x-2 transition-colors ${
                          bookmarkedPapers[paper.id]
                            ? 'text-primary-600 hover:text-primary-700'
                            : 'text-gray-600 hover:text-gray-900'
                        }`}
                      >
                        {bookmarkedPapers[paper.id] ? (
                          <BookmarkCheck className="w-4 h-4" />
                        ) : (
                          <Bookmark className="w-4 h-4" />
                        )}
                        <span className="text-sm">{bookmarkedPapers[paper.id] ? 'Bookmarked' : 'Bookmark'}</span>
                      </button>
                    </div>
                    <div className="flex items-center space-x-4">
                      {paper.pdf_url && (
                        <a
                          href={paper.pdf_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 font-medium transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <Download className="w-4 h-4" />
                          <span className="text-sm">PDF</span>
                        </a>
                      )}
                      {paper.url && (
                        <a
                          href={paper.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink className="w-4 h-4" />
                          <span className="text-sm">View Source</span>
                        </a>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-20"
            >
              <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-600 mb-2">No papers found</h3>
              <p className="text-gray-500">Try adjusting your search query or sources</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ResultsPage;
