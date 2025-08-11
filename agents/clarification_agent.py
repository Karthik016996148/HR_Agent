from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict, Optional
import json

class ClarificationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    async def process(self, user_input: str, company_context: Optional[str] = None) -> Dict:
        """Process user input and extract/clarify hiring requirements"""
        
        system_prompt = """You are a senior HR consultant specializing in startup hiring. 
        Your job is to analyze hiring requests and extract key information, asking clarifying questions when needed.
        
        Extract and structure the following information:
        1. Roles to be hired (titles, seniority levels)
        2. Required skills and qualifications
        3. Timeline and urgency
        4. Budget constraints (if mentioned)
        5. Company stage and context
        6. Team size and structure
        7. Remote/hybrid/onsite preferences
        8. Any specific requirements or preferences
        
        If information is missing or unclear, generate intelligent clarifying questions.
        Return your response as structured JSON."""
        
        context_info = f"Company Context: {company_context}" if company_context else "No company context provided."
        
        prompt = f"""
        User Request: "{user_input}"
        {context_info}
        
        Please analyze this hiring request and provide:
        1. Extracted information in structured format
        2. Clarifying questions for missing critical information
        3. Assumptions you're making based on the request
        
        Format as JSON with keys: extracted_info, clarifying_questions, assumptions
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            # Try to parse as JSON, fallback to structured text if needed
            result = json.loads(response.content)
        except json.JSONDecodeError:
            # Fallback parsing if JSON is malformed
            result = self._parse_fallback_response(response.content, user_input)
        
        return result
    
    def _parse_fallback_response(self, content: str, user_input: str) -> Dict:
        """Fallback parsing when JSON parsing fails"""
        
        # Extract basic role information from user input
        roles = []
        if "engineer" in user_input.lower():
            roles.append("Software Engineer")
        if "intern" in user_input.lower():
            roles.append("Intern")
        if "founding" in user_input.lower():
            roles.append("Founding Team Member")
        if "genai" in user_input.lower() or "ai" in user_input.lower():
            roles.append("AI/ML Engineer")
        
        return {
            "extracted_info": {
                "roles": roles,
                "skills": ["Technical skills", "Problem solving"],
                "timeline": "Not specified",
                "budget": "Not specified",
                "company_stage": "Startup",
                "team_size": "Small team",
                "work_mode": "Not specified"
            },
            "clarifying_questions": [
                "What is your budget range for these positions?",
                "What is your ideal timeline for hiring?",
                "What specific technical skills are most important?",
                "Do you prefer remote, hybrid, or onsite work?",
                "What is your company's current team size?"
            ],
            "assumptions": [
                "Assuming startup environment with fast-paced growth",
                "Assuming technical roles require strong problem-solving skills",
                "Assuming flexibility in role definitions due to startup nature"
            ]
        }
