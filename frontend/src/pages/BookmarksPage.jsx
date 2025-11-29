import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bookmark, Trash2, MessageSquare, ExternalLink, Calendar, FileText, Plus, Edit2, X, ChevronDown, Filter, Download, Tag, BookOpen, Star, Heart, Flag, Folder, Archive, Lightbulb, Target, Microscope } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  getBookmarks,
  getCategories,
  removeBookmark,
  moveBookmark,
  updateBookmarkNotes,
  addCategory,
  deleteCategory
} from '../services/bookmarkService';

// Professional icon options for categories
const categoryIconOptions = [
  { id: 'tag', icon: Tag, name: 'Tag' },
  { id: 'bookmark', icon: Bookmark, name: 'Bookmark' },
  { id: 'book', icon: BookOpen, name: 'Book' },
  { id: 'star', icon: Star, name: 'Star' },
  { id: 'heart', icon: Heart, name: 'Heart' },
  { id: 'flag', icon: Flag, name: 'Flag' },
  { id: 'folder', icon: Folder, name: 'Folder' },
  { id: 'archive', icon: Archive, name: 'Archive' },
  { id: 'lightbulb', icon: Lightbulb, name: 'Idea' },
  { id: 'target', icon: Target, name: 'Target' },
  { id: 'microscope', icon: Microscope, name: 'Research' },
];

