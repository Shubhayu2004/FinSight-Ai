#!/usr/bin/env python3
"""
Example usage of the Annual Report Processor with FinAgent

This script demonstrates how to use the annual report processor to:
1. Process PDF files from the Reports folder
2. Extract financial data and sections
3. Query the FinAgent about the reports
4. Handle the fine-tuned FinAgent model

Usage:
    python example_usage.py
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path to import the processor
sys.path.append(str(Path(__file__).parent.parent))

from annual_report_processor import AnnualReportProcessor, create_llm_client

def example_finagent_usage():
    """Example using the fine-tuned FinAgent model."""
    print("=== FinAgent Model Example ===")
    
    # Initialize processor with FinAgent
    processor = AnnualReportProcessor(
        llm_client_type="finagent",
        max_context_tokens=4000
    )
    
    # Check if FinAgent is available
    if not processor.llm_client.is_available():
        print("FinAgent model not available. Please check the model path and dependencies.")
        return
    
    # Get model info
    if hasattr(processor.llm_client, 'get_model_info'):
        model_info = processor.llm_client.get_model_info()
        print(f"✓ FinAgent model loaded successfully!")
        print(f"  - Base model: {model_info['base_model']}")
        print(f"  - Adapter type: {model_info['adapter_type']}")
        print(f"  - Device: {model_info['device']}")
    
    # Test with a simple query
    print("\n--- Testing FinAgent with sample data ---")
    test_context = "Revenue: ₹50,000 crores, Net Profit: ₹8,000 crores, EPS: ₹25.50"
    test_query = "What is the company's profit margin?"
    
    response = processor.finagent.query_annual_report(
        context=test_context,
        query=test_query,
        company_name="Test Company"
    )
    
    print(f"Query: {test_query}")
    print(f"Response: {response['response']}")
    print(f"Success: {response['success']}")

def example_tcs_report():
    """Example processing TCS annual report."""
    print("\n=== TCS Annual Report Example ===")
    
    processor = AnnualReportProcessor(llm_client_type="finagent")
    
    # TCS report path
    pdf_path = "../../Reports/AR_26456_TCS_2024_2025_A_27052025233502.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"TCS PDF file not found: {pdf_path}")
        print("Please ensure the TCS annual report is in the Reports folder.")
        return
    
    # Process the report
    print(f"Processing TCS annual report...")
    result = processor.process_annual_report(pdf_path)
    print(f"✓ Processed {result['file_name']}")
    print(f"  - Total chunks: {result['total_chunks']}")
    print(f"  - Financial data: {result['parsed_data']['financial_data']}")
    
    # Query about TCS performance
    tcs_queries = [
        "What was TCS's revenue and profit performance?",
        "How did TCS perform in the North American market?",
        "What are the key strategic initiatives mentioned?",
        "What are the main risk factors for TCS?"
    ]
    
    for query in tcs_queries:
        print(f"\nQuery: {query}")
        response = processor.query_annual_report(pdf_path, query, "TCS")
        print(f"Response: {response['response'][:200]}...")
        print(f"Success: {response['success']}")

def example_reliance_report():
    """Example processing Reliance annual report."""
    print("\n=== Reliance Annual Report Example ===")
    
    processor = AnnualReportProcessor(llm_client_type="finagent")
    
    # Reliance report path
    pdf_path = "../../Reports/AR_24850_RELIANCE_2023_2024_07082024143222.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Reliance PDF file not found: {pdf_path}")
        print("Please ensure the Reliance annual report is in the Reports folder.")
        return
    
    # Process the report
    print(f"Processing Reliance annual report...")
    result = processor.process_annual_report(pdf_path)
    print(f"✓ Processed {result['file_name']}")
    print(f"  - Total chunks: {result['total_chunks']}")
    print(f"  - Financial data: {result['parsed_data']['financial_data']}")
    
    # Query about Reliance performance
    reliance_queries = [
        "What was Reliance's revenue and profit performance?",
        "How did Reliance perform in the oil and gas segment?",
        "What are the key business segments and their performance?",
        "What are the main growth drivers for Reliance?"
    ]
    
    for query in reliance_queries:
        print(f"\nQuery: {query}")
        response = processor.query_annual_report(pdf_path, query, "Reliance Industries")
        print(f"Response: {response['response'][:200]}...")
        print(f"Success: {response['success']}")

def example_batch_processing():
    """Example of batch processing all reports in the Reports folder."""
    print("\n=== Batch Processing Example ===")
    
    processor = AnnualReportProcessor(llm_client_type="finagent")
    
    # Directory containing reports
    reports_directory = "../../Reports"
    
    if not os.path.exists(reports_directory):
        print(f"Reports directory not found: {reports_directory}")
        return
    
    # Process all PDFs in the directory
    print(f"Processing all PDFs in {reports_directory}...")
    results = processor.batch_process_reports(reports_directory)
    
    print(f"✓ Processed {len(results)} reports")
    for result in results:
        if result.get('success', True):
            print(f"  - {result['file_name']}: {result['total_chunks']} chunks")
            if result['parsed_data']['financial_data']:
                print(f"    Financial data: {result['parsed_data']['financial_data']}")
        else:
            print(f"  - {result['file_name']}: ERROR - {result.get('error', 'Unknown error')}")

def example_financial_analysis():
    """Example of extracting and analyzing financial data."""
    print("\n=== Financial Analysis Example ===")
    
    processor = AnnualReportProcessor(llm_client_type="finagent")
    
    # Process TCS report for financial analysis
    pdf_path = "../../Reports/AR_26456_TCS_2024_2025_A_27052025233502.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    # Get financial summary
    financial_data = processor.get_financial_summary(pdf_path)
    print("Financial Summary:")
    for metric, value in financial_data.items():
        print(f"  - {metric}: {value}")
    
    # Get available sections
    sections = processor.get_available_sections(pdf_path)
    print("\nAvailable Sections:")
    for section_type, section_list in sections.items():
        print(f"  - {section_type}: {len(section_list)} sections")
    
    # Query about financial performance
    financial_queries = [
        "What was the company's revenue and profit margin?",
        "How did the company's financial performance compare to industry peers?",
        "What were the main drivers of revenue growth?",
        "What is the company's debt position and financial health?"
    ]
    
    for query in financial_queries:
        print(f"\nQuery: {query}")
        response = processor.query_annual_report(pdf_path, query, "TCS")
        print(f"Response: {response['response'][:150]}...")

def example_conversation_history():
    """Example of managing conversation history."""
    print("\n=== Conversation History Example ===")
    
    processor = AnnualReportProcessor(llm_client_type="finagent")
    
    pdf_path = "../../Reports/AR_26456_TCS_2024_2025_A_27052025233502.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"PDF file not found: {pdf_path}")
        return
    
    # Make several queries
    queries = [
        "What is the company's business model?",
        "How did they perform in the US market?",
        "What are their future growth plans?"
    ]
    
    for query in queries:
        response = processor.query_annual_report(pdf_path, query, "TCS")
        print(f"Query: {query}")
        print(f"Response: {response['response'][:100]}...")
    
    # Get conversation history
    history = processor.get_conversation_history()
    print(f"\nConversation History ({len(history)} entries):")
    for i, entry in enumerate(history, 1):
        print(f"  {i}. {entry['query'][:50]}...")
    
    # Save conversation history
    processor.save_conversation_history("conversation_history.json")
    print("✓ Conversation history saved to conversation_history.json")

def main():
    """Main function to run all examples."""
    print("Annual Report Processor - FinAgent Example Usage")
    print("=" * 60)
    
    # Run examples
    try:
        example_finagent_usage()
    except Exception as e:
        print(f"FinAgent example failed: {e}")
    
    try:
        example_tcs_report()
    except Exception as e:
        print(f"TCS report example failed: {e}")
    
    try:
        example_reliance_report()
    except Exception as e:
        print(f"Reliance report example failed: {e}")
    
    try:
        example_batch_processing()
    except Exception as e:
        print(f"Batch processing example failed: {e}")
    
    try:
        example_financial_analysis()
    except Exception as e:
        print(f"Financial analysis example failed: {e}")
    
    try:
        example_conversation_history()
    except Exception as e:
        print(f"Conversation history example failed: {e}")
    
    print("\n" + "=" * 60)
    print("Example usage completed!")
    print("\nTo use with your own PDFs:")
    print("1. Place your annual report PDFs in the 'Reports' folder")
    print("2. The system will automatically use the fine-tuned FinAgent model")
    print("3. Run the examples again to test with your reports")

if __name__ == "__main__":
    main() 