# ResearchBuddy - AI-Powered Research Paper Search & Analysis 🔬

A full-stack web application for searching academic papers across multiple databases (arXiv, PubMed, Google Scholar) with AI-powered chat capabilities powered by Google's Gemini AI.

## ✨ Features

- **Multi-Source Paper Search**: Search across arXiv, PubMed, and Google Scholar simultaneously
- **AI Chat Integration**: Ask questions about papers and get intelligent responses using Gemini AI
- **Bookmark System**: Save and organize papers with categories and notes
- **Modern React UI**: Clean, responsive interface with smooth animations
- **Real-time Results**: Fast parallel search across multiple academic databases

## 🏗️ Tech Stack

**Backend:**
- FastAPI (Python web framework)
- Google Vertex AI (Gemini 2.0 for AI chat)
- Firebase/Firestore (optional - currently using local storage)
- Multiple academic APIs (arXiv, PubMed, Google Scholar)

**Frontend:**
- React 18 with Vite
- TailwindCSS for styling
- Framer Motion for animations
- Lucide React for icons
- LocalStorage for bookmarks

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Google Cloud account (for Gemini AI)
- Git

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ResearchBuddy-Research-Paper-API.git
cd ResearchBuddy-Research-Paper-API
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Google Cloud (for Gemini AI)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Optional: Google Scholar (for enhanced results)
SERP_API_KEY=your_serpapi_key_here

# Optional: IEEE Xplore
IEEE_API_KEY=your_ieee_key_here
```

**Getting Google Cloud Credentials:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Vertex AI API
4. Create service account and download JSON key
5. Place JSON file in project root
6. Update `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`

### 4. Frontend Setup

```bash
cd frontend
npm install
```

### 5. Start the Application

**Terminal 1 - Backend:**
```bash
# From project root
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8004
```

**Terminal 2 - Frontend:**
```bash
# From frontend directory
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8004
- API Documentation: http://127.0.0.1:8004/docs

## 📁 Project Structure

```
ResearchBuddy-Research-Paper-API/
├── app/                          # Backend application
│   ├── api/                      # API endpoints
│   │   └── v1/
│   │       └── endpoints/        # Search, chat endpoints
│   ├── core/                     # Configuration & dependencies
│   ├── models/                   # Data models (Paper, Chat, etc.)
│   └── services/                 # Business logic
│       ├── llm/                  # AI integration (Vertex AI)
│       ├── paper_search/         # Academic database searches
│       └── storage/              # Data persistence
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/                # Main pages (Search, Results, etc.)
│   │   └── services/             # API calls & bookmark service
│   └── public/
├── .mock_firestore_data/         # Local data storage (gitignored)
├── venv/                         # Python virtual environment
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Template for .env
├── requirements.txt              # Python dependencies
└── README.md
```

## 🔧 Usage

### Searching Papers

1. Enter your search query in the search box
2. Select sources (arXiv, PubMed, Google Scholar)
3. Click "Search Papers"
4. View results with paper metadata

### AI Chat

1. Click on any paper to open detail view
2. Type your question in the chat input
3. AI will respond based on paper content
4. Conversation history is maintained per paper

### Bookmarks

1. Click bookmark icon on any paper
2. Choose a category (To Read, Currently Reading, etc.)
3. Access bookmarks from navigation menu
4. Add notes, move between categories, or remove bookmarks

## 🔑 API Endpoints

### Search
- `POST /api/v1/search` - Start new paper search
- `GET /api/v1/search/{session_id}/status` - Check search status
- `GET /api/v1/search/{session_id}/results` - Get search results

### Chat
- `POST /api/v1/chat` - Chat with AI about a paper
- `GET /api/v1/chat/{session_id}/history` - Get chat history

## 🛠️ Configuration

### Mock vs Real Services

By default, the app uses **mock services** for development:
- Mock Firestore (local JSON files)
- Mock Vertex AI (scripted responses)

To use real services, update `app/main.py`:
```python
# Change from:
from app.core.mock_dependencies import get_firestore_manager, get_llm_service

# To:
from app.core.dependencies import get_firestore_manager, get_llm_service
```

### Customizing Search Sources

Edit `app/services/paper_search/aggregator.py` to enable/disable sources or adjust result limits.

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure virtual environment is activated
- Check Python version: `python --version` (3.8+)
- Verify all dependencies: `pip install -r requirements.txt`

**Frontend won't load:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (16+)
- Verify backend is running on port 8004

**API errors:**
- Check `.env` file exists and contains valid credentials
- Verify Google Cloud credentials are correct
- Check API quotas in Google Cloud Console

**No search results:**
- Check internet connection
- Verify API keys are valid
- Check terminal for error messages

## 📦 Data Storage

**Local Development:**
- Chat history: `.mock_firestore_data/`
- Bookmarks: Browser LocalStorage
- Search sessions: Temporary in-memory

**Production Ready:**
- Replace mock services with real Firestore
- Implement user authentication
- Add proper database persistence

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- arXiv for open access preprints
- PubMed/NCBI for biomedical literature
- Google Scholar for comprehensive academic search
- Google Cloud for Gemini AI
- FastAPI and React communities

## 📧 Contact

For questions or support, please open an issue on GitHub.

---
