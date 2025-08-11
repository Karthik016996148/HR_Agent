from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Any
import json

class MarketResearchAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    async def process(self, clarifications: Dict, search_tool: Any) -> Dict:
        """Conduct market research for the specified roles"""
        
        roles = clarifications.get("extracted_info", {}).get("roles", [])
        
        market_data = {}
        
        for role in roles:
            # Use search tool to get market data
            search_results = await self._search_role_data(role, search_tool)
            
            # Analyze the search results with LLM
            analysis = await self._analyze_market_data(role, search_results, clarifications)
            
            market_data[role] = analysis
        
        return {
            "roles_analyzed": roles,
            "market_data": market_data,
            "summary": await self._generate_market_summary(market_data)
        }
    
    async def _search_role_data(self, role: str, search_tool: Any) -> Dict:
        """Search for market data about a specific role"""
        
        search_queries = [
            f"{role} salary range 2024 startup",
            f"{role} hiring trends tech industry",
            f"{role} skills requirements market demand"
        ]
        
        search_results = {}
        for query in search_queries:
            try:
                results = await search_tool.search(query)
                search_results[query] = results
            except Exception as e:
                search_results[query] = f"Search failed: {str(e)}"
        
        return search_results
    
    async def _analyze_market_data(self, role: str, search_results: Dict, clarifications: Dict) -> Dict:
        """Analyze search results to extract market insights"""
        
        system_prompt = f"""You are a market research analyst specializing in tech hiring.
        Analyze the search results and provide insights about the {role} market.
        
        Focus on:
        1. Salary ranges (entry, mid, senior levels)
        2. In-demand skills and qualifications
        3. Market competition and demand
        4. Hiring trends and challenges
        5. Geographic variations (if relevant)
        
        Provide actionable insights for startup hiring."""
        
        search_summary = json.dumps(search_results, indent=2)[:2000]  # Limit context size
        
        prompt = f"""
        Role: {role}
        Search Results Summary: {search_summary}
        
        Company Context: {clarifications.get('extracted_info', {})}
        
        Please provide market analysis in JSON format with keys:
        salary_ranges, key_skills, market_demand, competition_level, hiring_tips
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._generate_fallback_analysis(role)
    
    async def _generate_market_summary(self, market_data: Dict) -> str:
        """Generate overall market summary"""
        
        system_prompt = """Summarize the market research findings across all roles.
        Provide key insights and recommendations for the hiring strategy."""
        
        prompt = f"Market Data: {json.dumps(market_data, indent=2)}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def _generate_fallback_analysis(self, role: str) -> Dict:
        """Fallback analysis when search/parsing fails"""
        
        fallback_data = {
            "Software Engineer": {
                "salary_ranges": {"entry": "$80k-120k", "mid": "$120k-180k", "senior": "$180k-250k"},
                "key_skills": ["Python/JavaScript", "System Design", "Problem Solving"],
                "market_demand": "Very High",
                "competition_level": "High",
                "hiring_tips": ["Focus on coding skills", "Emphasize growth opportunities", "Competitive compensation"]
            },
            "AI/ML Engineer": {
                "salary_ranges": {"entry": "$100k-140k", "mid": "$140k-200k", "senior": "$200k-300k"},
                "key_skills": ["Python", "TensorFlow/PyTorch", "Statistics", "Deep Learning"],
                "market_demand": "Extremely High",
                "competition_level": "Very High",
                "hiring_tips": ["Highlight AI projects", "Offer learning opportunities", "Premium compensation"]
            }
        }
        
        return fallback_data.get(role, {
            "salary_ranges": {"entry": "$60k-90k", "mid": "$90k-130k", "senior": "$130k-180k"},
            "key_skills": ["Domain expertise", "Communication", "Problem solving"],
            "market_demand": "Moderate",
            "competition_level": "Moderate",
            "hiring_tips": ["Clear role definition", "Growth path", "Competitive benefits"]
        })
