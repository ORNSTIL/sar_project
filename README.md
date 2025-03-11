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
1. **Set up Python environment**:
   ```sh
   # Using pyenv (recommended)
   pyenv install 3.9.6  # or your preferred version
   pyenv local 3.9.6

   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate     # On Windows
   ```
2. **Ensure dependencies are installed**:  
   ```sh
   pip install -r requirements.txt
   ```  
3. **Run the test file**:  
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

### ** Insights**  
From the feedback received, I learned that having both the "Found SAR-related articles" and "No SAR-related articles found" responses simultaneously was confusing for users. This was actually a bug which I did not find when testing, and I was able to fix it by updating my implementation of the **tests/test_media_analysis_agent.py** file. This bug made the output look cluttered and contradicted itself when no relevant articles were found. The suggestion to streamline this response improved the clarity and professionalism of the agent's output. Additionally, the recommendation to expand the README to include detailed instructions for setting up a Python virtual environment was valuable, as it makes sure that users with different levels of technical expertise can set up and test the agent easily.

### ** Modifications**
In response to the feedback, I modified the code in the file which tests the media analysis agent to ensure that the "Found SAR-related articles" message is only displayed if relevant articles are indeed found. This file is located at **tests/test_media_analysis_agent.py**. Now, if no articles pass the relevance check, only the "No SAR-related articles found" message is displayed, making the output clearer and more user-friendly. I also updated this file to send an additional message, *"Please make a new request with additional or different query words."* which I feel adds clarity to a user input which resulted in no results from the agent. Furthermore, I updated the README to include steps for setting up a Python virtual environment, similar to the instructions which Riley provided in her repository. This modification makes the setup process smoother for new users and helps prevent common errors during installation and testing.
