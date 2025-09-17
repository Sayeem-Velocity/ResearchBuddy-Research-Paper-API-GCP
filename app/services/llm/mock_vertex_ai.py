# app/services/llm/mock_vertex_ai.py
import asyncio
import logging
from typing import Dict, List, Optional, Any
import json
from app.models.paper import Paper, PaperAnalysis
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class MockVertexAIService:
    """Mock Vertex AI service for testing without Google Cloud dependencies"""

    def __init__(self):
        logger.info("Mock Vertex AI service initialized")

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """Generate mock analysis of a research paper"""
        try:
            # Simulate processing time
            await asyncio.sleep(0.5)

            # Generate mock analysis based on paper title and abstract
            analysis_data = self._generate_mock_analysis(paper)

            return PaperAnalysis(
                paper_id=paper.id,
                summary=analysis_data['summary'],
                strengths=analysis_data['strengths'],
                weaknesses=analysis_data['weaknesses'],
                research_gaps=analysis_data['research_gaps'],
                future_scope=analysis_data['future_scope'],
                key_contributions=analysis_data['key_contributions'],
                methodology=analysis_data['methodology'],
                main_findings=analysis_data['main_findings'],
                generated_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Error in mock analysis for paper {paper.id}: {e}")
            return PaperAnalysis(
                paper_id=paper.id,
                summary=f"Mock analysis failed: {str(e)}",
                generated_at=datetime.utcnow()
            )

    def _generate_mock_analysis(self, paper: Paper) -> Dict[str, Any]:
        """Generate mock analysis data"""
        title_words = paper.title.lower().split()
        abstract_words = paper.abstract.lower().split()[:50]  # First 50 words

        # Extract key terms for more realistic mock data
        key_terms = [word for word in title_words + abstract_words
                    if len(word) > 4 and word.isalpha()][:5]

        return {
            'summary': f"This paper explores {', '.join(key_terms[:3])} and presents novel approaches "
                      f"to address challenges in the field. The authors propose innovative methodologies "
                      f"that demonstrate significant improvements over existing approaches.",

            'key_contributions': [
                f"Novel approach to {key_terms[0] if key_terms else 'research problem'}",
                f"Comprehensive analysis of {key_terms[1] if len(key_terms) > 1 else 'methodology'}",
                f"Empirical validation demonstrating effectiveness",
                f"Framework for future {key_terms[2] if len(key_terms) > 2 else 'research'}"
            ],

            'methodology': f"The paper employs a mixed-methods approach combining theoretical analysis "
                          f"with empirical validation. The authors utilize {key_terms[0] if key_terms else 'advanced techniques'} "
                          f"and conduct extensive experiments to validate their hypotheses.",

            'main_findings': [
                f"Significant improvement in {key_terms[0] if key_terms else 'performance metrics'}",
                f"Novel insights into {key_terms[1] if len(key_terms) > 1 else 'research domain'}",
                f"Effective framework for practical applications",
                f"Strong correlation between proposed methods and outcomes"
            ],

            'strengths': [
                "Comprehensive theoretical foundation",
                "Rigorous experimental methodology",
                "Clear presentation of results",
                "Practical applicability of findings",
                "Strong validation through multiple experiments"
            ],

            'weaknesses': [
                "Limited scope of experimental validation",
                "Some assumptions may not hold in all contexts",
                "Computational complexity could be optimized"
            ],

            'research_gaps': [
                f"Scalability of {key_terms[0] if key_terms else 'proposed approach'} to larger datasets",
                f"Long-term effects of {key_terms[1] if len(key_terms) > 1 else 'methodology'}",
                f"Cross-domain applicability needs further investigation",
                "Real-world deployment challenges not fully addressed"
            ],

            'future_scope': [
                f"Extension to multi-domain {key_terms[0] if key_terms else 'applications'}",
                "Integration with emerging technologies",
                "Development of automated frameworks",
                f"Longitudinal studies on {key_terms[1] if len(key_terms) > 1 else 'effectiveness'}"
            ]
        }

    async def generate_summary(self, paper: Paper) -> str:
        """Generate a quick summary of a paper"""
        try:
            await asyncio.sleep(0.2)  # Simulate processing

            title_words = paper.title.split()[:3]
            key_focus = ' '.join(title_words).lower()

            return (f"This paper presents research on {key_focus} with novel contributions "
                   f"to the field. The authors demonstrate innovative approaches and provide "
                   f"empirical validation of their methods through comprehensive experiments.")

        except Exception as e:
            logger.error(f"Error generating mock summary for paper {paper.id}: {e}")
            return f"Summary generation failed: {str(e)}"

    async def chat_with_papers(
        self,
        message: str,
        papers_context: List[Paper],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Mock chat about papers with context"""
        try:
            await asyncio.sleep(0.3)  # Simulate processing

            paper_count = len(papers_context)
            if paper_count == 0:
                return "I don't have any papers in context to discuss. Please provide some papers first."

            # Extract key terms from the message
            message_words = message.lower().split()
            question_words = ['what', 'how', 'why', 'when', 'where', 'which']
            is_question = any(word in message_words for word in question_words)

            if is_question:
                return (f"Based on the {paper_count} papers in context, I can provide insights about your question. "
                       f"The papers discuss various aspects related to '{message_words[0] if message_words else 'your topic'}'. "
                       f"Key findings across these papers suggest innovative approaches and methodologies. "
                       f"Would you like me to elaborate on any specific aspect?")
            else:
                return (f"I understand you're interested in discussing {message}. "
                       f"Looking at the {paper_count} papers in our context, there are several relevant connections. "
                       f"These papers provide comprehensive coverage of the topic and offer valuable insights "
                       f"for your research interests.")

        except Exception as e:
            logger.error(f"Error in mock chat: {e}")
            return f"I'm sorry, I encountered an error while processing your question: {str(e)}"

    async def analyze_papers_batch(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """Analyze multiple papers in batch with mock data"""
        if not papers:
            return []

        logger.info(f"Starting mock batch analysis of {len(papers)} papers")

        # Simulate concurrent processing with delays
        tasks = [self.analyze_paper(paper) for paper in papers]
        analyses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_analyses = []
        for i, analysis in enumerate(analyses):
            if isinstance(analysis, Exception):
                logger.error(f"Mock analysis failed for paper {papers[i].id}: {analysis}")
            else:
                valid_analyses.append(analysis)

        logger.info(f"Completed {len(valid_analyses)} mock analyses out of {len(papers)} papers")
        return valid_analyses