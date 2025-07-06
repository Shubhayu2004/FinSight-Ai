"""
Annual Report Processor Package

A comprehensive system for extracting information from annual reports and 
interacting with FinGPT 7B for financial analysis.

Components:
- PDFParser: Extract text and sections from PDF files
- TextProcessor: Process and chunk text for LLM consumption
- LLMClient: Interface with various LLM providers (FinGPT, HuggingFace, etc.)
- AnnualReportProcessor: Main orchestrator for the entire pipeline

Usage:
    from annual_report_processor import AnnualReportProcessor
    
    # Initialize processor with FinGPT
    processor = AnnualReportProcessor(llm_client_type="fingpt")
    
    # Process and query an annual report
    result = processor.query_annual_report(
        pdf_path="TCS_Annual_Report_2023.pdf",
        query="How did the company perform in North America?"
    )
"""

from .processor import AnnualReportProcessor
from .pdf_parser import PDFParser
from .text_processor import TextProcessor, TextChunk
from .llm_client import (
    FinAgentClient, 
    create_llm_client,
    LLMClient,
    HuggingFaceLLMClient,
    LocalLLMClient,
    FinGPTLLMClient
)

__version__ = "1.0.0"
__author__ = "AI Finance Agent Team"

__all__ = [
    "AnnualReportProcessor",
    "PDFParser", 
    "TextProcessor",
    "TextChunk",
    "FinAgentClient",
    "create_llm_client",
    "LLMClient",
    "HuggingFaceLLMClient",
    "LocalLLMClient",
    "FinGPTLLMClient"
] 