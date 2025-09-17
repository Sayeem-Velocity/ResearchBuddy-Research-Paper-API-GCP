# Research Paper API 🔬

An AI-powered research paper analysis API that aggregates papers from multiple sources and provides intelligent analysis using Google's Gemini AI.

## 🚀 Features

- **Multi-Source Paper Search**: arXiv, PubMed, Google Scholar
- **AI-Powered Analysis**: Comprehensive paper analysis using Gemini 2.0
- **Research Gap Identification**: Cross-paper analysis to identify research opportunities
- **Research Scope Planning**: AI-generated research proposals with timelines
- **PDF Report Generation**: Professional reports combining all analyses
- **Rate Limiting**: Respectful API usage with Google Scholar daily limits

## 📊 API Endpoints

### Base URL
```
http://localhost:8004
```

### 🔍 Search & Analysis Endpoints

#### 1. Analyze Papers with AI
**POST** `/analyze/papers-with-ai`

Searches for papers and provides comprehensive AI analysis.

```json
{
  "query": "machine learning",
  "max_papers": 5,
  "sources": ["arxiv", "pubmed", "google_scholar"]
}
```

**Response:**
```json
{
  "query": "machine learning",
  "papers_found": 5,
  "analyses_generated": 5,
  "results": [
    {
      "paper": {
        "id": "http://arxiv.org/abs/2208.00733v1",
        "title": "The Rise of Quantum Internet Computing",
        "authors": ["Seng W. Loke"],
        "abstract": "This article highlights...",
        "published": "2022-08-01T10:36:13+00:00",
        "source": "arxiv",
        "venue": "arXiv",
        "citation_count": null
      },
      "analysis": {
        "summary": "This paper introduces the concept of quantum Internet computing...",
        "key_contributions": ["Defines quantum Internet computing...", "..."],
        "strengths": ["Provides clear definition...", "..."],
        "weaknesses": ["High-level overview without technical details...", "..."],
        "research_gaps": ["Specific quantum protocols need exploration...", "..."],
        "future_scope": ["Development of quantum protocols...", "..."],
        "methodology": "Conceptual overview based on literature review",
        "main_findings": ["Quantum Internet computing is distinct field...", "..."],
        "generated_at": "2025-09-17T00:40:51.942170"
      }
    }
  ]
}
```

#### 2. Research Gaps Analysis
**POST** `/analyze/research-gaps`

Identifies research gaps across multiple papers in a domain.

```json
{
  "query": "deep learning",
  "research_domain": "artificial intelligence",
  "max_papers": 10,
  "sources": ["arxiv", "pubmed"]
}
```

**Response:**
```json
{
  "query": "deep learning",
  "research_domain": "artificial intelligence",
  "papers_analyzed": 10,
  "research_gaps": {
    "domain": "artificial intelligence",
    "current_trends": ["Optimization techniques...", "Medical applications...", "..."],
    "research_gaps": [
      {
        "gap": "Theoretical understanding of optimization landscapes",
        "description": "While optimization algorithms are widely used...",
        "importance": "high"
      }
    ],
    "methodology_gaps": ["Rigorous benchmarking...", "..."],
    "future_opportunities": [
      {
        "opportunity": "Development of AutoML tools for medical applications",
        "description": "AutoML tools can automate the process...",
        "feasibility": "medium"
      }
    ],
    "cross_domain_connections": ["Statistics", "Control Theory", "..."],
    "recommendations": ["Focus on robust, explainable models...", "..."]
  }
}
```

#### 3. Research Scope Generation
**POST** `/analyze/research-scope`

Generates a comprehensive research plan based on papers and research question.

```json
{
  "query": "neural networks",
  "research_question": "How can we improve the interpretability of neural networks in medical diagnosis?",
  "timeline_months": 18,
  "max_papers": 8,
  "sources": ["arxiv", "pubmed"]
}
```

**Response:**
```json
{
  "query": "neural networks",
  "research_question": "How can we improve the interpretability of neural networks in medical diagnosis?",
  "timeline_months": 18,
  "research_scope": {
    "research_question": "How can we improve...",
    "timeline_months": 18,
    "research_objectives": [
      {
        "objective": "Develop explainable AI techniques",
        "description": "Create methods to make neural network decisions transparent",
        "priority": "high"
      }
    ],
    "methodology": {
      "approach": "Mixed-methods approach combining quantitative analysis...",
      "data_collection": ["Medical imaging datasets", "Clinical data", "..."],
      "analysis_methods": ["Statistical analysis", "Deep learning", "..."],
      "tools_required": ["Python", "TensorFlow", "..."]
    },
    "phases": [
      {
        "phase": "Phase 1: Literature Review",
        "duration_months": 3,
        "activities": ["Comprehensive literature review", "..."],
        "deliverables": ["Literature review report", "..."]
      }
    ],
    "expected_challenges": [
      {
        "challenge": "Data privacy concerns",
        "mitigation": "Use federated learning approaches",
        "risk_level": "medium"
      }
    ],
    "resources_needed": {
      "personnel": ["PhD researcher", "Medical expert", "..."],
      "equipment": ["GPU clusters", "Medical imaging equipment", "..."],
      "software": ["Deep learning frameworks", "..."],
      "estimated_budget": "$150,000 - $200,000"
    },
    "success_metrics": ["Improved model interpretability scores", "..."],
    "potential_outcomes": ["Novel interpretability framework", "..."]
  }
}
```

