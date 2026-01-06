"""
Document Crawler Service
Fetches content from various documentation sources (Confluence, README, etc.)
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse
import time


class DocumentCrawler:
    """Crawl and extract text from documentation sources"""
    
    def __init__(self, confluence_token: Optional[str] = None, confluence_email: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AG-Tools-Catalogue-Bot/1.0'
        })
        self.timeout = 30
        
        # Confluence authentication
        self.confluence_token = confluence_token
        self.confluence_email = confluence_email
        if confluence_token and confluence_email:
            # Use API token authentication
            self.session.auth = (confluence_email, confluence_token)
    
    def fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch content from URL and extract text
        
        Args:
            url: URL to fetch
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Detect document type by URL or content-type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'confluence' in url.lower():
                return self._extract_confluence(response.text)
            elif any(ext in url.lower() for ext in ['.md', 'readme']):
                return self._extract_markdown(response.text)
            elif 'text/html' in content_type:
                return self._extract_html(response.text)
            elif 'text/plain' in content_type or 'text/markdown' in content_type:
                return response.text
            else:
                # Try HTML extraction as fallback
                return self._extract_html(response.text)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error processing {url}: {e}")
            return None
    
    def _extract_confluence(self, html: str) -> str:
        """
        Extract main content from Confluence page
        
        Confluence pages have specific structure:
        - Main content in #main-content or .wiki-content
        - Sidebar and navigation should be excluded
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check if we hit a login page
        if any(phrase in html.lower() for phrase in ['login', 'sign in', 'enter your credentials']):
            print("⚠️  Warning: Detected login page - authentication required")
            return ""
        
        # Try different Confluence content selectors
        content_selectors = [
            '#main-content',
            '.wiki-content',
            '[id="content"]',
            '.page-content'
        ]
        
        main_content = None
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            # Fallback to body
            main_content = soup.find('body')
        
        if main_content:
            # Remove unwanted elements
            for element in main_content.select('script, style, nav, header, footer, .sidebar, .navigation'):
                element.decompose()
            
            # Extract text with proper spacing
            text = main_content.get_text(separator=' ', strip=True)
            
            # Clean up excessive whitespace
            text = ' '.join(text.split())
            
            return text
        
        return ""
    
    def _extract_markdown(self, content: str) -> str:
        """
        Extract text from Markdown content
        Remove markdown syntax but keep the text
        """
        # Simple markdown cleanup
        import re
        
        # Remove code blocks
        content = re.sub(r'```[\s\S]*?```', '', content)
        
        # Remove inline code
        content = re.sub(r'`[^`]+`', '', content)
        
        # Remove markdown links but keep text
        content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
        
        # Remove images
        content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)
        
        # Remove headers markers but keep text
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)
        
        # Remove bold/italic markers
        content = re.sub(r'[*_]{1,2}([^*_]+)[*_]{1,2}', r'\1', content)
        
        # Clean up
        content = ' '.join(content.split())
        
        return content
    
    def _extract_html(self, html: str) -> str:
        """
        Extract text from generic HTML page
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup.select('script, style, nav, header, footer, aside, .sidebar, .navigation, .menu'):
            element.decompose()
        
        # Try to find main content
        main_content = (
            soup.find('main') or 
            soup.find('article') or 
            soup.find(id='content') or 
            soup.find(class_='content') or
            soup.find('body')
        )
        
        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
            text = ' '.join(text.split())
            return text
        
        return ""
    
    def fetch_confluence_page(self, url: str, auth: Optional[tuple] = None) -> Optional[str]:
        """
        Fetch Confluence page with optional authentication
        
        Args:
            url: Confluence page URL
            auth: Optional (username, password) or (email, api_token) tuple
            
        Returns:
            Extracted text content
        """
        if auth:
            self.session.auth = auth
        
        # Try Confluence REST API first (better than HTML scraping)
        api_content = self._try_confluence_api(url)
        if api_content:
            return api_content
        
        # Fallback to HTML scraping
        return self.fetch_url(url)
    
    def _try_confluence_api(self, page_url: str) -> Optional[str]:
        """
        Try to fetch content via Confluence REST API
        
        Converts page URL to API endpoint and fetches content
        Example: /display/SPACE/Page -> /rest/api/content?title=Page&spaceKey=SPACE
        """
        try:
            # Extract space and page title from URL
            # Common patterns:
            # - /display/SPACE/Page+Title
            # - /spaces/SPACE/pages/123456/Page+Title
            
            import re
            from urllib.parse import unquote, urlparse
            
            parsed = urlparse(page_url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # Pattern 1: /display/SPACE/Page+Title
            display_match = re.search(r'/display/([^/]+)/(.+)', parsed.path)
            if display_match:
                space_key = display_match.group(1)
                page_title = unquote(display_match.group(2).replace('+', ' '))
                
                # Try API endpoint
                api_url = f"{base_url}/rest/api/content"
                params = {
                    'title': page_title,
                    'spaceKey': space_key,
                    'expand': 'body.storage,body.view'
                }
                
                response = self.session.get(api_url, params=params, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('results'):
                        page = data['results'][0]
                        # Get plain text content
                        body = page.get('body', {})
                        content = body.get('storage', {}).get('value', '') or body.get('view', {}).get('value', '')
                        
                        if content:
                            # Strip HTML tags
                            soup = BeautifulSoup(content, 'html.parser')
                            text = soup.get_text(separator=' ', strip=True)
                            text = ' '.join(text.split())
                            print(f"✅ Successfully fetched via Confluence API")
                            return text
            
            # Pattern 2: /spaces/SPACE/pages/123456
            spaces_match = re.search(r'/spaces/([^/]+)/pages/(\d+)', parsed.path)
            if spaces_match:
                page_id = spaces_match.group(2)
                
                api_url = f"{base_url}/rest/api/content/{page_id}"
                params = {'expand': 'body.storage,body.view'}
                
                response = self.session.get(api_url, params=params, timeout=self.timeout)
                if response.status_code == 200:
                    data = response.json()
                    body = data.get('body', {})
                    content = body.get('storage', {}).get('value', '') or body.get('view', {}).get('value', '')
                    
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        text = soup.get_text(separator=' ', strip=True)
                        text = ' '.join(text.split())
                        print(f"✅ Successfully fetched via Confluence API")
                        return text
        
        except Exception as e:
            print(f"⚠️  Confluence API fetch failed: {e}, falling back to HTML")
        
        return None
    
    def fetch_readme(self, url: str) -> Optional[str]:
        """
        Fetch README file (Markdown or plain text)
        
        Args:
            url: URL to README file
            
        Returns:
            Extracted text content
        """
        return self.fetch_url(url)
    
    def fetch_multiple_urls(self, urls: list[str], delay: float = 1.0) -> dict[str, Optional[str]]:
        """
        Fetch multiple URLs with delay between requests
        
        Args:
            urls: List of URLs to fetch
            delay: Delay between requests in seconds
            
        Returns:
            Dictionary mapping URL to extracted content
        """
        results = {}
        
        for i, url in enumerate(urls):
            if i > 0:
                time.sleep(delay)  # Be polite, don't hammer the server
            
            results[url] = self.fetch_url(url)
        
        return results


# Global instance
from app.core.config import settings

crawler = DocumentCrawler(
    confluence_token=settings.CONFLUENCE_API_TOKEN or None,
    confluence_email=settings.CONFLUENCE_EMAIL or None
)
