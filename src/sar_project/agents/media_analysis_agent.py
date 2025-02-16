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
            1. Ask the user for four keywords to search for SAR news.
            2. Search for news articles that contain all four keywords.
            3. Use OpenAI to determine if the article is SAR-relevant.
            4. If relevant, summarize the article using OpenAI.
            5. Return only SAR-related summaries."""
        )
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)

    def get_keywords_from_user(self):
        """
        Ask the user for four search keywords.
        Returns:
            list: A list of four keywords.
        """
        print("\nEnter four keywords to search for relevant SAR news articles.")
        keywords = []
        for i in range(4):
            keyword = input(f"Keyword {i + 1}: ").strip().lower()
            keywords.append(keyword)
        return keywords

    def search_news(self, keywords):
        """
        Searches for SAR-related articles using NewsAPI based on user keywords.
        Args:
            keywords (list): List of four user-provided keywords.
        Returns:
            list: A list of relevant article URLs.
        """
        if not self.newsapi_key:
            return {"error": "NewsAPI key missing. Please add it to .env."}

        query = " AND ".join(keywords)  # ✅ Search for articles containing all four keywords
        base_url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,  
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 5,  # ✅ Limit to 5 articles per request
            "apiKey": self.newsapi_key
        }

        response = requests.get(base_url, params=params)

        if response.status_code != 200:
            return {"error": f"Failed to fetch news articles. Status code: {response.status_code}, Response: {response.text}"}

        articles = response.json().get("articles", [])
        article_urls = [article["url"] for article in articles if "url" in article]

        return article_urls if article_urls else {"error": "No relevant articles found."}

    def fetch_full_article(self, url):
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

            # Remove scripts, styles, and irrelevant sections
            for tag in soup(["script", "style", "footer", "nav"]):
                tag.extract()

            paragraphs = [p.get_text() for p in soup.find_all(["p", "div", "span"]) if len(p.get_text()) > 50]  
            article_text = " ".join(paragraphs)

            return article_text if article_text else "Error: Could not extract article content."

        except requests.RequestException as e:
            return f"Error fetching article: {str(e)}"

    def check_relevance_with_openai(self, article_text, keywords):
        """
        Uses OpenAI to determine if the article is relevant to SAR.
        Args:
            article_text (str): The full article text.
            keywords (list): The user-provided keywords.
        Returns:
            bool: True if relevant, False otherwise.
        """
        if not article_text or article_text.startswith("Error:"):
            return False

        prompt = f"""
        Determine if the following article is relevant to Search and Rescue (SAR) operations based on the context of these keywords: {', '.join(keywords)}.
        If the article is about SAR-related missions (e.g., rescuing lost people, emergency response, disaster recovery), return 'Yes'.
        Otherwise, return 'No'.

        Article text:
        {article_text[:1500]}  # ✅ Limit to 1500 characters to avoid long processing times
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )
            relevance_response = response.choices[0].message.content.strip().lower()
            return "yes" in relevance_response
        except Exception as e:
            return False  # Assume not relevant if OpenAI check fails

    def summarize_with_openai(self, full_text):
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
        {full_text[:2000]}  # ✅ Limit to 2000 characters for efficiency
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
        Searches for relevant SAR articles, verifies relevance with OpenAI, and summarizes them.
        Returns:
            list: A list of analyzed articles with summaries.
        """
        keywords = self.get_keywords_from_user()
        article_urls = self.search_news(keywords)

        if isinstance(article_urls, dict) and "error" in article_urls:
            return article_urls

        results = []
        for url in article_urls:
            article_text = self.fetch_full_article(url)

            # ✅ Check with OpenAI if the article is SAR-relevant
            if not self.check_relevance_with_openai(article_text, keywords):
                continue  # Skip irrelevant articles

            summary = self.summarize_with_openai(article_text)
            
            results.append({
                "url": url,
                "summary": summary
            })

        return results if results else [{"error": "No SAR-related articles found after verification."}]

    def process_request(self, message):
        """
        Handle incoming requests from users.
        Returns:
            dict: Processed results.
        """
        if message.get("action") == "search_news":
            return self.analyze_media()
        return {"error": "Invalid request. Use {'action': 'search_news'} to fetch SAR news."}
