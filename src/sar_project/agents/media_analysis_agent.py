import requests
from bs4 import BeautifulSoup
import re
import json
import os
from dotenv import load_dotenv
from sar_project.agents.base_agent import SARBaseAgent

# Load environment variables (API keys)
load_dotenv()

class MediaAnalysisAgent(SARBaseAgent):
    def __init__(self, name="media_analysis"):
        super().__init__(
            name=name,
            role="Media Analysis Agent",
            system_message="""You monitor and analyze online media sources (news articles, social media) to extract and summarize 
            information relevant to SAR missions. Your role is to:
            1. Search for SAR-related articles from news sources.
            2. Scrape articles from multiple news sites.
            3. Extract and summarize relevant information.
            4. Provide real-time updates when new relevant stories appear."""
        )
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.keywords = ["missing person", "search and rescue", "lost hiker", "emergency response"]
        self.sources = ["bbc-news", "cnn", "cbc-news", "reuters", "al-jazeera-english"]  # NewsAPI sources

    def search_news(self):
        """
        Searches for SAR-related articles using NewsAPI.
        Returns:
            list: A list of relevant article URLs.
        """
        if not self.newsapi_key:
            return {"error": "NewsAPI key missing. Please add it to .env."}

        url = f"https://newsapi.org/v2/everything?q=search%20and%20rescue&apiKey={self.newsapi_key}"
        response = requests.get(url)

        if response.status_code != 200:
            return {"error": f"Failed to fetch news articles. Status code: {response.status_code}"}

        articles = response.json().get("articles", [])
        article_urls = [article["url"] for article in articles if "url" in article]

        return article_urls[:5]  # Return top 5 article URLs

    def fetch_web_content(self, url: str) -> str:
        """
        Fetch HTML content from a given URL.
        Args:
            url (str): The website URL to scrape.
        Returns:
            str: Extracted HTML content or error message.
        """
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            return f"Error fetching content: {str(e)}"

    def extract_relevant_text(self, html: str) -> list:
        """
        Extract paragraphs from HTML content and filter based on keywords.
        Args:
            html (str): HTML source content.
        Returns:
            list: Relevant text snippets containing keywords.
        """
        soup = BeautifulSoup(html, "html.parser")
        paragraphs = [p.get_text() for p in soup.find_all(["p", "div", "span"])]  # Extract from <p>, <div>, and <span>
        
        relevant_sentences = [
            sentence for paragraph in paragraphs
            for sentence in re.split(r'(?<=[.!?]) +', paragraph)
            if any(kw in sentence.lower() for kw in self.keywords)
        ]
        
        return relevant_sentences[:5]  # Return the top 5 relevant sentences

    def summarize_text(self, text_list: list) -> str:
        """
        Generate a summary based on extracted text.
        Args:
            text_list (list): List of relevant sentences.
        Returns:
            str: Summarized content.
        """
        if not text_list:
            return "No relevant content found."
        return " ".join(text_list[:3])  # Simple summary using first 3 relevant sentences

    def analyze_media(self):
        """
        Searches for relevant SAR articles and analyzes them.
        Returns:
            dict: A dictionary of analyzed articles with summaries.
        """
        article_urls = self.search_news()
        if isinstance(article_urls, dict):  # Check if an error was returned
            return article_urls

        results = []
        for url in article_urls:
            html_content = self.fetch_web_content(url)
            relevant_content = self.extract_relevant_text(html_content)
            summary = self.summarize_text(relevant_content)
            
            results.append({
                "url": url,
                "relevant_content": relevant_content,
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
