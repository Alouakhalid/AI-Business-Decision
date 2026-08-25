from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class BusinessModelCanvas(BaseModel):
    value_proposition: List[str] = Field(default_factory=lambda: ["AI-powered contract analysis"])
    customer_segments: List[str] = Field(default_factory=lambda: ["Enterprise Legal Teams", "SMB In-House Counsel"])
    revenue_streams: List[str] = Field(default_factory=lambda: ["SaaS Subscription Tiers", "Usage-Based API Fees"])
    channels: List[str] = Field(default_factory=lambda: ["Direct Sales", "Partner Integrations"])
    customer_relationships: List[str] = Field(default_factory=lambda: ["Dedicated Account Managers", "Self-Service Onboarding"])
    key_activities: List[str] = Field(default_factory=lambda: ["LLM Fine-Tuning", "Security Auditing"])
    key_resources: List[str] = Field(default_factory=lambda: ["Proprietary Legal Datasets", "Cloud AI Infrastructure"])
    key_partnerships: List[str] = Field(default_factory=lambda: ["Cloud Providers", "Legal Management Platforms"])
    cost_structure: List[str] = Field(default_factory=lambda: ["Compute & Inference Costs", "Sales & Marketing Expense"])

class FinancialMetric(BaseModel):
    year1: float = 150000.0
    year2: float = 450000.0
    year3: float = 1200000.0

class UnitEconomics(BaseModel):
    cac: float = 350.0
    ltv: float = 2400.0
    ltv_cac_ratio: float = 6.85
    payback_months: float = 6.0
    gross_margin_pct: float = 82.0
    breakeven_month: int = 14

class FinancialProjections(BaseModel):
    annual_revenue: FinancialMetric = Field(default_factory=FinancialMetric)
    operating_expenses: FinancialMetric = Field(default_factory=FinancialMetric)
    net_profit: FinancialMetric = Field(default_factory=FinancialMetric)
    mrr_end_of_year: FinancialMetric = Field(default_factory=FinancialMetric)
    unit_economics: UnitEconomics = Field(default_factory=UnitEconomics)
    pricing_summary: str = "B2B SaaS Tiered Pricing ($99 - $999/mo)"

class TechNode(BaseModel):
    id: str = "node_1"
    label: str = "FastAPI Service"
    type: str = "backend"
    description: str = "Core API Engine"
    cost_estimate: str = "$100/mo"

class TechEdge(BaseModel):
    source: str = "node_1"
    target: str = "node_2"
    label: str = "HTTPS"

class TechArchitecture(BaseModel):
    recommended_stack: List[str] = Field(default_factory=lambda: ["Next.js", "FastAPI", "PostgreSQL", "Redis"])
    ai_infra_requirements: List[str] = Field(default_factory=lambda: ["Groq LPU", "Cohere Vector RAG"])
    monthly_infra_cost_usd: float = 450.0
    build_vs_buy_recommendation: str = "Build core orchestration logic; buy Auth0 and Stripe billing."
    mvp_timeline_weeks: int = 8
    key_technical_risks: List[str] = Field(default_factory=lambda: ["API Rate Limits", "LLM Latency Variance"])
    architecture_nodes: List[TechNode] = Field(default_factory=list)
    architecture_edges: List[TechEdge] = Field(default_factory=list)

class GrowthStrategy(BaseModel):
    primary_acquisition_channels: List[str] = Field(default_factory=lambda: ["Outbound Sales", "SEO Content Marketing"])
    viral_coefficient_target: float = 1.2
    positioning_hook: str = "Automate 90% of legal review time with zero compromise on accuracy."
    pricing_tiers: List[Dict[str, Any]] = Field(default_factory=list)
    gtm_tactics_30_60_90: Dict[str, List[str]] = Field(default_factory=lambda: {"day30": ["Launch Beta"], "day60": ["Scale Cold Email"], "day90": ["Expand Partnerships"]})

class RiskFactor(BaseModel):
    vulnerability: str = "High CAC erosion in competitive market"
    severity: str = "HIGH"
    probability: str = "MEDIUM"
    red_team_attack_scenario: str = "Competitor slashes pricing by 50%."
    mitigation_strategy: str = "Lock in annual enterprise contracts."

class RiskAssessment(BaseModel):
    failure_risk_index: float = 24.5
    critical_vulnerabilities: List[RiskFactor] = Field(default_factory=list)
    regulatory_legal_hurdles: List[str] = Field(default_factory=lambda: ["Data Privacy Compliance (GDPR/CCPA)"])
    competitive_threats: List[str] = Field(default_factory=lambda: ["Legacy Legal Tech Vendors"])
    red_team_verdict: str = "APPROVED WITH CONDITIONAL RISK MITIGATION"

class StrategicRadar(BaseModel):
    market_demand: float = 85.0
    tech_feasibility: float = 90.0
    margin_profile: float = 82.0
    defensive_moat: float = 75.0
    scalability: float = 88.0
    regulatory_safety: float = 80.0

class AgentLog(BaseModel):
    agent: str
    role: str
    action: str
    thought: str
    timestamp: str = ""

