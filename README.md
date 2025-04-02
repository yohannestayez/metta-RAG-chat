# Knowledge Graph Chatbot

Using a **MeTTa**-based knowledge graph, a flexible and expressive language designed for defining, querying, and reasoning over dynamic hypergraphs within an atomspace. By transforming raw PDF content into structured data stored in `.metta` files, MeTTa enables the chatbot to offer insightful, fact-based answers.

---

## Overview

- **MeTTa-Powered Knowledge Graph:** Convert PDF data into structured information stored in `metta` files, ensuring efficient fact management and up-to-date knowledge.
- **Intelligent Responses:** Utilize the Gemini API along with short- and long-term memory to deliver context-aware answers based on the evolving MeTTa knowledge graph.
- **User Interaction:** A streamlined web interface allows for easy PDF uploads and question submissions.

---

## Project Structure

```
project_root/
│
├── src/
│   ├── chatbot.py         # Handles chatbot logic, query parsing, and response generation
│   ├── extractor.py       # Processes PDFs, extracts text, summarizes, and converts to JSON
│   ├── gemini.py          # Integrates with the Gemini API for response generation
│   ├── KG_add.py          # Updates the knowledge base with new information from PDFs
│   ├── metta_handler.py   # Manages interactions with MeTTa, including queries and facts
│   └── prompts.py         # Contains prompts for entity extraction, schema building, etc.
├──main.py                   # Flask application
├── metta/                  
│   ├── knowledge_base.metta # Structured knowledge graph data (initially empty)
│   └── user_memory.metta    # User-specific long term memory (initially empty)
└── templates/               # HTML templates for the web interface
```

---


1. **Configure:**
   - Create a `.env` file in the project root.
   - Add your Gemini API key:
     ```
     GEMINI_API=your_api_key_here
     ```

2. **Run the App:**
   ```bash
   python main.py
   ```
   - Open your browser at `http://localhost:5000`.
   - Upload PDFs to enrich the MeTTa-powered knowledge graph.
   - Submit queries and receive intelligent, data-driven responses.
