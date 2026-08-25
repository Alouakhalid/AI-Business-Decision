from typing import Dict, Any, List, Tuple
from app.agents.base_agent import BaseAgent
from app.core.llm_client import llm_client
from app.models.business_schema import GrowthStrategy, AgentLog

class CMOAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Chief Marketing Officer", role="Go-to-Market, Growth Engine & Positioning")

    def execute(self, idea_description: str, target_segments: List[str], value_prop: List[str]) -> Tuple[GrowthStrategy, List[AgentLog]]:
        logs = []
        logs.append(self.log(
            action="Go-To-Market Strategy Design",
            thought="Formulating customer acquisition funnels, positioning messaging, viral acquisition loops, and pricing tier packages."
        ))

        system_prompt = (
            "You are a top growth executive (ex-Reforge / ex-Stripe CMO). "
            "Build an aggressive Go-To-Market strategy, pricing breakdown, and viral acquisition loop."
        )

        prompt = f"""
Business Idea: {idea_description}
Target Customer Segments: {target_segments}
Value Proposition: {value_prop}

Provide Growth Strategy in JSON format matching:
{{
  "primary_acquisition_channels": ["3-4 growth channels, e.g. Product-Led Growth, Cold Outbound, Search SEO, Strategic Integrations"],
  "viral_coefficient_target": 1.35,
  "positioning_hook": "A 1-sentence memorable killer tagline/hook.",
  "pricing_tiers": [
    {{"tier": "Starter", "price": "$49/mo", "features": ["Feature A", "Feature B"]}},
    {{"tier": "Pro", "price": "$199/mo", "features": ["All Starter", "Advanced AI Agent", "Cohere Rerank API"]}},
    {{"tier": "Enterprise", "price": "Custom ($1,500+/mo)", "features": ["Dedicated VPC", "Custom Agent Fine-tuning"]}}
  ],
  "gtm_tactics_30_60_90": {{
    "day_0_30": ["Launch Beta", "Outreach to 100 ICP accounts"],
    "day_31_60": ["SEO Content Engine", "Partner App Marketplace listing"],
    "day_61_90": ["Automated Referral Incentive", "Enterprise Sales Motions"]
  }}
}}
"""
        growth_json = llm_client.generate_json(prompt=prompt, system_prompt=system_prompt)
        growth = GrowthStrategy(**growth_json)

        logs.append(self.log(
            action="GTM Execution Plan Synthetic Complete",
            thought=f"Established 3-tier pricing strategy with target viral K-factor of {growth.viral_coefficient_target}x."
        ))

        return growth, logs

cmo_agent = CMOAgent()
