# ResearchBuddy Frontend

A modern, beautiful React frontend for the ResearchBuddy Research Paper API.

## 🎨 Features

- **Modern UI/UX**: Built with React, TailwindCSS, and Framer Motion for smooth animations
- **Multi-Source Search**: Search across arXiv, PubMed, Google Scholar, and IEEE Xplore
- **AI-Powered Analysis**: View comprehensive paper analysis with strengths, weaknesses, and key findings
- **Interactive Chat**: Ask questions about papers and get AI-powered responses
- **Responsive Design**: Works beautifully on desktop, tablet, and mobile
- **Real-time Updates**: Live search status updates and results

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- ResearchBuddy API running on http://127.0.0.1:8004

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview
```

## 📦 Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **React Markdown** - Markdown rendering

## 🎯 Pages

- **Home** (`/`) - Landing page with features and call-to-action
- **Search** (`/search`) - Search interface with source selection
- **Results** (`/results/:sessionId`) - Display search results
- **Paper Detail** (`/paper/:paperId`) - View paper details and chat interface

## 🔧 Configuration

The API base URL is configured in `src/services/api.js`. Update if your backend runs on a different port:

```javascript
const API_BASE_URL = 'http://127.0.0.1:8004/api/v1';
```

## 🎨 Customization

### Colors

Edit `tailwind.config.js` to customize the color scheme:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      }
    }
  }
}
```

### Fonts

The app uses Inter font. Change it in `index.html` and `src/index.css`.

## 📱 Screenshots

The frontend includes:
- ✨ Smooth animations and transitions
- 🎨 Gradient backgrounds and modern design
- 📊 Real-time search status updates
- 💬 Interactive chat interface
- 📱 Fully responsive layout
- 🌙 Clean, professional aesthetic

## 🔗 API Integration

The frontend connects to the ResearchBuddy API endpoints:

- `POST /api/v1/papers/search` - Start a search
- `GET /api/v1/papers/search/:sessionId/status` - Get search status
- `GET /api/v1/papers/search/:sessionId/results` - Get results
- `POST /api/v1/papers/:paperId/chat` - Chat with paper
- `GET /api/v1/papers/:paperId/chat/history` - Get chat history

## 🤝 Contributing

Feel free to customize and enhance the frontend!

## 📄 License

MIT
