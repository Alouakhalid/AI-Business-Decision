from typing import List, Tuple
from app.agents.base_agent import BaseAgent
from app.core.llm_client import llm_client
from app.models.business_schema import TechArchitecture, AgentLog

class CTOAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Chief Technology Officer", role="Technical Architecture & Engineering Strategy")

    def execute(self, idea_description: str, key_activities: List[str]) -> Tuple[TechArchitecture, List[AgentLog]]:
        logs = []
        logs.append(self.log(
            action="System Architecture Design",
            thought="Designing optimal tech stack, estimating cloud infrastructure costs, and mapping interactive architecture nodes."
        ))

        system_prompt = (
            "You are an elite CTO who builds scalable, high-performance SaaS platforms. "
            "Design the technical architecture and output a valid JSON adhering exactly to the requested schema. "
            "You must generate 'architecture_nodes' and 'architecture_edges' to be rendered as an interactive graph."
        )

        prompt = f"""
Business Idea: {idea_description}
Key Operations: {key_activities}

Generate JSON for the technical architecture:
{{
  "recommended_stack": ["Next.js Frontend", "FastAPI Python Backend", "PostgreSQL", "Redis"],
  "ai_infra_requirements": ["Groq LPU Inference", "Cohere Semantic Search", "Pinecone Vector DB"],
  "monthly_infra_cost_usd": 1250.0,
  "build_vs_buy_recommendation": "Build core AI orchestration, buy authentication (Auth0) and payments (Stripe).",
  "mvp_timeline_weeks": 8,
  "key_technical_risks": ["Data privacy compliance", "High LLM API latency"],
  "architecture_nodes": [
    {{
      "id": "frontend",
      "label": "Next.js Web App",
      "type": "frontend",
      "description": "User dashboard & interactive UI",
      "cost_estimate": "$20/mo (Vercel)"
    }},
    {{
      "id": "backend",
      "label": "FastAPI Orchestrator",
      "type": "backend",
      "description": "API Gateway and Agent Swarm logic",
      "cost_estimate": "$150/mo (AWS ECS)"
    }},
    {{
      "id": "db",
      "label": "PostgreSQL DB",
      "type": "database",
      "description": "Relational storage for user accounts",
      "cost_estimate": "$50/mo (RDS)"
    }},
    {{
      "id": "ai",
      "label": "Groq LLM API",
      "type": "ai_model",
      "description": "Fast LPU Inference for agents",
      "cost_estimate": "$0.50 per 1M tokens"
    }}
  ],
  "architecture_edges": [
    {{"source": "frontend", "target": "backend", "label": "REST/WebSocket"}},
    {{"source": "backend", "target": "db", "label": "SQL Queries"}},
    {{"source": "backend", "target": "ai", "label": "API Calls"}}
  ]
}}
"""
        tech_json = llm_client.generate_json(prompt=prompt, system_prompt=system_prompt)
        
        if isinstance(tech_json, list) and len(tech_json) > 0:
            tech_json = tech_json[0]
        if isinstance(tech_json, dict) and "tech_architecture" in tech_json:
            tech_json = tech_json["tech_architecture"]
        if not isinstance(tech_json, dict):
            tech_json = {}

        try:
            tech = TechArchitecture(**tech_json)
        except Exception as err:
            print(f"Warning: TechArchitecture parsing issue ({err}). Using standard structure.")
            tech = TechArchitecture(
                recommended_stack=["Next.js", "FastAPI", "PostgreSQL", "Redis"],
                ai_infra_requirements=["Groq LPU Inference", "Cohere Semantic Rerank"],
                monthly_infra_cost_usd=850.0,
                build_vs_buy_recommendation="Build core multi-agent engine, buy Auth0 and Stripe billing.",
                mvp_timeline_weeks=6,
                key_technical_risks=["API Rate Limits", "Token Latency"],
                architecture_nodes=[
                    {"id": "node-1", "label": "Web Client Portal", "type": "frontend", "cost_estimate": "$20/mo", "description": "Single-page responsive Web app"},
                    {"id": "node-2", "label": "FastAPI Orchestrator", "type": "backend", "cost_estimate": "$80/mo", "description": "Async REST API gateway"},
                    {"id": "node-3", "label": "Vector RAG Store", "type": "database", "cost_estimate": "$60/mo", "description": "Cohere semantic search index"},
                    {"id": "node-4", "label": "Groq LPU Inference Pool", "type": "ai_model", "cost_estimate": "$150/mo", "description": "Multi-agent model pool"}
                ],
                architecture_edges=[
                    {"source": "node-1", "target": "node-2", "label": "HTTPS REST / WS"},
                    {"source": "node-2", "target": "node-3", "label": "Cohere Embed / RAG"},
                    {"source": "node-2", "target": "node-4", "label": "Groq LPU API"}
                ]
            )

        logs.append(self.log(
            action="Architecture Mapped",
            thought=f"Selected {tech.recommended_stack[0]} and {tech.ai_infra_requirements[0]}. Generated {len(tech.architecture_nodes)} nodes for the interactive architecture graph."
        ))

        return tech, logs

cto_agent = CTOAgent()
