# app/main_full.py - Full FastAPI app with mock dependencies
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting up Research Paper API (Full with Mocks)...")
    yield
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Research Paper Analysis API",
    description="API for searching, analyzing, and querying research papers",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with mock endpoints
from fastapi import APIRouter
from app.api.v1.endpoints import search_mock

api_router = APIRouter()
api_router.include_router(
    search_mock.router,
    prefix="/papers",
    tags=["papers"]
)

app.include_router(api_router, prefix=settings.api_v1_prefix)

@app.get("/")
async def root():
    return {"message": "Research Paper API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/sources")
async def get_available_sources():
    """Get available paper sources"""
    from app.models.paper import PaperSource
    return {
        "sources": [
            {"id": PaperSource.ARXIV, "name": "arXiv", "description": "Physics, Mathematics, Computer Science papers"},
            {"id": PaperSource.PUBMED, "name": "PubMed", "description": "Biomedical and life science literature"},
            {"id": PaperSource.GOOGLE_SCHOLAR, "name": "Google Scholar", "description": "Multidisciplinary academic search (rate limited)"}
        ]
    }

@app.get("/demo/search")
async def demo_search(query: str = "machine learning", max_results: int = 3):
    """Demo endpoint that shows direct search results"""
    try:
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource

        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.ARXIV],
            max_results=max_results,
            user_id="demo_user"
        )

        # Convert papers to dict format for JSON response
        results = []
        for paper in papers:
            results.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract,
                "authors": paper.authors,
                "published": paper.published,
                "source": str(paper.source),
                "venue": paper.venue,
                "pdf_url": paper.pdf_url
            })

        return {
            "query": query,
            "results_count": len(results),
            "papers": results
        }

    except Exception as e:
        logger.error(f"Demo search error: {e}")
        return {"error": str(e), "query": query, "papers": []}

@app.get("/demo/pubmed")
async def demo_pubmed_search(query: str = "cancer treatment", max_results: int = 3):
    """Demo endpoint for PubMed search"""
    try:
        from app.services.paper_search.pubmed_search import PubMedSearcher

        searcher = PubMedSearcher()
        papers = await searcher.search(query, max_results)

        # Convert papers to dict format for JSON response
        results = []
        for paper in papers:
            results.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract,
                "authors": paper.authors,
                "published": paper.published,
                "source": str(paper.source),
                "venue": paper.venue,
                "pdf_url": paper.pdf_url
            })

        return {
            "query": query,
            "source": "PubMed",
            "results_count": len(results),
            "papers": results
        }

    except Exception as e:
        logger.error(f"Demo PubMed search error: {e}")
        return {"error": str(e), "query": query, "papers": []}

@app.get("/demo/multi-source")
async def demo_multi_source_search(query: str = "machine learning", max_results: int = 5):
    """Demo endpoint for multi-source search (arXiv + PubMed)"""
    try:
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource

        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.ARXIV, PaperSource.PUBMED],
            max_results=max_results,
            user_id="demo_user"
        )

        # Convert papers to dict format for JSON response
        results = []
        for paper in papers:
            results.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract,
                "authors": paper.authors,
                "published": paper.published,
                "source": str(paper.source),
                "venue": paper.venue,
                "pdf_url": paper.pdf_url
            })

        return {
            "query": query,
            "sources": ["arXiv", "PubMed"],
            "results_count": len(results),
            "papers": results
        }

    except Exception as e:
        logger.error(f"Demo multi-source search error: {e}")
        return {"error": str(e), "query": query, "papers": []}

@app.get("/demo/google-scholar")
async def demo_google_scholar_search(query: str = "artificial intelligence", max_results: int = 3, user_id: str = "demo_user"):
    """Demo endpoint for Google Scholar search (rate limited - 1 search per user per day)"""
    try:
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource

        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.GOOGLE_SCHOLAR],
            max_results=max_results,
            user_id=user_id
        )

        # Convert papers to dict format for JSON response
        results = []
        for paper in papers:
            results.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract,
                "authors": paper.authors,
                "published": paper.published,
                "source": str(paper.source),
                "venue": paper.venue,
                "pdf_url": paper.pdf_url,
                "citation_count": paper.citation_count
            })

        return {
            "query": query,
            "source": "Google Scholar",
            "user_id": user_id,
            "rate_limit": "1 search per user per day",
            "results_count": len(results),
            "papers": results
        }

    except Exception as e:
        logger.error(f"Demo Google Scholar search error: {e}")
        return {"error": str(e), "query": query, "user_id": user_id, "papers": []}

