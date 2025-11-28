# app/services/paper_search/arxiv_search.py
import arxiv
import logging
import random
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
from app.models.paper import Paper, PaperSource

logger = logging.getLogger(__name__)

class ArxivSearcher:
    """Search service for arXiv papers"""

    def __init__(self):
        self.client = arxiv.Client()

    async def search(
        self,
        query: str,
        max_results: int = 10,
        date_range: Optional[Dict] = None
    ) -> List[Paper]:
        """Search arXiv for papers"""
        try:
            logger.info(f"Searching arXiv for: '{query}', max_results: {max_results}")

            # Run in executor to make it async
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                self._search_sync,
                query,
                max_results,
                date_range
            )

            logger.info(f"Found {len(results)} papers from arXiv")
            return results

        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []

    def _search_sync(self, query: str, max_results: int, date_range: Optional[Dict] = None) -> List[Paper]:
        """Synchronous search implementation"""
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []
        for result in self.client.results(search):
            try:
                
                # Check date filter if provided
                if date_range:
                    paper_date = result.published.date()
                    if date_range.get('start') and paper_date < datetime.fromisoformat(date_range['start']).date():
                        continue
                    if date_range.get('end') and paper_date > datetime.fromisoformat(date_range['end']).date():
                        continue

                paper = Paper(
                    id=result.entry_id,
                    title=result.title.strip(),
                    abstract=result.summary.strip().replace('\n', ' '),
                    authors=[author.name for author in result.authors],
                    published=result.published.isoformat(),
                    pdf_url=result.pdf_url,
                    source=PaperSource.ARXIV,
                    doi=None,  # arXiv doesn't have DOIs
                    citation_count=None,  # Not available from arXiv API
                    venue="arXiv",
                    keywords=result.categories,
                    is_open_access=True  # arXiv is always open access
                )

                papers.append(paper)

            except Exception as e:
                logger.warning(f"Error processing arXiv result: {e}")
                continue

        return papers