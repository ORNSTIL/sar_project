# **📌 Media Analysis Agent - Documentation**  
### **Search and Rescue (SAR) News Analysis**  
**Role: Social Network Profiler**  

## **🔹 Role of the Agent**  
The **Media Analysis Agent** falls under the **Social Network Profiler** role within Search and Rescue (SAR) operations. It is responsible for monitoring **online media sources** and identifying **relevant SAR-related news articles** to assist rescue teams and analysts.  

### **📍 Tasks & Responsibilities**  
- **Retrieve news articles** related to SAR efforts (e.g., missing persons, disaster rescues, emergency responses).  
- **Filter relevant articles** using OpenAI to determine whether they relate to SAR operations.  
- **Summarize articles** to provide concise and actionable insights for SAR teams.  
- **Output structured data** that includes article details, relevance explanations, and summaries.  

---

## **🔹 Setup Instructions**  
To run the agent, you must **set up a `.env` file** in the **root directory** with your **API keys**.  

### **📍 Creating the `.env` File**  
1. Navigate to your project's root directory:  

2. Create a `.env` file:  

3. Add the following lines to the `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   GNEWS_API_KEY=your_gnews_api_key_here
   ```

🔹 **Replace `your_openai_api_key_here` and `your_gnews_api_key_here`** with your actual API keys.  
🔹 **Do not share or commit your `.env` file** for security reasons.  

---

## **🔹 Activity & Sources of Knowledge**  
### **📍 How the Agent Works**  
1. **User provides up to three keywords** (e.g., `"earthquake", "missing", "emergency"`).  
2. The agent **queries GNews API** to **fetch recent articles** containing those words.  
3. The agent **checks each article’s relevance** using **OpenAI GPT-4o-mini** by asking:  
   > *“Does this article discuss an active Search and Rescue operation?”*  
4. If OpenAI confirms the article is SAR-related:  
   - **The agent extracts key details** (title, URL, content).  
   - **The article is summarized** using OpenAI.  
   - **A relevance explanation is generated** for SAR teams.  

---

## **🔹 Sources of Knowledge**  
| **Source**  | **Purpose**  | **Data Accessed**  |  
|-------------|-------------|--------------------|  
| **GNews API** | Fetches **recent news articles** | Headlines, descriptions, and URLs |  
| **OpenAI GPT-4o-mini** | **Validates relevance** of SAR articles | AI-generated classification ("Relevant" or "Not Relevant") |  
| **User Input** | **Guides search queries** | Up to three keywords |  

---

## **🔹 Data Output Format**  
### **📍 JSON Output**  
The agent **returns structured JSON** for each relevant article:  
```json
{
  "url": "https://example.com/article",
  "title": "Rescue Teams Save Hikers in Colorado",
  "summary": "SAR teams rescued three hikers stranded in Colorado after a sudden snowstorm...",
  "relevance": "This article discusses a live search and rescue operation involving stranded hikers."
}
```  

### **📍 Example Console Output**  
```
🔹 **Article 1**  
🔗 **URL:** https://example.com/rescue  
📄 **Title:** Rescue Teams Save Hikers in Colorado  
📖 **Summary:** SAR teams rescued three hikers stranded in Colorado after a sudden snowstorm...  
📝 **Relevance Explanation:** This article discusses a live search and rescue operation.  
```

---

## **🔹 How to Test the Agent**  
### **📍 Running Manual Tests**  
1. **Ensure dependencies are installed**:  
   ```sh
   pip install -r requirements.txt
   ```  
2. **Run the test file**:  
   ```sh
   python tests/test_media_analysis_agent.py
   ```  

### **📍 Expected Output**  
✅ If the agent finds SAR-related articles, the console will show:  
```
✅ Found SAR-related articles:  

🔹 **Article 1**  
🔗 **URL:** https://example.com/rescue  
📄 **Title:** Rescue Teams Save Hikers in Colorado  
📖 **Summary:** SAR teams rescued three hikers stranded in Colorado after a sudden snowstorm...  
📝 **Relevance Explanation:** This article discusses a live search and rescue operation.  
```
🚨 If **no relevant SAR articles are found**, the output will be:  
```
⚠️ No relevant SAR articles found after verification.  
```
