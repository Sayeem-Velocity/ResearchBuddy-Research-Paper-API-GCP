# app/services/paper_search/google_scholar.py
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import hashlib
import os
import json
from app.core.config import settings
from app.models.paper import Paper, PaperSource

logger = logging.getLogger(__name__)

# Import SERP API
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False
    logger.warning("SERP API client not installed. Google Scholar will use mock results.")

class GoogleScholarSearcher:
    """Google Scholar search with per-user daily rate limiting"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.serp_api_key
        self.rate_limit_file = ".scholar_usage.json"
        self.daily_limit_per_user = 1  # Limit to 1 search per user per day

    def _check_rate_limit(self, user_id: str) -> bool:
        """Check if user has exceeded daily rate limit"""
        try:
            if not os.path.exists(self.rate_limit_file):
                return True

            with open(self.rate_limit_file, 'r') as f:
                data = json.load(f)

            today_str = datetime.now().date().isoformat()
            user_data = data.get(user_id, {})

            # Check if user has searched today
            last_search_date = user_data.get('last_search_date', '')
            usage_count = user_data.get('usage_count', 0)

            # Reset if it's a new day
            if last_search_date != today_str:
                return True

            # Check if user has exceeded their daily limit
            return usage_count < self.daily_limit_per_user

        except Exception as e:
            logger.warning(f"Error checking rate limit for user {user_id}: {e}")
            return True

    def _update_rate_limit(self, user_id: str):
        """Update rate limit usage for specific user"""
        try:
            data = {}
            if os.path.exists(self.rate_limit_file):
                with open(self.rate_limit_file, 'r') as f:
                    data = json.load(f)

            today_str = datetime.now().date().isoformat()

            # Initialize or update user data
            if user_id not in data:
                data[user_id] = {}

            user_data = data[user_id]
            last_search_date = user_data.get('last_search_date', '')

            # Reset if new day
            if last_search_date != today_str:
                data[user_id] = {
                    'usage_count': 1,
                    'last_search_date': today_str,
                    'last_search_time': datetime.now().isoformat()
                }
            else:
                data[user_id]['usage_count'] = user_data.get('usage_count', 0) + 1
                data[user_id]['last_search_time'] = datetime.now().isoformat()

            with open(self.rate_limit_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.warning(f"Error updating rate limit for user {user_id}: {e}")

    async def search(self, query: str, max_results: int = 10, date_range: Optional[Dict] = None, user_id: str = "default") -> List[Paper]:
        """Search Google Scholar for papers with per-user rate limiting"""
        try:
            # Check user's rate limit first
            if not self._check_rate_limit(user_id):
                logger.warning(f"Google Scholar daily rate limit exceeded for user {user_id}")
                return []

            # If no API key or SERP API not available, return mock results
            if not self.api_key or not SERPAPI_AVAILABLE:
                logger.warning("No SERP API key available or SERP API not installed. Using mock results.")
                return self._mock_scholar_results(query, max_results)

            # Update rate limit counter
            self._update_rate_limit(user_id)

            # Perform real search using SERP API
            logger.info(f"Google Scholar search for user {user_id}: '{query}' (max: {max_results})")

            loop = asyncio.get_event_loop()
            papers = await loop.run_in_executor(
                None,
                self._search_sync,
                query,
                max_results,
                date_range
            )

            logger.info(f"Found {len(papers)} papers from Google Scholar for user {user_id}")
            return papers

        except Exception as e:
            logger.error(f"Error searching Google Scholar for user {user_id}: {e}")
            return []

    def _mock_scholar_results(self, query: str, max_results: int) -> List[Paper]:
        """Create mock Google Scholar results for testing"""
        papers = []
        for i in range(min(max_results, 3)):  # Return max 3 mock results
            paper_id = hashlib.md5(f"scholar_mock_{query}_{i}".encode()).hexdigest()
            papers.append(Paper(
                id=paper_id,
                title=f"Mock Google Scholar Paper {i+1} for '{query}'",
                abstract=f"This is a mock abstract for paper {i+1} from Google Scholar search. "
                         f"It contains relevant information about {query}.",
                authors=[f"Author {i+1}A", f"Author {i+1}B"],
                published=f"202{3-i}-01-01T00:00:00Z",
                pdf_url=f"https://example.com/paper{i+1}.pdf",
                source=PaperSource.GOOGLE_SCHOLAR,
                doi=f"10.1000/mock.scholar.{i+1}",
                citation_count=50 - (i * 10),
                venue=f"Mock Journal {i+1}",
                keywords=[f"keyword{i+1}", query.split()[0] if query.split() else "research"],
                is_open_access=True
            ))
        return papers

    def _search_sync(self, query: str, max_results: int, date_range: Optional[Dict] = None) -> List[Paper]:
        """Synchronous Google Scholar search"""
        papers = []

        try:
            # Build search parameters
            params = {
                "engine": "google_scholar",
                "q": query,
                "num": min(max_results, 20),  # Google Scholar limits to 20 per request
                "api_key": self.api_key,
                "hl": "en",
                "start": 0
            }

            # Add date range if provided
            if date_range:
                if date_range.get('start'):
                    params['as_ylo'] = date_range['start'][:4]  # Year from YYYY-MM-DD
                if date_range.get('end'):
                    params['as_yhi'] = date_range['end'][:4]

            # Perform search
            search = GoogleSearch(params)
            results = search.get_dict()

            if "organic_results" not in results:
                logger.warning("No organic results found in Google Scholar response")
                return papers

            # Process results
            for result in results["organic_results"]:
                try:
                    paper = self._parse_scholar_result(result)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing Google Scholar result: {e}")
                    continue

            logger.info(f"Found {len(papers)} papers from Google Scholar")
            return papers

        except Exception as e:
            logger.error(f"Google Scholar search failed: {e}")
            return papers

    def _parse_scholar_result(self, result: Dict) -> Optional[Paper]:
        """Parse a single Google Scholar result into a Paper object"""
        try:
            # Generate a unique ID based on title and source
            title = result.get("title", "")
            if not title:
                return None

            paper_id = hashlib.md5(f"scholar_{title}".encode()).hexdigest()

            # Extract authors
            authors = []
            if "publication_info" in result and "authors" in result["publication_info"]:
                authors = [author["name"] for author in result["publication_info"]["authors"]]

            # Extract publication info
            publication_info = result.get("publication_info", {})
            published_date = self._extract_publication_date(publication_info)

            # Extract PDF link
            pdf_url = None
            if "resources" in result:
                for resource in result["resources"]:
                    if resource.get("file_format") == "PDF":
                        pdf_url = resource.get("link")
                        break

            # Extract citation count
            citation_count = None
            if "inline_links" in result and "cited_by" in result["inline_links"]:
                cited_by = result["inline_links"]["cited_by"]
                if "total" in cited_by:
                    citation_count = cited_by["total"]

            # Extract venue information
            venue = publication_info.get("summary", "")

            return Paper(
                id=paper_id,
                title=title,
                abstract=result.get("snippet", ""),
                authors=authors,
                published=published_date,
                pdf_url=pdf_url,
                source=PaperSource.GOOGLE_SCHOLAR,
                doi=self._extract_doi(result.get("link", "")),
                citation_count=citation_count,
                venue=venue,
                keywords=[],
                is_open_access=pdf_url is not None  # Mark as open access if PDF is available
            )

        except Exception as e:
            logger.warning(f"Error parsing Google Scholar result: {e}")
            return None

    def _extract_publication_date(self, publication_info: Dict) -> str:
        """Extract publication date from publication info"""
        # Try to extract year from publication info
        summary = publication_info.get("summary", "")

        # Look for year pattern in summary (e.g., "2023", "2022")
        import re
        year_match = re.search(r'\b(20\d{2}|19\d{2})\b', summary)

        if year_match:
            year = year_match.group(1)
            return f"{year}-01-01T00:00:00Z"

        # Default to current year if no date found
        current_year = datetime.now().year
        return f"{current_year}-01-01T00:00:00Z"

    def _extract_doi(self, link: str) -> Optional[str]:
        """Extract DOI from link if possible"""
        if not link:
            return None

        # Check if link contains DOI pattern
        import re
        doi_match = re.search(r'doi\.org/(.+)', link)
        if doi_match:
            return doi_match.group(1)

        # Check for DOI in the URL parameters
        doi_match = re.search(r'doi[=/]([^&\s]+)', link, re.IGNORECASE)
        if doi_match:
            return doi_match.group(1)

        return None

    async def search_with_pagination(self, query: str, max_results: int = 50) -> List[Paper]:
        """Search with pagination to get more results"""
        all_papers = []
        start = 0
        results_per_page = 20  # Google Scholar limit

        while len(all_papers) < max_results and start < 100:  # Limit to 100 to avoid excessive requests
            try:
                loop = asyncio.get_event_loop()
                papers = await loop.run_in_executor(
                    None,
                    self._search_page_sync,
                    query,
                    start,
                    min(results_per_page, max_results - len(all_papers))
                )

                if not papers:
                    break

                all_papers.extend(papers)
                start += results_per_page

                # Add small delay to be respectful to the API
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in paginated search: {e}")
                break

        return all_papers[:max_results]

    def _search_page_sync(self, query: str, start: int, num_results: int) -> List[Paper]:
        """Search a specific page of results"""
        params = {
            "engine": "google_scholar",
            "q": query,
            "num": num_results,
            "start": start,
            "api_key": self.api_key,
            "hl": "en"
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        papers = []
        if "organic_results" in results:
            for result in results["organic_results"]:
                try:
                    paper = self._parse_scholar_result(result)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing result: {e}")
                    continue

        return papers