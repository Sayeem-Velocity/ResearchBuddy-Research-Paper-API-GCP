import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Send, Loader2, Bot, User as UserIcon, ExternalLink, Calendar, Users, FileText, Sparkles, Download, Bookmark, BookmarkCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { chatWithPaper, getChatHistory } from '../services/api';
import { addBookmark, removeBookmark, isBookmarked, getCategories } from '../services/bookmarkService';

const PaperDetailPage = () => {
  const { paperId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const chatEndRef = useRef(null);
  
  // Decode the paper ID from URL encoding (do this once at the top)
  const decodedPaperId = decodeURIComponent(paperId);
  
  const [paper, setPaper] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);
  const [showCategoryMenu, setShowCategoryMenu] = useState(false);
  const [categories, setCategories] = useState([]);

  // Fetch paper data from location state or sessionStorage
  useEffect(() => {
    
    // First, try to get paper from navigation state
    if (location.state?.paper) {
      setPaper(location.state.paper);
      setLoading(false);
      // Store in sessionStorage for page refresh
      sessionStorage.setItem(`paper_${decodedPaperId}`, JSON.stringify(location.state.paper));
      return;
    }

    // If not in state, try sessionStorage
    const cachedPaper = sessionStorage.getItem(`paper_${decodedPaperId}`);
    if (cachedPaper) {
      try {
        setPaper(JSON.parse(cachedPaper));
        setLoading(false);
        return;
      } catch (e) {
        console.error('Error parsing cached paper:', e);
      }
    }

    // If no paper data found, redirect back
    setLoading(false);
    console.warn('No paper data found for ID:', decodedPaperId);
  }, [paperId, location]);

  // Check bookmark status and load categories
  useEffect(() => {
    if (paper) {
      setBookmarked(isBookmarked(paper.id));
      setCategories(getCategories());
    }
  }, [paper]);

  // Load chat history when paper is loaded
  useEffect(() => {
    if (paper && !historyLoaded) {
      loadChatHistory();
    }
  }, [paper]);

  const loadChatHistory = async () => {
    try {
      const history = await getChatHistory(decodedPaperId);
      if (history.messages && history.messages.length > 0) {
        // Convert backend format to frontend format
        const formattedMessages = history.messages.map(msg => ({
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp
        }));
        setMessages(formattedMessages);
      }
      setHistoryLoaded(true);
    } catch (error) {
      console.error('Error loading chat history:', error);
      setHistoryLoaded(true);
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || chatLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setChatLoading(true);

    try {
      const response = await chatWithPaper(decodedPaperId, inputMessage, messages);
      const aiMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  const handleBookmark = (categoryId = 'to-read') => {
    if (bookmarked) {
      removeBookmark(paper.id);
      setBookmarked(false);
    } else {
      addBookmark(paper, categoryId);
      setBookmarked(true);
    }
    setShowCategoryMenu(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-primary-600 animate-spin" />
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-4">
        <FileText className="w-16 h-16 text-gray-300 mb-4" />
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Paper Not Found</h2>
        <p className="text-gray-600 mb-6">Unable to load paper details.</p>
        <button
          onClick={() => navigate(-1)}
          className="btn-primary flex items-center space-x-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Go Back</span>
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center space-x-2 text-gray-600 hover:text-primary-600 mb-4 transition-colors duration-200"
          >
            <ArrowLeft className="w-5 h-5" />
            <span className="font-medium">Back to Results</span>
          </button>
          
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">{paper?.title}</h1>
              <div className="flex flex-wrap items-center gap-4 text-gray-600">
                {paper?.authors && (
                  <div className="flex items-center">
                    <Users className="w-4 h-4 mr-2" />
                    <span className="text-sm">{paper.authors.join(', ')}</span>
                  </div>
                )}
                {paper?.published_date && (
                  <div className="flex items-center">
                    <Calendar className="w-4 h-4 mr-2" />
                    <span className="text-sm">{new Date(paper.published_date).toLocaleDateString()}</span>
                  </div>
                )}
                {paper?.citations !== undefined && (
                  <div className="badge bg-primary-100 text-primary-700">
                    {paper.citations} citations
                  </div>
                )}
                <div className="badge bg-blue-100 text-blue-700">
                  {paper?.source}
                </div>
              </div>
            </div>
            <div className="flex space-x-2 relative">
              {/* Bookmark Button */}
              <div className="relative">
                <button
                  onClick={() => bookmarked ? handleBookmark() : setShowCategoryMenu(!showCategoryMenu)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 font-medium ${
                    bookmarked
                      ? 'bg-primary-600 text-white hover:bg-primary-700 shadow-md'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                  }`}
                >
                  {bookmarked ? <BookmarkCheck className="w-4 h-4" /> : <Bookmark className="w-4 h-4" />}
                  <span>{bookmarked ? 'Bookmarked' : 'Bookmark'}</span>
                </button>

                {/* Category Menu */}
                <AnimatePresence>
                  {showCategoryMenu && (
                    <motion.div
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      className="absolute top-full right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50"
                    >
                      <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                        Save to category
                      </div>
                      {categories.map((category) => (
                        <button
                          key={category.id}
                          onClick={() => handleBookmark(category.id)}
                          className="w-full px-4 py-2 text-left hover:bg-gray-50 transition-colors flex items-center space-x-2"
                        >
                          <span>{category.icon}</span>
                          <span className="text-sm font-medium text-gray-700">{category.name}</span>
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {paper?.pdf_url && (
                <a
                  href={paper.pdf_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-medium transition-all duration-200 shadow-md"
                >
                  <Download className="w-4 h-4" />
                  <span>PDF</span>
                </a>
              )}
              {paper?.url && (
                <a
                  href={paper.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary flex items-center space-x-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  <span>View Source</span>
                </a>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Paper Details */}
          <div className="space-y-6">
            {/* Abstract */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card"
            >
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <FileText className="w-5 h-5 mr-2 text-primary-600" />
                Abstract
              </h2>
              <p className="text-gray-700 leading-relaxed">{paper?.abstract}</p>
            </motion.div>

            {/* AI Analysis */}
            {paper?.analysis && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="card bg-gradient-to-br from-primary-50 to-purple-50 border border-primary-100"
              >
                <h2 className="text-xl font-bold mb-4 flex items-center text-primary-900">
                  <Sparkles className="w-5 h-5 mr-2 text-primary-600" />
                  AI Analysis
                </h2>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">Summary</h3>
                    <p className="text-gray-700">{paper.analysis.summary}</p>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">✅ Strengths</h3>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      {paper.analysis.strengths.map((strength, idx) => (
                        <li key={idx}>{strength}</li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">⚠️ Weaknesses</h3>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      {paper.analysis.weaknesses.map((weakness, idx) => (
                        <li key={idx}>{weakness}</li>
                      ))}
                    </ul>
                  </div>

                  {paper.analysis.key_findings && paper.analysis.key_findings.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">🔬 Key Findings</h3>
                      <ul className="list-disc list-inside space-y-1 text-gray-700">
                        {paper.analysis.key_findings.map((finding, idx) => (
                          <li key={idx}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {paper.analysis.methodology && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">🔬 Methodology</h3>
                      <p className="text-gray-700">{paper.analysis.methodology}</p>
                    </div>
                  )}

                  {paper.analysis.key_contributions && paper.analysis.key_contributions.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">🎯 Key Contributions</h3>
                      <ul className="list-disc list-inside space-y-1 text-gray-700">
                        {paper.analysis.key_contributions.map((contribution, idx) => (
                          <li key={idx}>{contribution}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {paper.analysis.main_findings && paper.analysis.main_findings.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">📊 Main Findings</h3>
                      <ul className="list-disc list-inside space-y-1 text-gray-700">
                        {paper.analysis.main_findings.map((finding, idx) => (
                          <li key={idx}>{finding}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {paper.analysis.research_gaps && paper.analysis.research_gaps.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">🔍 Research Gaps</h3>
                      <ul className="list-disc list-inside space-y-1 text-gray-700">
                        {paper.analysis.research_gaps.map((gap, idx) => (
                          <li key={idx}>{gap}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {paper.analysis.future_scope && paper.analysis.future_scope.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">🚀 Future Scope</h3>
                      <ul className="list-disc list-inside space-y-1 text-gray-700">
                        {paper.analysis.future_scope.map((scope, idx) => (
                          <li key={idx}>{scope}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </div>

          {/* Chat Interface */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="lg:sticky lg:top-6 h-fit"
          >
            <div className="card h-[600px] flex flex-col">
              <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-200">
                <h2 className="text-xl font-bold flex items-center">
                  <Bot className="w-6 h-6 mr-2 text-primary-600" />
                  Chat with Paper
                </h2>
                <div className="flex items-center gap-2">
                  {messages.length > 0 && (
                    <button
                      onClick={() => {
                        if (window.confirm('Clear all chat history for this paper?')) {
                          setMessages([]);
                          setHistoryLoaded(false);
                        }
                      }}
                      className="text-sm text-gray-500 hover:text-red-600 transition-colors"
                      title="Clear chat history"
                    >
                      Clear
                    </button>
                  )}
                  <span className="badge bg-green-100 text-green-700">
                    AI Powered
                  </span>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-2">
                {!historyLoaded && messages.length === 0 && (
                  <div className="text-center py-12">
                    <Loader2 className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-2" />
                    <p className="text-gray-500 text-sm">Loading chat history...</p>
                  </div>
                )}
                {historyLoaded && messages.length === 0 && (
                  <div className="text-center py-12">
                    <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-500">Ask me anything about this paper!</p>
                    <div className="mt-4 space-y-2">
                      <button
                        onClick={() => setInputMessage("What are the main contributions?")}
                        className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors"
                      >
                        💡 What are the main contributions?
                      </button>
                      <button
                        onClick={() => setInputMessage("Explain the methodology")}
                        className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors"
                      >
                        🔬 Explain the methodology
                      </button>
                      <button
                        onClick={() => setInputMessage("What are the limitations?")}
                        className="block w-full text-left px-4 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-sm text-gray-700 transition-colors"
                      >
                        ⚠️ What are the limitations?
                      </button>
                    </div>
                  </div>
                )}

                <AnimatePresence>
                  {messages.map((message, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex items-start space-x-2 max-w-[85%] ${message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                          message.role === 'user' 
                            ? 'bg-primary-600' 
                            : 'bg-gradient-to-br from-purple-500 to-pink-500'
                        }`}>
                          {message.role === 'user' ? (
                            <UserIcon className="w-5 h-5 text-white" />
                          ) : (
                            <Bot className="w-5 h-5 text-white" />
                          )}
                        </div>
                        <div className={`px-4 py-3 rounded-2xl ${
                          message.role === 'user'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}>
                          <ReactMarkdown className="text-sm prose prose-sm max-w-none">
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {chatLoading && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-start space-x-2"
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div className="bg-gray-100 px-4 py-3 rounded-2xl">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                    </div>
                  </motion.div>
                )}
                <div ref={chatEndRef} />
              </div>

              {/* Input */}
              <form onSubmit={handleSendMessage} className="flex space-x-2 pt-4 border-t border-gray-200">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask about this paper..."
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                  disabled={chatLoading}
                />
                <button
                  type="submit"
                  disabled={chatLoading || !inputMessage.trim()}
                  className="btn-primary flex items-center space-x-2 px-6"
                >
                  {chatLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </form>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default PaperDetailPage;
