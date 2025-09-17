# Frontend Integration Guide 🎨

## Quick Start for Frontend Developers

### 📡 API Base URL
```
http://localhost:8004
```

### 🚨 Important Notes
- **CORS is configured** for frontend integration
- **Server runs on port 8004** (different from other services)
- **All responses are JSON** except PDF endpoints
- **Rate limiting**: Google Scholar limited to 1 search per user per day

## 🎯 Main Endpoints You'll Use

### 1. 🔍 **Paper Analysis with AI** (Primary Feature)
**Endpoint:** `POST /analyze/papers-with-ai`

**What it does:** Searches papers and provides comprehensive AI analysis

```javascript
const analyzePapers = async (query, maxPapers = 5) => {
  const response = await fetch('http://localhost:8004/analyze/papers-with-ai', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      max_papers: maxPapers,
      sources: ['arxiv', 'pubmed'] // Avoid google_scholar for now due to rate limits
    })
  });

  return await response.json();
};

// Usage
const results = await analyzePapers('machine learning', 3);
console.log(results.results[0].analysis.summary);
```

**Response Structure:**
```javascript
{
  query: "machine learning",
  papers_found: 3,
  analyses_generated: 3,
  results: [
    {
      paper: {
        id: "http://arxiv.org/abs/...",
        title: "Paper Title",
        authors: ["Author 1", "Author 2"],
        abstract: "Paper abstract...",
        published: "2022-08-01T10:36:13+00:00",
        source: "arxiv",
        venue: "Journal Name",
        citation_count: 25
      },
      analysis: {
        summary: "AI-generated summary...",
        key_contributions: ["Contribution 1", "Contribution 2"],
        strengths: ["Strength 1", "Strength 2"],
        weaknesses: ["Weakness 1", "Weakness 2"],
        research_gaps: ["Gap 1", "Gap 2"],
        future_scope: ["Future direction 1"],
        methodology: "Research methodology description",
        main_findings: ["Finding 1", "Finding 2"],
        generated_at: "2025-09-17T00:40:51.942170"
      }
    }
  ]
}
```

### 2. 🎯 **Research Gaps Analysis** (Advanced Feature)
**Endpoint:** `POST /analyze/research-gaps`

**What it does:** Identifies research gaps across multiple papers

```javascript
const analyzeResearchGaps = async (query, domain) => {
  const response = await fetch('http://localhost:8004/analyze/research-gaps', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      research_domain: domain,
      max_papers: 8,
      sources: ['arxiv', 'pubmed']
    })
  });

  return await response.json();
};

// Usage
const gaps = await analyzeResearchGaps('deep learning', 'artificial intelligence');
console.log(gaps.research_gaps.current_trends);
```

### 3. 📋 **Research Scope Planning** (Project Planning)
**Endpoint:** `POST /analyze/research-scope`

**What it does:** Creates detailed research plans based on papers

```javascript
const generateResearchScope = async (query, researchQuestion, timelineMonths) => {
  const response = await fetch('http://localhost:8004/analyze/research-scope', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      research_question: researchQuestion,
      timeline_months: timelineMonths,
      max_papers: 6,
      sources: ['arxiv']
    })
  });

  return await response.json();
};

// Usage
const scope = await generateResearchScope(
  'neural networks',
  'How can we improve interpretability in medical AI?',
  18
);
```

### 4. 📄 **PDF Report Generation** (Export Feature)
**Endpoint:** `POST /generate/comprehensive-report`

**What it does:** Generates downloadable PDF reports

```javascript
const generatePDFReport = async (query, domain, researchQuestion) => {
  const response = await fetch('http://localhost:8004/generate/comprehensive-report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      research_domain: domain,
      research_question: researchQuestion,
      timeline_months: 12,
      max_papers: 5,
      sources: ['arxiv'],
      report_title: `Research Analysis: ${query}`
    })
  });

  // Handle PDF download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `research-report-${Date.now()}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
```

## ⚡ React Components Examples

### 1. Paper Search Component
```jsx
import React, { useState } from 'react';

