import os
import json
import logging
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

# Import configuration
try:
    from config import get_model_name, FINGPT_MODEL_NAME, LLAMA2_MODEL_NAME, setup_model_cache, get_cache_dir
except ImportError:
    # Fallback if config is not available
    def get_model_name(model_type: str = "fingpt") -> str:
        return "meta-llama/Llama-2-7b-chat-hf"

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass

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

class FinGPTLLMClient(LLMClient):
    """FinGPT model client with PEFT adapter support."""
    
    def __init__(self, model_name: Optional[str] = None, device: str = "auto", use_llama2: bool = False):
        """
        Initialize the FinGPT LLM client.
        
        Args:
            model_name: Base model name (default: from config)
            device: Device to load the model on ("auto", "cuda", "cpu")
            use_llama2: Whether to try loading Llama-2 (requires access approval)
        """
        from config import FINGPT_MODEL_NAME, LLAMA2_MODEL_NAME, setup_model_cache, get_cache_dir
        
        # Setup local model cache
        setup_model_cache()
        
        self.device = device
        self.model = None
        self.tokenizer = None
        self._available = False
        self.use_peft = False
        
        # Get cache directory
        self.cache_dir = get_cache_dir("fingpt" if not use_llama2 else "llama2")
        
        # Determine which model to use
        if use_llama2 and model_name is None:
            self.model_name = LLAMA2_MODEL_NAME
            self.use_peft = True
        else:
            self.model_name = model_name or FINGPT_MODEL_NAME
            self.use_peft = False
        
        try:
            self._load_model()
        except Exception as e:
            logger.error(f"Failed to initialize FinGPT client: {e}")
            self._available = False
    
    def _load_model(self):
        """Load the FinGPT model with PEFT adapter or fallback model."""
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            
            logger.info(f"Loading model: {self.model_name}")
            
            if self.use_peft:
                # Try to load Llama-2 with PEFT adapter
                try:
                    from peft import PeftModel
                    
                    logger.info("Loading FinGPT base model (Llama-2)...")
                    
                    # Load base model with cache
                    load_kwargs = {
                        "trust_remote_code": True,
                        "device_map": self.device,
                        "torch_dtype": torch.float16,
                    }
                    if self.cache_dir:
                        load_kwargs["cache_dir"] = self.cache_dir
                    
                    self.base_model = AutoModelForCausalLM.from_pretrained(
                        self.model_name,
                        **load_kwargs
                    )
                    
                    # Load tokenizer with cache
                    tokenizer_kwargs = {}
                    if self.cache_dir:
                        tokenizer_kwargs["cache_dir"] = self.cache_dir
                    
                    self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, **tokenizer_kwargs)
                    
                    # Load PEFT adapter with cache
                    logger.info("Loading FinGPT PEFT adapter...")
                    adapter_kwargs = {}
                    if self.cache_dir:
                        adapter_kwargs["cache_dir"] = self.cache_dir
                    
                    self.model = PeftModel.from_pretrained(
                        self.base_model, 
                        'FinGPT/fingpt-forecaster_dow30_llama2-7b_lora',
                        **adapter_kwargs
                    )
                    
                    # Set model to evaluation mode
                    self.model = self.model.eval()
                    
                    logger.info("✅ FinGPT model with PEFT adapter loaded successfully!")
                    
                except Exception as e:
                    logger.warning(f"Failed to load Llama-2 with PEFT: {e}")
                    logger.info("Falling back to open-access model...")
                    self._load_fallback_model()
            else:
                # Load fallback model
                self._load_fallback_model()
            
            self._available = True
            
        except ImportError as e:
            logger.error(f"Required libraries not installed: {e}")
            logger.error("Install with: pip install transformers torch peft")
            raise
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_fallback_model(self):
        """Load a fallback open-access model."""
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        logger.info(f"Loading fallback model: {self.model_name}")
        
        # Load tokenizer with cache
        tokenizer_kwargs = {}
        if self.cache_dir:
            tokenizer_kwargs["cache_dir"] = self.cache_dir
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, **tokenizer_kwargs)
        
        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model with cache
        model_kwargs = {
            "torch_dtype": torch.float16 if torch.cuda.is_available() else torch.float32,
            "device_map": self.device,
            "trust_remote_code": True
        }
        if self.cache_dir:
            model_kwargs["cache_dir"] = self.cache_dir
        
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **model_kwargs
        )
        
        logger.info("✅ Fallback model loaded successfully!")
    
    def is_available(self) -> bool:
        return self._available
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response using FinGPT model."""
        if not self.is_available() or self.model is None or self.tokenizer is None:
            raise RuntimeError("FinGPT model not available")
        
        try:
            import torch
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=kwargs.get('max_new_tokens', 512),
                    temperature=kwargs.get('temperature', 0.7),
                    do_sample=True,
                    **kwargs
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the input prompt from response
            response = response[len(prompt):].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response with FinGPT: {e}")
            raise
    
    def create_financial_prompt(self, context: str, query: str, company_name: str) -> str:
        """Create a financial analysis prompt."""
        if self.use_peft:
            # Use specialized prompt for FinGPT with PEFT
            prompt = f"""You are a financial analyst assistant specialized in analyzing annual reports and financial data.

