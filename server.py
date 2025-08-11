from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

from agents.hiring_orchestrator import HiringOrchestrator
from utils.memory_manager import MemoryManager
from utils.analytics import AnalyticsTracker

load_dotenv()

app = FastAPI(title="HR Agent API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
memory_manager = MemoryManager()
analytics_tracker = AnalyticsTracker()
hiring_orchestrator = HiringOrchestrator()

# Request/Response models
class HiringRequest(BaseModel):
    user_input: str
    company_context: Optional[str] = None
    session_id: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    status: str

class HiringPlanResponse(BaseModel):
    session_id: str
    plan: Dict
    status: str
    agents_used: List[str]

@app.get("/")
async def root():
    return {"message": "HR Agent API is running", "status": "healthy"}

@app.post("/api/sessions", response_model=SessionResponse)
async def create_session():
    """Create a new hiring session"""
    session_id = str(uuid.uuid4())
    session_data = {
        "id": session_id,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "messages": [],
        "hiring_plan": None
    }
    
    memory_manager.create_session(session_id, session_data)
    analytics_tracker.track_session_created(session_id)
    
    return SessionResponse(session_id=session_id, status="created")

@app.post("/api/generate_hiring_plan", response_model=HiringPlanResponse)
async def generate_hiring_plan(request: HiringRequest):
    """Generate a comprehensive hiring plan using multi-agent system"""
    try:
        # Create session if not provided
        if not request.session_id:
            session_response = await create_session()
            session_id = session_response.session_id
        else:
            session_id = request.session_id
        
        # Track analytics
        analytics_tracker.track_plan_generation_started(session_id, request.user_input)
        
        # Run the multi-agent hiring orchestrator
        hiring_plan = await hiring_orchestrator.generate_hiring_plan(
            user_input=request.user_input,
            company_context=request.company_context,
            session_id=session_id
        )
        
        # Store the plan in memory
        memory_manager.update_session_plan(session_id, hiring_plan)
        
        # Track completion
        analytics_tracker.track_plan_generation_completed(session_id)
        
        return HiringPlanResponse(
            session_id=session_id,
            plan=hiring_plan,
            status="completed",
            agents_used=hiring_plan.get("agents_used", [])
        )
        
    except Exception as e:
        analytics_tracker.track_error(session_id if 'session_id' in locals() else None, str(e))
        raise HTTPException(status_code=500, detail=f"Error generating hiring plan: {str(e)}")

@app.post("/api/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat with AI assistant about hiring plans"""
    try:
        # Get session context
        session_data = memory_manager.get_session(request.session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate AI response using context
        response = await hiring_orchestrator.chat_response(
            message=request.message,
            session_context=session_data,
            session_id=request.session_id
        )
        
        # Store chat message
        memory_manager.add_chat_message(request.session_id, request.message, response)
        analytics_tracker.track_chat_interaction(request.session_id)
        
        return {"response": response, "session_id": request.session_id}
        
    except Exception as e:
        analytics_tracker.track_error(request.session_id, str(e))
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session data including hiring plan and chat history"""
    session_data = memory_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions"""
    return memory_manager.list_sessions()

@app.get("/api/analytics")
async def get_analytics():
    """Get usage analytics and statistics"""
    return analytics_tracker.get_analytics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