#### 4. Generate Comprehensive Report
**POST** `/generate/comprehensive-report`

Generates a professional PDF report combining all analyses.

```json
{
  "query": "quantum computing",
  "research_domain": "computer science",
  "research_question": "What are the applications of quantum computing in cryptography?",
  "timeline_months": 12,
  "max_papers": 5,
  "sources": ["arxiv"],
  "report_title": "Quantum Computing in Cryptography: Research Analysis"
}
```

**Response:** PDF file download

### 📄 Basic Search Endpoints

#### Search Papers
**POST** `/search`

Basic paper search without AI analysis.

```json
{
  "query": "machine learning",
  "sources": ["arxiv", "pubmed"],
  "max_results": 20,
  "generate_analysis": false,
  "sort_by": "recent",
  "date_range": {
    "start_year": 2020,
    "end_year": 2024
  }
}
```

#### Get Search Status
**GET** `/search/status/{session_id}`

Check the status of a search session.

#### Get Search Results
**GET** `/search/results/{session_id}`

Retrieve results from a completed search session.

#### Get User Sessions
**GET** `/sessions?limit=20&status_filter=completed`

List user's search sessions.

#### Delete Session
**DELETE** `/sessions/{session_id}`

Delete a search session and its data.

## 🛠️ Technical Details

### Models Used
- **Primary**: Gemini 2.0 Flash Experimental
- **Provider**: Google Vertex AI
- **Region**: us-central1

### Rate Limits
- **Google Scholar**: 1 search per user per day
- **arXiv**: No limits (free)
- **PubMed**: No limits (free)
- **Vertex AI**: Based on your Google Cloud quotas

### Response Times
- **Basic Search**: 2-5 seconds
- **AI Analysis**: 15-30 seconds per paper
- **Research Gaps**: 20-40 seconds
- **Research Scope**: 30-60 seconds
- **PDF Generation**: 10-20 seconds

## 🔧 Development Setup

### Prerequisites
```bash
Python 3.8+
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file with:
```bash
PROJECT_ID=your-gcp-project
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_API_KEY=your-vertex-ai-api-key
SERP_API_KEY=your-serp-api-key
SECRET_KEY=your-secret-key
```

### Running the Server
```bash
# Development
python -m uvicorn app.main_full:app --reload --host 127.0.0.1 --port 8004

# Production
python -m uvicorn app.main_full:app --host 0.0.0.0 --port 8000
```

### API Documentation
Visit `http://localhost:8004/docs` for interactive API documentation.

## 📝 Error Handling

All endpoints return standard HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (session not found)
- **429**: Rate Limit Exceeded (Google Scholar)
- **500**: Internal Server Error

Error response format:
```json
{
  "detail": "Error message description"
}
```

## 🔒 Security

- API keys are securely stored in environment variables
- Rate limiting prevents abuse
- CORS configured for frontend integration
- No sensitive data logged

## 📊 Usage Examples

### Frontend Integration (JavaScript)

```javascript
// Basic paper analysis
const response = await fetch('http://localhost:8004/analyze/papers-with-ai', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'artificial intelligence',
    max_papers: 5,
    sources: ['arxiv', 'pubmed']
  })
});

const data = await response.json();
console.log(data.results);

// Research gaps analysis
const gapsResponse = await fetch('http://localhost:8004/analyze/research-gaps', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'machine learning',
    research_domain: 'computer science',
    max_papers: 10,
    sources: ['arxiv']
  })
});

const gapsData = await gapsResponse.json();
console.log(gapsData.research_gaps);

// PDF report generation
const reportResponse = await fetch('http://localhost:8004/generate/comprehensive-report', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'quantum computing',
    research_domain: 'physics',
    research_question: 'What are the latest advances in quantum error correction?',
    timeline_months: 24,
    max_papers: 8,
    sources: ['arxiv'],
    report_title: 'Quantum Error Correction Research Analysis'
  })
});

// Handle PDF download
const blob = await reportResponse.blob();
const url = window.URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'research-report.pdf';
a.click();
```

### React Integration Example

```jsx
import React, { useState } from 'react';

const PaperAnalysis = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const analyzePapers = async () => {
    setLoading(true);
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
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter research query"
      />
      <button onClick={analyzePapers} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Papers'}
      </button>

      {results && (
        <div>
          <h3>Found {results.papers_found} papers</h3>
          {results.results.map((result, index) => (
            <div key={index}>
              <h4>{result.paper.title}</h4>
              <p><strong>Summary:</strong> {result.analysis.summary}</p>
              <p><strong>Key Contributions:</strong></p>
              <ul>
                {result.analysis.key_contributions.map((contrib, i) => (
                  <li key={i}>{contrib}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

## 🤝 Support

For technical issues or questions, contact the development team.

## 📄 License

Private project - All rights reserved.