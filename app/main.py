import os
import uvicorn
import requests
import urllib.request
import re
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.config import config
from app.models.business_schema import (
    AnalysisRequest, FullStrategyReport,
    SensitivitySimulationRequest, SensitivitySimulationResult
)
from app.agents.ceo_agent import ceo_agent
from app.agents.cfo_agent import cfo_agent
from app.core.llm_client import llm_client
from app.core.search_client import search_client

app = FastAPI(
    title="DecisionOS AI - Autonomous Multi-Agent Strategy Engine",
    description="Multi-agent platform with URL Ingestion, Node Architecture, and Terminal",
    version="5.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

latest_report_cache: Dict[str, FullStrategyReport] = {}

class AdminConfigUpdateRequest(BaseModel):
    groq_api_key: Optional[str] = None
    cohere_api_key: Optional[str] = None
    primary_model: Optional[str] = None
    fast_model: Optional[str] = None

class RedTeamChallengeRequest(BaseModel):
    vulnerability: str
    user_defense: str

class UrlIngestRequest(BaseModel):
    url: str

class AgentChatRequest(BaseModel):
    agent_id: str
    query: str

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "groq_api": bool(config.GROQ_API_KEY),
        "cohere_api": bool(config.COHERE_API_KEY),
        "primary_model": config.GROQ_MODEL_PRIMARY,
        "fast_model": config.GROQ_MODEL_FAST
    }

# --- ADMIN API KEY & CONFIGURATION PORTAL ENDPOINTS ---

@app.get("/api/admin/config")
def get_admin_config():
    groq_masked = f"{config.GROQ_API_KEY[:6]}...{config.GROQ_API_KEY[-4:]}" if len(config.GROQ_API_KEY) > 10 else "Not Configured"
    cohere_masked = f"{config.COHERE_API_KEY[:6]}...{config.COHERE_API_KEY[-4:]}" if len(config.COHERE_API_KEY) > 10 else "Not Configured"
    
    return {
        "groq_api_key_masked": groq_masked,
        "cohere_api_key_masked": cohere_masked,
        "primary_model": config.GROQ_MODEL_PRIMARY,
        "fast_model": config.GROQ_MODEL_FAST,
        "available_models": [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.6-27b",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768"
        ]
    }

@app.post("/api/admin/config")
def update_admin_config(req: AdminConfigUpdateRequest):
    config.update_keys(
        groq_key=req.groq_api_key,
        cohere_key=req.cohere_api_key,
        primary_model=req.primary_model,
        fast_model=req.fast_model
    )
    llm_client.api_key = config.GROQ_API_KEY
    llm_client.primary_model = config.GROQ_MODEL_PRIMARY
    llm_client.fast_model = config.GROQ_MODEL_FAST
    search_client.cohere_api_key = config.COHERE_API_KEY
    
    return {
        "message": "API keys and model configuration updated successfully!",
        "status": health_check()
    }

@app.post("/api/admin/test-keys")
def test_keys(req: AdminConfigUpdateRequest):
    test_groq_key = req.groq_api_key or config.GROQ_API_KEY
    test_cohere_key = req.cohere_api_key or config.COHERE_API_KEY
    
    groq_valid = False
    cohere_valid = False
    groq_msg = "Key not tested"
    cohere_msg = "Key not tested"

    if test_groq_key:
        try:
            import openai
            client = openai.OpenAI(api_key=test_groq_key, base_url="https://api.groq.com/openai/v1")
            res = client.models.list()
            groq_valid = True
            groq_msg = f"Connected successfully! {len(res.data)} models available."
        except Exception as e:
            groq_msg = f"Groq Error: {str(e)}"
    
    if test_cohere_key:
        try:
            import cohere
            co = cohere.Client(test_cohere_key)
            co.rerank(model="rerank-v3.5", query="test", documents=["test doc"], top_n=1)
            cohere_valid = True
            cohere_msg = "Connected successfully to Cohere Rerank API!"
        except Exception as e:
            cohere_msg = f"Cohere Error: {str(e)}"

    return {
        "groq": {"valid": groq_valid, "message": groq_msg},
        "cohere": {"valid": cohere_valid, "message": cohere_msg}
    }

# --- ADVANCED TECHNICAL INPUT: URL INGESTION ---

def extract_text_from_html(html_content: str) -> str:
    # A very basic regex based html tag stripper (sufficient for passing to LLM)
    text = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE|re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:8000] # Cap to avoid huge prompt

