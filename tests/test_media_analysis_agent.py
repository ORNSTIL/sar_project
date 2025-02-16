import pytest
from unittest.mock import patch, Mock
from sar_project.agents.media_analysis_agent import MediaAnalysisAgent

@pytest.fixture
def agent():
    return MediaAnalysisAgent()

def test_fetch_web_content_success(agent):
    with patch('requests.get') as mock_get:
        mock_response = Mock(status_code=200, text="<html><body><p>Test article content.</p></body></html>")
        mock_get.return_value = mock_response

        result = agent.fetch_web_content("http://example.com")
        assert "Test article content" in result

def test_extract_relevant_text(agent):
    html_content = "<html><body><p>The search and rescue team found a clue.</p><p>Unrelated information.</p></body></html>"
    relevant_sentences = agent.extract_relevant_text(html_content)
    
    assert len(relevant_sentences) == 1
    assert "search and rescue" in relevant_sentences[0]

def test_summarize_text(agent):
    sentences = [
        "The search and rescue team found a clue.",
        "The missing person was last seen near the lake."
    ]
    summary = agent.summarize_text(sentences)
    assert "search and rescue" in summary
    assert "missing person" in summary

def test_analyze_media_success(agent):
    html_content = "<html><body><p>The SAR team is actively searching for the missing person.</p></body></html>"
    with patch('sar_project.agents.media_analysis_agent.MediaAnalysisAgent.fetch_web_content', return_value=html_content):
        result = agent.analyze_media("http://example.com")
        assert "SAR team" in result["summary"]

def test_analyze_media_no_relevant_content(agent):
    html_content = "<html><body><p>This is an unrelated news article.</p></body></html>"
    with patch('sar_project.agents.media_analysis_agent.MediaAnalysisAgent.fetch_web_content', return_value=html_content):
        result = agent.analyze_media("http://example.com")
        assert result["summary"] == "No relevant content found."
        assert len(result["relevant_content"]) == 0

