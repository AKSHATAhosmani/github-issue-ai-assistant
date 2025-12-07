"""
FastAPI backend using Hugging Face Router (OpenAI-compatible API).

- Takes GitHub repo URL + issue number
- Fetches issue + comments from GitHub
- Sends prompt to HF Router as an OpenAI chat completion
- Expects JSON back from the model
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import httpx
import os
import re
import json

from openai import OpenAI
from openai_prompt import build_prompt

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
HF_MODEL_ID = os.getenv("HUGGINGFACE_MODEL_ID", "HuggingFaceTB/SmolLM3-3B:hf-inference")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not HF_API_KEY:
    raise RuntimeError("HUGGINGFACE_API_KEY not set in .env")

# Hugging Face router base URL (OpenAI-compatible)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_API_KEY,
)

GITHUB_API_HEADERS = {"Accept": "application/vnd.github.v3+json"}
if GITHUB_TOKEN:
    GITHUB_API_HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

app = FastAPI(title="GitHub Issue AI Assistant (HF Router)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    repo_url: str
    issue_number: int


@app.post("/analyze_issue")
async def analyze_issue(req: AnalyzeRequest):
    owner_repo = extract_owner_repo(req.repo_url)
    if not owner_repo:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

    owner, repo = owner_repo

    # --- Fetch issue + comments from GitHub ---
    async with httpx.AsyncClient() as http_client:
        issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{req.issue_number}"
        issue_resp = await http_client.get(issue_url, headers=GITHUB_API_HEADERS, timeout=30.0)
        if issue_resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Issue not found")
        issue_resp.raise_for_status()
        issue = issue_resp.json()

        comments = []
        if issue.get("comments", 0) > 0 and issue.get("comments_url"):
            comments_resp = await http_client.get(issue["comments_url"], headers=GITHUB_API_HEADERS, timeout=30.0)
            comments_resp.raise_for_status()
            comments = [c.get("body", "") for c in comments_resp.json()]

    combined_text = "\n\n".join(
        [
            issue.get("title", "") or "",
            issue.get("body", "") or "",
            "\n\nComments:\n" + "\n---\n".join(comments) if comments else "",
        ]
    )

    if len(combined_text) > 15000:
        combined_text = combined_text[:15000] + "\n\n[TRUNCATED]"

    prompt = build_prompt(combined_text)

    # --- Call Hugging Face Router using OpenAI-compatible client ---
    try:
        response = client.chat.completions.create(
            model=HF_MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that MUST return only valid JSON matching the requested schema.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.0,
            max_tokens=500,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM request failed: {e}")

    # Extract text content
    try:
        text = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected LLM response format: {e}")

    # Parse JSON from the model output
        # --- Parse JSON from the model output (cleaning away extra markup) ---
    cleaned = text.strip()

    # Remove <think>...</think> blocks if present
    if "<think>" in cleaned:
        # crude but effective: drop everything before the first '{'
        pass

    # If the model wrapped output in ```json ... ``` fences, strip them
    if cleaned.startswith("```"):
        # remove leading ``` or ```json
        cleaned = cleaned.lstrip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].lstrip()
    if cleaned.endswith("```"):
        cleaned = cleaned.rstrip("`").rstrip()

    # Extract the JSON object between the first '{' and last '}'
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise HTTPException(
            status_code=500,
            detail=f"Could not locate JSON in model output:\n{cleaned}",
        )

    json_str = cleaned[start : end + 1]

    try:
        parsed = json.loads(json_str)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JSON. Error: {e}\nRaw JSON string:\n{json_str}",
        )

    return parsed



def extract_owner_repo(url: str):
    """Extract owner/repo from a GitHub URL."""
    m = re.search(r"github.com/([^/]+/[^/]+)", url)
    if not m:
        return None
    owner_repo = m.group(1).rstrip("/")
    owner, repo = owner_repo.split("/")
    return owner, repo
