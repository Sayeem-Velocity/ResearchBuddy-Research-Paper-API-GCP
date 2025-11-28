import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import ResultsPage from './pages/ResultsPage';
import PaperDetailPage from './pages/PaperDetailPage';
import BookmarksPage from './pages/BookmarksPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <Navbar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/search" element={<SearchPage />} />
          <Route path="/results/:sessionId" element={<ResultsPage />} />
          <Route path="/paper/:paperId" element={<PaperDetailPage />} />
          <Route path="/bookmarks" element={<BookmarksPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
