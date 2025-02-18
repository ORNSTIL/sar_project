from sar_project.agents.media_analysis_agent import MediaAnalysisAgent

agent = MediaAnalysisAgent()

print("\n🔍 Searching for relevant SAR news articles based on your input...\n")
result = agent.process_request({"action": "search_news"})

if isinstance(result, dict) and "error" in result:
    print("\n❌ Error:", result["error"])
elif isinstance(result, list):
    if not result:
        print("\n❌ No relevant SAR articles found.")
    else:
        print("\n✅ Found SAR-related articles:\n")
        for i, article in enumerate(result, 1):
            print(f"🔹 **Article {i}**")
            print(f"🔗 **URL:** {article.get('url', 'N/A')}")
            print(f"📄 **Title:** {article.get('title', 'No title available')}")
            print(f"📖 **Summary:** {article.get('summary', 'No summary available')}")
            print(f"📝 **Relevance Explanation:** {article.get('relevance', 'No explanation available')}\n")
else:
    print("\n⚠️ Unexpected output format:", result)