@app.get("/demo/all-sources")
async def demo_all_sources_search(query: str = "machine learning", max_results: int = 6, user_id: str = "demo_user"):
    """Demo endpoint for all sources search (arXiv + PubMed + Google Scholar)"""
    try:
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource

        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.ARXIV, PaperSource.PUBMED, PaperSource.GOOGLE_SCHOLAR],
            max_results=max_results,
            user_id=user_id
        )

        # Convert papers to dict format for JSON response
        results = []
        for paper in papers:
            results.append({
                "id": paper.id,
                "title": paper.title,
                "abstract": paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract,
                "authors": paper.authors,
                "published": paper.published,
                "source": str(paper.source),
                "venue": paper.venue,
                "pdf_url": paper.pdf_url,
                "citation_count": paper.citation_count
            })

        return {
            "query": query,
            "sources": ["arXiv", "PubMed", "Google Scholar"],
            "user_id": user_id,
            "google_scholar_note": "Rate limited to 1 search per user per day",
            "results_count": len(results),
            "papers": results
        }

    except Exception as e:
        logger.error(f"Demo all sources search error: {e}")
        return {"error": str(e), "query": query, "user_id": user_id, "papers": []}

@app.post("/analyze/research-gaps")
async def analyze_research_gaps(request: dict):
    """Analyze research gaps from papers using real Vertex AI"""
    try:
        from app.services.llm.vertex_ai import VertexAIService
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource

        query = request.get("query", "")
        research_domain = request.get("research_domain", "")
        max_papers = request.get("max_papers", 10)
        user_id = request.get("user_id", "research_gaps_user")

        if not query:
            return {"error": "Query is required"}

        # Search for papers
        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.ARXIV, PaperSource.PUBMED, PaperSource.GOOGLE_SCHOLAR],
            max_results=max_papers,
            user_id=user_id
        )

        if not papers:
            return {"error": "No papers found for the given query", "query": query}

        # Analyze research gaps using Vertex AI
        vertex_ai = VertexAIService()
        research_gaps = await vertex_ai.identify_research_gaps(papers, research_domain)

        return {
            "query": query,
            "research_domain": research_domain,
            "papers_analyzed": len(papers),
            "research_gaps": research_gaps
        }

    except Exception as e:
        logger.error(f"Research gaps analysis error: {e}")
        return {"error": str(e), "query": query}

@app.post("/analyze/research-scope")
async def generate_research_scope(request: dict):
    """Generate research scope from papers using real Vertex AI"""
    try:
        from app.services.llm.vertex_ai import VertexAIService
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource

        query = request.get("query", "")
        research_question = request.get("research_question", "")
        timeline_months = request.get("timeline_months", 12)
        max_papers = request.get("max_papers", 10)
        user_id = request.get("user_id", "research_scope_user")

        if not query or not research_question:
            return {"error": "Both query and research_question are required"}

        # Search for papers
        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.ARXIV, PaperSource.PUBMED, PaperSource.GOOGLE_SCHOLAR],
            max_results=max_papers,
            user_id=user_id
        )

        if not papers:
            return {"error": "No papers found for the given query", "query": query}

        # Generate research scope using Vertex AI
        vertex_ai = VertexAIService()
        research_scope = await vertex_ai.generate_research_scope(papers, research_question, timeline_months)

        return {
            "query": query,
            "research_question": research_question,
            "timeline_months": timeline_months,
            "papers_analyzed": len(papers),
            "research_scope": research_scope
        }

    except Exception as e:
        logger.error(f"Research scope generation error: {e}")
        return {"error": str(e), "query": query}

