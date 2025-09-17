# API Endpoints Quick Reference 📚

## 🚀 Server Information
- **Base URL**: `http://localhost:8004`
- **Status**: ✅ Production Ready
- **Interactive Docs**: `http://localhost:8004/docs`
- **Model**: Gemini 2.0 Flash Experimental

## 🎯 Core AI-Powered Endpoints

### 1. **Paper Analysis with AI** ⭐ (Main Feature)
```
POST /analyze/papers-with-ai
```
**Purpose**: Search papers + AI analysis in one call
**Response Time**: 15-30 seconds
**Best For**: Primary search functionality

```json
// Request
{
  "query": "machine learning",
  "max_papers": 5,
  "sources": ["arxiv", "pubmed"]
}

// Response
{
  "papers_found": 5,
  "analyses_generated": 5,
  "results": [
    {
      "paper": { /* paper metadata */ },
      "analysis": {
        "summary": "AI-generated summary",
        "key_contributions": ["..."],
        "strengths": ["..."],
        "weaknesses": ["..."],
        "research_gaps": ["..."],
        "future_scope": ["..."],
        "methodology": "...",
        "main_findings": ["..."]
      }
    }
  ]
}
```

### 2. **Research Gaps Analysis** 🔍
```
POST /analyze/research-gaps
```
**Purpose**: Identify research opportunities across papers
**Response Time**: 20-40 seconds
**Best For**: Advanced research insights

```json
// Request
{
  "query": "deep learning",
  "research_domain": "artificial intelligence",
  "max_papers": 8,
  "sources": ["arxiv", "pubmed"]
}

// Response
{
  "research_gaps": {
    "current_trends": ["..."],
    "research_gaps": [
      {
        "gap": "...",
        "description": "...",
        "importance": "high|medium|low"
      }
    ],
    "future_opportunities": [
      {
        "opportunity": "...",
        "description": "...",
        "feasibility": "high|medium|low"
      }
    ],
    "recommendations": ["..."]
  }
}
```

### 3. **Research Scope Planning** 📋
```
POST /analyze/research-scope
```
**Purpose**: Generate detailed research plans
**Response Time**: 30-60 seconds
**Best For**: Project planning and proposals

```json
// Request
{
  "query": "neural networks",
  "research_question": "How to improve AI interpretability?",
  "timeline_months": 18,
  "max_papers": 6,
  "sources": ["arxiv"]
}

// Response
{
  "research_scope": {
    "research_objectives": [{"objective": "...", "priority": "high"}],
    "methodology": {
      "approach": "...",
      "data_collection": ["..."],
      "analysis_methods": ["..."]
    },
    "phases": [
      {
        "phase": "Phase 1: Literature Review",
        "duration_months": 3,
        "activities": ["..."],
        "deliverables": ["..."]
      }
    ],
    "resources_needed": {
      "personnel": ["..."],
      "estimated_budget": "$150,000 - $200,000"
    }
  }
}
```

### 4. **PDF Report Generation** 📄
```
POST /generate/comprehensive-report
```
**Purpose**: Export comprehensive PDF reports
**Response Time**: 10-20 seconds
**Returns**: PDF file download

```json
// Request
{
  "query": "quantum computing",
  "research_domain": "computer science",
  "research_question": "What are quantum computing applications?",
  "timeline_months": 12,
  "max_papers": 5,
  "sources": ["arxiv"],
  "report_title": "Quantum Computing Research Analysis"
}
```

## 📊 Basic Search Endpoints

### Search Papers (Without AI)
```
POST /search
```
**Purpose**: Basic paper search without AI analysis
**Response Time**: 2-5 seconds

### Session Management
```
GET /search/status/{session_id}     # Check search status
GET /search/results/{session_id}    # Get search results
GET /sessions                       # List user sessions
DELETE /sessions/{session_id}       # Delete session
```

## 🎨 Frontend Integration Examples

### React Hook for Paper Analysis
```jsx
import { useState, useCallback } from 'react';

const usePaperAnalysis = () => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzePapers = useCallback(async (query, maxPapers = 5) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8004/analyze/papers-with-ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          max_papers: maxPapers,
          sources: ['arxiv', 'pubmed']
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  return { results, loading, error, analyzePapers };
};
```

