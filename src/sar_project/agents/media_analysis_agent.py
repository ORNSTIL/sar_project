import requests
from bs4 import BeautifulSoup
import re
import json
from sar_project.agents.base_agent import SARBaseAgent

class MediaAnalysisAgent(SARBaseAgent):
    def __init__(self, name="media_analysis"):
        super().__init__(
            name=name,
            role="Media Analysis Agent",
            system_message="""You monitor and analyze online media sources (news articles, social media) to extract and summarize 
            information relevant to SAR missions. Your role is to:
            1. Scrape public news sources for relevant updates.
            2. Analyze social media posts for mentions of missing persons.
            3. Summarize findings for SAR teams in a structured format.
            4. Provide real-time updates when new relevant information is found."""
        )
        self.keywords = ["missing person", "search and rescue", "lost hiker", "emergency response"]

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
        paragraphs = [p.get_text() for p in soup.find_all("p")]
        
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

    def analyze_media(self, url: str) -> dict:
        """
        Analyze a news article or webpage for SAR-relevant information.
        Args:
            url (str): URL of the media source.
        Returns:
            dict: JSON-structured output with summarized information.
        """
        html_content = self.fetch_web_content(url)
        relevant_content = self.extract_relevant_text(html_content)
        summary = self.summarize_text(relevant_content)

        return {
            "url": url,
            "relevant_content": relevant_content,
            "summary": summary
        }

    def process_request(self, message: dict):
        """
        Handle incoming requests from other agents or users.
        Args:
            message (dict): Dictionary containing the 'url' key.
        Returns:
            dict: Processed results.
        """
        if "url" in message:
            return self.analyze_media(message["url"])
        return {"error": "Invalid request. Please provide a URL."}
