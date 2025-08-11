import os
import requests
from typing import Dict, List, Optional
from googleapiclient.discovery import build
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class GoogleSearchTool:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.cse_id = os.getenv("GOOGLE_CSE_ID")
        self.service = None
        
        if self.api_key and self.cse_id:
            try:
                self.service = build("customsearch", "v1", developerKey=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Google Search: {e}")
    
    async def search(self, query: str, num_results: int = 5) -> Dict:
        """Perform Google search and return results"""
        
        if not self.service:
            return {
                "query": query,
                "results": [],
                "error": "Google Search API not configured"
            }
        
        try:
            result = self.service.cse().list(
                q=query,
                cx=self.cse_id,
                num=num_results
            ).execute()
            
            items = result.get('items', [])
            search_results = []
            
            for item in items:
                search_results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "displayLink": item.get("displayLink", "")
                })
            
            return {
                "query": query,
                "results": search_results,
                "total_results": result.get("searchInformation", {}).get("totalResults", "0")
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "error": f"Search failed: {str(e)}"
            }

class EmailWriterTool:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    async def generate_email(self, email_type: str, context: Dict) -> Dict:
        """Generate professional emails for hiring process"""
        
        email_templates = {
            "rejection": "Write a professional, empathetic rejection email",
            "offer": "Write an exciting job offer email",
            "interview_invitation": "Write an interview invitation email",
            "follow_up": "Write a follow-up email to candidate",
            "reference_check": "Write a reference check request email"
        }
        
        system_prompt = f"""You are an expert HR professional. {email_templates.get(email_type, 'Write a professional email')}.
        
        Make it:
        - Professional but warm
        - Clear and actionable
        - Respectful of candidate's time
        - Aligned with company culture
        
        Include subject line and email body."""
        
        prompt = f"""
        Email Type: {email_type}
        Context: {context}
        
        Generate a complete email with subject and body.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            
            # Parse subject and body from response
            content = response.content
            lines = content.split('\n')
            
            subject = ""
            body = ""
            
            for i, line in enumerate(lines):
                if line.lower().startswith('subject:'):
                    subject = line.split(':', 1)[1].strip()
                    body = '\n'.join(lines[i+1:]).strip()
                    break
            
            if not subject:
                # Fallback if no subject line found
                subject = f"Regarding Your Application - {context.get('role', 'Position')}"
                body = content
            
            return {
                "email_type": email_type,
                "subject": subject,
                "body": body,
                "context": context
            }
            
        except Exception as e:
            return {
                "email_type": email_type,
                "subject": f"Regarding Your Application",
                "body": f"Thank you for your interest. We will be in touch soon.",
                "error": str(e)
            }

class DocumentGeneratorTool:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    async def generate_document(self, doc_type: str, content: Dict) -> str:
        """Generate various HR documents"""
        
        doc_templates = {
            "offer_letter": "Generate a formal job offer letter",
            "interview_scorecard": "Create an interview evaluation scorecard",
            "onboarding_checklist": "Create a new hire onboarding checklist",
            "job_posting": "Format a job posting for external platforms"
        }
        
        system_prompt = f"""You are an HR document specialist. {doc_templates.get(doc_type, 'Generate a professional document')}.
        
        Make it:
        - Legally compliant
        - Professional and clear
        - Complete and actionable
        - Industry standard format
        """
        
        prompt = f"""
        Document Type: {doc_type}
        Content: {content}
        
        Generate a complete, professional document.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            return f"Error generating {doc_type}: {str(e)}"