const BookmarksPage = () => {
  const navigate = useNavigate();
  const [bookmarks, setBookmarks] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [showCategoryModal, setShowCategoryModal] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryColor, setNewCategoryColor] = useState('blue');
  const [newCategoryIcon, setNewCategoryIcon] = useState('tag');
  const [editingNotes, setEditingNotes] = useState(null);
  const [notesText, setNotesText] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    setBookmarks(getBookmarks());
    setCategories(getCategories());
  };

  const handleRemoveBookmark = (paperId) => {
    if (window.confirm('Remove this bookmark?')) {
      removeBookmark(paperId);
      loadData();
    }
  };

  const handleMoveBookmark = (paperId, newCategoryId) => {
    moveBookmark(paperId, newCategoryId);
    loadData();
  };

  const handleSaveNotes = (paperId) => {
    updateBookmarkNotes(paperId, notesText);
    setEditingNotes(null);
    loadData();
  };

  const handleAddCategory = () => {
    if (newCategoryName.trim()) {
      addCategory(newCategoryName, newCategoryColor, newCategoryIcon);
      setShowCategoryModal(false);
      setNewCategoryName('');
      loadData();
    }
  };

  const handleDeleteCategory = (categoryId) => {
    if (window.confirm('Delete this category? All bookmarks will be moved to "To Read".')) {
      deleteCategory(categoryId);
      if (selectedCategory === categoryId) {
        setSelectedCategory('all');
      }
      loadData();
    }
  };

  const filteredBookmarks = selectedCategory === 'all' 
    ? bookmarks 
    : bookmarks.filter(b => b.categoryId === selectedCategory);

  const getSourceBadgeColor = (source) => {
    const colors = {
      arxiv: 'bg-blue-100 text-blue-700',
      pubmed: 'bg-green-100 text-green-700',
      google_scholar: 'bg-purple-100 text-purple-700',
      ieee: 'bg-yellow-100 text-yellow-700',
    };
    return colors[source] || 'bg-gray-100 text-gray-700';
  };

  const getCategoryColor = (color) => {
    const colors = {
      blue: 'bg-blue-500',
      yellow: 'bg-yellow-500',
      green: 'bg-green-500',
      red: 'bg-red-500',
      purple: 'bg-purple-500',
      pink: 'bg-pink-500',
      indigo: 'bg-indigo-500',
      orange: 'bg-orange-500'
    };
    return colors[color] || 'bg-gray-500';
  };

  // Render category icon (supports both new icon IDs and legacy emojis)
  const renderCategoryIcon = (iconId, className = "w-4 h-4") => {
    const iconOption = categoryIconOptions.find(opt => opt.id === iconId);
    if (iconOption) {
      const IconComponent = iconOption.icon;
      return <IconComponent className={className} />;
    }
    // Fallback for legacy emoji icons - show Tag icon
    return <Tag className={className} />;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                My Bookmarks
              </h1>
              <p className="text-gray-600">
                Organize and manage your saved research papers
              </p>
            </div>
            <button
              onClick={() => setShowCategoryModal(true)}
              className="btn-primary flex items-center gap-2"
            >
              <Plus className="w-5 h-5" />
              New Category
            </button>
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-3 overflow-x-auto pb-4">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
                selectedCategory === 'all'
                  ? 'bg-primary-600 text-white shadow-lg'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              All ({bookmarks.length})
            </button>
            {categories.map((category) => {
              const count = bookmarks.filter(b => b.categoryId === category.id).length;
              return (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
                    selectedCategory === category.id
                      ? 'bg-primary-600 text-white shadow-lg'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                  }`}
                >
                  {renderCategoryIcon(category.icon)}
                  <span>{category.name}</span>
                  <span className="text-sm opacity-75">({count})</span>
                  {category.isCustom && selectedCategory === category.id && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteCategory(category.id);
                      }}
                      className="ml-1 hover:text-red-300"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* Bookmarks Grid */}
        {filteredBookmarks.length === 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-16"
          >
            <Bookmark className="w-24 h-24 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-700 mb-2">No bookmarks yet</h3>
            <p className="text-gray-500 mb-6">Start saving papers to access them easily later</p>
            <Link to="/search" className="btn-primary">
              Search Papers
            </Link>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            <AnimatePresence mode="popLayout">
              {filteredBookmarks.map((bookmark) => {
                const category = categories.find(c => c.id === bookmark.categoryId);
                return (
                  <motion.div
                    key={bookmark.id}
                    layout
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all border border-gray-100 overflow-hidden"
                  >
                    <div className="p-6">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          {/* Title */}
                          <h3 className="text-xl font-semibold text-gray-900 mb-3 hover:text-primary-600 transition-colors">
                            <Link
                              to={`/paper/${encodeURIComponent(bookmark.paper.id)}`}
                              state={{ paper: bookmark.paper }}
                            >
                              {bookmark.paper.title}
                            </Link>
                          </h3>

                          {/* Metadata */}
                          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-4">
                            {bookmark.paper.authors && bookmark.paper.authors.length > 0 && (
                              <div className="flex items-center gap-1">
                                <FileText className="w-4 h-4" />
                                <span>{bookmark.paper.authors[0]}</span>
                                {bookmark.paper.authors.length > 1 && (
                                  <span className="text-gray-400">+{bookmark.paper.authors.length - 1}</span>
                                )}
                              </div>
                            )}
                            {bookmark.paper.published_date && (
                              <div className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                <span>{new Date(bookmark.paper.published_date).getFullYear()}</span>
                              </div>
                            )}
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSourceBadgeColor(bookmark.paper.source)}`}>
                              {bookmark.paper.source}
                            </span>
                          </div>

                          {/* Abstract Preview */}
                          {bookmark.paper.abstract && (
                            <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                              {bookmark.paper.abstract}
                            </p>
                          )}

                          {/* Notes */}
                          {editingNotes === bookmark.id ? (
                            <div className="mb-4">
                              <textarea
                                value={notesText}
                                onChange={(e) => setNotesText(e.target.value)}
                                placeholder="Add your notes..."
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                                rows="3"
                              />
                              <div className="flex gap-2 mt-2">
                                <button
                                  onClick={() => handleSaveNotes(bookmark.id)}
                                  className="btn-primary text-sm"
                                >
                                  Save
                                </button>
                                <button
                                  onClick={() => setEditingNotes(null)}
                                  className="btn-secondary text-sm"
                                >
                                  Cancel
                                </button>
                              </div>
                            </div>
                          ) : bookmark.notes ? (
                            <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                              <p className="text-sm text-gray-700">{bookmark.notes}</p>
                            </div>
                          ) : null}

                          {/* Category Selector */}
                          <div className="flex items-center gap-2 mb-4">
                            <span className="text-sm text-gray-600">Category:</span>
                            <select
                              value={bookmark.categoryId}
                              onChange={(e) => handleMoveBookmark(bookmark.id, e.target.value)}
                              className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            >
                              {categories.map((cat) => (
                                <option key={cat.id} value={cat.id}>
                                  {cat.icon} {cat.name}
                                </option>
                              ))}
                            </select>
                          </div>

                          {/* Actions */}
                          <div className="flex items-center gap-3">
                            <Link
                              to={`/paper/${encodeURIComponent(bookmark.paper.id)}`}
                              state={{ paper: bookmark.paper }}
                              className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
                            >
                              <MessageSquare className="w-4 h-4" />
                              Continue Chat
                            </Link>
                            {bookmark.paper.pdf_url && (
                              <a
                                href={bookmark.paper.pdf_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-primary-600 hover:text-primary-700 font-medium flex items-center gap-1"
                              >
                                <Download className="w-4 h-4" />
                                PDF
                              </a>
                            )}
                            {bookmark.paper.url && (
                              <a
                                href={bookmark.paper.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
                              >
                                <ExternalLink className="w-4 h-4" />
                                View Source
                              </a>
                            )}
                            <button
                              onClick={() => {
                                setEditingNotes(bookmark.id);
                                setNotesText(bookmark.notes || '');
                              }}
                              className="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-1"
                            >
                              <Edit2 className="w-4 h-4" />
                              {bookmark.notes ? 'Edit Notes' : 'Add Notes'}
                            </button>
                            <button
                              onClick={() => handleRemoveBookmark(bookmark.id)}
                              className="text-sm text-red-600 hover:text-red-700 flex items-center gap-1 ml-auto"
                            >
                              <Trash2 className="w-4 h-4" />
                              Remove
                            </button>
                          </div>
                        </div>

                        {/* Category Badge */}
                        {category && (
                          <div className={`${getCategoryColor(category.color)} text-white px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2 whitespace-nowrap`}>
                            <span>{category.icon}</span>
                            <span>{category.name}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </div>
        )}

        {/* Add Category Modal */}
        <AnimatePresence>
          {showCategoryModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
              onClick={() => setShowCategoryModal(false)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                onClick={(e) => e.stopPropagation()}
                className="bg-white rounded-xl shadow-xl p-6 max-w-md w-full"
              >
                <h3 className="text-2xl font-bold mb-4">Create New Category</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category Name
                    </label>
                    <input
                      type="text"
                      value={newCategoryName}
                      onChange={(e) => setNewCategoryName(e.target.value)}
                      placeholder="e.g., Machine Learning"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Color
                    </label>
                    <div className="flex gap-2">
                      {['blue', 'green', 'red', 'yellow', 'purple', 'pink', 'indigo', 'orange'].map((color) => (
                        <button
                          key={color}
                          onClick={() => setNewCategoryColor(color)}
                          className={`w-10 h-10 rounded-full ${getCategoryColor(color)} ${
                            newCategoryColor === color ? 'ring-4 ring-gray-300' : ''
                          }`}
                        />
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Icon
                    </label>
                    <div className="grid grid-cols-6 gap-2">
                      {categoryIconOptions.map((option) => {
                        const IconComponent = option.icon;
                        return (
                          <button
                            key={option.id}
                            type="button"
                            onClick={() => setNewCategoryIcon(option.id)}
                            className={`p-3 rounded-lg border-2 transition-all flex items-center justify-center ${
                              newCategoryIcon === option.id
                                ? 'border-primary-500 bg-primary-50'
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                            title={option.name}
                          >
                            <IconComponent className={`w-5 h-5 ${
                              newCategoryIcon === option.id ? 'text-primary-600' : 'text-gray-600'
                            }`} />
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>

                <div className="flex gap-3 mt-6">
                  <button
                    onClick={handleAddCategory}
                    className="btn-primary flex-1"
                  >
                    Create Category
                  </button>
                  <button
                    onClick={() => setShowCategoryModal(false)}
                    className="btn-secondary flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default BookmarksPage;
