import os
import torch
from typing import Optional
from unsloth import FastLanguageModel

class LLMClient:
    def __init__(self, model_path: str = "../llm fine tune/l3_finagent_step60/l3_finagent_step60"):
        self.model = None
        self.tokenizer = None
        self.model_path = model_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.load_model()
    
    def load_model(self):
        """Load the fine-tuned model and tokenizer"""
        try:
            print(f"Loading model from {self.model_path}")
            
            # Load model and tokenizer
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name=self.model_path,
                max_seq_length=2048,
                dtype=None,
                load_in_4bit=True,
            )
            
            # Set model to inference mode
            FastLanguageModel.for_inference(self.model)
            
            print("Model loaded successfully!")
            
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Using fallback mode - will return placeholder responses")
            self.model = None
            self.tokenizer = None
    
    def format_prompt(self, question: str, context: str) -> str:
        """Format the prompt for the fine-tuned model"""
        ft_prompt = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>
Below is a user question, paired with retrieved context. Write a response that appropriately answers the question,
include specific details in your response. <|eot_id|>

<|start_header_id|>user<|end_header_id|>

### Question:
{}

### Context:
{}

<|eot_id|>

### Response: <|start_header_id|>assistant<|end_header_id|>
{}"""
        
        return ft_prompt.format(question, context, "")
    
    def extract_response(self, text: str) -> str:
        """Extract just the assistant response from the full generated text"""
        start_token = "### Response: <|start_header_id|>assistant<|end_header_id|>"
        end_token = "<|eot_id|>"
        
        start_index = text.find(start_token)
        if start_index == -1:
            return text.strip()
        
        start_index += len(start_token)
        end_index = text.find(end_token, start_index)
        
        if end_index == -1:
            return text[start_index:].strip()
        
        return text[start_index:end_index].strip()
    
    def generate_answer(self, context: str, question: str) -> str:
        """Generate answer using the fine-tuned model"""
        if self.model is None or self.tokenizer is None:
            return f"Model not loaded. Would answer: '{question}' given the provided context."
        
        try:
            # Format the prompt
            prompt = self.format_prompt(question, context)
            
            # Tokenize input
            inputs = self.tokenizer([prompt], return_tensors="pt").to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    use_cache=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    temperature=0.7,
                    do_sample=True
                )
            
            # Decode response
            response = self.tokenizer.batch_decode(outputs)[0]
            
            # Extract just the assistant response
            answer = self.extract_response(response)
            
            return answer if answer else "No response generated."
            
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Error generating response: {str(e)}"

# Global instance
llm_client = LLMClient() 