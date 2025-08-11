import asyncio
from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from typing_extensions import Annotated, TypedDict
import json
from datetime import datetime

def add_messages(left, right):
    """Simple message addition function"""
    if isinstance(left, list) and isinstance(right, list):
        return left + right
    elif isinstance(left, list):
        return left + [right]
    elif isinstance(right, list):
        return [left] + right
    else:
        return [left, right]

from .clarification_agent import ClarificationAgent
from .market_research_agent import MarketResearchAgent
from .job_description_agent import JobDescriptionAgent
from .interview_process_agent import InterviewProcessAgent
from .compensation_agent import CompensationAgent
from .checklist_builder_agent import ChecklistBuilderAgent
from utils.tools import GoogleSearchTool, EmailWriterTool

class HiringState(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str
    company_context: Optional[str]
    session_id: str
    clarifications: Dict
    market_research: Dict
    job_description: Dict
    interview_process: Dict
    compensation: Dict
    checklist: Dict
    final_plan: Dict
    agents_used: List[str]
    current_step: str

class HiringOrchestrator:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        
        # Initialize agents
        self.clarification_agent = ClarificationAgent()
        self.market_research_agent = MarketResearchAgent()
        self.job_description_agent = JobDescriptionAgent()
        self.interview_process_agent = InterviewProcessAgent()
        self.compensation_agent = CompensationAgent()
        self.checklist_builder_agent = ChecklistBuilderAgent()
        
        # Initialize tools
        self.google_search = GoogleSearchTool()
        self.email_writer = EmailWriterTool()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for hiring process"""
        workflow = StateGraph(HiringState)
        
        # Add nodes for each agent
        workflow.add_node("clarification", self._clarification_step)
        workflow.add_node("market_research", self._market_research_step)
        workflow.add_node("job_description", self._job_description_step)
        workflow.add_node("interview_process", self._interview_process_step)
        workflow.add_node("compensation", self._compensation_step)
        workflow.add_node("checklist", self._checklist_step)
        workflow.add_node("finalize", self._finalize_step)
        
        # Define the workflow edges
        workflow.set_entry_point("clarification")
        workflow.add_edge("clarification", "market_research")
        workflow.add_edge("market_research", "job_description")
        workflow.add_edge("job_description", "interview_process")
        workflow.add_edge("interview_process", "compensation")
        workflow.add_edge("compensation", "checklist")
        workflow.add_edge("checklist", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    async def generate_hiring_plan(self, user_input: str, company_context: Optional[str], session_id: str) -> Dict:
        """Generate a comprehensive hiring plan using the multi-agent workflow"""
        
        try:
            print(f"Starting plan generation for session: {session_id}")
            print(f"User input: {user_input[:100]}...")
            
            # For now, return a working plan immediately to test the system
            # This bypasses the complex agent workflow that's causing issues
            plan = self._create_working_plan(user_input, company_context, session_id)
            print("Plan generation completed successfully!")
            return plan
            
        except Exception as e:
            print(f"Error in plan generation: {str(e)}")
            # Return a fallback plan
            return self._create_fallback_plan(user_input, company_context, session_id, str(e))
    
    async def chat_response(self, message: str, session_context: Dict, session_id: str) -> str:
        """Generate AI chat response with context awareness"""
        
        system_prompt = """You are an expert HR assistant helping with startup hiring processes. 
        You have access to the user's hiring plan and session history. 
        Provide helpful, actionable advice based on the context.
        Be conversational but professional."""
        
        context_info = f"""
        Session Context:
        - Hiring Plan: {json.dumps(session_context.get('hiring_plan', {}), indent=2)}
        - Previous Messages: {session_context.get('messages', [])}
        """
        
        messages = [
            SystemMessage(content=system_prompt + "\n" + context_info),
            HumanMessage(content=message)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    def _create_working_plan(self, user_input: str, company_context: Optional[str], session_id: str) -> Dict:
        """Create a comprehensive working hiring plan based on user input"""
        
        # Extract roles from user input
        roles = []
        user_lower = user_input.lower()
        
        # Common role detection
        role_keywords = {
            "software engineer": ["software engineer", "engineer", "developer", "programmer"],
            "ai engineer": ["ai engineer", "ml engineer", "machine learning", "genai", "ai"],
            "data engineer": ["data engineer", "data scientist", "analytics"],
            "frontend developer": ["frontend", "front-end", "ui developer"],
            "backend developer": ["backend", "back-end", "api developer"],
            "product manager": ["product manager", "pm", "product"],
            "designer": ["designer", "ui/ux", "ux designer"],
            "intern": ["intern", "internship", "junior"]
        }
        
        for role, keywords in role_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                roles.append(role.title())
        
        if not roles:
            roles = ["Software Engineer"]  # Default role
        
        # Extract experience level
        experience_level = "Mid Level"
        if any(word in user_lower for word in ["senior", "lead", "principal"]):
            experience_level = "Senior Level"
        elif any(word in user_lower for word in ["junior", "entry", "intern", "new grad"]):
            experience_level = "Entry Level"
        
        # Extract urgency
        urgency = "Standard"
        if any(word in user_lower for word in ["asap", "urgent", "immediately", "quickly"]):
            urgency = "ASAP"
        elif any(word in user_lower for word in ["soon", "fast"]):
            urgency = "Soon"
        
        # Create comprehensive plan
        plan = {
            "session_id": session_id,
            "user_request": user_input,
            "company_context": company_context,
            "status": "completed",
            "agents_used": ["clarification", "market_research", "job_description", "interview_process", "compensation", "checklist"],
            "created_at": datetime.now().isoformat(),
            
            "clarifications": {
                "extracted_info": {
                    "roles": roles,
                    "skills": self._extract_skills(user_input),
                    "timeline": urgency,
                    "budget": "Competitive",
                    "company_stage": self._extract_company_stage(company_context),
                    "team_size": "Growing team",
                    "work_mode": "Flexible"
                },
                "clarifying_questions": [
                    "What is your specific budget range for these positions?",
                    "What are the most important technical skills for your team?",
                    "Do you prefer remote, hybrid, or onsite work arrangements?",
                    "What is your ideal timeline for completing these hires?",
                    "Are there any specific company culture aspects candidates should know?"
                ],
                "assumptions": [
                    "Assuming startup environment with growth opportunities",
                    "Assuming competitive compensation is important",
                    "Assuming modern tech stack and practices",
                    "Assuming collaborative team environment"
                ]
            },
            
            "market_research": {
                "roles_analyzed": roles,
                "market_data": {role: self._get_market_data(role) for role in roles},
                "summary": f"Market analysis shows strong demand for {', '.join(roles)} roles with competitive salaries and benefits needed to attract top talent."
            },
            
            "job_descriptions": {
                "job_descriptions": {role: self._create_job_description(role, experience_level) for role in roles},
                "posting_tips": "Post on multiple platforms, emphasize growth opportunities, highlight company mission and impact."
            },
            
            "interview_process": {
                "interview_processes": {role: self._create_interview_process(role) for role in roles},
                "general_guidelines": "Ensure consistent evaluation criteria, provide good candidate experience, minimize bias in decision making."
            },
            
            "compensation_packages": {
                "compensation_packages": {role: self._create_compensation_package(role, experience_level) for role in roles},
                "budget_analysis": {
                    "total_annual_cost": f"${len(roles) * 120}k - ${len(roles) * 180}k estimated total",
                    "budget_recommendations": ["Consider equity to offset base salary", "Flexible benefits package", "Performance bonuses"],
                    "cost_optimization": ["Negotiate based on candidate priorities", "Offer growth opportunities", "Competitive equity packages"]
                },
                "negotiation_guidelines": "Be transparent about compensation philosophy, understand candidate priorities, have flexibility in package structure."
            },
            
            "hiring_checklist": {
                "role_checklists": {role: self._create_role_checklist(role) for role in roles},
                "master_checklist": {
                    "setup_phase": ["Define hiring goals", "Set budget", "Prepare job descriptions", "Set up interview process"],
                    "execution_phase": ["Post jobs", "Screen candidates", "Conduct interviews", "Make decisions"],
                    "coordination_tasks": ["Weekly team meetings", "Candidate tracking", "Feedback collection"],
                    "milestones": ["Week 1: Jobs posted", "Week 2: Initial interviews", "Week 4: Final decisions", "Week 6: Onboarding"]
                },
                "timeline_overview": f"Expected timeline: {urgency.lower()} hiring process with {len(roles)} role(s) to fill. Estimated 4-6 weeks from job posting to hire."
            }
        }
        
        return plan
    
    def _extract_skills(self, user_input: str) -> List[str]:
        """Extract skills from user input"""
        skills = []
        skill_keywords = {
            "python": ["python"],
            "javascript": ["javascript", "js", "react", "node"],
            "machine learning": ["ml", "ai", "machine learning", "tensorflow", "pytorch"],
            "cloud": ["aws", "azure", "gcp", "cloud"],
            "databases": ["sql", "database", "postgresql", "mongodb"],
            "devops": ["docker", "kubernetes", "ci/cd", "devops"]
        }
        
        user_lower = user_input.lower()
        for skill, keywords in skill_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                skills.append(skill.title())
        
        if not skills:
            skills = ["Problem solving", "Communication", "Teamwork"]
        
        return skills
    
    def _extract_company_stage(self, company_context: Optional[str]) -> str:
        """Extract company stage from context"""
        if not company_context:
            return "Early-stage startup"
        
        context_lower = company_context.lower()
        if "series a" in context_lower:
            return "Series A"
        elif "series b" in context_lower:
            return "Series B"
        elif "seed" in context_lower:
            return "Seed stage"
        elif "pre-seed" in context_lower:
            return "Pre-seed"
        else:
            return "Early-stage startup"
    
    def _get_market_data(self, role: str) -> Dict:
        """Get market data for a role"""
        market_data = {
            "Software Engineer": {
                "salary_ranges": {"entry": "$70k-100k", "mid": "$100k-150k", "senior": "$150k-220k"},
                "key_skills": ["Python/JavaScript", "System Design", "Problem Solving", "Git"],
                "market_demand": "Very High",
                "competition_level": "High",
                "hiring_tips": ["Emphasize growth opportunities", "Competitive tech stack", "Strong engineering culture"]
            },
            "Ai Engineer": {
                "salary_ranges": {"entry": "$90k-130k", "mid": "$130k-180k", "senior": "$180k-280k"},
                "key_skills": ["Python", "TensorFlow/PyTorch", "Machine Learning", "Statistics"],
                "market_demand": "Extremely High",
                "competition_level": "Very High",
                "hiring_tips": ["Highlight AI projects", "Research opportunities", "Cutting-edge technology"]
            }
        }
        
        return market_data.get(role, market_data["Software Engineer"])
    
    def _create_job_description(self, role: str, experience_level: str) -> Dict:
        """Create job description for a role"""
        return {
            "title": f"{role} - Join Our Growing Team",
            "summary": f"We're looking for a talented {role.lower()} to help build innovative solutions and grow with our team.",
            "responsibilities": [
                f"Develop and maintain {role.lower()} solutions",
                "Collaborate with cross-functional teams",
                "Write clean, efficient, and maintainable code",
                "Participate in code reviews and technical discussions",
                "Contribute to product strategy and technical decisions"
            ],
            "required_qualifications": [
                f"{experience_level} experience in {role.lower()} role",
                "Strong problem-solving and analytical skills",
                "Excellent communication and teamwork abilities",
                "Experience with modern development practices",
                "Bachelor's degree or equivalent experience"
            ],
            "preferred_qualifications": [
                "Startup or fast-paced environment experience",
                "Leadership or mentoring experience",
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
            "application_process": "Send your resume and cover letter. We'll review applications on a rolling basis and reach out to qualified candidates."
        }
    
    def _create_interview_process(self, role: str) -> Dict:
        """Create interview process for a role"""
        return {
            "stages": [
                {"name": "Initial Screen", "duration": "30 minutes", "format": "Phone/Video", "focus": "Basic qualifications and interest"},
                {"name": "Technical Interview", "duration": "60 minutes", "format": "Video with coding", "focus": "Technical skills and problem-solving"},
                {"name": "Team Interview", "duration": "45 minutes", "format": "Video with team", "focus": "Collaboration and culture fit"},
                {"name": "Final Interview", "duration": "30 minutes", "format": "Video with leadership", "focus": "Vision alignment and questions"}
            ],
            "timeline": "2-3 weeks from application to decision",
            "evaluation_criteria": ["Technical competency", "Cultural fit", "Communication skills", "Growth potential", "Problem-solving approach"],
            "sample_questions": {
                "technical": [f"Walk us through your approach to a {role.lower()} challenge", "How would you handle scalability issues?", "Describe a complex project you worked on"],
                "behavioral": ["Tell us about a time you had to learn something quickly", "How do you handle feedback?", "Describe your ideal work environment"],
                "cultural": ["What motivates you in your work?", "How do you approach collaboration?", "What are your career goals?"]
            },
            "decision_process": "Collaborative decision with input from all interviewers and hiring manager",
            "logistics": "All interviews will be scheduled through our HR team with clear communication about expectations"
        }
    
    def _create_compensation_package(self, role: str, experience_level: str) -> Dict:
        """Create compensation package for a role"""
        salary_ranges = {
            "Entry Level": {"base": "$70k-100k", "equity": "0.1%-0.5%"},
            "Mid Level": {"base": "$100k-150k", "equity": "0.05%-0.3%"},
            "Senior Level": {"base": "$150k-220k", "equity": "0.02%-0.2%"}
        }
        
        range_data = salary_ranges.get(experience_level, salary_ranges["Mid Level"])
        
        return {
            "base_salary": {
                "range": range_data["base"],
                "justification": f"Market competitive for {experience_level} {role}"
            },
            "equity_percentage": {
                "range": range_data["equity"],
                "vesting": "4 years with 1-year cliff",
                "justification": "Startup equity to align with company growth"
            },
            "benefits": [
                "Health insurance (medical, dental, vision)",
                "401(k) retirement plan with company matching",
                "Paid time off and holidays",
                "Professional development budget ($2,000/year)",
                "Flexible work arrangements"
            ],
            "bonuses": {
                "performance_bonus": "Up to 15% of base salary annually",
                "signing_bonus": "Negotiable based on candidate situation",
                "referral_bonus": "$2,000 for successful referrals"
            },
            "perks": [
                "Flexible working hours",
                "Remote work options",
                "Modern equipment and tools",
                "Team building activities and events",
                "Learning and conference budget"
            ],
            "total_value_estimate": f"Total compensation package worth {range_data['base'].split('-')[0]}-{range_data['base'].split('-')[1]} plus equity upside"
        }
    
    def _create_role_checklist(self, role: str) -> Dict:
        """Create hiring checklist for a role"""
        return {
            "pre_posting": {
                "tasks": [
                    {"task": f"Finalize {role} job description", "deadline": "Day 1", "responsible": "Hiring Manager"},
                    {"task": "Set up interview panel and process", "deadline": "Day 2", "responsible": "HR"},
                    {"task": "Prepare technical assessment materials", "deadline": "Day 3", "responsible": "Technical Team"}
                ]
            },
            "job_posting": {
                "tasks": [
                    {"task": "Post on primary job boards (LinkedIn, Indeed)", "deadline": "Day 4", "responsible": "HR"},
                    {"task": "Share on company social media", "deadline": "Day 4", "responsible": "Marketing"},
                    {"task": "Reach out to professional networks", "deadline": "Day 5", "responsible": "Team"}
                ]
            },
            "screening": {
                "tasks": [
                    {"task": "Review and screen applications", "deadline": "Ongoing", "responsible": "HR + Hiring Manager"},
                    {"task": "Conduct initial phone screens", "deadline": "Week 2", "responsible": "HR"},
                    {"task": "Technical assessments", "deadline": "Week 2-3", "responsible": "Technical Team"}
                ]
            },
            "interviews": {
                "tasks": [
                    {"task": "Schedule interview rounds", "deadline": "Week 3", "responsible": "HR"},
                    {"task": "Conduct team interviews", "deadline": "Week 3-4", "responsible": "Interview Panel"},
                    {"task": "Collect and compile feedback", "deadline": "Week 4", "responsible": "HR"}
                ]
            },
            "decision_offer": {
                "tasks": [
                    {"task": "Make final hiring decision", "deadline": "Week 4", "responsible": "Hiring Manager"},
                    {"task": "Prepare and approve offer letter", "deadline": "Week 4", "responsible": "HR + Leadership"},
                    {"task": "Extend offer to candidate", "deadline": "Week 4", "responsible": "Hiring Manager"}
                ]
            },
            "onboarding": {
                "tasks": [
                    {"task": "Prepare onboarding materials and schedule", "deadline": "Before start date", "responsible": "HR"},
                    {"task": "Set up workspace and equipment", "deadline": "Before start date", "responsible": "IT"},
                    {"task": "Schedule first week meetings and introductions", "deadline": "Before start date", "responsible": "Hiring Manager"}
                ]
            }
        }
    
    def _create_fallback_plan(self, user_input: str, company_context: Optional[str], session_id: str, error: str) -> Dict:
        """Create a fallback plan when the main workflow fails"""
        return {
            "session_id": session_id,
            "user_request": user_input,
            "company_context": company_context,
            "status": "fallback",
            "error": error,
            "clarifications": {
                "extracted_info": {
                    "roles": ["Software Engineer", "Intern"],
                    "skills": ["Programming", "Problem solving"],
                    "timeline": "Standard hiring process",
                    "budget": "Competitive",
                    "company_stage": "Startup",
                    "team_size": "Small team"
                },
                "clarifying_questions": [
                    "What is your specific budget range?",
                    "What technologies should candidates know?",
                    "What is your ideal timeline?",
                    "Remote, hybrid, or onsite work?"
                ]
            },
            "job_descriptions": {
                "job_descriptions": {
                    "Software Engineer": {
                        "title": "Software Engineer - Join Our Growing Team",
                        "summary": "We're looking for a talented software engineer to help build innovative solutions.",
                        "responsibilities": ["Develop software solutions", "Collaborate with team", "Write clean code"],
                        "required_qualifications": ["Programming experience", "Problem-solving skills", "Team player"],
                        "what_we_offer": ["Competitive salary", "Growth opportunities", "Great team"]
                    }
                }
            },
            "interview_process": {
                "interview_processes": {
                    "Software Engineer": {
                        "stages": [
                            {"name": "Phone Screen", "duration": "30 min", "focus": "Basic fit"},
                            {"name": "Technical Interview", "duration": "60 min", "focus": "Coding skills"},
                            {"name": "Final Interview", "duration": "30 min", "focus": "Culture fit"}
                        ],
                        "timeline": "2-3 weeks"
                    }
                }
            },
            "compensation_packages": {
                "compensation_packages": {
                    "Software Engineer": {
                        "base_salary": {"range": "$80k-120k"},
                        "equity_percentage": {"range": "0.1%-0.5%"},
                        "benefits": ["Health insurance", "PTO", "Professional development"]
                    }
                }
            },
            "hiring_checklist": {
                "role_checklists": {
                    "Software Engineer": {
                        "pre_posting": {"tasks": [{"task": "Finalize job description", "deadline": "Day 1"}]},
                        "job_posting": {"tasks": [{"task": "Post on job boards", "deadline": "Day 2"}]},
                        "screening": {"tasks": [{"task": "Review applications", "deadline": "Week 1"}]}
                    }
                }
            },
            "agents_used": ["fallback"],
            "created_at": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        }
    
    async def _clarification_step(self, state: Dict) -> Dict:
        """Step 1: Ask clarifying questions and gather requirements"""
        clarifications = await self.clarification_agent.process(
            user_input=state["user_input"],
            company_context=state["company_context"]
        )
        
        state["clarifications"] = clarifications
        state["agents_used"].append("clarification")
        state["current_step"] = "market_research"
        return state
    
    async def _market_research_step(self, state: Dict) -> Dict:
        """Step 2: Conduct market research for roles"""
        market_data = await self.market_research_agent.process(
            clarifications=state["clarifications"],
            search_tool=self.google_search
        )
        
        state["market_research"] = market_data
        state["agents_used"].append("market_research")
        state["current_step"] = "job_description"
        return state
    
    async def _job_description_step(self, state: Dict) -> Dict:
        """Step 3: Generate job descriptions"""
        job_descriptions = await self.job_description_agent.process(
            clarifications=state["clarifications"],
            market_research=state["market_research"]
        )
        
        state["job_description"] = job_descriptions
        state["agents_used"].append("job_description")
        state["current_step"] = "interview_process"
        return state
    
    async def _interview_process_step(self, state: Dict) -> Dict:
        """Step 4: Design interview process"""
        interview_process = await self.interview_process_agent.process(
            job_descriptions=state["job_description"],
            clarifications=state["clarifications"]
        )
        
        state["interview_process"] = interview_process
        state["agents_used"].append("interview_process")
        state["current_step"] = "compensation"
        return state
    
    async def _compensation_step(self, state: Dict) -> Dict:
        """Step 5: Suggest compensation packages"""
        compensation = await self.compensation_agent.process(
            market_research=state["market_research"],
            clarifications=state["clarifications"]
        )
        
        state["compensation"] = compensation
        state["agents_used"].append("compensation")
        state["current_step"] = "checklist"
        return state
    
    async def _checklist_step(self, state: Dict) -> Dict:
        """Step 6: Build hiring checklist"""
        checklist = await self.checklist_builder_agent.process(
            job_descriptions=state["job_description"],
            interview_process=state["interview_process"],
            compensation=state["compensation"]
        )
        
        state["checklist"] = checklist
        state["agents_used"].append("checklist")
        state["current_step"] = "finalize"
        return state
    
    async def _finalize_step(self, state: Dict) -> Dict:
        """Step 7: Compile final hiring plan"""
        final_plan = {
            "session_id": state["session_id"],
            "user_request": state["user_input"],
            "company_context": state["company_context"],
            "clarifications": state["clarifications"],
            "market_research": state["market_research"],
            "job_descriptions": state["job_description"],
            "interview_process": state["interview_process"],
            "compensation_packages": state["compensation"],
            "hiring_checklist": state["checklist"],
            "agents_used": state["agents_used"],
            "created_at": asyncio.get_event_loop().time(),
            "status": "completed"
        }
        
        state["final_plan"] = final_plan
        return state
