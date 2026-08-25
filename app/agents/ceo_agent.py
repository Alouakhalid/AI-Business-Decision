from typing import Dict, Any, List, Tuple
from app.agents.base_agent import BaseAgent
from app.agents.strategy_agent import strategy_agent
from app.agents.cfo_agent import cfo_agent
from app.agents.cto_agent import cto_agent
from app.agents.cmo_agent import cmo_agent
from app.agents.redteam_agent import redteam_agent
from app.core.llm_client import llm_client
from app.models.business_schema import (
    FullStrategyReport, StrategicRadar, AnalysisRequest, AgentLog,
    BoardroomDebateSession, DebateMessage, CompetitorPosition,
    CompetitiveLandscapeMatrix, PitchSlide, GTMMarketingAssets
)

class CEOAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CEO Orchestrator", role="Executive Deliberation, Strategic Alignment & Final Synthesis")

    def run_full_analysis(self, req: AnalysisRequest) -> FullStrategyReport:
        all_logs: List[AgentLog] = []

        all_logs.append(self.log(
            action="Deliberation Pipeline Initiated",
            thought=f"Deploying multi-agent executive board to analyze: '{req.idea_description}'"
        ))

        # Step 1: Strategy Agent (BMC + Cohere Rerank)
        bmc, market_signals, strategy_logs = strategy_agent.execute(
            idea_description=req.idea_description,
            target_industry=req.target_industry or "Technology",
            target_market=req.target_market or "Global B2B"
        )
        all_logs.extend(strategy_logs)

        # Step 2: CFO Agent (Financial Projections)
        fin, cfo_logs = cfo_agent.execute(
            idea_description=req.idea_description,
            initial_budget_usd=req.initial_budget_usd or 100000.0,
            revenue_streams=bmc.revenue_streams
        )
        all_logs.extend(cfo_logs)

        # Step 3: CTO Agent (Technical Architecture)
        tech, cto_logs = cto_agent.execute(
            idea_description=req.idea_description,
            key_activities=bmc.key_activities
        )
        all_logs.extend(cto_logs)

        # Step 4: CMO Agent (Growth & GTM Strategy)
        growth, cmo_logs = cmo_agent.execute(
            idea_description=req.idea_description,
            target_segments=bmc.customer_segments,
            value_prop=bmc.value_proposition
        )
        all_logs.extend(cmo_logs)

        # Step 5: Red Team Agent (Adversarial Audit)
        risk, redteam_logs = redteam_agent.execute(
            idea_description=req.idea_description,
            bmc_dict=bmc.model_dump() if hasattr(bmc, 'model_dump') else bmc.dict(),
            financial_dict=fin.model_dump() if hasattr(fin, 'model_dump') else fin.dict()
        )
        all_logs.extend(redteam_logs)

        # Step 6: CEO Synthesis, Strategic Radar Scoring & Viability Score
        all_logs.append(self.log(
            action="Executive Scoring & Consensus Synthesis",
            thought="Synthesizing multi-agent outputs, computing 6-axis strategic radar matrix and final Viability Score."
        ))

        margin_score = min(100.0, max(20.0, fin.unit_economics.gross_margin_pct * 1.1))
        ltv_cac_score = min(100.0, max(20.0, fin.unit_economics.ltv_cac_ratio * 12.0))
        risk_safety_score = max(10.0, 100.0 - risk.failure_risk_index)
        
        radar = StrategicRadar(
            market_demand=round(min(98.0, max(45.0, 85.0 + (len(market_signals) * 2))), 1),
            tech_feasibility=round(min(95.0, max(40.0, 100.0 - (tech.mvp_timeline_weeks * 4))), 1),
            margin_profile=round(margin_score, 1),
            defensive_moat=round(min(95.0, max(30.0, ltv_cac_score)), 1),
            scalability=round(min(98.0, max(50.0, (fin.annual_revenue.year3 / max(1.0, fin.operating_expenses.year3)) * 40)), 1),
            regulatory_safety=round(risk_safety_score, 1)
        )

        viability_score = round(
            (radar.market_demand * 0.20) +
            (radar.tech_feasibility * 0.15) +
            (radar.margin_profile * 0.20) +
            (radar.defensive_moat * 0.15) +
            (radar.scalability * 0.15) +
            (radar.regulatory_safety * 0.15),
            1
        )

        # --- ADVANCED FEATURE GENERATION ---

        # 1. Monte Carlo Stochastic Risk Simulation (1,000 Runs)
        monte_carlo_res = cfo_agent.run_monte_carlo(fin, num_trials=1000)

        # 2. Boardroom Multi-Round Agent Debate
        system_prompt_debate = "You are orchestrating a heated C-Suite boardroom debate between Red Team, CFO, and CTO regarding business vulnerabilities."
        prompt_debate = f"""
Business Idea: {req.idea_description}
Top Risk: {risk.critical_vulnerabilities[0].vulnerability if risk.critical_vulnerabilities else 'Customer acquisition friction'}
CFO CAC: ${fin.unit_economics.cac}
CTO Infra Spend: ${tech.monthly_infra_cost_usd}

Generate JSON for a 3-round C-Suite Debate matching:
{{
  "topic": "Unit Economics Feasibility & Competitive Defensibility",
  "rounds": [
    {{
      "speaker": "Adversarial Red Team Lead",
      "role": "Risk Auditor",
      "argument": "The estimated CAC of ${fin.unit_economics.cac} is far too optimistic. Enterprise sales cycles will push CAC past $1,200, eroding initial gross margins.",
      "counter_proposal": "Pivot to Product-Led Growth (PLG) self-serve tier to lower CAC before attacking enterprise sales."
    }},
    {{
      "speaker": "Chief Financial Officer",
      "role": "Financial Strategist",
      "argument": "If CAC rises to $1,200, our LTV of ${fin.unit_economics.ltv} still yields a 2.0x payback. However, introducing a PLG tier accelerates early cash flow.",
      "counter_proposal": "Cap initial enterprise sales headcount and reallocate budget to automated inbound SEO funnels."
    }},
    {{
      "speaker": "Chief Technology Officer",
      "role": "Systems Architect",
      "argument": "By utilizing Groq fast Llama inference and Cohere reranking, we keep per-query API latency under 200ms, protecting software gross margins at 78%.",
      "counter_proposal": "Deploy localized vector caching to reduce LLM token overhead by 35%."
    }}
  ],
  "consensus_resolution": "The C-Suite agrees to adopt a hybrid PLG + Enterprise motion, caching LLM queries via Groq/Cohere to defend 78% margins.",
  "revised_viability_score": {viability_score}
}}
"""
        debate_json = llm_client.generate_json(prompt=prompt_debate, system_prompt=system_prompt_debate)
        boardroom_debate = BoardroomDebateSession(**debate_json)

        # 3. 2x2 Competitive Positioning Matrix
        system_prompt_comp = "You are a competitive intelligence director. Map top 3 competitors and the proposed venture on a 2x2 matrix."
        prompt_comp = f"""
Business: {req.idea_description}
Industry: {req.target_industry}

Generate JSON for 2x2 Competitive Landscape matching:
{{
  "competitors": [
    {{
      "name": "Legacy Enterprise Incumbent",
      "x_feature_depth": 85.0,
      "y_price_point": 90.0,
      "strengths": ["Strong brand recognition", "Existing enterprise contracts"],
      "weaknesses": ["Slow legacy software", "High seat cost"],
      "cohere_relevance_score": 0.88
    }},
    {{
      "name": "Niche AI Tool",
      "x_feature_depth": 40.0,
      "y_price_point": 25.0,
      "strengths": ["Low cost", "Quick signup"],
      "weaknesses": ["Lack of enterprise security", "No multi-agent workflows"],
      "cohere_relevance_score": 0.76
    }}
  ],
  "proposed_position": {{
    "name": "Proposed Venture (DecisionOS Blueprint)",
    "x_feature_depth": 92.0,
    "y_price_point": 55.0,
    "strengths": ["Autonomous multi-agent orchestration", "Fast Groq processing & Cohere Rerank"],
    "weaknesses": ["New brand in market"],
    "cohere_relevance_score": 0.98
  }},
  "strategic_moat_verdict": "Venture occupies the High Feature Depth + Moderate Pricing sweet spot, outperforming legacy tools on velocity."
}}
"""
        comp_json = llm_client.generate_json(prompt=prompt_comp, system_prompt=system_prompt_comp)
        comp_matrix = CompetitiveLandscapeMatrix(**comp_json)

        # 4. 6 Interactive Pitch Deck Slides
        system_prompt_pitch = "Generate a venture capital pitch deck outline (6 slides) for founders."
        prompt_pitch = f"""
Business Title: {req.idea_description}
Year 3 Target ARR: ${fin.annual_revenue.year3:,.2f}
LTV/CAC: {fin.unit_economics.ltv_cac_ratio}x

Generate JSON matching array of 6 pitch slides:
{{
  "slides": [
    {{"slide_number": 1, "title": "Problem & Market Opportunity", "bullet_points": ["Point 1", "Point 2"], "visual_type": "quote", "speaker_notes": "Opening hook"}},
    {{"slide_number": 2, "title": "The Solution & AI Tech Architecture", "bullet_points": ["Point 1", "Point 2"], "visual_type": "grid", "speaker_notes": "Tech advantage"}},
    {{"slide_number": 3, "title": "Business Model & Unit Economics", "bullet_points": ["Point 1", "Point 2"], "visual_type": "metric", "speaker_notes": "Monetization details"}},
    {{"slide_number": 4, "title": "3-Year Financial Forecast", "bullet_points": ["Point 1", "Point 2"], "visual_type": "chart", "speaker_notes": "Revenue trajectory"}},
    {{"slide_number": 5, "title": "Go-To-Market & Growth Loops", "bullet_points": ["Point 1", "Point 2"], "visual_type": "grid", "speaker_notes": "Acquisition engine"}},
    {{"slide_number": 6, "title": "Risk Audit & Red Team Defense", "bullet_points": ["Point 1", "Point 2"], "visual_type": "quote", "speaker_notes": "Defensibility"}},
  ]
}}
"""
        pitch_json = llm_client.generate_json(prompt=prompt_pitch, system_prompt=system_prompt_pitch)
        pitch_slides = [PitchSlide(**s) for s in pitch_json.get("slides", [])]

        # 5. Automated GTM Assets & Python Code Snippet
        system_prompt_gtm = "Generate GTM copy assets and Python developer integration code snippet."
        prompt_gtm = f"""
Business: {req.idea_description}
Positioning Hook: {growth.positioning_hook}

Generate JSON matching:
{{
  "outbound_email_sequence": [
    {{"subject": "Automating {req.target_industry} workflows with AI", "body": "Hi {{FirstName}}, ..."}}
  ],
  "product_hunt_tagline": "The autonomous multi-agent engine for enterprise decisions.",
  "product_hunt_description": "Deploy AI C-Suite agents to research, score, and model business ventures in seconds.",
  "python_integration_snippet": "import requests\\n\\nres = requests.post('https://api.ventureos.ai/v1/analyze', json={{'concept': '{req.idea_description[:30]}...'}})\\nprint(res.json())"
}}
"""
        gtm_json = llm_client.generate_json(prompt=prompt_gtm, system_prompt=system_prompt_gtm)
        gtm_assets = GTMMarketingAssets(**gtm_json)

        # Executive Summary Generation
        system_prompt_meta = "You are the CEO & General Partner. Write a concise, commanding Executive Summary & Title for this strategic business blueprint."
        prompt_meta = f"""
Business Idea: {req.idea_description}
Viability Score: {viability_score}/100
Key Value Prop: {bmc.value_proposition[0] if bmc.value_proposition else ''}
Year 3 Target ARR: ${fin.annual_revenue.year3:,.2f}
LTV/CAC: {fin.unit_economics.ltv_cac_ratio}x

Provide JSON:
{{
  "project_title": "Memorable Product/Company Name (2-4 words)",
  "executive_summary": "High-impact 3-paragraph executive summary detailing strategic opportunity, capital efficiency, tech edge, and execution roadmap."
}}
"""
        exec_meta = llm_client.generate_json(prompt=prompt_meta, system_prompt=system_prompt_meta)

        all_logs.append(self.log(
            action="Deliberation Finalized",
            thought=f"Analysis complete. Assigned Viability Score of {viability_score}/100. Advanced Pitch Slides, Monte Carlo, and Debate modules compiled."
        ))

        return FullStrategyReport(
            project_title=exec_meta.get("project_title", "Venture Blueprint"),
            executive_summary=exec_meta.get("executive_summary", "Comprehensive business strategic analysis."),
            viability_score=viability_score,
            business_model_canvas=bmc,
            financials=fin,
            tech_architecture=tech,
            growth_strategy=growth,
            risk_assessment=risk,
            strategic_radar=radar,
            market_signals=market_signals,
            agent_logs=all_logs,
            boardroom_debate=boardroom_debate,
            monte_carlo=monte_carlo_res,
            competitive_matrix=comp_matrix,
            pitch_slides=pitch_slides,
            gtm_assets=gtm_assets
        )

ceo_agent = CEOAgent()
