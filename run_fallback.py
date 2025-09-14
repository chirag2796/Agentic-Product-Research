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
from utils.html_generator import HTMLReportGenerator
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


def save_results(results: dict, html_generator: HTMLReportGenerator):
    """Save results to files in organized folders"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create run-specific folder
    run_folder = f"results/run_{timestamp}"
    os.makedirs(run_folder, exist_ok=True)
    
    # Save JSON results
    json_filename = f"fallback_crm_research_{timestamp}.json"
    json_path = os.path.join(run_folder, json_filename)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    console.print(f"✅ JSON results saved to: {json_path}")
    
    # Save text summary
    txt_filename = f"fallback_crm_summary_{timestamp}.txt"
    txt_path = os.path.join(run_folder, txt_filename)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"Fallback CRM Research Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        if 'final_report' in results and 'final_report' in results['final_report']:
            f.write(results['final_report']['final_report'])
        else:
            f.write("Research completed successfully. See JSON file for detailed results.")
    
    console.print(f"✅ Text summary saved to: {txt_path}")
    
    # Generate HTML report
    try:
        html_filename = f"fallback_crm_report_{timestamp}.html"
        html_path = html_generator.generate_html_report(results, html_filename, run_folder)
        console.print(f"✅ HTML report saved to: {html_path}")
        
    except Exception as e:
        console.print(f"⚠️  HTML generation failed: {str(e)}")


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
        html_generator = HTMLReportGenerator()
        
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
        save_results(results, html_generator)
        
        console.print("\n✅ Research completed successfully!")
        console.print("📁 Check the 'results' folder for HTML reports")
        
    except Exception as e:
        console.print(f"\n❌ Error during research: {str(e)}")
        console.print("Please check your internet connection and API keys.")
        import traceback
        console.print(f"Full error: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
