from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict
import json

class InterviewProcessAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)
    
    async def process(self, job_descriptions: Dict, clarifications: Dict) -> Dict:
        """Design structured interview processes for each role"""
        
        roles = list(job_descriptions.get("job_descriptions", {}).keys())
        interview_processes = {}
        
        for role in roles:
            process = await self._design_interview_process(role, job_descriptions, clarifications)
            interview_processes[role] = process
        
        return {
            "interview_processes": interview_processes,
            "general_guidelines": await self._generate_interview_guidelines()
        }
    
    async def _design_interview_process(self, role: str, job_descriptions: Dict, clarifications: Dict) -> Dict:
        """Design a comprehensive interview process for a specific role"""
        
        system_prompt = """You are an expert in designing effective interview processes for startup hiring.
        Create a structured, fair, and efficient interview process that evaluates candidates thoroughly 
        while respecting their time and providing a good candidate experience.
        
        Design:
        1. Interview stages (screening, technical, cultural, final)
        2. Duration and format for each stage
        3. Key evaluation criteria
        4. Sample questions for each stage
        5. Decision-making process
        6. Timeline and logistics
        
        Focus on startup needs: speed, cultural fit, adaptability, and growth potential."""
        
        jd = job_descriptions.get("job_descriptions", {}).get(role, {})
        extracted_info = clarifications.get("extracted_info", {})
        
        prompt = f"""
        Role: {role}
        
        Job Description Summary:
        - Responsibilities: {jd.get('responsibilities', [])}
        - Required Skills: {jd.get('required_qualifications', [])}
        - Preferred Skills: {jd.get('preferred_qualifications', [])}
        
        Company Context:
        - Timeline: {extracted_info.get('timeline', 'Standard')}
        - Team Size: {extracted_info.get('team_size', 'Small')}
        - Work Mode: {extracted_info.get('work_mode', 'Flexible')}
        
        Design a complete interview process in JSON format with keys:
        stages, timeline, evaluation_criteria, sample_questions, decision_process, logistics
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._generate_fallback_process(role)
    
    async def _generate_interview_guidelines(self) -> str:
        """Generate general interview guidelines and best practices"""
        
        system_prompt = """Provide comprehensive interview guidelines and best practices 
        for startup hiring teams. Focus on legal compliance, bias reduction, and candidate experience."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Generate interview guidelines for startup hiring teams.")
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def _generate_fallback_process(self, role: str) -> Dict:
        """Fallback interview process when parsing fails"""
        
        return {
            "stages": [
                {
                    "name": "Initial Screening",
                    "duration": "30 minutes",
                    "format": "Phone/Video call",
                    "focus": "Basic qualifications and cultural fit"
                },
                {
                    "name": "Technical Assessment",
                    "duration": "60-90 minutes",
                    "format": "Technical interview/coding challenge",
                    "focus": "Technical skills and problem-solving"
                },
                {
                    "name": "Team Interview",
                    "duration": "45 minutes",
                    "format": "Video call with team members",
                    "focus": "Collaboration and communication skills"
                },
                {
                    "name": "Final Interview",
                    "duration": "30 minutes",
                    "format": "Interview with leadership",
                    "focus": "Vision alignment and final assessment"
                }
            ],
            "timeline": "2-3 weeks from application to decision",
            "evaluation_criteria": [
                "Technical competency",
                "Cultural fit",
                "Communication skills",
                "Growth potential",
                "Startup mindset"
            ],
            "sample_questions": {
                "screening": [
                    "Tell us about your experience with [relevant technology]",
                    "Why are you interested in joining a startup?",
                    "What are your career goals?"
                ],
                "technical": [
                    "Walk us through your approach to [technical problem]",
                    "How would you handle [scenario-based question]?",
                    "Explain a challenging project you worked on"
                ],
                "cultural": [
                    "How do you handle ambiguity and changing priorities?",
                    "Describe a time you had to learn something quickly",
                    "What motivates you in your work?"
                ]
            },
            "decision_process": "Collaborative decision with input from all interviewers",
            "logistics": "Coordinated through HR with clear communication to candidates"
        }
