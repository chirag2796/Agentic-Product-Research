"""
Run the CRM Research System in Fallback Mode (No LLM required)
"""
import json
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from agents.fallback_agents import FallbackCRMResearchSystem
from utils.pdf_generator import PDFReportGenerator
from config import CRM_TOOLS, RESEARCH_AREAS

console = Console()


def display_welcome():
    """Display welcome message"""
    welcome_text = """
🤖 AI Agent Team for CRM Research (Fallback Mode)

This system uses autonomous agents to research and compare CRM tools:
• Web Research Specialist - Gathers real-time data using web search
• Data Analysis Specialist - Structures and analyzes data
• Report Generation Specialist - Creates comprehensive comparison

Target CRM Tools: HubSpot, Zoho, Salesforce
Focus Areas: Pricing, Features, Integrations, Limitations

Note: This mode uses web search only - no LLM calls required
    """
    
    console.print(Panel(welcome_text, title="🚀 CRM Research Agent System (Fallback)", border_style="blue"))


def save_results(results: dict, pdf_generator: PDFReportGenerator):
    """Save results to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON results
    json_filename = f"crm_research_results_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    console.print(f"✅ JSON results saved to: {json_filename}")
    
    # Save text summary
    txt_filename = f"crm_research_summary_{timestamp}.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(f"CRM Research Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        if 'final_report' in results and 'final_report' in results['final_report']:
            f.write(results['final_report']['final_report'])
        else:
            f.write("Research completed successfully. See JSON file for detailed results.")
    
    console.print(f"✅ Text summary saved to: {txt_filename}")
    
    # Generate PDF reports
    try:
        pdf_filename = f"crm_research_report_{timestamp}.pdf"
        pdf_path = pdf_generator.generate_pdf_report(results, pdf_filename)
        console.print(f"✅ PDF report saved to: {pdf_path}")
        
        # Generate summary PDF
        summary_pdf_filename = f"crm_research_summary_{timestamp}.pdf"
        summary_pdf_path = pdf_generator.generate_summary_pdf(results, summary_pdf_filename)
        console.print(f"✅ PDF summary saved to: {summary_pdf_path}")
        
    except Exception as e:
        console.print(f"⚠️  PDF generation failed: {str(e)}")


def display_summary_table():
    """Display a summary table of what will be researched"""
    table = Table(title="Research Scope")
    table.add_column("CRM Tool", style="cyan")
    table.add_column("Research Areas", style="magenta")
    
    for tool in CRM_TOOLS:
        table.add_row(tool, ", ".join(RESEARCH_AREAS))
    
    console.print(table)


def main():
    """Main application function"""
    display_welcome()
    display_summary_table()
    
    # Confirm before starting
    console.print("\n" + "="*60)
    response = input("Start the research process? (y/n): ").lower().strip()
    
    if response != 'y':
        console.print("Research cancelled.")
        return
    
    console.print("\n🚀 Starting research process...")
    
    try:
        # Initialize fallback system
        console.print("🔧 Initializing fallback research system...")
        research_system = FallbackCRMResearchSystem()
        pdf_generator = PDFReportGenerator()
        
        # Run research
        console.print("🔍 Research in progress...")
        results = research_system.run_research()
        
        # Display final report
        console.print("\n" + "="*80)
        if 'final_report' in results and 'final_report' in results['final_report']:
            final_report = results['final_report']['final_report']
            # Show first 500 characters
            preview = final_report[:500] + "..." if len(final_report) > 500 else final_report
            console.print(Panel(preview, title="📊 Research Results Preview", border_style="green"))
        else:
            console.print(Panel("Research completed successfully. See generated files for detailed results.", 
                              title="📊 Research Results", border_style="green"))
        
        # Save results
        console.print("\n💾 Saving results...")
        save_results(results, pdf_generator)
        
        console.print("\n✅ Research completed successfully!")
        console.print("📁 Check the 'results' folder for PDF reports")
        
    except Exception as e:
        console.print(f"\n❌ Error during research: {str(e)}")
        console.print("Please check your internet connection and API keys.")
        import traceback
        console.print(f"Full error: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
