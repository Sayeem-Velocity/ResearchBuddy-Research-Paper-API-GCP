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

    async def chat_with_paper(
        self,
        message: str,
        paper: Paper,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Mock chat about a specific paper with context"""
        try:
            await asyncio.sleep(0.5)  # Simulate processing

            message_lower = message.lower()
            
            # Detect question type and provide relevant response
            if any(word in message_lower for word in ['contribution', 'contributions', 'contribute']):
                return (f"The main contributions of '{paper.title}' include:\n\n"
                       f"1. Novel methodological approaches in {paper.title.split()[0].lower()} research\n"
                       f"2. Comprehensive empirical validation demonstrating effectiveness\n"
                       f"3. Framework that advances the state-of-the-art in the field\n"
                       f"4. Practical insights for real-world applications\n\n"
                       f"The authors make significant contributions by addressing key challenges "
                       f"and providing solutions that build upon existing literature.")
            
            elif any(word in message_lower for word in ['methodology', 'method', 'approach', 'technique']):
                title_words = paper.title.lower().split()[:3]
                return (f"The methodology employed in this paper involves:\n\n"
                       f"**Research Approach:** The authors utilize a mixed-methods design combining "
                       f"theoretical analysis with empirical validation.\n\n"
                       f"**Data Collection:** Comprehensive datasets are gathered focusing on {' '.join(title_words)}.\n\n"
                       f"**Analysis Techniques:** Advanced analytical methods including statistical analysis, "
                       f"computational modeling, and systematic evaluation.\n\n"
                       f"**Validation:** Rigorous testing through experiments and comparison with baseline approaches.\n\n"
                       f"The methodology is designed to ensure reproducibility and reliability of findings.")
            
            elif any(word in message_lower for word in ['limitation', 'weakness', 'drawback', 'problem']):
                return (f"The limitations and potential weaknesses of this paper include:\n\n"
                       f"1. **Scope:** The study may have limited generalizability to broader contexts\n"
                       f"2. **Sample Size:** Some experiments might benefit from larger datasets\n"
                       f"3. **Computational Cost:** The proposed methods may require significant computational resources\n"
                       f"4. **Long-term Effects:** Limited exploration of longitudinal impacts\n\n"
                       f"These limitations provide opportunities for future research to extend and improve upon this work.")
            
            elif any(word in message_lower for word in ['finding', 'result', 'outcome', 'discover']):
                return (f"The key findings from '{paper.title}' include:\n\n"
                       f"• Significant improvements in performance metrics compared to existing approaches\n"
                       f"• Novel insights into the underlying mechanisms of the research domain\n"
                       f"• Strong empirical evidence supporting the proposed hypotheses\n"
                       f"• Practical implications for real-world applications\n\n"
                       f"The results demonstrate the effectiveness and feasibility of the proposed approach, "
                       f"with statistical significance confirmed through rigorous testing.")
            
            elif any(word in message_lower for word in ['future', 'next', 'extend', 'improve']):
                return (f"Future research directions based on this paper could include:\n\n"
                       f"1. **Scalability:** Extending the approach to larger and more diverse datasets\n"
                       f"2. **Cross-domain Application:** Testing applicability in different research domains\n"
                       f"3. **Real-world Deployment:** Investigating challenges in practical implementation\n"
                       f"4. **Integration:** Combining with emerging technologies and methods\n"
                       f"5. **Longitudinal Studies:** Examining long-term effects and sustainability\n\n"
                       f"These directions could significantly advance the field and address current limitations.")
            
            elif any(word in message_lower for word in ['summarize', 'summary', 'tldr', 'overview']):
                abstract_preview = paper.abstract[:200] + "..." if len(paper.abstract) > 200 else paper.abstract
                return (f"**Summary of '{paper.title}':**\n\n"
                       f"{abstract_preview}\n\n"
                       f"**Key Points:**\n"
                       f"• The paper addresses important challenges in the field\n"
                       f"• Novel approaches are proposed and validated empirically\n"
                       f"• Results demonstrate significant improvements\n"
                       f"• Practical applications and future directions are discussed\n\n"
                       f"This work makes valuable contributions to advancing research in this area.")
            
            elif any(word in message_lower for word in ['author', 'who wrote', 'researcher']):
                authors_list = ', '.join(paper.authors[:5])
                if len(paper.authors) > 5:
                    authors_list += f" and {len(paper.authors) - 5} others"
                return (f"This paper was authored by: **{authors_list}**\n\n"
                       f"Published: {paper.published}\n"
                       f"Source: {paper.source}\n"
                       f"{'Venue: ' + paper.venue if paper.venue else ''}\n\n"
                       f"The research team brings together expertise from various areas to address "
                       f"the key challenges presented in this work.")
            
            else:
                # General response for other questions
                return (f"Regarding your question about '{paper.title}':\n\n"
                       f"This paper explores important aspects of {paper.title.lower()}. "
                       f"The authors present comprehensive research that contributes to the field through "
                       f"innovative methodologies and rigorous empirical validation.\n\n"
                       f"**Specific aspects you might find interesting:**\n"
                       f"• The theoretical framework provides solid foundations\n"
                       f"• Experimental results show promising outcomes\n"
                       f"• Practical implications are clearly articulated\n\n"
                       f"Would you like me to elaborate on any specific aspect such as the methodology, "
                       f"findings, contributions, or limitations?")

        except Exception as e:
            logger.error(f"Error in mock chat: {e}")
            return f"I'm sorry, I encountered an error while processing your question: {str(e)}"
    
    async def chat_with_papers(
        self,
        message: str,
        papers_context: List[Paper],
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """Mock chat about multiple papers with context"""
        try:
            await asyncio.sleep(0.3)  # Simulate processing

            paper_count = len(papers_context)
            if paper_count == 0:
                return "I don't have any papers in context to discuss. Please provide some papers first."

            # Use the first paper as primary context
            if paper_count == 1:
                return await self.chat_with_paper(message, papers_context[0], chat_history)

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