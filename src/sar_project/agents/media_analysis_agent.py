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

        query = " ".join(keywords) if keywords else None
        print(f"\n📡 Debug: User Search Query -> {query}")
        return query

    def fetch_news_articles(self, query):
        """
        Fetches news articles from NewsAPI.
        Args:
            query (str): The search query (user input).
        Returns:
            list: A list of news articles with 'title', 'url', and 'content'.
        """
        if not query:
            print("\n⚠️ No search query provided. Skipping NewsAPI request.")
            return []

        url = f"https://newsapi.org/v2/top-headlines?q={query}&language=en&apiKey={self.news_api_key}"

        try:
            response = requests.get(url)
            if response.status_code == 401:
                print("\n❌ Error: Unauthorized. Check if your NewsAPI key is valid in the .env file.")
                return []
            elif response.status_code != 200:
                print(f"\n❌ Error fetching news articles. Status code: {response.status_code}")
                return []

            articles = response.json().get("articles", [])
            print(f"\n📡 Debug: Received {len(articles)} articles from NewsAPI.")  # DEBUG

            # Ensure articles always return valid content
            parsed_articles = [
                {
                    "title": art.get("title", "No Title Available"),
                    "url": art.get("url", "No URL Available"),
                    "content": art.get("description") or art.get("content") or "No content available"
                }
                for art in articles
            ]

            if parsed_articles:
                print(f"\n📡 Debug: First fetched article -> {parsed_articles[0]}")
            return parsed_articles

        except Exception as e:
            print(f"\n❌ Error fetching news articles: {e}")
            return []

    def check_relevance_with_openai(self, article_text, query):
        """
        Uses OpenAI to determine if an article is relevant to SAR.
        Args:
            article_text (str): The article text to evaluate.
            query (str): The user-provided search query.
        Returns:
            bool: True if the article is relevant, False otherwise.
        """
        if not article_text or article_text == "No content available":
            print("\n⚠️ Skipping article due to lack of valid content.")
            return False, "Article has no valid content to analyze."

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

        print(f"\n📡 Debug: OpenAI Response for relevance -> {response_text}")  # DEBUG

        return "yes" in response_text or "likely" in response_text, response_text

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
        summary = response.choices[0].message.content.strip()

        print(f"\n📡 Debug: OpenAI Summary -> {summary[:200]}...")  # DEBUG
        return summary

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

        if not results:
            print("\n⚠️ No SAR-related articles found after verification.")
            return [{"error": "No SAR-related articles found after verification."}]

        return results

    def process_request(self, message):
        """
        Handle incoming requests from users.
        Returns:
            dict: Processed results.
        """
        if message.get("action") == "search_news":
            return self.analyze_media()
        return {"error": "Invalid request. Use {'action': 'search_news'} to fetch SAR news."}
