import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="HR Agent - Startup Hiring Assistant",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8001"

# Custom CSS for attractive and colorful styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Main Header */
    .main-header {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background: linear-gradient(90deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 8px;
        color: white;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(240, 147, 251, 0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4);
    }
    
    /* Success Cards */
    .success-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
    }
    
    /* Info Cards */
    .info-card {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    /* Warning Cards */
    .warning-card {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3);
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 15px;
        border-left: 5px solid #667eea;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        font-family: 'Inter', sans-serif;
    }
    
    /* User Message */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 5px solid #f093fb;
        margin-left: 2rem;
    }
    
    /* Assistant Message */
    .assistant-message {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-left: 5px solid #10b981;
        margin-right: 2rem;
    }
    
    /* Form Styling */
    .stSelectbox > div > div {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 8px;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.4);
    }
    
    /* Success Box */
    .success-box {
        padding: 1.5rem;
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        border: 2px solid #10b981;
        border-radius: 15px;
        color: #065f46;
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
        color: #065f46;
    }
    
    /* Sidebar Navigation */
    .css-1d391kg .css-1v0mbdj {
        color: white;
        font-weight: 600;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    }
    
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 10px;
        font-weight: 600;
        color: #374151;
    }
    
    /* Data Frame Styling */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Custom Animation */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* Gradient Background */
    .main {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%, #f8fafc 100%);
    }
</style>
""", unsafe_allow_html=True)

# Beautiful, colorful header
st.markdown("""
<div class="main-header fade-in">
    🚀 HR Agent - AI Hiring Assistant 🎯
</div>
<div style="text-align: center; margin-bottom: 2rem;">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); 
                padding: 1rem; border-radius: 15px; margin: 1rem auto; max-width: 800px; 
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
        <h3 style="color: white; margin: 0; font-family: 'Inter', sans-serif;">
            🤖 AI-Powered Multi-Agent Hiring System
        </h3>
        <p style="color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;">
            ✨ Generate comprehensive hiring plans • 💬 Chat with AI assistants • 📊 Track analytics
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'hiring_plan' not in st.session_state:
        st.session_state.hiring_plan = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'sessions_list' not in st.session_state:
        st.session_state.sessions_list = []

def create_new_session():
    """Create a new hiring session"""
    try:
        response = requests.post(f"{API_BASE_URL}/api/sessions")
        if response.status_code == 200:
            data = response.json()
            st.session_state.session_id = data["session_id"]
            st.session_state.hiring_plan = None
            st.session_state.chat_history = []
            return True
        else:
            st.error(f"Failed to create session: {response.text}")
            return False
    except Exception as e:
        st.error(f"Error creating session: {str(e)}")
        return False

