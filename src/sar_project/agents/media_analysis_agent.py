import requests
from bs4 import BeautifulSoup
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
from sar_project.agents.base_agent import SARBaseAgent

# Load API keys from .env file
load_dotenv()

class MediaAnalysisAgent(SARBaseAgent):
    def __init__(self, name="media_analysis"):
        super().__init__(
            name=name,
            role="Media Analysis Agent",
            system_message="""You monitor and analyze online media sources (news articles, social media) to extract and summarize 
            information relevant to SAR missions. Your role is to:
            1. Search for SAR-related articles from news sources.
            2. Scrape articles that contain relevant SAR keywords.
            3. Provide the entire article text to OpenAI for summarization.
            4. Return a well-structured summary for SAR teams."""
        )
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)
        
        # Expanded SAR-related keywords for better filtering
        self.keywords = [
            "search and rescue", "SAR team", "missing person", "lost hiker", "emergency response",
            "disaster response", "rescue operation", "coast guard", "helicopter rescue", "boat rescue",
            "flood rescue", "earthquake response", "landslide rescue", "avalanche rescue", "trapped survivors",
            "fire rescue", "wilderness survival", "dive rescue", "mountain rescue", "airlift operation",
            "urban search and rescue", "natural disaster response", "lifesaving operation", "first responders",
            "emergency evacuation", "collapsed building rescue", "tornado rescue", "cyclone survivors",
            "water rescue", "swiftwater rescue", "hazardous materials rescue", "volunteer rescue teams",
            "disaster relief", "medical evacuation", "first aid response", "disaster recovery", "lost climber",
            "hiker found", "air rescue", "drowning victim rescue", "wildfire response", "earthquake victim search"
        ]
        self.sources = ["bbc-news", "cnn", "cbc-news", "reuters", "al-jazeera-english"]

    def search_news(self):
        """
        Searches for SAR-related articles using NewsAPI.
        Returns:
            list: A list of relevant article URLs.
        """
        if not self.newsapi_key:
            return {"error": "NewsAPI key missing. Please add it to .env."}
    
        base_url = "https://newsapi.org/v2/everything"
        headers = {"Authorization": self.newsapi_key}
    
        selected_keywords = self.keywords[:5]  # ✅ Limit to 5 keywords per request to avoid query errors
        query = " OR ".join(selected_keywords)
    
        params = {
            "q": query,  
            "language": "en",  # ✅ Only fetch English news
            "sortBy": "publishedAt",  
            "pageSize": 5,  # ✅ Limit results to 5 articles per query
            "apiKey": self.newsapi_key
        }
    
        response = requests.get(base_url, params=params, headers=headers)
    
        if response.status_code != 200:
            return {"error": f"Failed to fetch news articles. Status code: {response.status_code}, Response: {response.text}"}
    
        articles = response.json().get("articles", [])
        article_urls = [article["url"] for article in articles if "url" in article]
    
        return article_urls if article_urls else {"error": "No relevant articles found."}

    def fetch_full_article(self, url: str) -> str:
        """
        Fetches the full text of an article.
        Args:
            url (str): The website URL to scrape.
        Returns:
            str: Extracted full article text or error message.
        """
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts, styles, and non-content sections
            for tag in soup(["script", "style", "footer", "nav"]):
                tag.extract()

            paragraphs = [p.get_text() for p in soup.find_all(["p", "div", "span"]) if len(p.get_text()) > 50]  
            article_text = " ".join(paragraphs)

            return article_text if article_text else "Error: Could not extract article content."

        except requests.RequestException as e:
            return f"Error fetching article: {str(e)}"

    def summarize_with_openai(self, full_text: str) -> str:
        """
        Uses OpenAI GPT-4o-mini to generate a summary of the article.
        Args:
            full_text (str): The full article text.
        Returns:
            str: AI-generated summary.
        """
        if not full_text or full_text.startswith("Error:"):
            return "No relevant content found."

        prompt = f"""
        Summarize the following Search and Rescue (SAR) news report in a professional and concise manner:
        {full_text}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI summarization error: {str(e)}"

    def analyze_media(self):
        """
        Searches for relevant SAR articles, fetches their content, and summarizes them.
        Returns:
            list: A list of analyzed articles with summaries.
        """
        article_urls = self.search_news()
        if isinstance(article_urls, dict):  # Check if an error was returned
            return article_urls

        results = []
        for url in article_urls:
            article_text = self.fetch_full_article(url)
            summary = self.summarize_with_openai(article_text) if article_text else "No relevant content found."
            
            results.append({
                "url": url,
                "full_text": article_text[:500] + "...",  # Show preview of full article
                "summary": summary
            })

        return results

    def process_request(self, message: dict):
        """
        Handle incoming requests from other agents or users.
        Args:
            message (dict): Dictionary containing the request type.
        Returns:
            dict: Processed results.
        """
        if message.get("action") == "search_news":
            return self.analyze_media()
        return {"error": "Invalid request. Use {'action': 'search_news'} to fetch SAR news."}
