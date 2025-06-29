from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Dict
import logging

from ..chatbot.manager import chatbot_manager
from ..chatbot.models import ChatRequest, ChatResponse, ChatSession

router = APIRouter(prefix="/api/chat", tags=["Chatbot"])

@router.post("/ask")
async def ask_question(request: ChatRequest) -> ChatResponse:
    """Ask a question to the financial chatbot"""
    try:
        response = chatbot_manager.process_chat_request(request)
        if not response:
            raise HTTPException(status_code=500, detail="Failed to process chat request")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error processing chat request: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

@router.post("/session/create")
async def create_session(
    user_id: Optional[str] = Body(None),
    company_symbol: Optional[str] = Body(None),
    company_name: Optional[str] = Body(None)
) -> ChatSession:
    """Create a new chat session"""
    try:
        session = chatbot_manager.create_session(
            user_id=user_id,
            company_symbol=company_symbol,
            company_name=company_name
        )
        return session
    except Exception as e:
        logging.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Error creating chat session")

@router.get("/session/{session_id}")
async def get_session(session_id: str) -> Dict:
    """Get session information and messages"""
    try:
        session = chatbot_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = chatbot_manager.get_session_messages(session_id)
        
        return {
            "session": chatbot_manager.get_session_summary(session_id),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "message_type": msg.message_type.value
                }
                for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving session")

@router.get("/session/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 50
) -> List[Dict]:
    """Get messages from a session"""
    try:
        messages = chatbot_manager.get_session_messages(session_id, limit=limit)
        
        return [
            {
                "id": msg.id,
                "role": msg.role.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "message_type": msg.message_type.value,
                "metadata": msg.metadata
            }
            for msg in messages
        ]
    except Exception as e:
        logging.error(f"Error getting messages for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving messages")

@router.delete("/session/{session_id}")
async def delete_session(session_id: str) -> Dict:
    """Delete a chat session"""
    try:
        success = chatbot_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting session")

@router.post("/session/{session_id}/clear")
async def clear_session(session_id: str) -> Dict:
    """Clear messages from a session"""
    try:
        success = chatbot_manager.clear_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session cleared successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error clearing session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Error clearing session")

@router.get("/sessions/active")
async def get_active_sessions() -> List[Dict]:
    """Get list of active sessions"""
    try:
        sessions = chatbot_manager.get_active_sessions()
        return sessions
    except Exception as e:
        logging.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving active sessions")

@router.post("/sessions/cleanup")
async def cleanup_expired_sessions() -> Dict:
    """Clean up expired sessions"""
    try:
        expired_count = chatbot_manager.cleanup_expired_sessions()
        return {
            "message": f"Cleaned up {expired_count} expired sessions",
            "expired_count": expired_count
        }
    except Exception as e:
        logging.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(status_code=500, detail="Error cleaning up sessions")

@router.get("/status")
async def get_chatbot_status() -> Dict:
    """Get chatbot and LLM status"""
    try:
        status = chatbot_manager.get_llm_status()
        return status
    except Exception as e:
        logging.error(f"Error getting chatbot status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving chatbot status")

@router.post("/session/{session_id}/context")
async def update_session_context(
    session_id: str,
    context_data: Dict = Body(...)
) -> Dict:
    """Update session context with additional data"""
    try:
        success = chatbot_manager.update_session_context(session_id, context_data)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session context updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating session context for {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating session context") 