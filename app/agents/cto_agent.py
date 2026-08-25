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

        def normalize_str_list(lst):
            if not isinstance(lst, list):
                return []
            res = []
            for item in lst:
                if isinstance(item, str):
                    res.append(item)
                elif isinstance(item, dict):
                    name = item.get("name") or item.get("technology") or item.get("label") or (list(item.values())[0] if item.values() else str(item))
                    desc = item.get("description") or ""
                    res.append(f"{name}: {desc}".strip(": "))
                else:
                    res.append(str(item))
            return res

        for field_name in ["recommended_stack", "ai_infra_requirements", "key_technical_risks"]:
            if field_name in tech_json:
                tech_json[field_name] = normalize_str_list(tech_json[field_name])

        if "build_vs_buy_recommendation" in tech_json and not isinstance(tech_json["build_vs_buy_recommendation"], str):
            tech_json["build_vs_buy_recommendation"] = str(tech_json["build_vs_buy_recommendation"])

        try:
            tech = TechArchitecture(**tech_json)
        except Exception as err:
            print(f"Warning: TechArchitecture parsing issue ({err}). Using standard structure.")
            tech = TechArchitecture(
                recommended_stack=["Next.js Frontend", "FastAPI Core", "PostgreSQL Database", "Redis Cache"],
                ai_infra_requirements=["Groq LPU Acceleration", "Cohere RAG Index"],
                monthly_infra_cost_usd=450.0,
                build_vs_buy_recommendation="Build core multi-agent logic; buy third-party auth and payment gateways.",
                mvp_timeline_weeks=8,
                key_technical_risks=["API Rate Limit Bottlenecks", "Model Latency Variance"],
                architecture_nodes=[
                    TechNode(id="frontend", label="Web Client Portal", type="frontend", description="Interactive User Dashboard", cost_estimate="$20/mo"),
                    TechNode(id="backend", label="FastAPI Orchestrator", type="backend", description="Multi-Agent Pipeline Engine", cost_estimate="$150/mo"),
                    TechNode(id="database", label="PostgreSQL & Redis", type="database", description="Persistent State & Cache", cost_estimate="$80/mo"),
                    TechNode(id="ai_model", label="Groq LPU Inference", type="ai_model", description="Llama 3 70B High Speed LLM", cost_estimate="$200/mo")
                ],
                architecture_edges=[
                    TechEdge(source="frontend", target="backend", label="HTTPS / WSS"),
                    TechEdge(source="backend", target="database", label="SQL Connection"),
                    TechEdge(source="backend", target="ai_model", label="REST API Calls")
                ]
            )

        logs.append(self.log(
            action="Architecture Mapped",
            thought=f"Selected {tech.recommended_stack[0]} and {tech.ai_infra_requirements[0]}. Generated {len(tech.architecture_nodes)} nodes for the interactive architecture graph."
        ))

        return tech, logs

cto_agent = CTOAgent()
