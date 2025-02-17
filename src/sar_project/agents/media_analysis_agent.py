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
            2. Scrape articles from NASAR, KSBY, and MarineLink.
            3. Use OpenAI to determine if an article is SAR-relevant.
            4. If relevant, summarize the article using OpenAI.
            5. Return only SAR-related summaries."""
        )
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

    def fetch_sar_news(self):
        """
        Scrapes SAR-related articles from NASAR, KSBY, and MarineLink.
        Returns:
            list: A list of article dictionaries with 'title', 'url', and 'content'.
        """
        sources = [
            {"name": "NASAR", "url": "https://nasar.org/news/", "parser": self.scrape_nasar_news},
            {"name": "KSBY", "url": "https://www.ksby.com/", "parser": self.scrape_ksby_news},
            {"name": "MarineLink", "url": "https://www.marinelink.com/news/maritime/search-and-rescue", "parser": self.scrape_marinelink_news},
        ]

        articles = []
        for source in sources:
            print(f"Fetching news from {source['name']}...")
            articles.extend(source["parser"](source["url"]))

        return articles

    def process_request(self, message):
        """
        Handle incoming requests from users.
        Returns:
            dict: Processed results.
        """
        if message.get("action") == "search_news":
            return self.analyze_media()
        return {"error": "Invalid request. Use {'action': 'search_news'} to fetch SAR news."}


    def scrape_nasar_news(self, url):
        """
        Scrapes NASAR News for SAR articles.
        Args:
            url (str): NASAR News URL.
        Returns:
            list: List of articles with 'title', 'url', and 'content'.
        """
        articles = []
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, "html.parser")

            for article in soup.find_all("article"):
                title = article.find("h2").text if article.find("h2") else "No Title"
                link = article.find("a")["href"] if article.find("a") else None
                if link:
                    full_url = link if "http" in link else f"https://nasar.org{link}"
                    content = self.fetch_full_article(full_url)
                    articles.append({"title": title, "url": full_url, "content": content})

        except Exception as e:
            print(f"Error fetching NASAR news: {e}")

        return articles

    def scrape_ksby_news(self, url):
        """
        Scrapes KSBY News for SAR articles.
        """
        articles = []
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, "html.parser")

            for article in soup.find_all("article"):
                title = article.find("h2").text if article.find("h2") else "No Title"
                link = article.find("a")["href"] if article.find("a") else None
                if link:
                    full_url = link if "http" in link else f"https://www.ksby.com{link}"
                    content = self.fetch_full_article(full_url)
                    articles.append({"title": title, "url": full_url, "content": content})

        except Exception as e:
            print(f"Error fetching KSBY news: {e}")

        return articles

    def scrape_marinelink_news(self, url):
        """
        Scrapes MarineLink for SAR articles.
        """
        articles = []
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, "html.parser")

            for article in soup.find_all("article"):
                title = article.find("h2").text if article.find("h2") else "No Title"
                link = article.find("a")["href"] if article.find("a") else None
                if link:
                    full_url = link if "http" in link else f"https://www.marinelink.com{link}"
                    content = self.fetch_full_article(full_url)
                    articles.append({"title": title, "url": full_url, "content": content})

        except Exception as e:
            print(f"Error fetching MarineLink news: {e}")

        return articles

    def fetch_full_article(self, url):
        """
        Fetches the full text of an article.
        """
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for tag in soup(["script", "style", "footer", "nav"]):
                tag.extract()

            paragraphs = [p.get_text() for p in soup.find_all("p") if len(p.get_text()) > 50]
            return " ".join(paragraphs)

        except Exception as e:
            return f"Error fetching article: {str(e)}"

    def analyze_media(self):
        """
        Scrapes SAR news, verifies relevance with OpenAI, and summarizes them.
        """
        keywords = self.get_keywords_from_user()
        articles = self.fetch_sar_news()

        results = []
        for article in articles:
            if self.check_relevance_with_openai(article["content"], keywords):
                summary = self.summarize_with_openai(article["content"])
                results.append({"url": article["url"], "summary": summary})

        return results if results else [{"error": "No SAR-related articles found after verification."}]

    def check_relevance_with_openai(self, article_text, keywords):
        """
        Uses OpenAI to determine if the article is relevant to SAR.
        """
        prompt = f"""
        Determine if the following article is relevant to Search and Rescue (SAR) operations based on these keywords: {', '.join(keywords)}.
        Article:
        {article_text[:1500]}
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return "yes" in response.choices[0].message.content.strip().lower()

