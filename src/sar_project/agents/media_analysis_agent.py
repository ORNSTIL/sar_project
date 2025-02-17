import os
import requests
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
            system_message="""You monitor and analyze online media sources to extract and summarize 
            information relevant to SAR missions. Your role is to:
            1. Prompt the user for up to three search words (optional).
            2. Use NewsAPI to fetch articles matching those words.
            3. Use OpenAI to verify relevance to SAR.
            4. If relevant, provide a summary and description of relevance."""
        )
        self.news_api_key = os.getenv("NEWS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.openai_api_key)

    def get_keywords_from_user(self):
        """
        Ask the user for up to three search words.
        Returns:
            str: A query string combining all entered words.
        """
        print("\nEnter up to three words to search for SAR news articles. Press enter to skip.")
        keywords = []
        for i in range(3):
            word = input(f"Word {i + 1}: ").strip()
            if word:
                keywords.append(word)
        
        return " ".join(keywords) if keywords else None  # Return combined string or None

    def fetch_news_articles(self, query):
        """
        Fetches news articles from NewsAPI.
        Args:
            query (str): The search query (user input).
        Returns:
            list: A list of news articles with 'title', 'url', and 'content'.
        """
        if not query:
            return []

        url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={self.news_api_key}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Error fetching news articles. Status code: {response.status_code}")
            return []
        
        articles = response.json().get("articles", [])
        return [{"title": art["title"], "url": art["url"], "content": art.get("description", "No content available")} for art in articles]

    def check_relevance_with_openai(self, article_text, query):
        """
        Uses OpenAI to determine if an article is relevant to SAR.
        Args:
            article_text (str): The article text to evaluate.
            query (str): The user-provided search query.
        Returns:
            bool: True if the article is relevant, False otherwise.
        """
        prompt = f"""
        Determine if the following article is relevant to Search and Rescue (SAR) efforts based on the search words: {query}.
        If the article is related to SAR operations (e.g., rescues, missing persons, disaster response), return 'Yes' with a brief explanation.
        Otherwise, return 'No'.

        Article:
        {article_text[:1500]}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = response.choices[0].message.content.strip().lower()
        
        return "yes" in response_text, response_text

    def summarize_with_openai(self, article_text):
        """
        Generates a summary of the article using OpenAI.
        Args:
            article_text (str): The article text to summarize.
        Returns:
            str: A concise summary of the article.
        """
        prompt = f"""
        Summarize the following news article in 3-4 sentences while preserving key details:

        {article_text[:3000]}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()

    def analyze_media(self):
        """
        Fetches SAR news articles, verifies relevance with OpenAI, and summarizes them.
        Returns:
            list: A list of relevant articles with summaries.
        """
        query = self.get_keywords_from_user()
        articles = self.fetch_news_articles(query)

        results = []
        for article in articles:
            is_relevant, relevance_explanation = self.check_relevance_with_openai(article["content"], query)
            if is_relevant:
                summary = self.summarize_with_openai(article["content"])
                results.append({
                    "url": article["url"],
                    "title": article["title"],
                    "summary": summary,
                    "relevance": relevance_explanation
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
