"""
Demo script for the CRM Research Agent System
"""
from rich.console import Console
from rich.panel import Panel
from agents.simple_agents import CRMResearchSystem
from utils.pdf_generator import PDFReportGenerator
import json

console = Console()

def demo_single_agent():
    """Demo a single agent working"""
    console.print(Panel("🤖 Demo: Single Agent Research", title="Demo", border_style="blue"))
    
    # Initialize just the web research agent
    from agents.simple_agents import WebResearchAgent
    researcher = WebResearchAgent()
    
    console.print("🔍 Testing web research agent with HubSpot...")
    result = researcher.research_crm_tool("HubSpot")
    
    console.print("✅ Research completed!")
    console.print(f"📊 Research data length: {len(str(result))} characters")
    
    return result

def demo_pdf_generation():
    """Demo PDF generation"""
    console.print(Panel("📄 Demo: PDF Generation", title="Demo", border_style="green"))
    
    # Create sample data
    sample_data = {
        "final_report": {
            "final_report": """
# CRM Research Report

## Executive Summary
This is a sample CRM research report demonstrating the system's capabilities.

## Key Findings
- HubSpot: Excellent for small businesses
- Zoho: Great value for money
- Salesforce: Enterprise-grade solution

## Recommendations
Choose based on your business size and budget.
            """
        },
        "research_plan": {
            "plan": "Sample research plan for demonstration purposes."
        }
    }
    
    # Generate PDF
    pdf_generator = PDFReportGenerator()
    pdf_path = pdf_generator.generate_pdf_report(sample_data, "demo_report.pdf")
    
    console.print(f"✅ PDF generated: {pdf_path}")
    return pdf_path

def main():
    """Run demos"""
    console.print("🎬 CRM Research Agent System - Demo")
    console.print("=" * 50)
    
    # Demo 1: Single agent
    demo_single_agent()
    console.print()
    
    # Demo 2: PDF generation
    demo_pdf_generation()
    console.print()
    
    console.print("🎉 Demo completed! The system is ready for full research.")
    console.print("Run 'python main.py' to start the complete research process.")

if __name__ == "__main__":
    main()
