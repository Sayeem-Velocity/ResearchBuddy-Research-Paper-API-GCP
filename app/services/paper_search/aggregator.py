# app/services/paper_search/aggregator.py
import asyncio
import logging
from typing import List, Dict, Optional, Set
from collections import defaultdict
import hashlib

from app.models.paper import Paper, PaperSource, SortBy
from app.services.paper_search.arxiv_search import ArxivSearcher
from app.services.paper_search.google_scholar import GoogleScholarSearcher
from app.services.paper_search.pubmed_search import PubMedSearcher

logger = logging.getLogger(__name__)

class PaperSearchAggregator:
    """Aggregates search results from multiple paper sources"""

    def __init__(self):
        self.sources = {
            PaperSource.ARXIV: ArxivSearcher(),
            PaperSource.GOOGLE_SCHOLAR: GoogleScholarSearcher(),
            PaperSource.PUBMED: PubMedSearcher()
            # IEEE removed - not implementing for now
        }

    async def search_all_sources(
        self,
        query: str,
        sources: List[PaperSource],
        max_results: int = 20,
        date_range: Optional[Dict] = None,
        sort_by: SortBy = SortBy.RELEVANCE,
        user_id: str = "default"
    ) -> List[Paper]:
        """
        Search across multiple sources and return aggregated results
        """
        try:
            logger.info(f"Starting search across {len(sources)} sources: {sources}")

            # Calculate results per source
            results_per_source = max(1, max_results // len(sources))

            # Create search tasks for each source
            tasks = []
            source_names = []

            for source in sources:
                if source in self.sources:
                    searcher = self.sources[source]
                    task = asyncio.create_task(
                        self._safe_search(searcher, query, results_per_source, date_range, user_id),
                        name=f"search_{source.value}"
                    )
                    tasks.append(task)
                    source_names.append(source.value)
                else:
                    logger.warning(f"Unknown source: {source}")

            if not tasks:
                logger.warning("No valid sources provided")
                return []

            # Execute all searches concurrently
            logger.info(f"Executing {len(tasks)} search tasks concurrently")
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            all_papers = []
            for i, result in enumerate(results):
                source_name = source_names[i]

                if isinstance(result, Exception):
                    logger.error(f"Search failed for {source_name}: {result}")
                    continue

                if isinstance(result, list):
                    logger.info(f"Found {len(result)} papers from {source_name}")
                    all_papers.extend(result)
                else:
                    logger.warning(f"Unexpected result type from {source_name}: {type(result)}")

            # Remove duplicates and sort
            unique_papers = self._deduplicate_papers(all_papers)
            sorted_papers = self._sort_papers(unique_papers, sort_by)

            # Limit to requested number of results
            final_results = sorted_papers[:max_results]

            logger.info(f"Returning {len(final_results)} unique papers (from {len(all_papers)} total)")
            return final_results

        except Exception as e:
            logger.error(f"Error in aggregated search: {e}")
            return []

    async def _safe_search(
        self,
        searcher,
        query: str,
        max_results: int,
        date_range: Optional[Dict],
        user_id: str = "default"
    ) -> List[Paper]:
        """
        Safely execute a search with error handling
        """
        try:
            # Check if searcher supports user_id parameter (Google Scholar)
            if hasattr(searcher, '__class__') and 'GoogleScholarSearcher' in searcher.__class__.__name__:
                return await searcher.search(query, max_results, date_range, user_id)
            else:
                return await searcher.search(query, max_results, date_range)
        except Exception as e:
            logger.error(f"Search failed for {searcher.__class__.__name__}: {e}")
            return []

    def _deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        """
        Remove duplicate papers based on title similarity and DOI
        """
        if not papers:
            return []

        seen_dois: Set[str] = set()
        seen_titles: Set[str] = set()
        unique_papers: List[Paper] = []

        for paper in papers:
            # Skip if we've seen this DOI before
            if paper.doi and paper.doi in seen_dois:
                logger.debug(f"Skipping duplicate DOI: {paper.doi}")
                continue

            # Create a normalized title for comparison
            normalized_title = self._normalize_title(paper.title)

            # Skip if we've seen a very similar title
            if self._is_similar_title(normalized_title, seen_titles):
                logger.debug(f"Skipping similar title: {paper.title[:50]}...")
                continue

            # This is a unique paper
            unique_papers.append(paper)

            if paper.doi:
                seen_dois.add(paper.doi)

            seen_titles.add(normalized_title)

        logger.info(f"Deduplicated {len(papers)} papers to {len(unique_papers)} unique papers")
        return unique_papers

    def _normalize_title(self, title: str) -> str:
        """
        Normalize title for comparison
        """
        if not title:
            return ""

        # Convert to lowercase and remove special characters
        import re
        normalized = re.sub(r'[^\w\s]', '', title.lower())

        # Remove extra whitespace
        normalized = ' '.join(normalized.split())

        return normalized

    def _is_similar_title(self, title: str, seen_titles: Set[str]) -> bool:
        """
        Check if title is similar to any seen titles
        """
        if not title:
            return False

        for seen_title in seen_titles:
            if self._calculate_title_similarity(title, seen_title) > 0.85:
                return True

        return False

    def _calculate_title_similarity(self, title1: str, title2: str) -> float:
        """
        Calculate similarity between two titles using simple ratio
        """
        if not title1 or not title2:
            return 0.0

        # Simple similarity based on common words
        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _sort_papers(self, papers: List[Paper], sort_by: SortBy) -> List[Paper]:
        """
        Sort papers based on the specified criteria
        """
        if not papers:
            return papers

        try:
            if sort_by == SortBy.RECENT:
                # Sort by publication date (newest first)
                return sorted(
                    papers,
                    key=lambda p: p.published,
                    reverse=True
                )

            elif sort_by == SortBy.CITED:
                # Sort by citation count (highest first)
                # Papers without citation count go to the end
                def citation_key(paper):
                    return (
                        paper.citation_count if paper.citation_count is not None else -1,
                        paper.published  # Secondary sort by date
                    )

                return sorted(
                    papers,
                    key=citation_key,
                    reverse=True
                )

            else:  # SortBy.RELEVANCE (default)
                # For relevance, maintain the order from search engines
                # but group by source to ensure diversity
                return self._sort_by_relevance_with_diversity(papers)

        except Exception as e:
            logger.error(f"Error sorting papers: {e}")
            return papers

    def _sort_by_relevance_with_diversity(self, papers: List[Paper]) -> List[Paper]:
        """
        Sort by relevance while ensuring source diversity
        """
        # Group papers by source
        source_groups = defaultdict(list)
        for paper in papers:
            source_groups[paper.source].append(paper)

        # Interleave papers from different sources
        sorted_papers = []
        max_length = max(len(group) for group in source_groups.values()) if source_groups else 0

        for i in range(max_length):
            for source, group in source_groups.items():
                if i < len(group):
                    sorted_papers.append(group[i])

        return sorted_papers

    async def get_source_status(self) -> Dict[str, bool]:
        """
        Check the status of all configured sources
        """
        status = {}

        for source_name, searcher in self.sources.items():
            try:
                # Try a simple search to check if the source is working
                test_results = await self._safe_search(searcher, "test", 1, None)
                status[source_name.value] = True
                logger.info(f"Source {source_name.value} is working")

            except Exception as e:
                status[source_name.value] = False
                logger.warning(f"Source {source_name.value} is not working: {e}")

        return status

    def get_available_sources(self) -> List[PaperSource]:
        """
        Get list of available sources
        """
        return list(self.sources.keys())

    async def search_single_source(
        self,
        source: PaperSource,
        query: str,
        max_results: int = 20,
        date_range: Optional[Dict] = None
    ) -> List[Paper]:
        """
        Search a single source
        """
        if source not in self.sources:
            raise ValueError(f"Unknown source: {source}")

        searcher = self.sources[source]
        return await self._safe_search(searcher, query, max_results, date_range)