@app.post("/api/ingest-url")
def ingest_url(req: UrlIngestRequest):
    try:
        url = req.url if req.url.startswith("http") else "https://" + req.url
        
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res_http = requests.get(url, headers=headers, timeout=10)
        res_http.raise_for_status()
        
        html = res_http.text
        raw_text = extract_text_from_html(html)
        
        if not raw_text or len(raw_text) < 10:
            raise Exception("Extracted text is empty or too short.")

        prompt = f"""
We have scraped the following text from a URL: {url}
TEXT EXCERPT:
{raw_text}

Task: Extract the core business model, target audience, and main value proposition from this text. 
Return ONLY a concise 2-3 sentence business idea description that can be fed into an AI business simulator.
"""
        res = llm_client.generate(prompt=prompt, system_prompt="You are a data extractor.")
        return {"extracted_idea": res.strip()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch or parse URL: {str(e)}")


# --- ADVANCED TECHNICAL OUTPUT: AGENT TERMINAL ---

@app.post("/api/agent-chat")
def chat_with_agent(req: AgentChatRequest):
    latest_report = latest_report_cache.get("latest")
    context = ""
    if latest_report:
        context = f"Business Idea: {latest_report.business_model_canvas.value_proposition}\n"
    
    agent_prompts = {
        "ceo": "You are the CEO Orchestrator. Answer the query decisively based on the business context.",
        "cso": "You are the Chief Strategy Officer. Answer with market signal insights, competitive dynamics, and business model canvas strategy.",
        "cfo": "You are the CFO. Answer with financial metrics, ROI, and numeric pragmatism.",
        "cto": "You are the CTO. Answer with technical system design, architecture, and engineering facts.",
        "cmo": "You are the CMO. Answer with growth metrics, GTM strategy, and marketing hooks.",
        "redteam": "You are the Red Team Auditor. Answer pessimistically, identifying risks and vulnerabilities."
    }
    
    system_p = agent_prompts.get(req.agent_id.lower(), "You are an AI advisor.")
    
    prompt = f"{context}\n\nUser Query: {req.query}"
    res = llm_client.generate(prompt=prompt, system_prompt=system_p)
    return {"response": res}


# --- RED TEAM VS HUMAN INTERACTIVE CHALLENGER ARENA ---

@app.post("/api/redteam/challenge")
def challenge_red_team(req: RedTeamChallengeRequest):
    if not req.user_defense or len(req.user_defense.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please enter a meaningful counter-defense strategy.")
    
    system_prompt = "You are the Lead Adversarial Red Team Auditor evaluating a founder's counter-defense strategy against a identified venture vulnerability."
    prompt = f"""
Identified Vulnerability: {req.vulnerability}
Founder Counter-Defense Strategy: {req.user_defense}

Evaluate the defense and return JSON:
{{
  "defense_score": 88.0,
  "verdict": "ACCEPTED or NEEDS_WORK or REJECTED",
  "red_team_critique": "Detailed critique of the founder's defense strategy...",
  "residual_risk_pct": 12.0,
  "actionable_enhancements": ["Enhancement 1", "Enhancement 2"]
}}
"""
    res = llm_client.generate_json(prompt=prompt, system_prompt=system_prompt)
    return res

# --- CORE ANALYSIS & SIMULATION ENDPOINTS ---

@app.post("/api/analyze", response_model=FullStrategyReport)
def analyze_business(req: AnalysisRequest):
    if not req.idea_description or len(req.idea_description.strip()) < 5:
        raise HTTPException(status_code=400, detail="Please provide a valid business idea description (at least 5 characters).")
    
    try:
        report = ceo_agent.run_full_analysis(req)
        latest_report_cache["latest"] = report
        return report
    except Exception as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate", response_model=SensitivitySimulationResult)
def simulate_sensitivity(sim_req: SensitivitySimulationRequest):
    latest_report = latest_report_cache.get("latest")
    if not latest_report:
        raise HTTPException(status_code=400, detail="No active business analysis report found. Please run an analysis first.")
    
    try:
        result = cfo_agent.simulate_sensitivity(latest_report.financials, sim_req)
        return result
    except Exception as e:
        print(f"Error during simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "DecisionOS Backend API is running."}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=config.API_HOST, port=config.API_PORT, reload=True)
