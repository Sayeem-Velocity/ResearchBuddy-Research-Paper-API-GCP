# app/services/paper_search/ieee_search.py
import asyncio
import logging
import aiohttp
from typing import List, Dict, Optional
from app.core.config import settings
from app.models.paper import Paper, PaperSource
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class IEEESearcher:
    """IEEE Xplore search using IEEE API"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ieee_api_key
        self.base_url = "https://ieeexploreapi.ieee.org/api/v1/search/articles"

    async def search(self, query: str, max_results: int = 10, date_range: Optional[Dict] = None) -> List[Paper]:
        """Search IEEE Xplore for papers - Currently in pass mode"""
        logger.info("IEEE search is currently disabled (pass mode)")
        return []

    async def _execute_search(self, params: Dict) -> List[Paper]:
        """Execute the IEEE search request"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_ieee_response(data)
                    elif response.status == 429:
                        logger.warning("IEEE API rate limit exceeded")
                        return []
                    else:
                        logger.error(f"IEEE search failed with status: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Error executing IEEE search: {e}")
            return []

    def _parse_ieee_response(self, data: Dict) -> List[Paper]:
        """Parse IEEE API response into Paper objects"""
        papers = []

        try:
            articles = data.get("articles", [])

            for article in articles:
                try:
                    paper = self._parse_single_article(article)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing IEEE article: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error parsing IEEE response: {e}")

        return papers

    def _parse_single_article(self, article: Dict) -> Optional[Paper]:
        """Parse a single IEEE article into a Paper object"""
        try:
            # Extract basic information
            title = article.get("title", "").strip()
            if not title:
                return None

            # Generate paper ID
            ieee_id = article.get("article_number", "")
            paper_id = f"ieee_{ieee_id}" if ieee_id else hashlib.md5(f"ieee_{title}".encode()).hexdigest()

            # Extract abstract
            abstract = article.get("abstract", "").strip()

            # Extract authors
            authors = []
            authors_data = article.get("authors", {})
            if "authors" in authors_data:
                for author in authors_data["authors"]:
                    if isinstance(author, dict):
                        full_name = author.get("full_name", "")
                        if full_name:
                            authors.append(full_name)
                    elif isinstance(author, str):
                        authors.append(author)

            # Extract publication date
            pub_date = self._extract_publication_date(article)

            # Extract DOI
            doi = article.get("doi", "")

            # Extract venue information
            venue_parts = []
            if article.get("publication_title"):
                venue_parts.append(article["publication_title"])
            if article.get("conference_location"):
                venue_parts.append(article["conference_location"])

            venue = ", ".join(venue_parts) if venue_parts else ""

            # Construct PDF URL
            pdf_url = None
            if article.get("pdf_url"):
                pdf_url = article["pdf_url"]
            elif ieee_id:
                pdf_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber={ieee_id}"

            # Extract keywords
            keywords = []
            if article.get("index_terms"):
                index_terms = article["index_terms"]
                if isinstance(index_terms, dict):
                    # Extract IEEE terms, author keywords, etc.
                    for term_type in ["ieee_terms", "author_terms"]:
                        terms = index_terms.get(term_type, {}).get("terms", [])
                        keywords.extend(terms)
                elif isinstance(index_terms, list):
                    keywords.extend(index_terms)

            # Extract citation count if available
            citation_count = article.get("citing_paper_count")

            return Paper(
                id=paper_id,
                title=title,
                abstract=abstract,
                authors=authors,
                published=pub_date,
                pdf_url=pdf_url,
                source=PaperSource.IEEE,
                doi=doi,
                citation_count=citation_count,
                venue=venue,
                keywords=keywords
            )

        except Exception as e:
            logger.warning(f"Error parsing single IEEE article: {e}")
            return None

    def _extract_publication_date(self, article: Dict) -> str:
        """Extract publication date from IEEE article"""
        try:
            # Try different date fields
            date_fields = [
                "publication_date",
                "publication_year",
                "conference_dates",
                "insert_date"
            ]

            for field in date_fields:
                if field in article and article[field]:
                    date_str = str(article[field])

                    # Handle different date formats
                    if field == "publication_year" and date_str.isdigit():
                        return f"{date_str}-01-01T00:00:00Z"

                    # Try to parse full date
                    if len(date_str) >= 4:
                        year = date_str[:4]
                        if year.isdigit():
                            # Extract month if available
                            if len(date_str) >= 7 and date_str[4] in ['-', '/']:
                                month = date_str[5:7]
                                if month.isdigit() and 1 <= int(month) <= 12:
                                    return f"{year}-{month}-01T00:00:00Z"

                            return f"{year}-01-01T00:00:00Z"

        except Exception as e:
            logger.warning(f"Error extracting IEEE publication date: {e}")

        # Default to current year
        current_year = datetime.now().year
        return f"{current_year}-01-01T00:00:00Z"

    def _build_date_filter(self, date_range: Dict) -> Optional[str]:
        """Build date filter for IEEE query"""
        try:
            filters = []

            if date_range.get('start'):
                start_year = date_range['start'][:4]  # Extract year from YYYY-MM-DD
                filters.append(f"publication_year:{start_year}")

            if date_range.get('end'):
                end_year = date_range['end'][:4]
                if filters:
                    # Modify to range if we have both start and end
                    start_year = date_range['start'][:4]
                    if start_year != end_year:
                        filters = [f"publication_year:[{start_year} TO {end_year}]"]
                else:
                    filters.append(f"publication_year:{end_year}")

            return " AND ".join(filters) if filters else None

        except Exception as e:
            logger.warning(f"Error building IEEE date filter: {e}")
            return None

    async def search_with_pagination(self, query: str, max_results: int = 100) -> List[Paper]:
        """Search with pagination to get more results"""
        if not self.api_key:
            logger.warning("IEEE API key not configured")
            return []

        all_papers = []
        page_size = 25  # IEEE recommended page size
        start_record = 1

        while len(all_papers) < max_results and start_record <= 200:  # IEEE limit
            try:
                params = {
                    "apikey": self.api_key,
                    "querytext": query,
                    "max_records": min(page_size, max_results - len(all_papers)),
                    "start_record": start_record,
                    "sort_field": "publication_year",
                    "sort_order": "desc",
                    "format": "json"
                }

                papers = await self._execute_search(params)

                if not papers:
                    break

                all_papers.extend(papers)
                start_record += page_size

                # Add delay between requests
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in IEEE paginated search: {e}")
                break

        return all_papers[:max_results]