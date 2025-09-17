# app/services/paper_search/pubmed_search.py
import asyncio
import logging
import aiohttp
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from app.models.paper import Paper, PaperSource
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class PubMedSearcher:
    """PubMed search using E-utilities API"""

    def __init__(self):
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.search_url = f"{self.base_url}esearch.fcgi"
        self.fetch_url = f"{self.base_url}efetch.fcgi"
        self.summary_url = f"{self.base_url}esummary.fcgi"

    async def search(self, query: str, max_results: int = 10, date_range: Optional[Dict] = None) -> List[Paper]:
        """Search PubMed for papers"""
        try:
            # Step 1: Search for PMIDs
            pmids = await self._search_pmids(query, max_results, date_range)
            if not pmids:
                logger.info("No PMIDs found for query")
                return []

            # Step 2: Fetch paper details
            papers = await self._fetch_paper_details(pmids)
            logger.info(f"Found {len(papers)} papers from PubMed")
            return papers

        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []

    async def _search_pmids(self, query: str, max_results: int, date_range: Optional[Dict] = None) -> List[str]:
        """Search for PubMed IDs (PMIDs)"""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance",
            "tool": "research_paper_api",
            "email": "research@example.com"  # Required by NCBI
        }

        # Add date range if provided
        if date_range:
            date_filter = self._build_date_filter(date_range)
            if date_filter:
                params["term"] = f"({query}) AND {date_filter}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        pmids = data.get("esearchresult", {}).get("idlist", [])
                        return pmids
                    else:
                        logger.error(f"PubMed search failed with status: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Error searching PMIDs: {e}")
            return []

    async def _fetch_paper_details(self, pmids: List[str]) -> List[Paper]:
        """Fetch detailed information for PMIDs"""
        if not pmids:
            return []

        # Split PMIDs into chunks to avoid overwhelming the API
        chunk_size = 200  # PubMed recommended batch size
        all_papers = []

        for i in range(0, len(pmids), chunk_size):
            chunk_pmids = pmids[i:i + chunk_size]
            papers = await self._fetch_chunk_details(chunk_pmids)
            all_papers.extend(papers)

            # Add small delay between requests
            if i + chunk_size < len(pmids):
                await asyncio.sleep(0.5)

        return all_papers

    async def _fetch_chunk_details(self, pmids: List[str]) -> List[Paper]:
        """Fetch details for a chunk of PMIDs"""
        pmid_string = ",".join(pmids)

        params = {
            "db": "pubmed",
            "id": pmid_string,
            "retmode": "xml",
            "rettype": "abstract",
            "tool": "research_paper_api",
            "email": "research@example.com"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.fetch_url, params=params) as response:
                    if response.status == 200:
                        xml_content = await response.text()
                        return self._parse_pubmed_xml(xml_content)
                    else:
                        logger.error(f"PubMed fetch failed with status: {response.status}")
                        return []

        except Exception as e:
            logger.error(f"Error fetching PubMed details: {e}")
            return []

    def _parse_pubmed_xml(self, xml_content: str) -> List[Paper]:
        """Parse PubMed XML response into Paper objects"""
        papers = []

        try:
            root = ET.fromstring(xml_content)

            for article in root.findall(".//PubmedArticle"):
                try:
                    paper = self._parse_single_article(article)
                    if paper:
                        papers.append(paper)
                except Exception as e:
                    logger.warning(f"Error parsing PubMed article: {e}")
                    continue

        except ET.ParseError as e:
            logger.error(f"Error parsing PubMed XML: {e}")

        return papers

    def _parse_single_article(self, article_element) -> Optional[Paper]:
        """Parse a single PubMed article element"""
        try:
            # Extract PMID
            pmid_elem = article_element.find(".//PMID")
            pmid = pmid_elem.text if pmid_elem is not None else ""

            # Extract title
            title_elem = article_element.find(".//ArticleTitle")
            title = title_elem.text if title_elem is not None else ""

            if not title:
                return None

            # Generate paper ID
            paper_id = f"pubmed_{pmid}" if pmid else hashlib.md5(f"pubmed_{title}".encode()).hexdigest()

            # Extract abstract
            abstract_parts = []
            abstract_elems = article_element.findall(".//AbstractText")
            for abstract_elem in abstract_elems:
                if abstract_elem.text:
                    # Include label if available
                    label = abstract_elem.get("Label", "")
                    text = abstract_elem.text
                    if label:
                        abstract_parts.append(f"{label}: {text}")
                    else:
                        abstract_parts.append(text)

            abstract = " ".join(abstract_parts) if abstract_parts else ""

            # Extract authors
            authors = []
            author_elems = article_element.findall(".//Author")
            for author_elem in author_elems:
                last_name = author_elem.find("LastName")
                first_name = author_elem.find("ForeName")

                if last_name is not None and first_name is not None:
                    full_name = f"{first_name.text} {last_name.text}"
                    authors.append(full_name)
                elif last_name is not None:
                    authors.append(last_name.text)

            # Extract publication date
            pub_date = self._extract_publication_date(article_element)

            # Extract DOI
            doi = self._extract_doi(article_element)

            # Extract journal information
            journal_elem = article_element.find(".//Journal/Title")
            venue = journal_elem.text if journal_elem is not None else ""

            # Construct PDF URL (PubMed Central if available)
            pdf_url = None
            if pmid:
                # Try to construct PMC URL (not all papers have free PDFs)
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmid}/pdf/"

            # Extract keywords/MeSH terms
            keywords = []
            mesh_elems = article_element.findall(".//MeshHeading/DescriptorName")
            for mesh_elem in mesh_elems:
                if mesh_elem.text:
                    keywords.append(mesh_elem.text)

            return Paper(
                id=paper_id,
                title=title,
                abstract=abstract,
                authors=authors,
                published=pub_date,
                pdf_url=pdf_url,
                source=PaperSource.PUBMED,
                doi=doi,
                citation_count=None,  # PubMed doesn't provide citation counts
                venue=venue,
                keywords=keywords
            )

        except Exception as e:
            logger.warning(f"Error parsing single PubMed article: {e}")
            return None

    def _extract_publication_date(self, article_element) -> str:
        """Extract publication date from article element"""
        # Try different date elements
        date_elements = [
            ".//PubDate",
            ".//ArticleDate",
            ".//DateCompleted"
        ]

        for date_path in date_elements:
            date_elem = article_element.find(date_path)
            if date_elem is not None:
                year_elem = date_elem.find("Year")
                month_elem = date_elem.find("Month")
                day_elem = date_elem.find("Day")

                year = year_elem.text if year_elem is not None else datetime.now().year
                month = month_elem.text if month_elem is not None else "01"
                day = day_elem.text if day_elem is not None else "01"

                # Handle month names
                month_map = {
                    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04",
                    "May": "05", "Jun": "06", "Jul": "07", "Aug": "08",
                    "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"
                }

                if month in month_map:
                    month = month_map[month]

                try:
                    # Ensure month and day are zero-padded
                    month = f"{int(month):02d}" if month.isdigit() else "01"
                    day = f"{int(day):02d}" if day.isdigit() else "01"
                    return f"{year}-{month}-{day}T00:00:00Z"
                except ValueError:
                    continue

        # Default to current year if no date found
        current_year = datetime.now().year
        return f"{current_year}-01-01T00:00:00Z"

    def _extract_doi(self, article_element) -> Optional[str]:
        """Extract DOI from article element"""
        # Look for DOI in article IDs
        article_id_elems = article_element.findall(".//ArticleId")
        for id_elem in article_id_elems:
            if id_elem.get("IdType") == "doi":
                return id_elem.text

        return None

    def _build_date_filter(self, date_range: Dict) -> Optional[str]:
        """Build date filter for PubMed query"""
        try:
            filters = []

            if date_range.get('start'):
                start_date = date_range['start']
                # Convert YYYY-MM-DD to YYYY/MM/DD for PubMed
                start_formatted = start_date.replace('-', '/')
                filters.append(f"{start_formatted}[PDAT]:")

            if date_range.get('end'):
                end_date = date_range['end']
                end_formatted = end_date.replace('-', '/')

                if filters:
                    # Modify the last filter to include end date
                    filters[-1] = filters[-1].replace(':', f":{end_formatted}")
                else:
                    filters.append(f":{end_formatted}[PDAT]")

            return filters[0] if filters else None

        except Exception as e:
            logger.warning(f"Error building date filter: {e}")
            return None