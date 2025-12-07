# github-issue-ai-assistant
AI-powered assistant that analyzes GitHub issues
# GitHub Issue AI Assistant

This is an end-to-end application that analyzes public GitHub issues using a Language Model (LLM) through the Hugging Face Inference Router.  
The system fetches issue details (title, body, comments), processes the text through a structured prompt, and returns a clean JSON summary that helps in issue triage and understanding.

---

##  Features

- Analyze **any public GitHub issue**
- Automatically fetch:
  - Issue title  
  - Issue description  
  - Comments  
- Generates structured JSON containing:
  - `summary`
  - `type` (bug / feature_request / documentation / question / other)
  - `priority_score`
  - `suggested_labels`
  - `potential_impact`
- Backend built with **FastAPI**
- Frontend built with **HTML + JavaScript**
- Uses **Hugging Face Router (OpenAI-compatible API)**

---

##  Tech Stack

### Backend
- Python  
- FastAPI  
- Uvicorn  
- Hugging Face Router API  
- HTTPX  
- python-dotenv  
- Pydantic  

### Frontend
- HTML  
- CSS  
- JavaScript  

---

##  Project Structure

```
Git_hub_issue_assistant_project/
│
├── backend/
│   ├── main.py
│   ├── openai_prompt.py
│   ├── requirements.txt
│   ├── .env.example
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│
└── README.md
```

---

##  Setup Instructions

### 1. Navigate to backend folder
```
cd backend
```

### 2. Create virtual environment
```
python -m venv .venv
```

### 3. Activate venv (Windows)
```
.\.venv\Scripts\activate
```

### 4. Install dependencies
```
pip install -r requirements.txt
```

### 5. Create `.env` file
```
copy .env.example .env
```

Edit the `.env` file:

```
HUGGINGFACE_API_KEY=hf_your_token_here
HUGGINGFACE_MODEL_ID=HuggingFaceTB/SmolLM3-3B:hf-inference
GITHUB_TOKEN=
```

### 6. Start backend server
```
uvicorn main:app --reload --port=8000
```

Backend will run at:
```
http://127.0.0.1:8000
```

### 7. Run frontend
Open this file in your browser:

```
frontend/index.html
```

---

##  How to Use

1. Enter a GitHub repository URL  
   Example:
   ```
   https://github.com/facebook/react
   ```
2. Enter an issue number  
   Example:
   ```
   29000
   ```
3. Click **Analyze Issue**

You will receive a JSON response similar to:

```json
{
  "summary": "Deprecation warning when using ReactDOMTestUtils.act.",
  "type": "bug",
  "priority_score": "4 - High impact on testing workflows.",
  "suggested_labels": ["bug", "react-testing"],
  "potential_impact": "Could cause unexpected behavior in future React versions."
}


```
##  Output Screenshot

<img width="1013" height="867"
     alt="App output"
     src="https://github.com/user-attachments/assets/34a5fdf6-6948-4160-a234-caa03b1939c4" />

---

##  Prompt Logic

Prompt construction happens inside:

```
backend/openai_prompt.py
```

The prompt includes:
- JSON schema  
- Example input/output  
- Strict format instructions  
- Enforcement of JSON-only output  

---

##  Error Handling

Backend handles:
- Invalid repository URL  
- Issue not found  
- GitHub API rate limits  
- Model responses containing:
  - `<think>` blocks  
  - Markdown fences like ```json  
  - Extra characters around JSON  
- JSON parsing errors  
- Network failures  

---

##  Future Improvements

- Add UI enhancements  
- Dark mode  
- Loading spinner  
- JSON export button  
- Model selection dropdown  
- History of analyzed issues  

---

##  License

This project is for educational and assessment purposes.  
Feel free to modify or extend it.





