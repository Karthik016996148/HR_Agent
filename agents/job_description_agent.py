from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict
import json

class JobDescriptionAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    async def process(self, clarifications: Dict, market_research: Dict) -> Dict:
        """Generate tailored job descriptions based on requirements and market data"""
        
        roles = clarifications.get("extracted_info", {}).get("roles", [])
        job_descriptions = {}
        
        for role in roles:
            jd = await self._generate_job_description(role, clarifications, market_research)
            job_descriptions[role] = jd
        
        return {
            "job_descriptions": job_descriptions,
            "posting_tips": await self._generate_posting_tips(job_descriptions)
        }
    
    async def _generate_job_description(self, role: str, clarifications: Dict, market_research: Dict) -> Dict:
        """Generate a comprehensive job description for a specific role"""
        
        system_prompt = """You are an expert HR professional specializing in writing compelling job descriptions for startups.
        Create a comprehensive, attractive job description that will attract top talent while being realistic about startup constraints.
        
        Include:
        1. Compelling role title and summary
        2. Key responsibilities
        3. Required qualifications
        4. Preferred qualifications
        5. What we offer (benefits, growth, culture)
        6. Application process
        
        Make it startup-friendly: emphasize growth, impact, and learning opportunities."""
        
        extracted_info = clarifications.get("extracted_info", {})
        market_data = market_research.get("market_data", {}).get(role, {})
        
        prompt = f"""
        Role: {role}
        
        Company Context:
        - Stage: {extracted_info.get('company_stage', 'Startup')}
        - Team Size: {extracted_info.get('team_size', 'Small team')}
        - Work Mode: {extracted_info.get('work_mode', 'Flexible')}
        
        Requirements:
        - Skills: {extracted_info.get('skills', [])}
        - Timeline: {extracted_info.get('timeline', 'ASAP')}
        - Budget: {extracted_info.get('budget', 'Competitive')}
        
        Market Data:
        - Key Skills: {market_data.get('key_skills', [])}
        - Salary Range: {market_data.get('salary_ranges', {})}
        - Market Demand: {market_data.get('market_demand', 'Moderate')}
        
        Generate a complete job description in JSON format with keys:
        title, summary, responsibilities, required_qualifications, preferred_qualifications, 
        what_we_offer, application_process
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._generate_fallback_jd(role, extracted_info)
    
    async def _generate_posting_tips(self, job_descriptions: Dict) -> str:
        """Generate tips for posting and promoting job descriptions"""
        
        system_prompt = """Provide actionable tips for posting and promoting these job descriptions 
        to attract the best candidates. Focus on startup-specific strategies."""
        
        prompt = f"Job Descriptions: {json.dumps(job_descriptions, indent=2)[:1500]}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def _generate_fallback_jd(self, role: str, extracted_info: Dict) -> Dict:
        """Fallback job description when parsing fails"""
        
        return {
            "title": f"{role} - Join Our Growing Startup",
            "summary": f"We're looking for a talented {role} to join our innovative startup team and help build the future.",
            "responsibilities": [
                f"Lead {role.lower()} initiatives and projects",
                "Collaborate with cross-functional teams",
                "Drive innovation and technical excellence",
                "Mentor junior team members",
                "Contribute to product strategy and roadmap"
            ],
            "required_qualifications": [
                f"3+ years of experience in {role.lower()} role",
                "Strong technical and problem-solving skills",
                "Excellent communication and teamwork abilities",
                "Startup mindset and adaptability",
                "Bachelor's degree or equivalent experience"
            ],
            "preferred_qualifications": [
                "Experience in fast-paced startup environment",
                "Leadership and mentoring experience",
                "Open source contributions",
                "Advanced degree in relevant field"
            ],
            "what_we_offer": [
                "Competitive salary and equity package",
                "Flexible work arrangements",
                "Professional development opportunities",
                "Health and wellness benefits",
                "Collaborative and innovative culture"
            ],
            "application_process": "Send your resume and cover letter explaining why you're excited about this opportunity."
        }
