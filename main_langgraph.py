"""
Main application for LangGraph-based CRM Research Agent System
Meets all assignment requirements with natural language query initiation
"""
import json
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from agents.langgraph_agents import CRMResearchOrchestrator
from utils.html_generator import HTMLReportGenerator

console = Console()

# The exact query from the assignment
ASSIGNMENT_QUERY = """We're evaluating CRM tools. Give me a summarized comparison between HubSpot, Zoho, and Salesforce for small to mid-size B2B businesses. Focus on pricing, features, integrations, and limitations."""


def display_welcome():
    """Display welcome message"""
    welcome_text = """
🤖 AI Agent Team for CRM Research (LangGraph Framework)

This system uses 7 autonomous agents that interact dynamically:
• Query Analyzer - Analyzes natural language business queries
• Research Coordinator - Plans and coordinates research strategy
• Web Research Specialist - Gathers real-time data using web search
• Data Analysis Specialist - Structures and analyzes research data
• Validation Specialist - Cross-checks findings and ensures accuracy
• Quality Controller - Performs overall quality assurance
• Report Generation Specialist - Creates comprehensive comparison reports

Framework: LangGraph (StateGraph-based orchestration)
Target CRM Tools: HubSpot, Zoho, Salesforce
Focus Areas: Pricing, Features, Integrations, Limitations
    """
    
    console.print(Panel(welcome_text, title="🚀 LangGraph CRM Research Agent System", border_style="blue"))


def display_query():
    """Display the assignment query"""
    console.print(Panel(ASSIGNMENT_QUERY, title="📝 Business Query", border_style="green"))


def save_results(results: dict, html_generator: HTMLReportGenerator):
    """Save results to files in organized folders"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create run-specific folder
    run_folder = f"results/run_{timestamp}"
    os.makedirs(run_folder, exist_ok=True)
    
    # Save JSON results
    json_filename = f"langgraph_crm_research_{timestamp}.json"
    json_path = os.path.join(run_folder, json_filename)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    console.print(f"✅ JSON results saved to: {json_path}")
    
    # Save text summary
    txt_filename = f"langgraph_crm_summary_{timestamp}.txt"
    txt_path = os.path.join(run_folder, txt_filename)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"LangGraph CRM Research Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Query: {results.get('query', 'N/A')}\n\n")
        f.write(results.get('final_report', 'No report generated'))
    
    console.print(f"✅ Text summary saved to: {txt_path}")
    
    # Generate HTML report
    try:
        html_filename = f"langgraph_crm_report_{timestamp}.html"
        html_path = html_generator.generate_html_report(results, html_filename, run_folder)
        console.print(f"✅ HTML report saved to: {html_path}")
        
    except Exception as e:
        console.print(f"⚠️  HTML generation failed: {str(e)}")


def display_agent_communications(results: dict):
    """Display agent communication log"""
    if 'agent_messages' in results:
        console.print("\n" + "="*60)
        console.print("🤖 Agent Communication Log")
        console.print("="*60)
        
        for i, message in enumerate(results['agent_messages'], 1):
            console.print(f"{i}. {message}")
        
        console.print(f"\nTotal agent interactions: {len(results['agent_messages'])}")


def display_architecture_info():
    """Display system architecture information"""
    architecture_text = """
🏗️ System Architecture (LangGraph StateGraph)

Agent Communication Flow:
Query Analyzer → Research Coordinator → Web Researcher
                ↓
Data Analyst ← Validation Agent ← Quality Controller
                ↓
            Report Generator

Key Features:
• Dynamic routing based on agent decisions
• Non-linear workflow with conditional edges
• Agent state sharing and communication
• Iterative research with quality control
• Autonomous agent reasoning and delegation
    """
    
    console.print(Panel(architecture_text, title="🏗️ System Architecture", border_style="cyan"))


def main():
    """Main application function"""
    display_welcome()
    display_query()
    display_architecture_info()
    
    # Confirm before starting
    console.print("\n" + "="*60)
    response = input("Start the agentic research process? (y/n): ").lower().strip()
    
    if response != 'y':
        console.print("Research cancelled.")
        return
    
    console.print("\n🚀 Starting LangGraph-based research process...")
    
    try:
        # Initialize system
        console.print("🔧 Initializing LangGraph orchestrator...")
        orchestrator = CRMResearchOrchestrator()
        html_generator = HTMLReportGenerator()
        
        # Run research with the assignment query
        console.print("🤖 Agents are now working autonomously...")
        results = orchestrator.run_research(ASSIGNMENT_QUERY)
        
        # Display final report
        console.print("\n" + "="*80)
        if 'final_report' in results and results['final_report']:
            final_report = results['final_report']
            # Show first 800 characters
            preview = final_report[:800] + "..." if len(final_report) > 800 else final_report
            console.print(Panel(preview, title="📊 Research Results Preview", border_style="green"))
        else:
            console.print(Panel("Research completed successfully. See generated files for detailed results.", 
                              title="📊 Research Results", border_style="green"))
        
        # Display agent communications
        display_agent_communications(results)
        
        # Save results
        console.print("\n💾 Saving results...")
        save_results(results, html_generator)
        
        console.print("\n✅ LangGraph-based research completed successfully!")
        console.print("📁 Check the 'results' folder for HTML reports")
        console.print("🤖 Agent communication log saved in JSON file")
        
    except Exception as e:
        console.print(f"\n❌ Error during research: {str(e)}")
        console.print("Please check your API keys and internet connection.")
        import traceback
        console.print(f"Full error: {traceback.format_exc()}")


if __name__ == "__main__":
    main()
