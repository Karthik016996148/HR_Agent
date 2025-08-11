from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict
import json

class CompensationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    async def process(self, market_research: Dict, clarifications: Dict) -> Dict:
        """Design competitive compensation packages for each role"""
        
        roles = list(market_research.get("market_data", {}).keys())
        compensation_packages = {}
        
        for role in roles:
            package = await self._design_compensation_package(role, market_research, clarifications)
            compensation_packages[role] = package
        
        return {
            "compensation_packages": compensation_packages,
            "budget_analysis": await self._analyze_total_budget(compensation_packages, clarifications),
            "negotiation_guidelines": await self._generate_negotiation_guidelines()
        }
    
    async def _design_compensation_package(self, role: str, market_research: Dict, clarifications: Dict) -> Dict:
        """Design a comprehensive compensation package for a specific role"""
        
        system_prompt = """You are a compensation specialist for startups. Design competitive, 
        fair compensation packages that attract top talent while being financially responsible.
        
        Consider:
        1. Base salary ranges (market competitive)
        2. Equity/stock options (startup appropriate)
        3. Benefits package
        4. Performance bonuses
        5. Professional development budget
        6. Flexible perks
        
        Balance competitiveness with startup budget constraints."""
        
        market_data = market_research.get("market_data", {}).get(role, {})
        extracted_info = clarifications.get("extracted_info", {})
        budget_info = extracted_info.get("budget", "Competitive")
        
        prompt = f"""
        Role: {role}
        
        Market Data:
        - Salary Ranges: {market_data.get('salary_ranges', {})}
        - Market Demand: {market_data.get('market_demand', 'Moderate')}
        - Competition Level: {market_data.get('competition_level', 'Moderate')}
        
        Company Context:
        - Budget Constraint: {budget_info}
        - Company Stage: {extracted_info.get('company_stage', 'Early startup')}
        - Team Size: {extracted_info.get('team_size', 'Small')}
        
        Design a complete compensation package in JSON format with keys:
        base_salary, equity_percentage, benefits, bonuses, perks, total_value_estimate
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._generate_fallback_package(role, market_data)
    
    async def _analyze_total_budget(self, compensation_packages: Dict, clarifications: Dict) -> Dict:
        """Analyze total budget requirements and provide recommendations"""
        
        system_prompt = """Analyze the total compensation budget and provide insights 
        on affordability, budget allocation, and cost optimization strategies for a startup."""
        
        prompt = f"""
        Compensation Packages: {json.dumps(compensation_packages, indent=2)}
        Company Context: {clarifications.get('extracted_info', {})}
        
        Provide budget analysis with total costs, recommendations, and optimization strategies.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "total_annual_cost": "Varies by package selection",
                "budget_recommendations": [
                    "Prioritize equity over high base salaries",
                    "Focus on growth and learning opportunities",
                    "Consider performance-based compensation"
                ],
                "cost_optimization": [
                    "Negotiate based on candidate priorities",
                    "Offer flexible benefits packages",
                    "Use equity to offset lower base salaries"
                ]
            }
    
    async def _generate_negotiation_guidelines(self) -> str:
        """Generate guidelines for salary negotiations"""
        
        system_prompt = """Provide practical negotiation guidelines for startup hiring managers 
        when discussing compensation with candidates."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate compensation negotiation guidelines for startups.")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def _generate_fallback_package(self, role: str, market_data: Dict) -> Dict:
        """Fallback compensation package when parsing fails"""
        
        salary_ranges = market_data.get('salary_ranges', {})
        base_salary = salary_ranges.get('mid', '$100k-150k')
        
        return {
            "base_salary": {
                "range": base_salary,
                "justification": "Market competitive based on role and experience"
            },
            "equity_percentage": {
                "range": "0.1% - 1.0%",
                "vesting": "4 years with 1-year cliff",
                "justification": "Startup equity to align with company growth"
            },
            "benefits": [
                "Health insurance (medical, dental, vision)",
                "Retirement plan (401k with matching)",
                "Paid time off (vacation, sick, personal)",
                "Professional development budget",
                "Flexible work arrangements"
            ],
            "bonuses": {
                "performance_bonus": "Up to 15% of base salary",
                "signing_bonus": "Negotiable based on candidate",
                "referral_bonus": "Available for successful hires"
            },
            "perks": [
                "Flexible working hours",
                "Remote work options",
                "Modern equipment and tools",
                "Team building activities",
                "Learning and conference budget"
            ],
            "total_value_estimate": "Competitive package with strong upside potential"
        }
