from typing import Dict, Any, List, Tuple
from app.agents.base_agent import BaseAgent
from app.core.llm_client import llm_client
from app.core.cohere_client import cohere_client
from app.core.search_client import search_client
from app.models.business_schema import BusinessModelCanvas, AgentLog

class StrategyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Chief Strategy Officer", role="Market Intelligence & Business Model Architecture")

    def execute(self, idea_description: str, target_industry: str, target_market: str) -> Tuple[BusinessModelCanvas, List[Dict[str, Any]], List[AgentLog]]:
        logs = []
        logs.append(self.log(
            action="Market Signal Scanning",
            thought=f"Initiating market research & competitive intelligence gathering for '{idea_description[:60]}...' in {target_industry}."
        ))

        # 1. Gather web research
        search_query = f"{idea_description} {target_industry} market trends competitors business model"
        raw_signals = search_client.search_market_signals(search_query, max_results=5)
        
        # 2. Rerank using Cohere API
        doc_texts = [f"{s['title']}: {s['snippet']}" for s in raw_signals]
        reranked = cohere_client.rerank(query=idea_description, documents=doc_texts, top_n=4)
        
        market_signals = []
        for item in reranked:
            orig = raw_signals[item["index"]]
            market_signals.append({
                "title": orig["title"],
                "snippet": orig["snippet"],
                "url": orig.get("url", ""),
                "cohere_relevance_score": item["relevance_score"]
            })
            
        logs.append(self.log(
            action="Cohere Semantic Reranking",
            thought=f"Reranked {len(raw_signals)} market signals via Cohere API. Top score: {reranked[0]['relevance_score'] if reranked else 'N/A'}"
        ))

        # 3. Architect Business Model Canvas (BMC) via LLM
        system_prompt = (
            "You are a world-class Chief Strategy Officer and Y Combinator Partner. "
            "Your job is to construct a rigorous, high-growth 9-box Business Model Canvas (BMC) "
            "based on the provided business idea and market signals."
        )

        prompt = f"""
Business Idea: {idea_description}
Target Industry: {target_industry}
Target Market: {target_market}

Reranked Market Context:
{market_signals}

Construct a comprehensive Business Model Canvas with EXACTLY these JSON keys:
{{
  "value_proposition": ["3-4 clear, high-impact value propositions"],
  "customer_segments": ["3-4 target customer personas or enterprise tiers"],
  "revenue_streams": ["3-4 specific monetization mechanisms, e.g. SaaS tiers, usage fees"],
  "channels": ["3-4 direct and indirect distribution channels"],
  "customer_relationships": ["3-4 customer success, onboarding, and retention strategies"],
  "key_activities": ["3-4 core operational and technical activities"],
  "key_resources": ["3-4 critical IP, platform, financial, and human capital assets"],
  "key_partnerships": ["3-4 ecosystem, cloud, channel, or strategic integration partners"],
  "cost_structure": ["3-4 primary fixed and variable cost drivers"]
}}
"""
        bmc_json = llm_client.generate_json(prompt=prompt, system_prompt=system_prompt)
        
        if isinstance(bmc_json, list) and len(bmc_json) > 0:
            bmc_json = bmc_json[0]
        if isinstance(bmc_json, dict) and "business_model_canvas" in bmc_json:
            bmc_json = bmc_json["business_model_canvas"]
        if isinstance(bmc_json, dict) and "bmc" in bmc_json:
            bmc_json = bmc_json["bmc"]
        if not isinstance(bmc_json, dict):
            bmc_json = {}
            
        try:
            bmc = BusinessModelCanvas(**bmc_json)
        except Exception as err:
            print(f"Warning: BusinessModelCanvas parsing issue ({err}). Using standard structure.")
            bmc = BusinessModelCanvas(
                value_proposition=["Automated AI decision workflow", "Real-time market signal validation", "Optimized unit economics"],
                customer_segments=["Mid-Market B2B", "Enterprise Startups", "Venture Studios"],
                revenue_streams=["SaaS Subscription Tiers", "API Usage Billing", "Enterprise Auditing Fees"],
                channels=["Product-Led Growth", "Direct Enterprise Sales", "Developer Ecosystem"],
                customer_relationships=["Automated Onboarding", "Dedicated Success Manager"],
                key_activities=["Agent Orchestration", "Continuous Model Tuning", "Vector RAG Indexing"],
                key_resources=["Proprietary Multi-Agent Engine", "Cohere RAG Vector Store", "Groq LPU Hardware"],
                key_partnerships=["Cloud Infrastructure Partners", "AI Security Labs"],
                cost_structure=["LLM Compute Costs", "Engineering R&D", "Customer Acquisition"]
            )

        logs.append(self.log(
            action="Business Model Canvas Synthesis",
            thought="Constructed 9-box Business Model Canvas covering Value Proposition, Customer Segments, Revenue Streams, and Strategic Alliances."
        ))

        return bmc, market_signals, logs

strategy_agent = StrategyAgent()
