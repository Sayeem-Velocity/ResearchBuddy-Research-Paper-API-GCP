# app/services/llm/vertex_ai.py
import asyncio
import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from google import genai
from google.genai import types

from app.core.config import settings
from app.models.paper import Paper, PaperAnalysis

logger = logging.getLogger(__name__)

class VertexAIService:
    """Google Vertex AI service using the new GenAI client library"""

    def __init__(self):
        self.project_id = settings.project_id
        self.location = settings.vertex_ai_location
        self.api_key = settings.vertex_ai_api_key

        if not self.api_key:
            raise ValueError("VERTEX_AI_API_KEY must be set in environment variables")

        # Initialize the new GenAI client
        try:
            self.client = genai.Client(
                vertexai=True,
                api_key=self.api_key,
            )
            logger.info(f"GenAI client initialized for project {self.project_id} in {self.location}")
        except Exception as e:
            logger.error(f"Failed to initialize GenAI client: {e}")
            raise

        # Use the latest available model
        self.model_name = "gemini-2.0-flash-exp"

    async def analyze_paper(self, paper: Paper) -> PaperAnalysis:
        """
        Generate comprehensive analysis of a research paper
        """
        try:
            prompt = f"""
            Analyze this research paper comprehensively:

            Title: {paper.title}
            Authors: {', '.join(paper.authors)}
            Abstract: {paper.abstract}
            Publication Date: {paper.published}
            Source: {paper.source}
            Venue: {paper.venue or 'Not specified'}

            Please provide a detailed analysis covering:

            1. **Summary**: A concise 2-3 sentence summary of the paper's main contribution
            2. **Key Contributions**: List 3-5 specific contributions this paper makes to the field
            3. **Strengths**: Identify 3-4 strong points of this research
            4. **Weaknesses**: Point out 2-3 potential limitations or areas for improvement
            5. **Research Gaps**: Identify 2-3 gaps or future research directions this paper reveals
            6. **Future Scope**: Suggest 3-4 potential research directions building on this work
            7. **Methodology**: Describe the research methodology used (if apparent from abstract)
            8. **Main Findings**: List 3-4 key findings or results

            Format your response as valid JSON with the following structure:
            {{
                "summary": "...",
                "key_contributions": ["...", "...", "..."],
                "strengths": ["...", "...", "..."],
                "weaknesses": ["...", "...", "..."],
                "research_gaps": ["...", "...", "..."],
                "future_scope": ["...", "...", "..."],
                "methodology": "...",
                "main_findings": ["...", "...", "..."]
            }}
            """

            # Use the new GenAI client
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            ]

            config = types.GenerateContentConfig(
                temperature=0.3,
                top_p=0.8,
                max_output_tokens=4096,
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE"
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_NONE"
                    )
                ]
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            # Parse the response
            response_text = response.text.strip()

            # Clean up the response to ensure it's valid JSON
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()

            try:
                analysis_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning(f"Failed to parse JSON response for paper {paper.id}")
                analysis_data = {
                    "summary": response_text[:500] + "..." if len(response_text) > 500 else response_text,
                    "key_contributions": [],
                    "strengths": [],
                    "weaknesses": [],
                    "research_gaps": [],
                    "future_scope": [],
                    "methodology": "Analysis methodology not available",
                    "main_findings": []
                }

            return PaperAnalysis(
                paper_id=paper.id,
                summary=analysis_data.get("summary", ""),
                key_contributions=analysis_data.get("key_contributions", []),
                strengths=analysis_data.get("strengths", []),
                weaknesses=analysis_data.get("weaknesses", []),
                research_gaps=analysis_data.get("research_gaps", []),
                future_scope=analysis_data.get("future_scope", []),
                methodology=analysis_data.get("methodology", ""),
                main_findings=analysis_data.get("main_findings", []),
                generated_at=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error analyzing paper {paper.id}: {e}")
            # Return a failed analysis with error message
            return PaperAnalysis(
                paper_id=paper.id,
                summary=f"Analysis failed: {str(e)}",
                key_contributions=[],
                strengths=[],
                weaknesses=[],
                research_gaps=[],
                future_scope=[],
                methodology="",
                main_findings=[],
                generated_at=datetime.now()
            )

    async def analyze_papers_batch(self, papers: List[Paper]) -> List[PaperAnalysis]:
        """
        Analyze multiple papers in batch
        """
        logger.info(f"Starting batch analysis of {len(papers)} papers")

        # Process papers concurrently (but with some rate limiting)
        batch_size = 3  # Process 3 papers at a time to avoid overwhelming the API
        results = []

        for i in range(0, len(papers), batch_size):
            batch = papers[i:i + batch_size]
            batch_tasks = [self.analyze_paper(paper) for paper in batch]

            try:
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                for result in batch_results:
                    if isinstance(result, Exception):
                        logger.error(f"Error in batch analysis: {result}")
                        # Create a failed analysis for this paper
                        failed_analysis = PaperAnalysis(
                            paper_id="unknown",
                            summary=f"Batch analysis failed: {str(result)}",
                            key_contributions=[],
                            strengths=[],
                            weaknesses=[],
                            research_gaps=[],
                            future_scope=[],
                            methodology="",
                            main_findings=[],
                            generated_at=datetime.now()
                        )
                        results.append(failed_analysis)
                    else:
                        results.append(result)

            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
                # Add failed analyses for this batch
                for paper in batch:
                    failed_analysis = PaperAnalysis(
                        paper_id=paper.id,
                        summary=f"Batch processing failed: {str(e)}",
                        key_contributions=[],
                        strengths=[],
                        weaknesses=[],
                        research_gaps=[],
                        future_scope=[],
                        methodology="",
                        main_findings=[],
                        generated_at=datetime.now()
                    )
                    results.append(failed_analysis)

            # Small delay between batches to be respectful to the API
            if i + batch_size < len(papers):
                await asyncio.sleep(1)

        logger.info(f"Completed {len(results)} analyses out of {len(papers)} papers")
        return results

    async def identify_research_gaps(self, papers: List[Paper], research_domain: str = "") -> Dict[str, Any]:
        """
        Identify research gaps across multiple papers
        """
        try:
            paper_summaries = []
            for paper in papers[:10]:  # Limit to 10 papers for analysis
                summary = f"Title: {paper.title}\nAbstract: {paper.abstract[:500]}..."
                paper_summaries.append(summary)

            papers_text = "\n\n".join(paper_summaries)

            prompt = f"""
            Analyze these research papers in the domain of "{research_domain or 'general research'}" and identify research gaps:

            {papers_text}

            Based on these papers, identify:
            1. **Current Research Trends**: What are the main themes and approaches?
            2. **Research Gaps**: What important questions remain unanswered?
            3. **Methodology Gaps**: What research methods are underutilized?
            4. **Future Opportunities**: What are the most promising research directions?
            5. **Cross-Domain Connections**: How could this research connect with other fields?

            Provide a comprehensive analysis in JSON format:
            {{
                "domain": "{research_domain or 'General Research'}",
                "current_trends": ["...", "...", "..."],
                "research_gaps": [
                    {{"gap": "...", "description": "...", "importance": "high/medium/low"}},
                    {{"gap": "...", "description": "...", "importance": "high/medium/low"}}
                ],
                "methodology_gaps": ["...", "...", "..."],
                "future_opportunities": [
                    {{"opportunity": "...", "description": "...", "feasibility": "high/medium/low"}},
                    {{"opportunity": "...", "description": "...", "feasibility": "high/medium/low"}}
                ],
                "cross_domain_connections": ["...", "...", "..."],
                "recommendations": ["...", "...", "..."]
            }}
            """

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            ]

            config = types.GenerateContentConfig(
                temperature=0.4,
                top_p=0.9,
                max_output_tokens=4096
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            response_text = response.text.strip()

            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse research gaps JSON response")
                return {
                    "domain": research_domain or "General Research",
                    "current_trends": ["Analysis available in raw text"],
                    "research_gaps": [{"gap": "Analysis failed", "description": response_text[:500], "importance": "unknown"}],
                    "methodology_gaps": [],
                    "future_opportunities": [],
                    "cross_domain_connections": [],
                    "recommendations": []
                }

        except Exception as e:
            logger.error(f"Error identifying research gaps: {e}")
            return {
                "domain": research_domain or "General Research",
                "error": str(e),
                "current_trends": [],
                "research_gaps": [],
                "methodology_gaps": [],
                "future_opportunities": [],
                "cross_domain_connections": [],
                "recommendations": []
            }

    async def generate_research_scope(self, papers: List[Paper], research_question: str, timeline_months: int = 12) -> Dict[str, Any]:
        """
        Generate a research scope and plan based on papers and research question
        """
        try:
            paper_summaries = []
            for paper in papers[:8]:  # Limit to 8 papers for scope generation
                summary = f"Title: {paper.title}\nAuthors: {', '.join(paper.authors)}\nAbstract: {paper.abstract[:400]}..."
                paper_summaries.append(summary)

            papers_text = "\n\n".join(paper_summaries)

            prompt = f"""
            Create a comprehensive research scope and plan based on:

            Research Question: "{research_question}"
            Timeline: {timeline_months} months
            Related Papers:
            {papers_text}

            Generate a detailed research plan in JSON format:
            {{
                "research_question": "{research_question}",
                "timeline_months": {timeline_months},
                "research_objectives": [
                    {{"objective": "...", "description": "...", "priority": "high/medium/low"}},
                    {{"objective": "...", "description": "...", "priority": "high/medium/low"}}
                ],
                "methodology": {{
                    "approach": "...",
                    "data_collection": ["...", "...", "..."],
                    "analysis_methods": ["...", "...", "..."],
                    "tools_required": ["...", "...", "..."]
                }},
                "phases": [
                    {{
                        "phase": "Phase 1: Literature Review",
                        "duration_months": 2,
                        "activities": ["...", "...", "..."],
                        "deliverables": ["...", "..."]
                    }},
                    {{
                        "phase": "Phase 2: ...",
                        "duration_months": 3,
                        "activities": ["...", "...", "..."],
                        "deliverables": ["...", "..."]
                    }}
                ],
                "expected_challenges": [
                    {{"challenge": "...", "mitigation": "...", "risk_level": "high/medium/low"}},
                    {{"challenge": "...", "mitigation": "...", "risk_level": "high/medium/low"}}
                ],
                "resources_needed": {{
                    "personnel": ["...", "...", "..."],
                    "equipment": ["...", "...", "..."],
                    "software": ["...", "...", "..."],
                    "estimated_budget": "..."
                }},
                "success_metrics": ["...", "...", "..."],
                "potential_outcomes": ["...", "...", "..."]
            }}
            """

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )
            ]

            config = types.GenerateContentConfig(
                temperature=0.5,
                top_p=0.9,
                max_output_tokens=6000
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            response_text = response.text.strip()

            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()

            try:
                return json.loads(response_text)
            except json.JSONDecodeError:
                logger.warning("Failed to parse research scope JSON response")
                return {
                    "research_question": research_question,
                    "timeline_months": timeline_months,
                    "error": "Failed to parse structured response",
                    "raw_response": response_text[:1000],
                    "research_objectives": [],
                    "methodology": {},
                    "phases": [],
                    "expected_challenges": [],
                    "resources_needed": {},
                    "success_metrics": [],
                    "potential_outcomes": []
                }

        except Exception as e:
            logger.error(f"Error generating research scope: {e}")
            return {
                "research_question": research_question,
                "timeline_months": timeline_months,
                "error": str(e),
                "research_objectives": [],
                "methodology": {},
                "phases": [],
                "expected_challenges": [],
                "resources_needed": {},
                "success_metrics": [],
                "potential_outcomes": []
            }

    async def generate_comprehensive_report_pdf(
        self,
        papers: List[Paper],
        analyses: List[PaperAnalysis],
        research_gaps: Dict[str, Any],
        research_scope: Dict[str, Any],
        report_title: str = "Research Analysis Report"
    ) -> bytes:
        """
        Generate a comprehensive PDF report
        """
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from io import BytesIO
            import textwrap

            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Center alignment
            )

            story = []

            # Title page
            story.append(Paragraph(report_title, title_style))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"Total Papers Analyzed: {len(papers)}", styles['Normal']))
            story.append(PageBreak())

            # Executive Summary
            story.append(Paragraph("Executive Summary", styles['Heading1']))
            story.append(Spacer(1, 12))

            summary_text = f"""
            This report presents a comprehensive analysis of {len(papers)} research papers.
            The analysis includes individual paper assessments, identification of research gaps,
            and strategic research scope recommendations.
            """
            story.append(Paragraph(summary_text, styles['Normal']))
            story.append(Spacer(1, 20))

            # Papers Overview
            story.append(Paragraph("Papers Overview", styles['Heading1']))
            story.append(Spacer(1, 12))

            for i, paper in enumerate(papers, 1):
                story.append(Paragraph(f"{i}. {paper.title}", styles['Heading3']))
                story.append(Paragraph(f"Authors: {', '.join(paper.authors)}", styles['Normal']))
                story.append(Paragraph(f"Source: {paper.source} | Published: {paper.published}", styles['Normal']))
                story.append(Spacer(1, 10))

            story.append(PageBreak())

            # Individual Paper Analyses
            story.append(Paragraph("Individual Paper Analyses", styles['Heading1']))
            story.append(Spacer(1, 12))

            for paper, analysis in zip(papers, analyses):
                story.append(Paragraph(f"Analysis: {paper.title}", styles['Heading2']))
                story.append(Spacer(1, 8))

                story.append(Paragraph("Summary:", styles['Heading3']))
                story.append(Paragraph(analysis.summary, styles['Normal']))
                story.append(Spacer(1, 8))

                if analysis.key_contributions:
                    story.append(Paragraph("Key Contributions:", styles['Heading3']))
                    for contrib in analysis.key_contributions:
                        story.append(Paragraph(f"• {contrib}", styles['Normal']))
                    story.append(Spacer(1, 8))

                if analysis.strengths:
                    story.append(Paragraph("Strengths:", styles['Heading3']))
                    for strength in analysis.strengths:
                        story.append(Paragraph(f"• {strength}", styles['Normal']))
                    story.append(Spacer(1, 8))

                story.append(Spacer(1, 15))

            story.append(PageBreak())

            # Research Gaps
            story.append(Paragraph("Research Gaps Analysis", styles['Heading1']))
            story.append(Spacer(1, 12))

            if research_gaps.get('current_trends'):
                story.append(Paragraph("Current Research Trends:", styles['Heading2']))
                for trend in research_gaps['current_trends']:
                    story.append(Paragraph(f"• {trend}", styles['Normal']))
                story.append(Spacer(1, 12))

            if research_gaps.get('research_gaps'):
                story.append(Paragraph("Identified Research Gaps:", styles['Heading2']))
                for gap in research_gaps['research_gaps']:
                    if isinstance(gap, dict):
                        story.append(Paragraph(f"• {gap.get('gap', 'Unknown gap')}: {gap.get('description', 'No description')}", styles['Normal']))
                    else:
                        story.append(Paragraph(f"• {gap}", styles['Normal']))
                story.append(Spacer(1, 12))

            story.append(PageBreak())

            # Research Scope
            if research_scope:
                story.append(Paragraph("Research Scope & Recommendations", styles['Heading1']))
                story.append(Spacer(1, 12))

                if research_scope.get('research_objectives'):
                    story.append(Paragraph("Research Objectives:", styles['Heading2']))
                    for obj in research_scope['research_objectives']:
                        if isinstance(obj, dict):
                            story.append(Paragraph(f"• {obj.get('objective', 'Unknown objective')}: {obj.get('description', 'No description')}", styles['Normal']))
                        else:
                            story.append(Paragraph(f"• {obj}", styles['Normal']))
                    story.append(Spacer(1, 12))

            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer.getvalue()

        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            # Return a simple error PDF
            buffer = BytesIO()
            try:
                from reportlab.platypus import SimpleDocTemplate, Paragraph
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib.pagesizes import A4

                doc = SimpleDocTemplate(buffer, pagesize=A4)
                styles = getSampleStyleSheet()
                story = [
                    Paragraph("PDF Generation Error", styles['Title']),
                    Paragraph(f"Error: {str(e)}", styles['Normal'])
                ]
                doc.build(story)
                buffer.seek(0)
                return buffer.getvalue()
            except:
                return b"PDF generation failed"