@app.post("/generate/comprehensive-report")
async def generate_comprehensive_report(request: dict):
    """Generate comprehensive PDF report with papers, analysis, gaps, and scope"""
    try:
        from app.services.llm.vertex_ai import VertexAIService
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource
        from fastapi.responses import StreamingResponse
        from io import BytesIO

        query = request.get("query", "")
        research_question = request.get("research_question", "")
        research_domain = request.get("research_domain", "")
        max_papers = request.get("max_papers", 8)
        timeline_months = request.get("timeline_months", 12)
        report_title = request.get("report_title", "Comprehensive Research Analysis Report")
        user_id = request.get("user_id", "report_user")
        include_analysis = request.get("include_analysis", True)
        include_gaps = request.get("include_gaps", True)
        include_scope = request.get("include_scope", True)

        if not query:
            return {"error": "Query is required"}

        # Search for papers
        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.ARXIV, PaperSource.PUBMED, PaperSource.GOOGLE_SCHOLAR],
            max_results=max_papers,
            user_id=user_id
        )

        if not papers:
            return {"error": "No papers found for the given query", "query": query}

        # Initialize Vertex AI service
        vertex_ai = VertexAIService()

        # Generate paper analyses if requested
        analyses = None
        if include_analysis:
            logger.info(f"Generating AI analyses for {len(papers)} papers...")
            analyses = await vertex_ai.analyze_papers_batch(papers[:5])  # Limit to 5 for cost control

        # Identify research gaps if requested
        research_gaps = None
        if include_gaps:
            logger.info("Identifying research gaps...")
            research_gaps = await vertex_ai.identify_research_gaps(papers, research_domain)

        # Generate research scope if requested
        research_scope = None
        if include_scope and research_question:
            logger.info("Generating research scope...")
            research_scope = await vertex_ai.generate_research_scope(papers, research_question, timeline_months)

        # Generate PDF report
        logger.info("Generating comprehensive PDF report...")
        pdf_bytes = await vertex_ai.generate_comprehensive_report_pdf(
            papers=papers,
            analyses=analyses,
            research_gaps=research_gaps,
            research_scope=research_scope,
            custom_title=report_title
        )

        # Return PDF as streaming response
        pdf_buffer = BytesIO(pdf_bytes)

        # Create safe filename
        import re
        safe_filename = re.sub(r'[^\w\s-]', '', query.replace(' ', '_'))[:50]
        filename = f"research_report_{safe_filename}.pdf"

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Comprehensive report generation error: {e}")
        return {"error": str(e), "query": query}

@app.post("/analyze/papers-with-ai")
async def analyze_papers_with_ai(request: dict):
    """Analyze specific papers with Vertex AI"""
    try:
        from app.services.llm.vertex_ai import VertexAIService
        from app.services.paper_search.aggregator import PaperSearchAggregator
        from app.models.paper import PaperSource

        query = request.get("query", "")
        max_papers = request.get("max_papers", 5)
        user_id = request.get("user_id", "ai_analysis_user")

        if not query:
            return {"error": "Query is required"}

        # Search for papers
        aggregator = PaperSearchAggregator()
        papers = await aggregator.search_all_sources(
            query=query,
            sources=[PaperSource.ARXIV, PaperSource.PUBMED, PaperSource.GOOGLE_SCHOLAR],
            max_results=max_papers,
            user_id=user_id
        )

        if not papers:
            return {"error": "No papers found for the given query", "query": query}

        # Analyze papers using Vertex AI
        vertex_ai = VertexAIService()
        analyses = await vertex_ai.analyze_papers_batch(papers)

        # Combine papers with analyses
        results = []
        for paper in papers:
            # Find matching analysis
            matching_analysis = next((a for a in analyses if a.paper_id == paper.id), None)

            paper_result = {
                "paper": {
                    "id": paper.id,
                    "title": paper.title,
                    "authors": paper.authors,
                    "abstract": paper.abstract[:300] + "..." if len(paper.abstract) > 300 else paper.abstract,
                    "published": paper.published,
                    "source": str(paper.source),
                    "venue": paper.venue,
                    "citation_count": paper.citation_count
                }
            }

            if matching_analysis:
                paper_result["analysis"] = {
                    "summary": matching_analysis.summary,
                    "key_contributions": matching_analysis.key_contributions,
                    "strengths": matching_analysis.strengths,
                    "weaknesses": matching_analysis.weaknesses,
                    "research_gaps": matching_analysis.research_gaps,
                    "future_scope": matching_analysis.future_scope,
                    "methodology": matching_analysis.methodology,
                    "main_findings": matching_analysis.main_findings,
                    "generated_at": matching_analysis.generated_at.isoformat()
                }

            results.append(paper_result)

        return {
            "query": query,
            "papers_found": len(papers),
            "analyses_generated": len(analyses),
            "results": results
        }

    except Exception as e:
        logger.error(f"AI paper analysis error: {e}")
        return {"error": str(e), "query": query}

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Run with: uvicorn app.main_full:app --reload