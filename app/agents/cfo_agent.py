import math
import random
from typing import Dict, Any, List, Tuple
from app.agents.base_agent import BaseAgent
from app.core.llm_client import llm_client
from app.models.business_schema import (
    FinancialProjections, FinancialMetric, UnitEconomics,
    SensitivitySimulationRequest, SensitivitySimulationResult,
    MonteCarloSimulationResult, AgentLog
)

class CFOAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Chief Financial Officer", role="Financial Modeling, Unit Economics & Monte Carlo Risk")

    def execute(self, idea_description: str, initial_budget_usd: float, revenue_streams: List[str]) -> Tuple[FinancialProjections, List[AgentLog]]:
        logs = []
        logs.append(self.log(
            action="Financial Forecast Initialization",
            thought=f"Building 3-Year P&L model and Unit Economics projection with initial capital of ${initial_budget_usd:,.2f}."
        ))

        system_prompt = (
            "You are a veteran Silicon Valley CFO and quantitative strategist. "
            "Generate realistic, venture-grade 3-year financial projections and unit economics for the business model."
        )

        prompt = f"""
Business Idea: {idea_description}
Initial Capital / Budget: ${initial_budget_usd}
Revenue Streams: {revenue_streams}

Produce realistic, mathematically sound projections in JSON format:
{{
  "annual_revenue": {{"year1": 250000.0, "year2": 1200000.0, "year3": 4500000.0}},
  "operating_expenses": {{"year1": 200000.0, "year2": 750000.0, "year3": 2200000.0}},
  "net_profit": {{"year1": 50000.0, "year2": 450000.0, "year3": 230000.0}},
  "mrr_end_of_year": {{"year1": 25000.0, "year2": 110000.0, "year3": 400000.0}},
  "unit_economics": {{
    "cac": 350.0,
    "ltv": 2400.0,
    "ltv_cac_ratio": 6.85,
    "payback_months": 5.5,
    "gross_margin_pct": 78.0,
    "breakeven_month": 14
  }},
  "pricing_summary": "Summary of pricing tiers, ARPU, and revenue engine dynamics."
}}
Note: net_profit = annual_revenue - operating_expenses. Ensure internal numeric consistency.
"""
        fin_json = llm_client.generate_json(prompt=prompt, system_prompt=system_prompt)
        
        rev = fin_json["annual_revenue"]
        opex = fin_json["operating_expenses"]
        fin_json["net_profit"] = {
            "year1": round(rev["year1"] - opex["year1"], 2),
            "year2": round(rev["year2"] - opex["year2"], 2),
            "year3": round(rev["year3"] - opex["year3"], 2),
        }
        
        fin = FinancialProjections(**fin_json)

        logs.append(self.log(
            action="Financial Modeling Complete",
            thought=f"Projected Year 3 ARR/Revenue at ${fin.annual_revenue.year3:,.2f} with LTV/CAC ratio of {fin.unit_economics.ltv_cac_ratio}x."
        ))

        return fin, logs

    def simulate_sensitivity(self, base_fin: FinancialProjections, sim_req: SensitivitySimulationRequest) -> SensitivitySimulationResult:
        """Simulates 'What-If' sensitivity scenarios when CAC, Churn, ARPU or Conversion changes."""
        base_unit = base_fin.unit_economics
        
        sim_cac = base_unit.cac * sim_req.cac_multiplier
        sim_arpu_factor = sim_req.arpu_multiplier
        sim_churn_factor = (3.0 / max(0.5, sim_req.monthly_churn_pct))
        
        sim_ltv = base_unit.ltv * sim_arpu_factor * sim_churn_factor
        sim_ltv_cac = round(sim_ltv / max(1.0, sim_cac), 2)
        
        conversion_factor = (sim_req.conversion_rate_pct / 2.0)
        rev_mod = sim_arpu_factor * conversion_factor
        opex_mod = sim_req.cac_multiplier
        
        sim_y1_rev = base_fin.annual_revenue.year1 * rev_mod
        sim_y1_opex = base_fin.operating_expenses.year1 * opex_mod
        sim_y1_profit = round(sim_y1_rev - sim_y1_opex, 2)
        
        breakeven_shift = int((sim_req.cac_multiplier - 1.0) * 4 + (sim_req.monthly_churn_pct - 3.0) * 1.5)
        sim_breakeven = max(3, base_unit.breakeven_month + breakeven_shift)
        
        risk_delta = round((sim_req.cac_multiplier - 1.0) * 15 + (sim_req.monthly_churn_pct - 3.0) * 3 - (sim_arpu_factor - 1.0) * 10, 1)

        cfo_assessment = (
            f"Under the tested sensitivity parameters (CAC x{sim_req.cac_multiplier}, ARPU x{sim_req.arpu_multiplier}, Churn {sim_req.monthly_churn_pct}%), "
            f"LTV/CAC shifts from {base_unit.ltv_cac_ratio:.2f}x to {sim_ltv_cac:.2f}x. "
            f"Year 1 Net Profit changes by ${(sim_y1_profit - base_fin.net_profit.year1):+,.2f}."
        )

        return SensitivitySimulationResult(
            baseline_ltv_cac=base_unit.ltv_cac_ratio,
            simulated_ltv_cac=sim_ltv_cac,
            baseline_year1_profit=base_fin.net_profit.year1,
            simulated_year1_profit=sim_y1_profit,
            baseline_breakeven_month=base_unit.breakeven_month,
            simulated_breakeven_month=sim_breakeven,
            risk_score_delta=risk_delta,
            cfo_assessment=cfo_assessment
        )

    def run_monte_carlo(self, base_fin: FinancialProjections, num_trials: int = 1000) -> MonteCarloSimulationResult:
        """Executes 1,000 stochastic Monte Carlo simulation runs in Python to project probabilistic risk distributions."""
        base_y3_rev = base_fin.annual_revenue.year3
        base_cac = base_fin.unit_economics.cac
        
        y3_results = []
        profitable_count = 0
        
        for _ in range(num_trials):
            # Sample random variables from stochastic normal distribution
            cac_sample = max(50.0, random.gauss(base_cac, base_cac * 0.25))
            churn_sample = max(0.5, random.gauss(3.0, 1.2))
            market_conv_sample = max(0.2, random.gauss(2.0, 0.6))
            arpu_mult_sample = max(0.5, random.gauss(1.0, 0.2))
            
            # Compute Y3 revenue sample
            rev_mult = (arpu_mult_sample * (market_conv_sample / 2.0) * (3.0 / churn_sample))
            y3_rev_sample = base_y3_rev * rev_mult
            
            # Expense scaling
            opex_sample = (base_fin.operating_expenses.year3 * (cac_sample / max(1.0, base_cac)))
            y3_profit_sample = y3_rev_sample - opex_sample
            
            y3_results.append(y3_rev_sample)
            if y3_profit_sample > 0:
                profitable_count += 1
                
        y3_results.sort()
        prob_profitable = round((profitable_count / num_trials) * 100, 1)
        expected_y3_rev = round(sum(y3_results) / num_trials, 2)
        var_5_pct = round(y3_results[int(num_trials * 0.05)] - base_fin.operating_expenses.year3, 2)

        # Generate 6 histogram bins & counts
        min_v = y3_results[0]
        max_v = y3_results[-1]
        step = (max_v - min_v) / 6.0
        
        bins = [round(min_v + i * step / 1e6, 2) for i in range(7)]  # represented in Millions
        counts = [0] * 6
        
        for v in y3_results:
            idx = min(5, int((v - min_v) / max(1.0, step)))
            counts[idx] += 1

        cfo_summary = (
            f"Over {num_trials:,} stochastic Monte Carlo trial runs, the probability of achieving profitable unit economics by Year 3 is {prob_profitable}%. "
            f"Expected Year 3 ARR stands at ${expected_y3_rev:,.2f} with a 95% Downside Value-at-Risk (VaR) of ${abs(var_5_pct):,.2f}."
        )

        return MonteCarloSimulationResult(
            num_trials=num_trials,
            probability_of_profitability_pct=prob_profitable,
            expected_year3_revenue_usd=expected_y3_rev,
            var_95_downside_usd=var_5_pct,
            revenue_distribution_bins=bins,
            revenue_distribution_counts=counts,
            cfo_summary=cfo_summary
        )

cfo_agent = CFOAgent()
