// Local storage-based bookmark service
const BOOKMARKS_KEY = 'research_buddy_bookmarks';
const CATEGORIES_KEY = 'research_buddy_categories';

// Default categories
const DEFAULT_CATEGORIES = [
  { id: 'to-read', name: 'To Read', color: 'blue', icon: '📚' },
  { id: 'reading', name: 'Currently Reading', color: 'yellow', icon: '📖' },
  { id: 'completed', name: 'Completed', color: 'green', icon: '✅' },
  { id: 'favorites', name: 'Favorites', color: 'red', icon: '⭐' },
  { id: 'research', name: 'For Research', color: 'purple', icon: '🔬' }
];

// Get all bookmarks
export const getBookmarks = () => {
  try {
    const bookmarks = localStorage.getItem(BOOKMARKS_KEY);
    return bookmarks ? JSON.parse(bookmarks) : [];
  } catch (error) {
    console.error('Error loading bookmarks:', error);
    return [];
  }
};

// Get all categories
export const getCategories = () => {
  try {
    const categories = localStorage.getItem(CATEGORIES_KEY);
    return categories ? JSON.parse(categories) : DEFAULT_CATEGORIES;
  } catch (error) {
    console.error('Error loading categories:', error);
    return DEFAULT_CATEGORIES;
  }
};

// Add a bookmark
export const addBookmark = (paper, categoryId = 'to-read') => {
  try {
    const bookmarks = getBookmarks();
    const newBookmark = {
      id: paper.id,
      paper: paper,
      categoryId: categoryId,
      addedAt: new Date().toISOString(),
      notes: ''
    };
    
    // Check if already bookmarked
    const existingIndex = bookmarks.findIndex(b => b.id === paper.id);
    if (existingIndex >= 0) {
      // Update category if different
      bookmarks[existingIndex].categoryId = categoryId;
    } else {
      bookmarks.push(newBookmark);
    }
    
    localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
    return true;
  } catch (error) {
    console.error('Error adding bookmark:', error);
    return false;
  }
};

// Remove a bookmark
export const removeBookmark = (paperId) => {
  try {
    const bookmarks = getBookmarks();
    const filtered = bookmarks.filter(b => b.id !== paperId);
    localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('Error removing bookmark:', error);
    return false;
  }
};

// Check if paper is bookmarked
export const isBookmarked = (paperId) => {
  const bookmarks = getBookmarks();
  return bookmarks.some(b => b.id === paperId);
};

// Get bookmark for a specific paper
export const getBookmark = (paperId) => {
  const bookmarks = getBookmarks();
  return bookmarks.find(b => b.id === paperId);
};

// Update bookmark notes
export const updateBookmarkNotes = (paperId, notes) => {
  try {
    const bookmarks = getBookmarks();
    const index = bookmarks.findIndex(b => b.id === paperId);
    if (index >= 0) {
      bookmarks[index].notes = notes;
      localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error updating bookmark notes:', error);
    return false;
  }
};

// Move bookmark to different category
export const moveBookmark = (paperId, newCategoryId) => {
  try {
    const bookmarks = getBookmarks();
    const index = bookmarks.findIndex(b => b.id === paperId);
    if (index >= 0) {
      bookmarks[index].categoryId = newCategoryId;
      localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
      return true;
    }
    return false;
  } catch (error) {
    console.error('Error moving bookmark:', error);
    return false;
  }
};

// Get bookmarks by category
export const getBookmarksByCategory = (categoryId) => {
  const bookmarks = getBookmarks();
  return bookmarks.filter(b => b.categoryId === categoryId);
};

// Add custom category
export const addCategory = (name, color, icon) => {
  try {
    const categories = getCategories();
    const newCategory = {
      id: `custom-${Date.now()}`,
      name,
      color,
      icon,
      isCustom: true
    };
    categories.push(newCategory);
    localStorage.setItem(CATEGORIES_KEY, JSON.stringify(categories));
    return newCategory;
  } catch (error) {
    console.error('Error adding category:', error);
    return null;
  }
};

// Delete custom category (move bookmarks to 'to-read')
export const deleteCategory = (categoryId) => {
  try {
    const categories = getCategories();
    const category = categories.find(c => c.id === categoryId);
    
    // Don't allow deleting default categories
    if (!category || !category.isCustom) {
      return false;
    }
    
    // Move all bookmarks from this category to 'to-read'
    const bookmarks = getBookmarks();
    bookmarks.forEach(b => {
      if (b.categoryId === categoryId) {
        b.categoryId = 'to-read';
      }
    });
    localStorage.setItem(BOOKMARKS_KEY, JSON.stringify(bookmarks));
    
    // Remove category
    const filtered = categories.filter(c => c.id !== categoryId);
    localStorage.setItem(CATEGORIES_KEY, JSON.stringify(filtered));
    return true;
  } catch (error) {
    console.error('Error deleting category:', error);
    return false;
  }
};

export default {
  getBookmarks,
  getCategories,
  addBookmark,
  removeBookmark,
  isBookmarked,
  getBookmark,
  updateBookmarkNotes,
  moveBookmark,
  getBookmarksByCategory,
  addCategory,
  deleteCategory
};
