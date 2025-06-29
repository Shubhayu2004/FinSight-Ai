import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, Dict, Any, List
import logging
import time
import os
from datetime import datetime

from .models import ChatContext, ChatResponse, ChatMessage, MessageRole, MessageType

class LLMClient:
    """Client for fine-tuned LLM model"""
    
    def __init__(self, model_path: str = "../llm fine tune/l3_finagent_step60/l3_finagent_step60/"):
        self.model_path = model_path
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.max_length = 2048
        self.load_model()
    
    def load_model(self):
        """Load the fine-tuned model"""
        try:
            logging.info(f"Loading model from {self.model_path}")
            
            # Check if model path exists
            if not os.path.exists(self.model_path):
                logging.error(f"Model path not found: {self.model_path}")
                return
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True
            )
            
            if self.device == "cpu":
                self.model = self.model.to(self.device)
            
            self.model.eval()
            logging.info(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            self.model = None
            self.tokenizer = None
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None
    
    def generate_response(
        self, 
        prompt: str, 
        max_tokens: int = 512, 
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True
    ) -> Optional[str]:
        """Generate response from the model"""
        if not self.is_loaded():
            logging.error("Model not loaded")
            return None
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt, 
                return_tensors="pt", 
                truncation=True, 
                max_length=self.max_length
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=do_sample,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return None
    
    def create_financial_prompt(
        self, 
        question: str, 
        context: Optional[ChatContext] = None,
        prompt_type: str = "qa"
    ) -> str:
        """Create a financial analysis prompt"""
        
        if prompt_type == "qa":
            return self._create_qa_prompt(question, context)
        elif prompt_type == "analysis":
            return self._create_analysis_prompt(question, context)
        elif prompt_type == "summary":
            return self._create_summary_prompt(question, context)
        else:
            return self._create_general_prompt(question, context)
    
    def _create_qa_prompt(self, question: str, context: Optional[ChatContext] = None) -> str:
        """Create Q&A prompt"""
        prompt = "You are a financial analyst assistant. Answer the following question based on the provided context.\n\n"
        
        if context and context.company_name:
            prompt += f"Company: {context.company_name} ({context.company_symbol})\n\n"
        
        if context and context.annual_report_text:
            # Truncate report text to avoid token limit
            report_text = context.annual_report_text[:2000] + "..." if len(context.annual_report_text) > 2000 else context.annual_report_text
            prompt += f"Annual Report Context:\n{report_text}\n\n"
        
        if context and context.technical_data:
            prompt += f"Technical Data: {str(context.technical_data)[:500]}...\n\n"
        
        prompt += f"Question: {question}\n\nAnswer:"
        
        return prompt
    
    def _create_analysis_prompt(self, question: str, context: Optional[ChatContext] = None) -> str:
        """Create analysis prompt"""
        prompt = "You are a senior financial analyst. Provide a detailed analysis based on the following information.\n\n"
        
        if context and context.company_name:
            prompt += f"Company: {context.company_name} ({context.company_symbol})\n\n"
        
        if context and context.fundamental_data:
            prompt += f"Fundamental Data: {str(context.fundamental_data)[:1000]}...\n\n"
        
        if context and context.annual_report_text:
            report_text = context.annual_report_text[:1500] + "..." if len(context.annual_report_text) > 1500 else context.annual_report_text
            prompt += f"Annual Report Excerpts:\n{report_text}\n\n"
        
        prompt += f"Analysis Request: {question}\n\nAnalysis:"
        
        return prompt
    
    def _create_summary_prompt(self, question: str, context: Optional[ChatContext] = None) -> str:
        """Create summary prompt"""
        prompt = "You are a financial analyst. Provide a concise summary of the key points.\n\n"
        
        if context and context.company_name:
            prompt += f"Company: {context.company_name} ({context.company_symbol})\n\n"
        
        if context and context.annual_report_text:
            report_text = context.annual_report_text[:2500] + "..." if len(context.annual_report_text) > 2500 else context.annual_report_text
            prompt += f"Annual Report:\n{report_text}\n\n"
        
        prompt += f"Summary Request: {question}\n\nSummary:"
        
        return prompt
    
    def _create_general_prompt(self, question: str, context: Optional[ChatContext] = None) -> str:
        """Create general financial prompt"""
        prompt = "You are a financial analyst assistant. Help with the following financial question.\n\n"
        
        if context and context.company_name:
            prompt += f"Company: {context.company_name} ({context.company_symbol})\n\n"
        
        prompt += f"Question: {question}\n\nAnswer:"
        
        return prompt
    
    def process_chat_request(
        self, 
        question: str, 
        context: Optional[ChatContext] = None,
        session_id: str = "default"
    ) -> Optional[ChatResponse]:
        """Process a chat request and return response"""
        start_time = time.time()
        
        try:
            # Determine prompt type based on question
            prompt_type = self._determine_prompt_type(question)
            
            # Create prompt
            prompt = self.create_financial_prompt(question, context, prompt_type)
            
            # Generate response
            response_text = self.generate_response(
                prompt, 
                max_tokens=512, 
                temperature=0.7
            )
            
            if not response_text:
                return None
            
            # Create chat message
            message = ChatMessage(
                id=f"msg_{int(time.time())}",
                session_id=session_id,
                role=MessageRole.ASSISTANT,
                content=response_text,
                message_type=MessageType.TEXT,
                metadata={"prompt_type": prompt_type}
            )
            
            # Create response
            processing_time = time.time() - start_time
            
            chat_response = ChatResponse(
                message=message,
                context_used={
                    "company_symbol": context.company_symbol if context else None,
                    "prompt_type": prompt_type,
                    "context_length": len(context.annual_report_text) if context and context.annual_report_text else 0
                },
                confidence=0.8,  # Placeholder
                processing_time=processing_time,
                sources=["annual_report", "financial_data"] if context else []
            )
            
            return chat_response
            
        except Exception as e:
            logging.error(f"Error processing chat request: {e}")
            return None
    
    def _determine_prompt_type(self, question: str) -> str:
        """Determine the type of prompt based on the question"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["analyze", "analysis", "evaluate", "assessment"]):
            return "analysis"
        elif any(word in question_lower for word in ["summarize", "summary", "overview", "key points"]):
            return "summary"
        elif any(word in question_lower for word in ["what", "how", "why", "when", "where", "explain", "describe"]):
            return "qa"
        else:
            return "general"
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "model_path": self.model_path,
            "is_loaded": self.is_loaded(),
            "device": self.device,
            "max_length": self.max_length,
            "model_type": "fine_tuned_llama3" if self.is_loaded() else "not_loaded"
        }

# Global instance
llm_client = LLMClient() 