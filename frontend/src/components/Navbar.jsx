import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Search, Home, Bookmark, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const navLinks = [
    { to: '/', label: 'Home', icon: Home },
    { to: '/bookmarks', label: 'Bookmarks', icon: Bookmark },
  ];

  return (
    <nav className="bg-white shadow-md sticky top-0 z-50 border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 sm:space-x-3 group flex-shrink-0">
            <img 
              src="/RBAI_LOGO.webp" 
              alt="ResearchBuddy AI" 
              className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg group-hover:scale-110 transition-transform duration-200"
            />
            <span className="text-lg sm:text-2xl font-bold bg-gradient-to-r from-primary-600 to-teal-600 bg-clip-text text-transparent">
              ResearchBuddy AI
            </span>
          </Link>
          
          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            {navLinks.map((link) => (
              <Link 
                key={link.to}
                to={link.to} 
                className={`flex items-center space-x-2 transition-colors duration-200 font-medium ${
                  isActive(link.to) 
                    ? 'text-primary-600' 
                    : 'text-gray-700 hover:text-primary-600'
                }`}
              >
                <link.icon className="w-5 h-5" />
                <span>{link.label}</span>
              </Link>
            ))}
            <Link 
              to="/search" 
              className={`flex items-center space-x-2 px-5 py-2 rounded-lg transition-all duration-200 shadow-md hover:shadow-lg font-medium ${
                isActive('/search')
                  ? 'bg-primary-700 text-white'
                  : 'bg-primary-600 hover:bg-primary-700 text-white'
              }`}
            >
              <Search className="w-5 h-5" />
              <span>Search Papers</span>
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden bg-white border-t border-gray-100 overflow-hidden"
          >
            <div className="px-4 py-3 space-y-2">
              {navLinks.map((link) => (
                <Link 
                  key={link.to}
                  to={link.to} 
                  onClick={() => setIsOpen(false)}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200 font-medium ${
                    isActive(link.to) 
                      ? 'bg-primary-50 text-primary-600' 
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <link.icon className="w-5 h-5" />
                  <span>{link.label}</span>
                </Link>
              ))}
              <Link 
                to="/search" 
                onClick={() => setIsOpen(false)}
                className="flex items-center justify-center space-x-2 bg-primary-600 hover:bg-primary-700 text-white px-5 py-3 rounded-lg transition-all duration-200 shadow-md font-medium w-full"
              >
                <Search className="w-5 h-5" />
                <span>Search Papers</span>
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