const PaperSearch = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const searchPapers = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8004/analyze/papers-with-ai', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          max_papers: 5,
          sources: ['arxiv', 'pubmed']
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="paper-search">
      <div className="search-form">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter research query (e.g., 'machine learning')"
          onKeyPress={(e) => e.key === 'Enter' && searchPapers()}
        />
        <button onClick={searchPapers} disabled={loading}>
          {loading ? 'Analyzing...' : 'Search & Analyze'}
        </button>
      </div>

      {error && (
        <div className="error">
          Error: {error}
        </div>
      )}

      {results && (
        <div className="results">
          <h3>Found {results.papers_found} papers with AI analysis</h3>

          {results.results.map((result, index) => (
            <div key={index} className="paper-result">
              <h4>{result.paper.title}</h4>
              <p><strong>Authors:</strong> {result.paper.authors.join(', ')}</p>
              <p><strong>Source:</strong> {result.paper.source}</p>
              <p><strong>Published:</strong> {new Date(result.paper.published).toLocaleDateString()}</p>

              <div className="ai-analysis">
                <h5>AI Analysis:</h5>
                <p><strong>Summary:</strong> {result.analysis.summary}</p>

                {result.analysis.key_contributions.length > 0 && (
                  <div>
                    <strong>Key Contributions:</strong>
                    <ul>
                      {result.analysis.key_contributions.map((contrib, i) => (
                        <li key={i}>{contrib}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {result.analysis.research_gaps.length > 0 && (
                  <div>
                    <strong>Research Gaps:</strong>
                    <ul>
                      {result.analysis.research_gaps.map((gap, i) => (
                        <li key={i}>{gap}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PaperSearch;
```

### 2. Research Gaps Component
```jsx
import React, { useState } from 'react';

const ResearchGaps = () => {
  const [formData, setFormData] = useState({
    query: '',
    domain: ''
  });
  const [gaps, setGaps] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzeGaps = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8004/analyze/research-gaps', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: formData.query,
          research_domain: formData.domain,
          max_papers: 8,
          sources: ['arxiv', 'pubmed']
        })
      });

      const data = await response.json();
      setGaps(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="research-gaps">
      <div className="form">
        <input
          type="text"
          placeholder="Research query"
          value={formData.query}
          onChange={(e) => setFormData({...formData, query: e.target.value})}
        />
        <input
          type="text"
          placeholder="Research domain"
          value={formData.domain}
          onChange={(e) => setFormData({...formData, domain: e.target.value})}
        />
        <button onClick={analyzeGaps} disabled={loading}>
          {loading ? 'Analyzing Gaps...' : 'Analyze Research Gaps'}
        </button>
      </div>

      {gaps && (
        <div className="gaps-results">
          <h3>Research Gaps in {gaps.research_gaps.domain}</h3>

          <section>
            <h4>Current Trends:</h4>
            <ul>
              {gaps.research_gaps.current_trends.map((trend, i) => (
                <li key={i}>{trend}</li>
              ))}
            </ul>
          </section>

          <section>
            <h4>Identified Gaps:</h4>
            {gaps.research_gaps.research_gaps.map((gap, i) => (
              <div key={i} className={`gap-item priority-${gap.importance}`}>
                <h5>{gap.gap}</h5>
                <p>{gap.description}</p>
                <span className="importance">Importance: {gap.importance}</span>
              </div>
            ))}
          </section>

          <section>
            <h4>Future Opportunities:</h4>
            {gaps.research_gaps.future_opportunities.map((opp, i) => (
              <div key={i} className="opportunity-item">
                <h5>{opp.opportunity}</h5>
                <p>{opp.description}</p>
                <span className="feasibility">Feasibility: {opp.feasibility}</span>
              </div>
            ))}
          </section>
        </div>
      )}
    </div>
  );
};

export default ResearchGaps;
```

## 🎨 UI/UX Recommendations

### Loading States
- **Paper Analysis**: 15-30 seconds - Show progress indicator
- **Research Gaps**: 20-40 seconds - Show "Analyzing patterns..." message
- **PDF Generation**: 10-20 seconds - Show "Generating report..." message

### Error Handling
```javascript
const handleAPIError = (error, response) => {
  if (response?.status === 429) {
    return "Rate limit exceeded. Please try again later.";
  }
  if (response?.status === 500) {
    return "Server error. Please try again.";
  }
  return error.message || "An unexpected error occurred.";
};
```

### Responsive Design Tips
- **Cards for papers**: Easy to scan on mobile
- **Collapsible sections**: For analysis details
- **Progress indicators**: For long-running operations
- **Export buttons**: Prominent placement for PDF downloads

## 🔧 Configuration & Environment

### CORS Setup
The API is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:8080` (Vue default)

### Environment Variables (For Production)
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8004';
```

## 📊 Data Visualization Ideas

### For Paper Analysis:
- **Timeline**: Publication dates
- **Source Distribution**: Pie chart of arxiv vs pubmed
- **Keyword Cloud**: From abstracts
- **Citation Counts**: Bar charts

### For Research Gaps:
- **Gap Importance**: Color-coded priority levels
- **Opportunity Matrix**: Feasibility vs Impact
- **Trend Timeline**: Evolution of research themes

## 🚀 Performance Tips

### Optimize API Calls:
```javascript
// Debounce search queries
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
};

// Cache results
const resultsCache = new Map();

const getCachedResults = (query) => {
  const cacheKey = JSON.stringify(query);
  return resultsCache.get(cacheKey);
};
```

### Handle Large Responses:
```javascript
// Paginate large result sets
const [displayedResults, setDisplayedResults] = useState([]);
const [currentPage, setCurrentPage] = useState(0);
const RESULTS_PER_PAGE = 5;

useEffect(() => {
  if (results) {
    const start = currentPage * RESULTS_PER_PAGE;
    const end = start + RESULTS_PER_PAGE;
    setDisplayedResults(results.results.slice(start, end));
  }
}, [results, currentPage]);
```

## 📱 Mobile Considerations

- **Touch-friendly buttons**: Minimum 44px height
- **Swipe gestures**: For paper cards
- **Collapsed details**: Expandable analysis sections
- **Offline handling**: Cache recent searches

## 🔍 Testing the API

### Quick Test Commands:
```bash
# Test server status
curl http://localhost:8004/docs

# Test paper analysis
curl -X POST "http://localhost:8004/analyze/papers-with-ai" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "max_papers": 1, "sources": ["arxiv"]}'
```

### Test Data Suggestions:
- **Quick queries**: "machine learning", "quantum computing"
- **Medical queries**: "cancer detection", "medical imaging"
- **CS queries**: "neural networks", "algorithms"

## 📞 Support & Communication

### Common Issues:
1. **CORS errors**: Check if API is running on port 8004
2. **Slow responses**: Normal for AI analysis (15-30s)
3. **Rate limits**: Use arxiv/pubmed, avoid google_scholar
4. **Empty results**: Try broader search terms

### API Status:
- Check server logs for detailed error messages
- Monitor response times for performance issues
- Track usage for Google Scholar rate limiting

Your API is **production-ready** and waiting for frontend integration! 🚀