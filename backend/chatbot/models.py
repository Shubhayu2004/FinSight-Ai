from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class MessageRole(Enum):
    """Message roles in chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class MessageType(Enum):
    """Types of messages"""
    TEXT = "text"
    QUERY = "query"
    ANALYSIS = "analysis"
    ERROR = "error"

@dataclass
class ChatMessage:
    """Individual chat message"""
    id: str
    session_id: str
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ChatSession:
    """Chat session with context"""
    id: str
    user_id: Optional[str] = None
    company_symbol: Optional[str] = None
    company_name: Optional[str] = None
    created_at: datetime = None
    last_activity: datetime = None
    messages: List[ChatMessage] = None
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.messages is None:
            self.messages = []
        if self.context is None:
            self.context = {}

@dataclass
class ChatContext:
    """Context for LLM responses"""
    company_symbol: Optional[str] = None
    company_name: Optional[str] = None
    annual_report_text: Optional[str] = None
    report_sections: Optional[Dict[str, str]] = None
    technical_data: Optional[Dict[str, Any]] = None
    fundamental_data: Optional[Dict[str, Any]] = None
    conversation_history: Optional[List[ChatMessage]] = None
    user_preferences: Optional[Dict[str, Any]] = None

@dataclass
class ChatResponse:
    """Response from chatbot"""
    message: ChatMessage
    context_used: Optional[Dict[str, Any]] = None
    confidence: Optional[float] = None
    processing_time: Optional[float] = None
    sources: Optional[List[str]] = None

@dataclass
class ChatRequest:
    """Request to chatbot"""
    session_id: str
    message: str
    company_symbol: Optional[str] = None
    include_context: bool = True
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None

@dataclass
class PromptTemplate:
    """Template for LLM prompts"""
    name: str
    template: str
    variables: List[str]
    description: str
    category: str  # e.g., "analysis", "qa", "summary"

@dataclass
class AnalysisRequest:
    """Request for financial analysis"""
    company_symbol: str
    analysis_type: str  # "technical", "fundamental", "risk", "summary"
    specific_questions: Optional[List[str]] = None
    include_charts: bool = False
    depth: str = "standard"  # "basic", "standard", "detailed" 