def generate_hiring_plan(user_input, company_context=""):
    """Generate hiring plan using the multi-agent system"""
    try:
        payload = {
            "user_input": user_input,
            "company_context": company_context,
            "session_id": st.session_state.session_id
        }
        
        with st.spinner("🤖 Our AI agents are working on your hiring plan..."):
            response = requests.post(f"{API_BASE_URL}/api/generate_hiring_plan", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.hiring_plan = data["plan"]
            st.session_state.session_id = data["session_id"]
            return data["plan"]
        else:
            st.error(f"Failed to generate hiring plan: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error generating hiring plan: {str(e)}")
        return None

def send_chat_message(message):
    """Send chat message to AI assistant"""
    try:
        payload = {
            "message": message,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(f"{API_BASE_URL}/api/chat", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data["response"]
        else:
            st.error(f"Chat error: {response.text}")
            return None
    except Exception as e:
        st.error(f"Error in chat: {str(e)}")
        return None

def get_analytics():
    """Get analytics data from the backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/analytics")
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching analytics: {str(e)}")
        return None

def display_hiring_plan(plan):
    """Display the hiring plan in a structured format"""
    if not plan:
        return
    
    st.markdown("## 📋 Your Comprehensive Hiring Plan")
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Overview", "💼 Job Descriptions", "🎯 Interview Process", 
        "💰 Compensation", "✅ Checklist", "📊 Market Research"
    ])
    
    with tab1:
        st.markdown("### 🎯 Hiring Overview")
        if "clarifications" in plan:
            clarifications = plan["clarifications"]
            extracted_info = clarifications.get("extracted_info", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Roles to Hire:**")
                for role in extracted_info.get("roles", []):
                    st.markdown(f"• {role}")
                
                st.markdown("**Timeline:**")
                st.markdown(f"• {extracted_info.get('timeline', 'Not specified')}")
            
            with col2:
                st.markdown("**Budget:**")
                st.markdown(f"• {extracted_info.get('budget', 'Not specified')}")
                
                st.markdown("**Work Mode:**")
                st.markdown(f"• {extracted_info.get('work_mode', 'Not specified')}")
            
            if clarifications.get("clarifying_questions"):
                st.markdown("### ❓ Clarifying Questions")
                for question in clarifications["clarifying_questions"]:
                    st.markdown(f"• {question}")
    
    with tab2:
        st.markdown("### 💼 Job Descriptions")
        if "job_descriptions" in plan:
            jd_data = plan["job_descriptions"]
            job_descriptions = jd_data.get("job_descriptions", {})
            
            for role, jd in job_descriptions.items():
                with st.expander(f"📄 {role} - Job Description"):
                    st.markdown(f"**{jd.get('title', role)}**")
                    st.markdown(f"*{jd.get('summary', 'No summary available')}*")
                    
                    st.markdown("**Key Responsibilities:**")
                    for resp in jd.get("responsibilities", []):
                        st.markdown(f"• {resp}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Required Qualifications:**")
                        for qual in jd.get("required_qualifications", []):
                            st.markdown(f"• {qual}")
                    
                    with col2:
                        st.markdown("**Preferred Qualifications:**")
                        for qual in jd.get("preferred_qualifications", []):
                            st.markdown(f"• {qual}")
                    
                    st.markdown("**What We Offer:**")
                    for offer in jd.get("what_we_offer", []):
                        st.markdown(f"• {offer}")
    
    with tab3:
        st.markdown("### 🎯 Interview Process")
        if "interview_process" in plan:
            interview_data = plan["interview_process"]
            processes = interview_data.get("interview_processes", {})
            
            for role, process in processes.items():
                with st.expander(f"🎤 {role} - Interview Process"):
                    stages = process.get("stages", [])
                    
                    st.markdown("**Interview Stages:**")
                    for i, stage in enumerate(stages, 1):
                        st.markdown(f"""
                        **Stage {i}: {stage.get('name', 'Unknown')}**
                        - Duration: {stage.get('duration', 'TBD')}
                        - Format: {stage.get('format', 'TBD')}
                        - Focus: {stage.get('focus', 'TBD')}
                        """)
                    
                    st.markdown(f"**Timeline:** {process.get('timeline', 'TBD')}")
                    
                    st.markdown("**Evaluation Criteria:**")
                    for criteria in process.get("evaluation_criteria", []):
                        st.markdown(f"• {criteria}")
    
    with tab4:
        st.markdown("### 💰 Compensation Packages")
        if "compensation_packages" in plan:
            comp_data = plan["compensation_packages"]
            packages = comp_data.get("compensation_packages", {})
            
            for role, package in packages.items():
                with st.expander(f"💵 {role} - Compensation Package"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Base Salary:**")
                        salary_info = package.get("base_salary", {})
                        if isinstance(salary_info, dict):
                            st.markdown(f"• Range: {salary_info.get('range', 'TBD')}")
                            st.markdown(f"• Justification: {salary_info.get('justification', 'Market competitive')}")
                        else:
                            st.markdown(f"• {salary_info}")
                        
                        st.markdown("**Equity:**")
                        equity_info = package.get("equity_percentage", {})
                        if isinstance(equity_info, dict):
                            st.markdown(f"• Range: {equity_info.get('range', 'TBD')}")
                            st.markdown(f"• Vesting: {equity_info.get('vesting', '4 years')}")
                        else:
                            st.markdown(f"• {equity_info}")
                    
                    with col2:
                        st.markdown("**Benefits:**")
                        for benefit in package.get("benefits", []):
                            st.markdown(f"• {benefit}")
                        
                        st.markdown("**Perks:**")
                        for perk in package.get("perks", []):
                            st.markdown(f"• {perk}")
    
    with tab5:
        st.markdown("### ✅ Hiring Checklist")
        if "hiring_checklist" in plan:
            checklist_data = plan["hiring_checklist"]
            role_checklists = checklist_data.get("role_checklists", {})
            
            for role, checklist in role_checklists.items():
                with st.expander(f"📋 {role} - Hiring Checklist"):
                    for phase_name, phase_data in checklist.items():
                        if isinstance(phase_data, dict) and "tasks" in phase_data:
                            st.markdown(f"**{phase_name.replace('_', ' ').title()}:**")
                            for task in phase_data["tasks"]:
                                if isinstance(task, dict):
                                    st.markdown(f"• {task.get('task', 'Unknown task')} (Due: {task.get('deadline', 'TBD')}) - {task.get('responsible', 'TBD')}")
                                else:
                                    st.markdown(f"• {task}")
            
            # Master checklist
            if "master_checklist" in checklist_data:
                st.markdown("### 🎯 Master Checklist")
                master = checklist_data["master_checklist"]
                for phase, tasks in master.items():
                    st.markdown(f"**{phase.replace('_', ' ').title()}:**")
                    for task in tasks:
                        st.markdown(f"• {task}")
    
    with tab6:
        st.markdown("### 📊 Market Research")
        if "market_research" in plan:
            market_data = plan["market_research"]
            roles_data = market_data.get("market_data", {})
            
            for role, data in roles_data.items():
                with st.expander(f"📈 {role} - Market Analysis"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Salary Ranges:**")
                        salary_ranges = data.get("salary_ranges", {})
                        for level, range_val in salary_ranges.items():
                            st.markdown(f"• {level.title()}: {range_val}")
                        
                        st.markdown(f"**Market Demand:** {data.get('market_demand', 'Unknown')}")
                        st.markdown(f"**Competition Level:** {data.get('competition_level', 'Unknown')}")
                    
                    with col2:
                        st.markdown("**Key Skills:**")
                        for skill in data.get("key_skills", []):
                            st.markdown(f"• {skill}")
                        
                        st.markdown("**Hiring Tips:**")
                        for tip in data.get("hiring_tips", []):
                            st.markdown(f"• {tip}")

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    # Sidebar with enhanced styling
    with st.sidebar:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem; 
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
            <h2 style="color: white; margin: 0; text-align: center; font-family: 'Inter', sans-serif;">
                🎛️ Control Panel
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Session management with colorful cards
        st.markdown("""
        <div class="info-card">
            <h3 style="margin: 0 0 1rem 0; color: white;">🔧 Session Management</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🆕 New Hiring Session", type="primary"):
            if create_new_session():
                st.markdown("""
                <div class="success-card">
                    <p style="margin: 0; color: white;">✅ New session created successfully!</p>
                </div>
                """, unsafe_allow_html=True)
                st.rerun()
        
        if st.session_state.session_id:
            st.markdown(f"""
            <div class="success-card">
                <p style="margin: 0; color: white;">🎯 Active Session: {st.session_state.session_id[:8]}...</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Navigation moved to main area - keeping sidebar clean
        
        # Add helpful tips
        st.markdown("""
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 1rem; border-radius: 10px; margin-top: 1rem;">
            <h4 style="color: white; margin: 0 0 0.5rem 0;">💡 Quick Tips</h4>
            <ul style="color: white; margin: 0; font-size: 0.9rem;">
                <li>Start with "Generate Plan" for new hires</li>
                <li>Use "Chat Assistant" for questions</li>
                <li>Check "Analytics" for insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation in main area - top right corner
    col1, col2 = st.columns([3, 1])
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 0.5rem; border-radius: 10px; margin-bottom: 1rem;">
            <p style="color: white; margin: 0; text-align: center; font-weight: 600;">🧭 Navigation</p>
        </div>
        """, unsafe_allow_html=True)
        page = st.selectbox("Choose a page:", [
            "📋 Generate Plan", "💬 Chat Assistant", "📊 Analytics", "📚 Sessions"
        ], label_visibility="collapsed")
    
    # Main content based on selected page
    if page == "📋 Generate Plan":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; 
                    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
            <h2 style="color: white; margin: 0; text-align: center; font-family: 'Inter', sans-serif;">
                📋 Generate Hiring Plan
            </h2>
            <p style="color: rgba(255,255,255,0.9); text-align: center; margin: 0.5rem 0 0 0;">
                🚀 Let our AI agents create a comprehensive hiring strategy for your company
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if not st.session_state.session_id:
            st.markdown("""
            <div class="warning-card">
                <h3 style="margin: 0; color: white;">⚠️ Session Required</h3>
                <p style="margin: 0.5rem 0 0 0; color: white;">Please create a new session first using the sidebar to get started.</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        st.markdown("### Tell us about your hiring needs:")
        
        # Input form with structured options
        with st.form("hiring_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**🎯 Roles & Requirements**")
                
                # Role selection
                roles_needed = st.multiselect(
                    "Select roles to hire:",
                    [
                        "Software Engineer", "Senior Software Engineer", "Lead Engineer",
                        "Frontend Developer", "Backend Developer", "Full Stack Developer",
                        "DevOps Engineer", "Data Engineer", "ML Engineer", "AI Engineer",
                        "Product Manager", "Designer (UI/UX)", "QA Engineer",
                        "Marketing Manager", "Sales Representative", "HR Manager",
                        "Intern", "Other"
                    ],
                    help="Select all roles you need to hire"
                )
                
                # Custom role input if "Other" is selected
                custom_roles = ""
                if "Other" in roles_needed:
                    custom_roles = st.text_input("Specify other roles:", placeholder="e.g., Blockchain Developer, Growth Hacker")
                
                # Experience level
                experience_level = st.selectbox(
                    "Primary experience level needed:",
                    ["Entry Level (0-2 years)", "Mid Level (2-5 years)", "Senior Level (5+ years)", "Mixed levels"]
                )
                
                # Urgency
                urgency = st.selectbox(
                    "Hiring urgency:",
                    ["ASAP (within 2 weeks)", "Soon (within 1 month)", "Standard (1-3 months)", "Long-term (3+ months)"]
                )
            
            with col2:
                st.markdown("**🏢 Company Context**")
                
                # Company stage
                company_stage = st.selectbox(
                    "Company stage:",
                    ["Pre-seed", "Seed", "Series A", "Series B+", "Growth stage", "Established"]
                )
                
                # Team size
                team_size = st.selectbox(
                    "Current team size:",
                    ["1-5 people", "6-15 people", "16-50 people", "51-100 people", "100+ people"]
                )
                
                # Budget range
                budget_range = st.selectbox(
                    "Budget per role (annual salary):",
                    ["<$50k", "$50k-$80k", "$80k-$120k", "$120k-$180k", "$180k-$250k", "$250k+", "Flexible/Competitive"]
                )
                
                # Work arrangement
                work_mode = st.selectbox(
                    "Work arrangement:",
                    ["Remote", "Hybrid", "On-site", "Flexible"]
                )
                
                # Location
                location = st.text_input("Location/Time zone:", placeholder="e.g., San Francisco, EST, Global")
            
            # Key skills and requirements
            st.markdown("**🛠️ Key Skills & Requirements**")
            key_skills = st.text_area(
                "Essential skills and technologies:",
                placeholder="e.g., Python, React, AWS, Machine Learning, Agile, etc.",
                height=60
            )
            
            # Additional context
            st.markdown("**📝 Additional Context**")
            additional_context = st.text_area(
                "Any specific requirements or context:",
                placeholder="Company culture, specific projects, growth plans, etc.",
                height=80
            )
            
            # Free form input (optional)
            st.markdown("**💬 Or describe in your own words:**")
            user_input = st.text_area(
                "Free-form description (optional):",
                placeholder="Example: I need to hire a founding engineer and a GenAI intern. Can you help?",
                height=80
            )
            
            submitted = st.form_submit_button("🚀 Generate Hiring Plan", type="primary")
        
        if submitted and (roles_needed or user_input):
            # Construct comprehensive input from structured form data
            structured_input = []
            
            # Add roles
            if roles_needed:
                roles_list = roles_needed.copy()
                if custom_roles:
                    roles_list.append(custom_roles)
                structured_input.append(f"Roles needed: {', '.join(roles_list)}")
            
            # Add experience level
            if experience_level:
                structured_input.append(f"Experience level: {experience_level}")
            
            # Add urgency
            if urgency:
                structured_input.append(f"Timeline: {urgency}")
            
            # Add key skills
            if key_skills:
                structured_input.append(f"Key skills required: {key_skills}")
            
            # Combine with free-form input if provided
            if user_input:
                structured_input.append(f"Additional details: {user_input}")
            
            final_user_input = ". ".join(structured_input)
            
            # Construct company context from structured data
            company_context_parts = []
            if company_stage:
                company_context_parts.append(f"Company stage: {company_stage}")
            if team_size:
                company_context_parts.append(f"Team size: {team_size}")
            if budget_range:
                company_context_parts.append(f"Budget range: {budget_range}")
            if work_mode:
                company_context_parts.append(f"Work arrangement: {work_mode}")
            if location:
                company_context_parts.append(f"Location: {location}")
            if additional_context:
                company_context_parts.append(f"Additional context: {additional_context}")
            
            final_company_context = ". ".join(company_context_parts)
            
            # Generate the plan
            plan = generate_hiring_plan(final_user_input, final_company_context)
            if plan:
                st.success("🎉 Hiring plan generated successfully!")
                
                # Show what was processed
                with st.expander("📋 Input Summary", expanded=False):
                    st.markdown("**Processed Requirements:**")
                    st.write(final_user_input)
                    if final_company_context:
                        st.markdown("**Company Context:**")
                        st.write(final_company_context)
                
                display_hiring_plan(plan)
            else:
                st.error("Failed to generate hiring plan. Please try again or check your inputs.")
        
        # Display existing plan if available
        elif st.session_state.hiring_plan:
            st.markdown("### Your Current Hiring Plan:")
            display_hiring_plan(st.session_state.hiring_plan)
    
    elif page == "💬 Chat Assistant":
        st.markdown("## 💬 Chat with HR Assistant")
        
        if not st.session_state.session_id:
            st.warning("Please create a new session first using the sidebar.")
            return
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for i, (user_msg, ai_msg) in enumerate(st.session_state.chat_history):
                st.markdown(f'<div class="chat-message"><strong>You:</strong> {user_msg}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-message"><strong>AI Assistant:</strong> {ai_msg}</div>', unsafe_allow_html=True)
        
        # Chat input
        with st.form("chat_form", clear_on_submit=True):
            user_message = st.text_input("Ask me anything about your hiring plan or HR best practices:")
            sent = st.form_submit_button("Send", type="primary")
        
        if sent and user_message:
            ai_response = send_chat_message(user_message)
            if ai_response:
                st.session_state.chat_history.append((user_message, ai_response))
                st.rerun()
    
    elif page == "📊 Analytics":
        st.markdown("## 📊 Analytics Dashboard")
        
        analytics_data = get_analytics()
        if analytics_data:
            # Overview metrics
            overview = analytics_data.get("overview", {})
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", overview.get("total_sessions", 0))
            with col2:
                st.metric("Plans Generated", overview.get("total_plans_generated", 0))
            with col3:
                st.metric("Chat Interactions", overview.get("total_chat_interactions", 0))
            with col4:
                st.metric("Total Errors", overview.get("total_errors", 0))
            
            # Recent activity
            st.markdown("### 📈 Recent Activity")
            recent = analytics_data.get("recent_activity", {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Sessions Created:**")
                st.markdown(f"• Last 24h: {recent.get('sessions_24h', 0)}")
                st.markdown(f"• Last 7d: {recent.get('sessions_7d', 0)}")
                st.markdown(f"• Last 30d: {recent.get('sessions_30d', 0)}")
            
            with col2:
                st.markdown("**Plans Generated:**")
                st.markdown(f"• Last 24h: {recent.get('plans_24h', 0)}")
                st.markdown(f"• Last 7d: {recent.get('plans_7d', 0)}")
                st.markdown(f"• Last 30d: {recent.get('plans_30d', 0)}")
            
            # Usage patterns with enhanced charts
            usage_patterns = analytics_data.get("usage_patterns", {})
            
            # Peak hours chart
            if usage_patterns.get("peak_hours"):
                st.markdown("### ⏰ Peak Usage Hours")
                peak_data = usage_patterns["peak_hours"]
                df = pd.DataFrame(peak_data)
                if not df.empty:
                    fig = px.bar(
                        df, x="hour", y="sessions", 
                        title="Sessions by Hour of Day",
                        color="sessions",
                        color_continuous_scale="viridis"
                    )
                    fig.update_layout(
                        xaxis_title="Hour of Day",
                        yaxis_title="Number of Sessions",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Activity trends over time
            st.markdown("### 📈 Activity Trends")
            col1, col2 = st.columns(2)
            
            with col1:
                # Sessions trend (simulated data for demo)
                dates = pd.date_range(start='2024-01-01', end='2024-01-30', freq='D')
                sessions_trend = pd.DataFrame({
                    'Date': dates,
                    'Sessions': [max(0, 5 + int(10 * (0.5 - abs(i - 15) / 30))) for i in range(len(dates))]
                })
                
                fig_sessions = px.line(
                    sessions_trend, x='Date', y='Sessions',
                    title="Daily Sessions Trend",
                    color_discrete_sequence=["#1f77b4"]
                )
                fig_sessions.update_layout(showlegend=False)
                st.plotly_chart(fig_sessions, use_container_width=True)
            
            with col2:
                # Plans generated trend (simulated data for demo)
                plans_trend = pd.DataFrame({
                    'Date': dates,
                    'Plans': [max(0, 3 + int(8 * (0.5 - abs(i - 15) / 30))) for i in range(len(dates))]
                })
                
                fig_plans = px.line(
                    plans_trend, x='Date', y='Plans',
                    title="Daily Plans Generated",
                    color_discrete_sequence=["#ff7f0e"]
                )
                fig_plans.update_layout(showlegend=False)
                st.plotly_chart(fig_plans, use_container_width=True)
            
            # Agent usage distribution
            st.markdown("### 🤖 Agent Usage Distribution")
            agent_data = pd.DataFrame({
                'Agent': ['Clarification', 'Market Research', 'Job Description', 'Interview Process', 'Compensation', 'Checklist'],
                'Usage': [95, 87, 92, 89, 85, 88]  # Simulated usage percentages
            })
            
            fig_agents = px.pie(
                agent_data, values='Usage', names='Agent',
                title="Agent Utilization Rate (%)",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_agents.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_agents, use_container_width=True)
            
            # Performance metrics with gauges
            performance = analytics_data.get("performance_metrics", {})
            if performance:
                st.markdown("### 🎯 Performance Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Success rate gauge
                    success_rate = performance.get('plan_generation_success_rate', 85)
                    fig_success = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = success_rate,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Success Rate (%)"},
                        delta = {'reference': 80},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 80], 'color': "gray"},
                                {'range': [80, 100], 'color': "lightgreen"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ))
                    fig_success.update_layout(height=300)
                    st.plotly_chart(fig_success, use_container_width=True)
                
                with col2:
                    # Error rate gauge
                    error_rate = performance.get('error_rate', 5)
                    fig_error = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = error_rate,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Error Rate (%)"},
                        gauge = {
                            'axis': {'range': [None, 20]},
                            'bar': {'color': "darkred"},
                            'steps': [
                                {'range': [0, 5], 'color': "lightgreen"},
                                {'range': [5, 10], 'color': "yellow"},
                                {'range': [10, 20], 'color': "lightcoral"}
                            ]
                        }
                    ))
                    fig_error.update_layout(height=300)
                    st.plotly_chart(fig_error, use_container_width=True)
                
                with col3:
                    # Response time gauge (simulated)
                    response_time = 2.3  # seconds
                    fig_response = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = response_time,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': "Avg Response Time (s)"},
                        gauge = {
                            'axis': {'range': [None, 10]},
                            'bar': {'color': "darkgreen"},
                            'steps': [
                                {'range': [0, 3], 'color': "lightgreen"},
                                {'range': [3, 6], 'color': "yellow"},
                                {'range': [6, 10], 'color': "lightcoral"}
                            ]
                        }
                    ))
                    fig_response.update_layout(height=300)
                    st.plotly_chart(fig_response, use_container_width=True)
            
            # User engagement metrics
            st.markdown("### 👥 User Engagement")
            col1, col2 = st.columns(2)
            
            with col1:
                # Session duration distribution
                durations = pd.DataFrame({
                    'Duration Range': ['< 5 min', '5-15 min', '15-30 min', '30+ min'],
                    'Sessions': [12, 35, 28, 15]
                })
                
                fig_duration = px.bar(
                    durations, x='Duration Range', y='Sessions',
                    title="Session Duration Distribution",
                    color='Sessions',
                    color_continuous_scale="blues"
                )
                fig_duration.update_layout(showlegend=False)
                st.plotly_chart(fig_duration, use_container_width=True)
            
            with col2:
                # Feature usage heatmap
                features = ['Generate Plan', 'Chat Assistant', 'Analytics', 'Sessions']
                days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                
                # Simulated heatmap data
                heatmap_data = [[15, 12, 8, 5], [18, 14, 10, 6], [22, 16, 12, 8], 
                               [20, 15, 11, 7], [25, 18, 14, 9], [10, 8, 6, 4], [8, 6, 4, 3]]
                
                fig_heatmap = px.imshow(
                    heatmap_data,
                    x=features,
                    y=days,
                    title="Feature Usage Heatmap",
                    color_continuous_scale="viridis",
                    aspect="auto"
                )
                st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.warning("Unable to fetch analytics data. Make sure the backend is running.")
    
    elif page == "📚 Sessions":
        st.markdown("## 📚 Session History")
        
        try:
            response = requests.get(f"{API_BASE_URL}/api/sessions")
            if response.status_code == 200:
                sessions = response.json()
                if sessions:
                    df = pd.DataFrame(sessions)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("No sessions found.")
            else:
                st.error("Failed to fetch sessions.")
        except Exception as e:
            st.error(f"Error fetching sessions: {str(e)}")

if __name__ == "__main__":
    main()