### Vue.js Composition API
```javascript
import { ref, reactive } from 'vue';

export function usePaperAnalysis() {
  const results = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const analyzePapers = async (query, maxPapers = 5) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch('http://localhost:8004/analyze/papers-with-ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          max_papers: maxPapers,
          sources: ['arxiv', 'pubmed']
        })
      });

      const data = await response.json();
      results.value = data;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  return { results, loading, error, analyzePapers };
}
```

### JavaScript/TypeScript Types
```typescript
interface Paper {
  id: string;
  title: string;
  authors: string[];
  abstract: string;
  published: string;
  source: 'arxiv' | 'pubmed' | 'google_scholar';
  venue?: string;
  citation_count?: number;
}

interface PaperAnalysis {
  summary: string;
  key_contributions: string[];
  strengths: string[];
  weaknesses: string[];
  research_gaps: string[];
  future_scope: string[];
  methodology: string;
  main_findings: string[];
  generated_at: string;
}

interface AnalysisResult {
  paper: Paper;
  analysis: PaperAnalysis;
}

interface PaperAnalysisResponse {
  query: string;
  papers_found: number;
  analyses_generated: number;
  results: AnalysisResult[];
}
```

## ⚡ Performance Guidelines

### Recommended Settings
```javascript
const OPTIMAL_SETTINGS = {
  // For quick demos
  demo: {
    max_papers: 2,
    sources: ['arxiv']
  },

  // For research work
  research: {
    max_papers: 5,
    sources: ['arxiv', 'pubmed']
  },

  // For comprehensive analysis
  comprehensive: {
    max_papers: 8,
    sources: ['arxiv', 'pubmed'] // Avoid google_scholar due to rate limits
  }
};
```

### Error Handling
```javascript
const handleAPIError = (response, error) => {
  switch (response?.status) {
    case 429:
      return "Rate limit exceeded. Please wait before trying again.";
    case 500:
      return "Server error. Please try again later.";
    case 404:
      return "Endpoint not found. Check API URL.";
    default:
      return error?.message || "An unexpected error occurred.";
  }
};
```

## 🎯 UI/UX Recommendations

### Loading States
- **Paper Analysis**: "Searching and analyzing papers..." (15-30s)
- **Research Gaps**: "Identifying research opportunities..." (20-40s)
- **Research Scope**: "Generating research plan..." (30-60s)
- **PDF Generation**: "Creating report..." (10-20s)

### Data Display
- **Paper Cards**: Title, authors, source, publication date
- **Analysis Sections**: Collapsible/expandable for mobile
- **Progress Indicators**: Show analysis completion
- **Export Buttons**: Prominent PDF download options

### Mobile Optimization
- **Touch Targets**: 44px minimum button height
- **Scrollable Cards**: Horizontal scroll for paper results
- **Collapsed Details**: Tap to expand analysis sections
- **Offline Indicators**: Show when API is unreachable

## 🚨 Important Notes

### Rate Limits
- **Google Scholar**: 1 search per user per day ⚠️
- **arXiv**: Unlimited ✅
- **PubMed**: Unlimited ✅
- **Vertex AI**: Based on your Google Cloud quotas

### Best Practices
1. **Start with arXiv/PubMed** to avoid rate limits
2. **Cache results** to improve user experience
3. **Show progress** during long operations
4. **Handle errors gracefully** with user-friendly messages
5. **Debounce search inputs** to reduce API calls

### Production Checklist
- [ ] Update API base URL for production
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Set up analytics for API usage
- [ ] Implement proper loading states
- [ ] Add offline detection
- [ ] Set up caching strategy

## 📞 Support

### Quick Tests
```bash
# Test if API is running
curl http://localhost:8004/docs

# Quick paper analysis test
curl -X POST "http://localhost:8004/analyze/papers-with-ai" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_papers": 1, "sources": ["arxiv"]}'
```

### Common Issues
1. **CORS Errors**: Ensure API runs on port 8004
2. **Slow Responses**: Normal for AI analysis (15-30s)
3. **Empty Results**: Try broader search terms
4. **Rate Limits**: Use arXiv/PubMed, avoid Google Scholar

Your AI-powered Research Paper API is **ready for frontend integration**! 🚀

The API provides:
✅ **Real AI Analysis** with Gemini 2.0
✅ **Multi-source Search** (arXiv, PubMed, Google Scholar)
✅ **Research Insights** (gaps, opportunities, planning)
✅ **PDF Reports** for export
✅ **Production-ready** with proper error handling