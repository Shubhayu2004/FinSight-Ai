import os
import json
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

# Import configuration
try:
    from config import get_model_path
except ImportError:
    # Fallback if config is not available
    def get_model_path(model_type: str = "finagent") -> str:
        if model_type == "finagent":
            return "../../llm fine tune/l3_finagent_step60/l3_finagent_step60"
        return ""

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM service is available."""
        pass

class OpenAILLMClient(LLMClient):
    """OpenAI API client for LLM interactions."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = model
            self._available = True
        except ImportError:
            logger.error("OpenAI library not installed. Install with: pip install openai")
            self._available = False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        return self._available
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using OpenAI API."""
        if not self.is_available():
            raise RuntimeError("OpenAI client not available")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a financial analyst assistant specialized in analyzing annual reports."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.3),
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response with OpenAI: {e}")
            raise

class HuggingFaceLLMClient(LLMClient):
    """HuggingFace Transformers client for local LLM models."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            if torch.cuda.is_available():
                self.model = self.model.to('cuda')
            
            self._available = True
            
        except ImportError:
            logger.error("Transformers library not installed. Install with: pip install transformers torch")
            self._available = False
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace client: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        return self._available
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using HuggingFace model."""
        if not self.is_available():
            raise RuntimeError("HuggingFace client not available")
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            if torch.cuda.is_available():
                inputs = inputs.to('cuda')
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=kwargs.get('max_length', 512),
                    temperature=kwargs.get('temperature', 0.7),
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from response
            response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response with HuggingFace: {e}")
            raise

class LocalLLMClient(LLMClient):
    """Client for local LLM models (e.g., LM Studio, Ollama)."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self._available = self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if the local LLM service is available."""
        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Local LLM service not available at {self.base_url}: {e}")
            return False
    
    def is_available(self) -> bool:
        return self._available
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using local LLM service."""
        if not self.is_available():
            raise RuntimeError("Local LLM service not available")
        
        try:
            import requests
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "top_p": kwargs.get('top_p', 0.9),
                    "max_tokens": kwargs.get('max_tokens', 1000)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                raise Exception(f"API request failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error generating response with local LLM: {e}")
            raise

class FinAgentLLMClient(LLMClient):
    """Specialized client for the fine-tuned FinAgent model."""
    
    def __init__(self, model_path: str = None, device: str = "auto"):
        """
        Initialize the FinAgent LLM client.
        
        Args:
            model_path: Path to the fine-tuned model directory
            device: Device to load the model on ("auto", "cuda", "cpu")
        """
        self.model_path = model_path or get_model_path("finagent")
        self.device = device
        self.model = None
        self.tokenizer = None
        self._available = False
        
        try:
            self._load_model()
        except Exception as e:
            logger.error(f"Failed to load FinAgent model: {e}")
            self._available = False
    
    def _load_model(self):
        """Load the fine-tuned FinAgent model."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from peft import PeftModel
            import torch
            import os
            
            logger.info(f"Loading FinAgent model from {self.model_path}")
            
            # Check if model path exists
            if not os.path.exists(self.model_path):
                logger.error(f"Model path does not exist: {self.model_path}")
                self._available = False
                return
            
            # Load base model and tokenizer
            base_model_name = "unsloth/llama-3-8b-instruct-bnb-4bit"
            
            # Load tokenizer from base model first, then from local path
            try:
                # Try to load tokenizer from local path
                self.tokenizer = AutoTokenizer.from_pretrained(
                    self.model_path,
                    trust_remote_code=True,
                    local_files_only=True
                )
            except Exception as e:
                logger.warning(f"Could not load tokenizer from local path: {e}")
                # Fallback to base model tokenizer
                self.tokenizer = AutoTokenizer.from_pretrained(
                    base_model_name,
                    trust_remote_code=True
                )
            
            # Load base model
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_name,
                torch_dtype=torch.float16,
                device_map="auto" if self.device == "auto" else self.device,
                trust_remote_code=True
            )
            
            # Load LoRA adapters
            self.model = PeftModel.from_pretrained(
                base_model,
                self.model_path,
                torch_dtype=torch.float16
            )
            
            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            self._available = True
            logger.info("FinAgent model loaded successfully")
            
        except ImportError as e:
            logger.error(f"Required libraries not installed: {e}")
            logger.error("Install with: pip install transformers peft torch accelerate")
            self._available = False
        except Exception as e:
            logger.error(f"Error loading FinAgent model: {e}")
            self._available = False
    
    def is_available(self) -> bool:
        """Check if the FinAgent model is available."""
        return self._available
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using the FinAgent model."""
        if not self.is_available():
            raise RuntimeError("FinAgent model not available")
        
        try:
            import torch
            
            # Prepare input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=kwargs.get('max_length', 4096)
            )
            
            # Move to device
            if torch.cuda.is_available():
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get('max_new_tokens', 512),
                    temperature=kwargs.get('temperature', 0.7),
                    top_p=kwargs.get('top_p', 0.9),
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                    **kwargs
                )
            
            # Decode response
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"Error generating response with FinAgent: {e}")
            raise
    
    def create_financial_prompt(self, context: str, query: str, company_name: str) -> str:
        """Create a prompt specifically formatted for the FinAgent model."""
        
        # Use the chat template format
        prompt = f"""<|start_header_id|>system<|end_header_id|>

