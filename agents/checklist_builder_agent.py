from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Dict
import json

class ChecklistBuilderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    async def process(self, job_descriptions: Dict, interview_process: Dict, compensation: Dict) -> Dict:
        """Build comprehensive hiring checklists and action plans"""
        
        roles = list(job_descriptions.get("job_descriptions", {}).keys())
        
        # Generate role-specific checklists
        role_checklists = {}
        for role in roles:
            checklist = await self._build_role_checklist(role, job_descriptions, interview_process, compensation)
            role_checklists[role] = checklist
        
        # Generate overall hiring plan checklist
        master_checklist = await self._build_master_checklist(role_checklists)
        
        return {
            "role_checklists": role_checklists,
            "master_checklist": master_checklist,
            "timeline_overview": await self._generate_timeline_overview(role_checklists)
        }
    
    async def _build_role_checklist(self, role: str, job_descriptions: Dict, interview_process: Dict, compensation: Dict) -> Dict:
        """Build a detailed checklist for hiring a specific role"""
        
        system_prompt = """You are an expert HR operations specialist. Create a comprehensive, 
        actionable checklist for hiring a specific role. Include all steps from job posting 
        to onboarding, with timelines and responsible parties.
        
        Organize into phases:
        1. Pre-posting preparation
        2. Job posting and sourcing
        3. Screening and interviews
        4. Decision and offer
        5. Onboarding preparation
        
        Make each item specific, actionable, and time-bound."""
        
        jd = job_descriptions.get("job_descriptions", {}).get(role, {})
        interview_stages = interview_process.get("interview_processes", {}).get(role, {})
        comp_package = compensation.get("compensation_packages", {}).get(role, {})
        
        prompt = f"""
        Role: {role}
        
        Job Description: {json.dumps(jd, indent=2)[:800]}
        Interview Process: {json.dumps(interview_stages, indent=2)[:800]}
        Compensation: {json.dumps(comp_package, indent=2)[:800]}
        
        Create a detailed hiring checklist in JSON format with keys:
        pre_posting, job_posting, screening, interviews, decision_offer, onboarding
        
        Each phase should have: tasks (with deadlines), responsible_party, dependencies
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._generate_fallback_checklist(role)
    
    async def _build_master_checklist(self, role_checklists: Dict) -> Dict:
        """Build an overall master checklist coordinating all roles"""
        
        system_prompt = """Create a master hiring checklist that coordinates hiring for multiple roles.
        Focus on dependencies, resource allocation, and overall project management."""
        
        prompt = f"""
        Role Checklists: {json.dumps(role_checklists, indent=2)[:1500]}
        
        Create a master checklist that coordinates all hiring activities.
        Include: setup_phase, execution_phase, coordination_tasks, milestones
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return self._generate_fallback_master_checklist()
    
    async def _generate_timeline_overview(self, role_checklists: Dict) -> str:
        """Generate a timeline overview for the entire hiring process"""
        
        system_prompt = """Create a timeline overview showing the hiring process flow 
        for multiple roles, highlighting key milestones and dependencies."""
        
        prompt = f"Role Checklists: {json.dumps(role_checklists, indent=2)[:1000]}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def _generate_fallback_checklist(self, role: str) -> Dict:
        """Fallback checklist when parsing fails"""
        
        return {
            "pre_posting": {
                "tasks": [
                    {"task": "Finalize job description", "deadline": "Day 1", "responsible": "HR"},
                    {"task": "Set up interview panel", "deadline": "Day 2", "responsible": "Hiring Manager"},
                    {"task": "Prepare interview materials", "deadline": "Day 3", "responsible": "HR"}
                ]
            },
            "job_posting": {
                "tasks": [
                    {"task": "Post on job boards", "deadline": "Day 4", "responsible": "HR"},
                    {"task": "Share on social media", "deadline": "Day 4", "responsible": "Marketing"},
                    {"task": "Reach out to network", "deadline": "Day 5", "responsible": "Team"}
                ]
            },
            "screening": {
                "tasks": [
                    {"task": "Review applications", "deadline": "Ongoing", "responsible": "HR"},
                    {"task": "Conduct phone screens", "deadline": "Week 2-3", "responsible": "HR"},
                    {"task": "Technical assessments", "deadline": "Week 2-3", "responsible": "Technical Team"}
                ]
            },
            "interviews": {
                "tasks": [
                    {"task": "Schedule interviews", "deadline": "Week 3-4", "responsible": "HR"},
                    {"task": "Conduct interviews", "deadline": "Week 3-4", "responsible": "Interview Panel"},
                    {"task": "Collect feedback", "deadline": "Week 4", "responsible": "HR"}
                ]
            },
            "decision_offer": {
                "tasks": [
                    {"task": "Make hiring decision", "deadline": "Week 4", "responsible": "Hiring Manager"},
                    {"task": "Prepare offer letter", "deadline": "Week 4", "responsible": "HR"},
                    {"task": "Extend offer", "deadline": "Week 4", "responsible": "Hiring Manager"}
                ]
            },
            "onboarding": {
                "tasks": [
                    {"task": "Prepare onboarding materials", "deadline": "Before start date", "responsible": "HR"},
                    {"task": "Set up workspace", "deadline": "Before start date", "responsible": "IT"},
                    {"task": "Schedule first week meetings", "deadline": "Before start date", "responsible": "Manager"}
                ]
            }
        }
    
    def _generate_fallback_master_checklist(self) -> Dict:
        """Fallback master checklist when parsing fails"""
        
        return {
            "setup_phase": [
                "Define hiring goals and priorities",
                "Allocate budget and resources",
                "Set up hiring infrastructure",
                "Train interview team"
            ],
            "execution_phase": [
                "Launch job postings simultaneously",
                "Coordinate screening processes",
                "Manage interview schedules",
                "Track candidate pipeline"
            ],
            "coordination_tasks": [
                "Weekly hiring team meetings",
                "Candidate experience monitoring",
                "Budget tracking and reporting",
                "Process optimization"
            ],
            "milestones": [
                "Week 1: All job postings live",
                "Week 2: First round of interviews",
                "Week 4: Initial offers extended",
                "Week 6: New hires onboarded"
            ]
        }
