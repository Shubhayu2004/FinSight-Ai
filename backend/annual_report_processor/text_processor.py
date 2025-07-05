import re
import json
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    chunk_id: str
    section_type: str
    start_pos: int
    end_pos: int
    token_count: int
    metadata: Dict[str, any]

class TextProcessor:
    """Process and prepare text for LLM consumption."""
    
    def __init__(self, max_chunk_tokens: int = 1000, overlap_tokens: int = 100):
        self.max_chunk_tokens = max_chunk_tokens
        self.overlap_tokens = overlap_tokens
        
        # Rough token estimation (1 token ≈ 4 characters for English)
        self.chars_per_token = 4
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for a text string."""
        return len(text) // self.chars_per_token
    
    def chunk_text(self, text: str, section_type: str = "general") -> List[TextChunk]:
        """Split text into manageable chunks for LLM processing."""
        chunks = []
        
        # Split by sentences first
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        current_start = 0
        chunk_id = 0
        
        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would exceed token limit
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence
            estimated_tokens = self.estimate_tokens(test_chunk)
            
            if estimated_tokens > self.max_chunk_tokens and current_chunk:
                # Save current chunk
                chunk = TextChunk(
                    text=current_chunk.strip(),
                    chunk_id=f"{section_type}_{chunk_id}",
                    section_type=section_type,
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk),
                    token_count=self.estimate_tokens(current_chunk),
                    metadata={'sentence_count': len(current_chunk.split('.'))}
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = overlap_text + " " + sentence
                current_start = current_start + len(current_chunk) - len(overlap_text)
                chunk_id += 1
            else:
                current_chunk = test_chunk
        
        # Add final chunk
        if current_chunk.strip():
            chunk = TextChunk(
                text=current_chunk.strip(),
                chunk_id=f"{section_type}_{chunk_id}",
                section_type=section_type,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk),
                token_count=self.estimate_tokens(current_chunk),
                metadata={'sentence_count': len(current_chunk.split('.'))}
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex."""
        # Split by sentence endings, but preserve abbreviations
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _get_overlap_text(self, text: str) -> str:
        """Get the last portion of text for overlap."""
        words = text.split()
        overlap_words = words[-self.overlap_tokens//4:]  # Rough estimation
        return " ".join(overlap_words)
    
    def extract_key_sections(self, parsed_data: Dict[str, any]) -> Dict[str, List[TextChunk]]:
        """Extract and chunk key sections from parsed PDF data."""
        section_chunks = {}
        
        for section_type, sections in parsed_data['sections'].items():
            if not sections:
                continue
                
            section_chunks[section_type] = []
            
            for i, (start_line, end_line, section_text) in enumerate(sections):
                # Chunk this section
                chunks = self.chunk_text(section_text, f"{section_type}_{i}")
                section_chunks[section_type].extend(chunks)
        
        return section_chunks
    
    def create_context_for_llm(self, 
                             parsed_data: Dict[str, any], 
                             query: str,
                             max_context_tokens: int = 4000) -> str:
        """Create optimized context for LLM based on user query."""
        
        # Extract key sections
        section_chunks = self.extract_key_sections(parsed_data)
        
        # Determine relevant sections based on query
        relevant_sections = self._identify_relevant_sections(query, section_chunks)
        
        # Build context within token limits
        context_parts = []
        current_tokens = 0
        
        # Add financial data first (always relevant)
        if parsed_data.get('financial_data'):
            financial_summary = self._format_financial_data(parsed_data['financial_data'])
            context_parts.append(f"FINANCIAL SUMMARY:\n{financial_summary}")
            current_tokens += self.estimate_tokens(financial_summary)
        
        # Add relevant sections
        for section_type, chunks in relevant_sections.items():
            for chunk in chunks:
                if current_tokens + chunk.token_count > max_context_tokens:
                    break
                    
                context_parts.append(f"\n{section_type.upper()}:\n{chunk.text}")
                current_tokens += chunk.token_count
        
        return "\n".join(context_parts)
    
    def _identify_relevant_sections(self, query: str, section_chunks: Dict[str, List[TextChunk]]) -> Dict[str, List[TextChunk]]:
        """Identify which sections are most relevant to the query."""
        query_lower = query.lower()
        relevant_sections = {}
        
        # Define query keywords for each section
        section_keywords = {
            'financial_statements': ['revenue', 'profit', 'financial', 'earnings', 'performance', 'growth'],
            'management_discussion': ['management', 'strategy', 'outlook', 'future', 'plans', 'commentary'],
            'risk_factors': ['risk', 'challenge', 'uncertainty', 'threat', 'concern'],
            'esg': ['environmental', 'social', 'governance', 'sustainability', 'csr', 'esg'],
            'business_overview': ['business', 'operations', 'market', 'industry', 'overview'],
            'corporate_governance': ['governance', 'board', 'directors', 'compliance']
        }
        
        # Score sections based on keyword matches
        section_scores = {}
        for section_type, keywords in section_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                section_scores[section_type] = score
        
        # Sort sections by relevance score
        sorted_sections = sorted(section_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Include top relevant sections
        for section_type, score in sorted_sections[:3]:  # Top 3 most relevant
            if section_type in section_chunks:
                relevant_sections[section_type] = section_chunks[section_type]
        
        # Always include management_discussion if available (usually most relevant)
        if 'management_discussion' in section_chunks and 'management_discussion' not in relevant_sections:
            relevant_sections['management_discussion'] = section_chunks['management_discussion']
        
        return relevant_sections
    
    def _format_financial_data(self, financial_data: Dict[str, str]) -> str:
        """Format financial data into readable text."""
        if not financial_data:
            return "No financial data extracted."
        
        lines = []
        if 'revenue' in financial_data:
            lines.append(f"Revenue: ₹{financial_data['revenue']}")
        if 'net_profit' in financial_data:
            lines.append(f"Net Profit: ₹{financial_data['net_profit']}")
        if 'eps' in financial_data:
            lines.append(f"EPS: ₹{financial_data['eps']}")
        
        return "\n".join(lines)
    
    def create_structured_prompt(self, 
                               context: str, 
                               query: str,
                               company_name: str = "the company") -> str:
        """Create a structured prompt for the LLM."""
        
        prompt = f"""You are a financial analyst assistant. You have access to the annual report of {company_name}.

CONTEXT FROM ANNUAL REPORT:
{context}

USER QUERY: {query}

Please provide a comprehensive answer based on the information available in the annual report. If specific information is not available in the provided context, please state that clearly. Include relevant financial data and insights where applicable.

ANSWER:"""
        
        return prompt
    
    def save_processed_data(self, processed_data: Dict[str, any], output_path: str):
        """Save processed data to JSON file."""
        try:
            # Convert TextChunk objects to dictionaries for JSON serialization
            serializable_data = {}
            for key, value in processed_data.items():
                if key == 'section_chunks':
                    serializable_data[key] = {}
                    for section_type, chunks in value.items():
                        serializable_data[key][section_type] = [
                            {
                                'text': chunk.text,
                                'chunk_id': chunk.chunk_id,
                                'section_type': chunk.section_type,
                                'start_pos': chunk.start_pos,
                                'end_pos': chunk.end_pos,
                                'token_count': chunk.token_count,
                                'metadata': chunk.metadata
                            }
                            for chunk in chunks
                        ]
                else:
                    serializable_data[key] = value
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(serializable_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Processed data saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving processed data: {e}")
            raise

# Example usage
if __name__ == "__main__":
    processor = TextProcessor()
    # chunks = processor.chunk_text("Your long text here...")
    # print(f"Created {len(chunks)} chunks") 