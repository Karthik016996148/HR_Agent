import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import uuid

class MemoryManager:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.sessions_file = os.path.join(storage_dir, "sessions.json")
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        # Initialize sessions file if it doesn't exist
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump({}, f)
    
    def create_session(self, session_id: str, session_data: Dict) -> bool:
        """Create a new session"""
        try:
            sessions = self._load_sessions()
            sessions[session_id] = session_data
            self._save_sessions(sessions)
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data by ID"""
        try:
            sessions = self._load_sessions()
            return sessions.get(session_id)
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def update_session_plan(self, session_id: str, hiring_plan: Dict) -> bool:
        """Update session with hiring plan"""
        try:
            sessions = self._load_sessions()
            if session_id in sessions:
                sessions[session_id]["hiring_plan"] = hiring_plan
                sessions[session_id]["updated_at"] = datetime.now().isoformat()
                self._save_sessions(sessions)
                return True
            return False
        except Exception as e:
            print(f"Error updating session plan: {e}")
            return False
    
    def add_chat_message(self, session_id: str, user_message: str, ai_response: str) -> bool:
        """Add chat message to session"""
        try:
            sessions = self._load_sessions()
            if session_id in sessions:
                if "messages" not in sessions[session_id]:
                    sessions[session_id]["messages"] = []
                
                sessions[session_id]["messages"].append({
                    "timestamp": datetime.now().isoformat(),
                    "user_message": user_message,
                    "ai_response": ai_response
                })
                
                sessions[session_id]["updated_at"] = datetime.now().isoformat()
                self._save_sessions(sessions)
                return True
            return False
        except Exception as e:
            print(f"Error adding chat message: {e}")
            return False
    
    def list_sessions(self) -> List[Dict]:
        """List all sessions with summary info"""
        try:
            sessions = self._load_sessions()
            session_list = []
            
            for session_id, data in sessions.items():
                session_list.append({
                    "session_id": session_id,
                    "created_at": data.get("created_at"),
                    "updated_at": data.get("updated_at"),
                    "status": data.get("status"),
                    "has_hiring_plan": bool(data.get("hiring_plan")),
                    "message_count": len(data.get("messages", []))
                })
            
            # Sort by creation date, newest first
            session_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            return session_list
            
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            sessions = self._load_sessions()
            if session_id in sessions:
                del sessions[session_id]
                self._save_sessions(sessions)
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def _load_sessions(self) -> Dict:
        """Load sessions from file"""
        try:
            with open(self.sessions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_sessions(self, sessions: Dict) -> bool:
        """Save sessions to file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(sessions, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving sessions: {e}")
            return False