class AnalysisRequest(BaseModel):
    idea_description: str
    target_industry: Optional[str] = "Technology / AI / SaaS"
    target_market: Optional[str] = "Global / B2B"
    initial_budget_usd: Optional[float] = 100000.0

class SensitivitySimulationRequest(BaseModel):
    cac_multiplier: float = 1.0
    arpu_multiplier: float = 1.0
    monthly_churn_pct: float = 3.0
    conversion_rate_pct: float = 2.0

class SensitivitySimulationResult(BaseModel):
    baseline_ltv_cac: float = 6.85
    simulated_ltv_cac: float = 6.85
    baseline_year1_profit: float = 50000.0
    simulated_year1_profit: float = 50000.0
    baseline_breakeven_month: int = 14
    simulated_breakeven_month: int = 14
    risk_score_delta: float = 0.0
    cfo_assessment: str = "Unit economics remain healthy."

class DebateMessage(BaseModel):
    speaker: str = "CFO"
    role: str = "Chief Financial Officer"
    argument: str = "CAC must be constrained."
    counter_proposal: Optional[str] = "Implement viral referral loop."

class BoardroomDebateSession(BaseModel):
    topic: str = "CAC & Unit Economics Optimization"
    rounds: List[DebateMessage] = Field(default_factory=list)
    consensus_resolution: str = "Unanimous agreement to optimize outbound channel mix."
    revised_viability_score: float = 88.5

class MonteCarloSimulationResult(BaseModel):
    num_trials: int = 1000
    probability_of_profitability_pct: float = 78.5
    expected_year3_revenue_usd: float = 3850000.0
    var_95_downside_usd: float = -120000.0
    revenue_distribution_bins: List[float] = Field(default_factory=lambda: [0.5, 1.5, 2.5, 3.5, 4.5, 5.5])
    revenue_distribution_counts: List[int] = Field(default_factory=lambda: [40, 150, 380, 270, 120, 40])
    cfo_summary: str = "Monte Carlo 1,000 trials confirm 78.5% chance of profitability by Year 3."

class CompetitorPosition(BaseModel):
    name: str = "Legacy Enterprise Competitor"
    x_feature_depth: float = 30.0
    y_price_point: float = 80.0
    strengths: List[str] = Field(default_factory=lambda: ["Brand Recognition"])
    weaknesses: List[str] = Field(default_factory=lambda: ["High Price", "Slow UI"])
    cohere_relevance_score: float = 0.85

class CompetitiveLandscapeMatrix(BaseModel):
    competitors: List[CompetitorPosition] = Field(default_factory=list)
    proposed_position: CompetitorPosition = Field(default_factory=lambda: CompetitorPosition(name="DecisionOS Proposed Venture", x_feature_depth=85.0, y_price_point=40.0))
    strategic_moat_verdict: str = "Strong competitive positioning in High Feature / Fair Price quadrant."

class PitchSlide(BaseModel):
    slide_number: int = 1
    title: str = "Executive Vision"
    bullet_points: List[str] = Field(default_factory=lambda: ["Revolutionizing business strategy."])
    visual_type: str = "metric"
    speaker_notes: str = "Focus on the total addressable market size."

class GTMMarketingAssets(BaseModel):
    outbound_email_sequence: List[Dict[str, str]] = Field(default_factory=list)
    product_hunt_tagline: str = "Autonomous C-Suite Multi-Agent Business Strategy Platform"
    product_hunt_description: str = "Deploy an AI C-Suite to simulate business models, run Monte Carlo trials, and plot market positioning."
    python_integration_snippet: str = "import decisionos\nclient = decisionos.Client()\nreport = client.analyze('My SaaS Idea')"

class FullStrategyReport(BaseModel):
    project_title: str = "AI Strategy Blueprint"
    executive_summary: str = "Comprehensive strategy synthesized by autonomous C-Suite agent swarm."
    viability_score: float = 88.5
    business_model_canvas: BusinessModelCanvas = Field(default_factory=BusinessModelCanvas)
    financials: FinancialProjections = Field(default_factory=FinancialProjections)
    tech_architecture: TechArchitecture = Field(default_factory=TechArchitecture)
    growth_strategy: GrowthStrategy = Field(default_factory=GrowthStrategy)
    risk_assessment: RiskAssessment = Field(default_factory=RiskAssessment)
    strategic_radar: StrategicRadar = Field(default_factory=StrategicRadar)
    market_signals: List[Dict[str, Any]] = Field(default_factory=list)
    agent_logs: List[AgentLog] = Field(default_factory=list)
    
    boardroom_debate: Optional[BoardroomDebateSession] = Field(default_factory=BoardroomDebateSession)
    monte_carlo: Optional[MonteCarloSimulationResult] = Field(default_factory=MonteCarloSimulationResult)
    competitive_matrix: Optional[CompetitiveLandscapeMatrix] = Field(default_factory=CompetitiveLandscapeMatrix)
    pitch_slides: Optional[List[PitchSlide]] = Field(default_factory=list)
    gtm_assets: Optional[GTMMarketingAssets] = Field(default_factory=GTMMarketingAssets)
