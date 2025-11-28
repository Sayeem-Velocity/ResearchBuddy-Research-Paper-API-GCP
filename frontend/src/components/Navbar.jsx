import { Link } from 'react-router-dom';
import { BookOpen, Search, Home, Bookmark } from 'lucide-react';

const Navbar = () => {
  return (
    <nav className="bg-white shadow-md sticky top-0 z-50 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link to="/" className="flex items-center space-x-3 group">
            <div className="bg-gradient-to-r from-primary-500 to-purple-600 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
              <BookOpen className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-purple-600 bg-clip-text text-transparent">
              ResearchBuddy
            </span>
          </Link>
          
          <div className="flex items-center space-x-6">
            <Link 
              to="/" 
              className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors duration-200 font-medium"
            >
              <Home className="w-5 h-5" />
              <span>Home</span>
            </Link>
            <Link 
              to="/bookmarks" 
              className="flex items-center space-x-2 text-gray-700 hover:text-primary-600 transition-colors duration-200 font-medium"
            >
              <Bookmark className="w-5 h-5" />
              <span>Bookmarks</span>
            </Link>
            <Link 
              to="/search" 
              className="flex items-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white px-5 py-2 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg font-medium"
            >
              <Search className="w-5 h-5" />
              <span>Search Papers</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
