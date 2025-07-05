import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

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

class FinAgentLLMClient:
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
            
            logger.info(f"Loading FinAgent model from {self.model_path}")
            
            # Load base model and tokenizer
            base_model_name = "unsloth/llama-3-8b-instruct-bnb-4bit"
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
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

# Factory function for easy integration
def create_finagent_client(model_path: str = None, device: str = "auto") -> FinAgentLLMClient:
    """Create a FinAgent LLM client."""
    return FinAgentLLMClient(model_path, device)

# Example usage
if __name__ == "__main__":
    # Test the FinAgent client
    client = create_finagent_client()
    
    if client.is_available():
        print("FinAgent model loaded successfully!")
        print(f"Model info: {client.get_model_info()}")
        
        # Test response
        test_prompt = client.create_financial_prompt(
            context="Revenue: ₹50,000 crores, Net Profit: ₹8,000 crores",
            query="What is the company's profit margin?",
            company_name="Test Company"
        )
        
        response = client.generate_response(test_prompt)
        print(f"Test response: {response}")
    else:
        print("Failed to load FinAgent model") 