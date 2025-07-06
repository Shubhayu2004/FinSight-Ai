import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .pdf_parser import PDFParser
from .text_processor import TextProcessor
from .llm_client import FinAgentClient, create_llm_client

logger = logging.getLogger(__name__)

class AnnualReportProcessor:
    """Main processor for handling annual report analysis with FinAgent."""
    
    def __init__(self, 
                 llm_client_type: str = "fingpt",
                 llm_client_kwargs: Optional[Dict[str, Any]] = None,
                 max_context_tokens: int = 4000,
                 cache_dir: str = "cache"):

        self.max_context_tokens = max_context_tokens
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.pdf_parser = PDFParser()
        self.text_processor = TextProcessor()
        
        # Initialize LLM client
        llm_client_kwargs = llm_client_kwargs or {}
        self.llm_client = create_llm_client(llm_client_type, **llm_client_kwargs)
        self.finagent = FinAgentClient(self.llm_client)
        
        logger.info(f"Initialized AnnualReportProcessor with {llm_client_type} LLM client")
    
    def process_annual_report(self, pdf_path: str, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Process an annual report PDF and extract structured data.
        
        Args:
            pdf_path: Path to the PDF file
            force_reprocess: Force reprocessing even if cached data exists
            
        Returns:
            Dictionary containing processed data
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Check cache
        cache_file = self.cache_dir / f"{pdf_path.stem}_processed.json"
        
        if not force_reprocess and cache_file.exists():
            logger.info(f"Loading cached data for {pdf_path.name}")
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cached data: {e}")
        
        # Process the PDF
        logger.info(f"Processing annual report: {pdf_path.name}")
        
        # Step 1: Parse PDF
        parsed_data = self.pdf_parser.parse_annual_report(str(pdf_path))
        
        # Step 2: Process text and create chunks
        section_chunks = self.text_processor.extract_key_sections(parsed_data)
        
        # Step 3: Compile results
        processed_data = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'parsed_data': parsed_data,
            'section_chunks': section_chunks,
            'total_chunks': sum(len(chunks) for chunks in section_chunks.values()),
            'processing_timestamp': self._get_timestamp()
        }
        
        # Cache the results
        try:
            self.text_processor.save_processed_data(processed_data, str(cache_file))
            logger.info(f"Processed data cached to {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to cache processed data: {e}")
        
        return processed_data
    
    def query_annual_report(self, 
                          pdf_path: str, 
                          query: str, 
                          company_name: Optional[str] = None,
                          force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Query the FinAgent about an annual report.
        
        Args:
            pdf_path: Path to the PDF file
            query: User query about the annual report
            company_name: Name of the company (extracted from filename if not provided)
            force_reprocess: Force reprocessing of the PDF
            
        Returns:
            Dictionary containing the query response
        """
        # Process the annual report
        processed_data = self.process_annual_report(pdf_path, force_reprocess)
        
        # Extract company name if not provided
        if not company_name:
            company_name = self._extract_company_name(processed_data['file_name'])
        
        # Create context for LLM
        context = self.text_processor.create_context_for_llm(
            processed_data['parsed_data'], 
            query, 
            self.max_context_tokens
        )
        
        # Query FinAgent
        result = self.finagent.query_annual_report(context, query, company_name)
        
        # Add metadata
        result.update({
            'pdf_file': processed_data['file_name'],
            'company_name': company_name,
            'context_tokens': len(context) // 4,  # Rough estimation
            'total_chunks_available': processed_data['total_chunks']
        })
        
        return result
    
    def batch_process_reports(self, pdf_directory: str) -> List[Dict[str, Any]]:
        """
        Process all PDF files in a directory.
        
        Args:
            pdf_directory: Directory containing PDF files
            
        Returns:
            List of processing results
        """
        pdf_dir = Path(pdf_directory)
        if not pdf_dir.exists():
            raise FileNotFoundError(f"Directory not found: {pdf_directory}")
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_directory}")
            return []
        
        results = []
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing {pdf_file.name}")
                result = self.process_annual_report(str(pdf_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
                results.append({
                    'file_path': str(pdf_file),
                    'file_name': pdf_file.name,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def get_available_sections(self, pdf_path: str) -> Dict[str, List[str]]:
        """
        Get available sections in a processed annual report.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary mapping section types to available section names
        """
        processed_data = self.process_annual_report(pdf_path)
        sections = processed_data['parsed_data']['sections']
        
        available_sections = {}
        for section_type, section_list in sections.items():
            if section_list:
                available_sections[section_type] = [
                    f"Section {i+1}" for i in range(len(section_list))
                ]
        
        return available_sections
    
    def get_financial_summary(self, pdf_path: str) -> Dict[str, str]:
        """
        Get financial summary from an annual report.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary containing financial metrics
        """
        processed_data = self.process_annual_report(pdf_path)
        return processed_data['parsed_data']['financial_data']
    
    def save_conversation_history(self, file_path: str):
        """Save the conversation history to a file."""
        self.finagent.save_conversation(file_path)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.finagent.get_conversation_history()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.finagent.clear_history()
    
    def _extract_company_name(self, filename: str) -> str:
        """Extract company name from filename."""
        # Remove common suffixes
        name = filename.replace('.pdf', '').replace('_Annual_Report', '').replace('_', ' ')
        
        # Extract year if present
        import re
        year_match = re.search(r'\d{4}', name)
        if year_match:
            name = name.replace(year_match.group(), '').strip()
        
        return name.strip()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        cache_files = list(self.cache_dir.glob("*_processed.json"))
        
        stats = {
            'total_processed_files': len(cache_files),
            'cache_directory': str(self.cache_dir),
            'llm_client_type': type(self.llm_client).__name__,
            'llm_available': self.llm_client.is_available(),
            'conversation_history_length': len(self.finagent.get_conversation_history())
        }
        
        return stats

# Example usage and testing
def main():
    """Example usage of the AnnualReportProcessor."""
    
    # Initialize processor
    processor = AnnualReportProcessor(
        llm_client_type="fingpt",  # or "local", "huggingface"
        max_context_tokens=4000
    )
    
    # Example: Process a single report
    # pdf_path = "path/to/TCS_Annual_Report_2023.pdf"
    # result = processor.process_annual_report(pdf_path)
    # print(f"Processed {result['file_name']}")
    
    # Example: Query the report
    # query = "How did the company perform in the North American market?"
    # response = processor.query_annual_report(pdf_path, query)
    # print(f"Response: {response['response']}")
    
    # Example: Batch process
    # pdf_directory = "path/to/annual_reports/"
    # results = processor.batch_process_reports(pdf_directory)
    # print(f"Processed {len(results)} reports")

if __name__ == "__main__":
    main() 