import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from config import GROQ_API_KEY, MODEL_NAME

class Tool:
    pass

class CVParser(Tool):
    def parse_cv(self, pdf_path: str) -> str:
        if not os.path.exists(pdf_path):
            logger.error(f"CV file not found: {pdf_path}")
            return ""
        
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            logger.error(f"Error parsing CV: {str(e)}")
            return ""

class WebSearch(Tool):
    def search(self, query: str) -> List[Dict[str, str]]:
        """Real web search using DuckDuckGo (Free)."""
        logger.info(f"WebSearch: Searching for '{query}' using DuckDuckGo")
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=10)]
                return [{"title": r['title'], "link": r['href'], "snippet": r['body']} for r in results]
        except Exception as e:
            logger.error(f"DuckDuckGo Search failed: {str(e)}")
            return []

class WebScraper(Tool):
    def __init__(self):
        from config import HEADERS, TIMEOUT
        self.headers = HEADERS
        self.timeout = TIMEOUT

    def scrape_url(self, url: str) -> str:
        logger.info(f"Scraping: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Clean up
            for script_or_style in soup(["script", "style", "nav", "footer"]):
                script_or_style.decompose()
                
            return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.error(f"Scraping failed for {url}: {str(e)}")
            return ""

    def scrape_playwright(self, url: str) -> str:
        """Fallback for JS-heavy sites using real Playwright browser."""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=30 * 1000)
                content = page.content()
                browser.close()
                soup = BeautifulSoup(content, 'html.parser')
                return soup.get_text(separator=' ', strip=True)
        except Exception as e:
            logger.error(f"Playwright scraping failed: {str(e)}")
            return self.scrape_url(url)

class RankingCalculator(Tool):
    def calculate_match(self, profile: str, target_description: str) -> Dict[str, Any]:
        """Real matching logic using LLM for profile comparison."""
        from .llm_utils import llm
        
        system_prompt = "You are a PhD matching expert. Compare a student profile with a research opportunity."
        user_prompt = f"""
        Student Profile: {profile}
        Research/University Description: {target_description}
        
        Rate the match and explain why.
        Output JSON: {{"score": 85, "reasoning": "Detailed explanation..."}}
        """
        
        response = llm.generate_response(system_prompt, user_prompt)
        return llm.parse_json_response(response)
