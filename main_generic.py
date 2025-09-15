"""
Generic AI Agent Research System
Demonstrates true agentic orchestration for any research task
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from agents.generic_agents import GenericResearchOrchestrator, GenericAgentState
from utils.html_generator import HTMLReportGenerator
from config import ASSIGNMENT_QUERY

console = Console()


def pause_for_explanation(title: str, explanation: str, interactive_mode: bool):
    """Pause for user input in interactive mode"""
    if interactive_mode:
        console.print(f"\n[bold blue]STAGE: {title}[/bold blue]")
        console.print(Panel(explanation, title="Explanation", border_style="blue"))
        input("\nPress Enter to continue (): ")


def show_agent_working(agent_name: str, action: str):
    """Show agent working status"""
    console.print(f"\n🤖 {agent_name}: {action}")


def show_state_info(state: dict, interactive_mode: bool):
    """Show current system state"""
    if interactive_mode:
        console.print(f"\n📊 Current System State:")
        console.print(f"  • Entities: {', '.join(state.get('parsed_entities', []))}")
        console.print(f"  • Focus Areas: {', '.join(state.get('research_focus_areas', []))}")
        console.print(f"  • Current Agent: {state.get('current_agent', 'None')}")
        console.print(f"  • Agent Messages: {len(state.get('agent_messages', []))}")
        console.print(f"  • Iteration Count: {state.get('iteration_count', 0)}/{state.get('max_iterations', 5)}")
        console.print(f"  • Research Data: {len(state.get('research_data', {}))} entities")
        console.print(f"  • Analysis Results: {len(state.get('analysis_results', {}))} entities")
        console.print(f"  • Validation Status: {'Complete' if state.get('validation_results') else 'Pending'}")


def save_results(state: dict, results_dir: Path):
    """Save research results to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = results_dir / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON data
    json_file = run_dir / "research_data.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, default=str)
    
    # Save text report
    txt_file = run_dir / "research_report.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(state.get("final_report", "No report generated"))
    
    # Generate HTML report
    html_generator = HTMLReportGenerator()
    html_content = html_generator.generate_html_report(state)
    html_file = run_dir / "research_report.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    console.print(f"📁 Results saved to: {run_dir}")
    console.print(f"  • JSON: {json_file.name}")
    console.print(f"  • TXT: {txt_file.name}")
    console.print(f"  • HTML: {html_file.name}")


def run_generic_research(query: str, interactive_mode: bool = False):
    """Run generic research with step-by-step explanations"""
    console.print("🚀 Starting Generic AI Agent Research System...")
    
    # Initialize the generic orchestrator
    console.print("🔧 Initializing Generic Research Orchestrator...")
    orchestrator = GenericResearchOrchestrator()
    
    # Show system capabilities
    console.print(Panel(
        f"""
🎪 GENERIC AI AGENT RESEARCH SYSTEM - {'INTERACTIVE' if interactive_mode else 'AUTOMATED'} MODE

🎯 System Capabilities:
• Handles ANY research query (products, companies, technologies, concepts)
• 6+ autonomous agents with dynamic orchestration
• Non-linear workflow with intelligent routing
• Collaborative agent behavior with reasoning and delegation
• Quality validation and iterative improvement

🔧 Framework: LangGraph with StateGraph
🤖 Agents: Query Parser, Research Planner, Data Collector, Data Analyzer, Quality Validator, Report Synthesizer
📊 Output: Comprehensive research reports in multiple formats

🎯 Current Query: {query[:100]}...
        """,
        title="🤖 Generic AI Agent Research System",
        border_style="green"
    ))
    
    if interactive_mode:
        console.print("\n🎭 **ORCHESTRATOR INITIATION**: The **ORCHESTRATOR** is now initiating the multi-agent workflow with dynamic decision-making based on agent results.")
        input("\nPress Enter to start the research process...")
    
    # Run the research
    try:
        result = orchestrator.run_research(query, max_iterations=8)
        
        # Show results
        console.print(f"\n✅ Research completed successfully!")
        console.print(f"📊 Total agent interactions: {len(result.get('agent_messages', []))}")
        console.print(f"📊 Research entities: {len(result.get('parsed_entities', []))}")
        console.print(f"📊 Analysis results: {len(result.get('analysis_results', {}))}")
        console.print(f"📊 Report length: {len(result.get('final_report', ''))} characters")
        
        # Save results
        results_dir = Path("results")
        save_results(result, results_dir)
        
        # Show agent communication log
        console.print(f"\n🤖 Agent Communication Log:")
        for i, message in enumerate(result.get('agent_messages', []), 1):
            console.print(f"  {i}. {message}")
        
        console.print(f"\n📁 Check the 'results' folder for generated files")
        console.print("🎪 Perfect for demonstrating generic agentic AI capabilities!")
        
    except Exception as e:
        console.print(f"❌ Research failed: {e}")
        raise


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generic AI Agent Research System")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--query", type=str, default=ASSIGNMENT_QUERY, help="Research query")
    
    args = parser.parse_args()
    
    # Run the research
    run_generic_research(args.query, args.interactive)


if __name__ == "__main__":
    main()
