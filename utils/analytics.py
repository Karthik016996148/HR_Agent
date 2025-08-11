import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

class AnalyticsTracker:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.analytics_file = os.path.join(storage_dir, "analytics.json")
        self.ensure_storage_dir()
    
    def ensure_storage_dir(self):
        """Ensure storage directory exists"""
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        
        # Initialize analytics file if it doesn't exist
        if not os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'w') as f:
                json.dump({
                    "sessions": [],
                    "plan_generations": [],
                    "chat_interactions": [],
                    "errors": []
                }, f)
    
    def track_session_created(self, session_id: str):
        """Track when a new session is created"""
        self._add_event("sessions", {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "session_created"
        })
    
    def track_plan_generation_started(self, session_id: str, user_input: str):
        """Track when plan generation starts"""
        self._add_event("plan_generations", {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "plan_generation_started",
            "user_input": user_input[:200]  # Truncate for storage
        })
    
    def track_plan_generation_completed(self, session_id: str):
        """Track when plan generation completes"""
        self._add_event("plan_generations", {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "plan_generation_completed"
        })
    
    def track_chat_interaction(self, session_id: str):
        """Track chat interactions"""
        self._add_event("chat_interactions", {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "chat_message"
        })
    
    def track_error(self, session_id: Optional[str], error_message: str):
        """Track errors for debugging"""
        self._add_event("errors", {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": "error",
            "error_message": error_message[:500]  # Truncate for storage
        })
    
    def get_analytics(self) -> Dict:
        """Get comprehensive analytics data"""
        try:
            data = self._load_analytics()
            
            # Calculate metrics
            now = datetime.now()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            last_30d = now - timedelta(days=30)
            
            def filter_by_time(events, time_threshold):
                return [
                    event for event in events
                    if datetime.fromisoformat(event["timestamp"]) >= time_threshold
                ]
            
            sessions_24h = filter_by_time(data["sessions"], last_24h)
            sessions_7d = filter_by_time(data["sessions"], last_7d)
            sessions_30d = filter_by_time(data["sessions"], last_30d)
            
            plans_24h = filter_by_time(data["plan_generations"], last_24h)
            plans_7d = filter_by_time(data["plan_generations"], last_7d)
            plans_30d = filter_by_time(data["plan_generations"], last_30d)
            
            chats_24h = filter_by_time(data["chat_interactions"], last_24h)
            chats_7d = filter_by_time(data["chat_interactions"], last_7d)
            chats_30d = filter_by_time(data["chat_interactions"], last_30d)
            
            errors_24h = filter_by_time(data["errors"], last_24h)
            errors_7d = filter_by_time(data["errors"], last_7d)
            
            return {
                "overview": {
                    "total_sessions": len(data["sessions"]),
                    "total_plans_generated": len([e for e in data["plan_generations"] if e["event_type"] == "plan_generation_completed"]),
                    "total_chat_interactions": len(data["chat_interactions"]),
                    "total_errors": len(data["errors"])
                },
                "recent_activity": {
                    "sessions_24h": len(sessions_24h),
                    "sessions_7d": len(sessions_7d),
                    "sessions_30d": len(sessions_30d),
                    "plans_24h": len([e for e in plans_24h if e["event_type"] == "plan_generation_completed"]),
                    "plans_7d": len([e for e in plans_7d if e["event_type"] == "plan_generation_completed"]),
                    "plans_30d": len([e for e in plans_30d if e["event_type"] == "plan_generation_completed"]),
                    "chats_24h": len(chats_24h),
                    "chats_7d": len(chats_7d),
                    "chats_30d": len(chats_30d)
                },
                "error_analysis": {
                    "errors_24h": len(errors_24h),
                    "errors_7d": len(errors_7d),
                    "recent_errors": errors_7d[-5:] if errors_7d else []  # Last 5 errors
                },
                "usage_patterns": self._analyze_usage_patterns(data),
                "performance_metrics": self._calculate_performance_metrics(data)
            }
            
        except Exception as e:
            return {
                "error": f"Failed to generate analytics: {str(e)}",
                "overview": {"total_sessions": 0, "total_plans_generated": 0}
            }
    
    def _analyze_usage_patterns(self, data: Dict) -> Dict:
        """Analyze usage patterns from the data"""
        
        # Analyze hourly usage
        hourly_usage = defaultdict(int)
        for event in data["sessions"]:
            try:
                hour = datetime.fromisoformat(event["timestamp"]).hour
                hourly_usage[hour] += 1
            except:
                continue
        
        # Find peak hours
        peak_hours = sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Analyze session duration (approximate based on chat interactions)
        session_interactions = defaultdict(int)
        for event in data["chat_interactions"]:
            session_interactions[event["session_id"]] += 1
        
        avg_interactions_per_session = (
            sum(session_interactions.values()) / len(session_interactions)
            if session_interactions else 0
        )
        
        return {
            "peak_hours": [{"hour": h, "sessions": c} for h, c in peak_hours],
            "avg_interactions_per_session": round(avg_interactions_per_session, 2),
            "active_sessions": len(session_interactions)
        }
    
    def _calculate_performance_metrics(self, data: Dict) -> Dict:
        """Calculate performance and success metrics"""
        
        # Calculate plan generation success rate
        started = len([e for e in data["plan_generations"] if e["event_type"] == "plan_generation_started"])
        completed = len([e for e in data["plan_generations"] if e["event_type"] == "plan_generation_completed"])
        
        success_rate = (completed / started * 100) if started > 0 else 0
        
        # Calculate error rate
        total_events = len(data["sessions"]) + len(data["plan_generations"]) + len(data["chat_interactions"])
        error_rate = (len(data["errors"]) / total_events * 100) if total_events > 0 else 0
        
        return {
            "plan_generation_success_rate": round(success_rate, 2),
            "error_rate": round(error_rate, 2),
            "total_events_processed": total_events
        }
    
    def _add_event(self, event_type: str, event_data: Dict):
        """Add an event to analytics"""
        try:
            data = self._load_analytics()
            data[event_type].append(event_data)
            
            # Keep only last 1000 events per type to prevent file from growing too large
            if len(data[event_type]) > 1000:
                data[event_type] = data[event_type][-1000:]
            
            self._save_analytics(data)
        except Exception as e:
            print(f"Error adding analytics event: {e}")
    
    def _load_analytics(self) -> Dict:
        """Load analytics data from file"""
        try:
            with open(self.analytics_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "sessions": [],
                "plan_generations": [],
                "chat_interactions": [],
                "errors": []
            }
    
    def _save_analytics(self, data: Dict):
        """Save analytics data to file"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving analytics: {e}")
