import pytest
from unittest.mock import patch, MagicMock
from sar_project.agents.media_analysis_agent import MediaAnalysisAgent

@pytest.fixture
def agent():
    """Initialize the media analysis agent."""
    return MediaAnalysisAgent()

def test_fetch_news_articles_success(agent):
    """Test fetching news articles successfully from GNews API."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "articles": [
                {"title": "SAR Team Rescues Hiker", "url": "https://example.com/rescue", "description": "SAR teams saved a hiker."}
            ]
        }
        mock_get.return_value = mock_response

        articles = agent.fetch_news_articles("rescue")
        assert len(articles) == 1
        assert articles[0]["title"] == "SAR Team Rescues Hiker"

def test_fetch_news_articles_empty(agent):
    """Test when the API returns no articles."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"articles": []}
        mock_get.return_value = mock_response

        articles = agent.fetch_news_articles("random query")
        assert articles == []

def test_fetch_news_articles_unauthorized(agent):
    """Test handling of unauthorized API access (invalid API key)."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        articles = agent.fetch_news_articles("rescue")
        assert articles == []

def test_check_relevance_with_openai(agent):
    """Test OpenAI relevance verification for SAR articles."""
    with patch.object(agent.client.chat.completions, "create") as mock_openai:
        mock_openai.return_value.choices = [
            MagicMock(message=MagicMock(content="Yes, this article is related to SAR operations."))
        ]

        is_relevant, explanation = agent.check_relevance_with_openai("Rescue teams saved 5 people.", "rescue")
        assert is_relevant
        assert "sar operations" in explanation.lower()

def test_check_irrelevant_with_openai(agent):
    """Test OpenAI rejecting non-SAR-related articles."""
    with patch.object(agent.client.chat.completions, "create") as mock_openai:
        mock_openai.return_value.choices = [
            MagicMock(message=MagicMock(content="No, this article is not related to SAR operations."))
        ]

        is_relevant, explanation = agent.check_relevance_with_openai("Football team wins championship.", "sports")
        assert not is_relevant
        assert "not related to sar operations" in explanation.lower()

def test_analyze_media_success(agent):
    """Test the full media analysis workflow."""
    with patch.object(agent, "fetch_news_articles") as mock_fetch, \
         patch.object(agent, "check_relevance_with_openai") as mock_relevance, \
         patch.object(agent, "get_keywords_from_user", return_value="rescue"):

        mock_fetch.return_value = [
            {"title": "Wildfire Rescue Efforts", "url": "https://example.com/fire-rescue", "content": "SAR teams evacuated families from a wildfire zone."}
        ]
        mock_relevance.return_value = (True, "Yes, this article discusses an active SAR operation.")

        results = agent.analyze_media()
        assert len(results) == 1
        assert results[0]["title"] == "Wildfire Rescue Efforts"
        assert "active SAR operation" in results[0]["relevance"]
