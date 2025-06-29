import uuid
from typing import Optional, Dict, List
import logging
from datetime import datetime, timedelta

from .models import (
    ChatSession, ChatMessage, ChatContext, ChatResponse, ChatRequest,
    MessageRole, MessageType
)
from .llm_client import llm_client

class ChatbotManager:
    """Manager for chatbot functionality"""
    
    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = timedelta(hours=24)  # 24 hour timeout
        self.max_context_length = 4000  # Max characters for context
    
    def create_session(
        self, 
        user_id: Optional[str] = None,
        company_symbol: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            company_symbol=company_symbol,
            company_name=company_name
        )
        
        self.sessions[session_id] = session
        logging.info(f"Created chat session {session_id} for company {company_symbol}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a chat session by ID"""
        session = self.sessions.get(session_id)
        
        if session:
            # Check if session has expired
            if datetime.now() - session.last_activity > self.session_timeout:
                logging.info(f"Session {session_id} expired, removing")
                del self.sessions[session_id]
                return None
            
            # Update last activity
            session.last_activity = datetime.now()
        
        return session
    
    def add_message_to_session(
        self, 
        session_id: str, 
        role: MessageRole, 
        content: str,
        message_type: MessageType = MessageType.TEXT,
        metadata: Optional[Dict] = None
    ) -> Optional[ChatMessage]:
        """Add a message to a session"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        message = ChatMessage(
            id=f"msg_{int(datetime.now().timestamp())}",
            session_id=session_id,
            role=role,
            content=content,
            message_type=message_type,
            metadata=metadata
        )
        
        session.messages.append(message)
        session.last_activity = datetime.now()
        
        return message
    
    def get_session_messages(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        """Get messages from a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Return last N messages
        return session.messages[-limit:] if limit > 0 else session.messages
    
    def clear_session(self, session_id: str) -> bool:
        """Clear a session's messages"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.messages = []
        session.context = {}
        session.last_activity = datetime.now()
        
        logging.info(f"Cleared session {session_id}")
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logging.info(f"Deleted session {session_id}")
            return True
        return False
    
    def update_session_context(
        self, 
        session_id: str, 
        context_data: Dict
    ) -> bool:
        """Update session context with new data"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        if session.context is None:
            session.context = {}
        
        session.context.update(context_data)
        session.last_activity = datetime.now()
        
        return True
    
    def create_chat_context(
        self, 
        session_id: str,
        company_symbol: Optional[str] = None,
        annual_report_text: Optional[str] = None,
        technical_data: Optional[Dict] = None,
        fundamental_data: Optional[Dict] = None
    ) -> Optional[ChatContext]:
        """Create chat context for LLM"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Truncate report text if too long
        if annual_report_text and len(annual_report_text) > self.max_context_length:
            annual_report_text = annual_report_text[:self.max_context_length] + "..."
        
        # Get recent conversation history
        recent_messages = self.get_session_messages(session_id, limit=10)
        
        context = ChatContext(
            company_symbol=company_symbol or session.company_symbol,
            company_name=session.company_name,
            annual_report_text=annual_report_text,
            technical_data=technical_data,
            fundamental_data=fundamental_data,
            conversation_history=recent_messages,
            user_preferences=session.context.get('user_preferences', {})
        )
        
        return context
    
    def process_chat_request(self, request: ChatRequest) -> Optional[ChatResponse]:
        """Process a chat request"""
        try:
            # Get or create session
            session = self.get_session(request.session_id)
            if not session:
                session = self.create_session(company_symbol=request.company_symbol)
            
            # Add user message to session
            user_message = self.add_message_to_session(
                session_id=request.session_id,
                role=MessageRole.USER,
                content=request.message
            )
            
            if not user_message:
                return None
            
            # Create context if requested
            context = None
            if request.include_context:
                context = self.create_chat_context(
                    session_id=request.session_id,
                    company_symbol=request.company_symbol
                )
            
            # Process with LLM
            if not llm_client.is_loaded():
                # Fallback response if LLM not loaded
                fallback_response = ChatResponse(
                    message=ChatMessage(
                        id=f"msg_{int(datetime.now().timestamp())}",
                        session_id=request.session_id,
                        role=MessageRole.ASSISTANT,
                        content="I apologize, but the AI model is currently not available. Please try again later.",
                        message_type=MessageType.ERROR
                    ),
                    processing_time=0.1
                )
                return fallback_response
            
            chat_response = llm_client.process_chat_request(
                question=request.message,
                context=context,
                session_id=request.session_id
            )
            
            if chat_response:
                # Add assistant message to session
                self.add_message_to_session(
                    session_id=request.session_id,
                    role=MessageRole.ASSISTANT,
                    content=chat_response.message.content,
                    message_type=chat_response.message.message_type,
                    metadata=chat_response.message.metadata
                )
            
            return chat_response
            
        except Exception as e:
            logging.error(f"Error processing chat request: {e}")
            return None
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get summary of a session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "company_symbol": session.company_symbol,
            "company_name": session.company_name,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "message_count": len(session.messages),
            "context_keys": list(session.context.keys()) if session.context else []
        }
    
    def get_active_sessions(self) -> List[Dict]:
        """Get list of active sessions"""
        active_sessions = []
        
        for session_id, session in self.sessions.items():
            if datetime.now() - session.last_activity <= self.session_timeout:
                active_sessions.append(self.get_session_summary(session_id))
        
        return active_sessions
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and return count of removed sessions"""
        expired_count = 0
        current_time = datetime.now()
        
        session_ids_to_remove = []
        
        for session_id, session in self.sessions.items():
            if current_time - session.last_activity > self.session_timeout:
                session_ids_to_remove.append(session_id)
        
        for session_id in session_ids_to_remove:
            del self.sessions[session_id]
            expired_count += 1
        
        if expired_count > 0:
            logging.info(f"Cleaned up {expired_count} expired sessions")
        
        return expired_count
    
    def get_llm_status(self) -> Dict:
        """Get LLM status"""
        return {
            "llm_loaded": llm_client.is_loaded(),
            "model_info": llm_client.get_model_info(),
            "active_sessions": len(self.sessions),
            "session_timeout_hours": self.session_timeout.total_seconds() / 3600
        }

# Global instance
chatbot_manager = ChatbotManager() 