Context about {company_name}:
{context}

Question: {query}

Please provide a detailed financial analysis based on the information provided. Focus on:
- Key financial metrics and trends
- Risk factors and opportunities
- Business performance insights
- Investment considerations

Analysis:"""
        else:
            # Use simpler prompt for fallback model
            prompt = f"""Financial Analysis for {company_name}:

Context: {context}

Question: {query}

Please provide a financial analysis:"""
        
        return prompt
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        import torch
        
        model_type = "FinGPT with PEFT Adapter" if self.use_peft else "Fallback Model"
        description = "FinGPT financial forecasting model with PEFT adapter for Dow30 analysis" if self.use_peft else f"Open-access model: {self.model_name}"
        
        return {
            "model_name": self.model_name,
            "model_type": model_type,
            "device": str(self.model.device) if self.model else "Not loaded",
            "cuda_available": torch.cuda.is_available() if 'torch' in globals() else False,
            "parameters": "7B (Llama-2-7b-chat-hf + FinGPT LoRA)" if self.use_peft else "Varies by model",
            "description": description,
            "uses_peft": self.use_peft
        }

class FinAgentClient:
    """Client for financial analysis using LLM."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.conversation_history = []
    
    def query_annual_report(self, 
                          context: str, 
                          query: str, 
                          company_name: str = "the company",
                          **kwargs) -> Dict[str, Any]:
        """Query the annual report with financial analysis."""
        try:
            # Create prompt
            if isinstance(self.llm_client, FinGPTLLMClient):
                prompt = self.llm_client.create_financial_prompt(context, query, company_name)
            else:
                prompt = f"Financial Analysis for {company_name}:\n\nContext: {context}\n\nQuestion: {query}\n\nAnalysis:"
            
            # Generate response
            response = self.llm_client.generate_response(prompt, **kwargs)
            
            # Create result
            result = {
                "success": True,
                "response": response,
                "query": query,
                "company_name": company_name,
                "timestamp": self._get_timestamp(),
                "model_info": self.llm_client.get_model_info() if isinstance(self.llm_client, FinGPTLLMClient) else {}
            }
            
            # Add to conversation history
            self.conversation_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying annual report: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "company_name": company_name,
                "timestamp": self._get_timestamp()
            }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def save_conversation(self, file_path: str):
        """Save conversation history to file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            logger.info(f"Conversation saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

def create_llm_client(client_type: str = "finagent", **kwargs) -> LLMClient:
    """Create an LLM client based on the specified type."""
    if client_type == "finagent":
        return FinGPTLLMClient(**kwargs)
    elif client_type == "huggingface":
        return HuggingFaceLLMClient(**kwargs)
    elif client_type == "local":
        return LocalLLMClient(**kwargs)
    else:
        raise ValueError(f"Unknown client type: {client_type}")

# Example usage
if __name__ == "__main__":
    # Example with FinGPT (default)
    # client = create_llm_client("fingpt")
    # finagent = FinAgentClient(client)
    
    # Example with OpenAI
    # client = create_llm_client("openai", model="gpt-3.5-turbo")
    # finagent = FinAgentClient(client)
    
    # Example with local model
    # client = create_llm_client("local", base_url="http://localhost:11434", model="llama2")
    # finagent = FinAgentClient(client)
    
    pass 