You are FinAgent, a specialized financial analyst AI trained to analyze annual reports and provide insights. You have expertise in financial analysis, risk assessment, and business strategy.

<|eot_id|><|start_header_id|>user<|end_header_id|>

COMPANY: {company_name}

ANNUAL REPORT CONTEXT:
{context}

USER QUERY: {query}

Please provide a comprehensive financial analysis based on the annual report information. Include specific data points, trends, and insights where available.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        return prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        if not self.is_available():
            return {"status": "not_loaded"}
        
        return {
            "model_path": self.model_path,
            "base_model": "unsloth/llama-3-8b-instruct-bnb-4bit",
            "adapter_type": "LoRA",
            "device": str(next(self.model.parameters()).device),
            "parameters": sum(p.numel() for p in self.model.parameters()),
            "trainable_parameters": sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        }

class FinAgentClient:
    """Main client for interacting with the FinAgent LLM."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.conversation_history = []
    
    def query_annual_report(self, 
                          context: str, 
                          query: str, 
                          company_name: str = "the company",
                          **kwargs) -> Dict[str, Any]:
        """Query the FinAgent about an annual report."""
        
        # Create structured prompt
        if isinstance(self.llm_client, FinAgentLLMClient):
            # Use specialized prompt for FinAgent model
            prompt = self.llm_client.create_financial_prompt(context, query, company_name)
        else:
            # Use generic prompt for other models
            prompt = self._create_financial_prompt(context, query, company_name)
        
        try:
            # Generate response
            response = self.llm_client.generate_response(prompt, **kwargs)
            
            # Store in conversation history
            conversation_entry = {
                'query': query,
                'context_length': len(context),
                'response': response,
                'timestamp': self._get_timestamp()
            }
            self.conversation_history.append(conversation_entry)
            
            # Format response
            result = {
                'query': query,
                'response': response,
                'context_used': len(context),
                'company': company_name,
                'success': True
            }
            
            logger.info(f"Successfully generated response for query: {query[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error querying FinAgent: {e}")
            return {
                'query': query,
                'response': f"Error generating response: {str(e)}",
                'context_used': len(context),
                'company': company_name,
                'success': False,
                'error': str(e)
            }
    
    def _create_financial_prompt(self, context: str, query: str, company_name: str) -> str:
        """Create a specialized financial analysis prompt."""
        
        prompt = f"""You are FinAgent, a specialized financial analyst AI trained to analyze annual reports and provide insights.

COMPANY: {company_name}
ANNUAL REPORT CONTEXT:
{context}

USER QUERY: {query}

INSTRUCTIONS:
1. Analyze the provided annual report context carefully
2. Provide specific, data-driven insights based on the information available
3. If the context doesn't contain relevant information, clearly state this
4. Include relevant financial metrics and trends when available
5. Provide actionable insights and implications
6. Use professional financial analysis language
7. Cite specific sections or data points from the context when possible

Please provide a comprehensive analysis:"""
        
        return prompt
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def save_conversation(self, file_path: str):
        """Save conversation history to file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
            logger.info(f"Conversation history saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving conversation history: {e}")
            raise

def create_llm_client(client_type: str = "finagent", **kwargs) -> LLMClient:
    """Factory function to create LLM client based on type."""
    
    if client_type.lower() == "openai":
        return OpenAILLMClient(**kwargs)
    elif client_type.lower() == "huggingface":
        return HuggingFaceLLMClient(**kwargs)
    elif client_type.lower() == "local":
        return LocalLLMClient(**kwargs)
    elif client_type.lower() == "finagent":
        return FinAgentLLMClient(**kwargs)
    else:
        raise ValueError(f"Unknown LLM client type: {client_type}")

# Example usage
if __name__ == "__main__":
    # Example with FinAgent (default)
    # client = create_llm_client("finagent")
    # finagent = FinAgentClient(client)
    
    # Example with OpenAI
    # client = create_llm_client("openai", model="gpt-3.5-turbo")
    # finagent = FinAgentClient(client)
    
    # Example with local model
    # client = create_llm_client("local", base_url="http://localhost:11434", model="llama2")
    # finagent = FinAgentClient(client)
    
    pass 