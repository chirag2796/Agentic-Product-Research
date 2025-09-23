"""
Dynamic Generic AI Agent Research System
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from agents.agents import GenericResearchOrchestrator, GenericAgentState
from utils.html_generator import HTMLReportGenerator
from config import ASSIGNMENT_QUERY
from agents.agents import (
    orchestrator_decision, _assess_data_completeness,
    QueryParserAgent, ResearchPlannerAgent, DataCollectorAgent, 
    DataAnalyzerAgent, QualityValidatorAgent, ReportSynthesizerAgent
)

console = Console()


def pause_for_explanation(title: str, explanation: str, interactive_mode: bool):
    """Pause for user input in interactive mode"""
    if interactive_mode:
        console.print(f"\n[bold blue]STAGE: {title}[/bold blue]")
        console.print(Panel(explanation, title="Explanation", border_style="blue"))
        input("\nPress Enter to continue: ")


def show_agent_working(agent_name: str, action: str):
    """Show agent working status"""
    console.print(f"\n{agent_name}: {action}")


def show_llm_call(prompt: str, response: str, agent_name: str):
    """Show full LLM input and output for transparency"""
    console.print(f"\n[bold]{agent_name} LLM CALL:[/bold]")
    console.print(f"[bold]INPUT PROMPT:[/bold]")
    console.print(f"[dim]{prompt[:500]}{'...' if len(prompt) > 500 else ''}[/dim]")
    console.print(f"\n[bold]LLM RESPONSE:[/bold]")
    console.print(f"[green]{response[:500]}{'...' if len(response) > 500 else ''}[/green]")


def show_agent_transfer_chain(agent_messages: list):
    """Show the complete agent transfer chain in one line"""
    # Extract agent names from messages (including duplicates to show actual flow)
    agent_chain = []
    for message in agent_messages:
        if ":" in message:
            agent_name = message.split(":")[0].strip()
            agent_chain.append(agent_name)
    
    # Create the chain string showing actual flow
    chain_str = " → ".join(agent_chain)
    console.print(f"\n[bold]COMPLETE AGENT TRANSFER CHAIN:[/bold] {chain_str}")


def show_agent_transfer(from_agent: str, to_agent: str, reason: str = ""):
    """Show clear agent transfer with reason"""
    console.print(f"\n[bold]CONTROL TRANSFER:[/bold] {from_agent} → {to_agent}")
    if reason:
        console.print(f"   Reason: {reason}")


def show_state_info(state: dict, interactive_mode: bool):
    """Show current system state"""
    if interactive_mode:
        console.print(f"\nCurrent System State:")
        console.print(f"  • Entities: {', '.join(state.get('parsed_entities', []))}")
        console.print(f"  • Focus Areas: {', '.join(state.get('research_focus_areas', []))}")
        console.print(f"  • Current Agent: {state.get('current_agent', 'None')}")
        console.print(f"  • Agent Messages: {len(state.get('agent_messages', []))}")
        console.print(f"  • Iteration Count: {state.get('iteration_count', 0)}/{state.get('max_iterations', 8)}")
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
    
    # Save markdown report
    md_file = run_dir / "research_report.md"
    with open(md_file, 'w', encoding='utf-8') as f:
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
    console.print(f"  • MD: {md_file.name}")
    console.print(f"  • HTML: {html_file.name}")


# orchestrator_decision function moved to agents/agents.py for better organization


def _assess_data_completeness(state: dict) -> str:
    """Assess data completeness"""
    research_data = state.get("research_data", {})
    analysis_results = state.get("analysis_results", {})
    
    if len(research_data) == 0:
        return "No data"
    elif len(research_data) < 2:
        return "Incomplete"
    elif len(analysis_results) == 0:
        return "Partial"
    else:
        return "Complete"


def run_research(query: str, interactive_mode: bool = False):
    """Run dynamic research with orchestration"""
    console.print("🚀 Starting AI Research System...")
    
    # Initialize the generic orchestrator
    console.print("🔧 Initializing Generic Research Orchestrator...")
    orchestrator = GenericResearchOrchestrator()
    
    # Show system capabilities
    console.print(Panel(
        f"""
🎪 DYNAMIC AI AGENT RESEARCH SYSTEM - {'INTERACTIVE' if interactive_mode else 'AUTOMATED'} MODE

System Capabilities:
• Handles ANY research query with true dynamic orchestration
• 6+ autonomous agents with intelligent routing
• Non-linear workflow with real inter-agent communication
• Collaborative agent behavior with reasoning and delegation
• Quality validation and iterative improvement
• Orchestrator makes intelligent decisions to loop back and enhance

🔧 Framework: LangGraph with StateGraph
Agents: Query Parser, Research Planner, Data Collector, Data Analyzer, Quality Validator, Report Synthesizer
Output: Comprehensive research reports with true agentic orchestration

Current Query: {query[:100]}...
        """,
        title="Truly Dynamic AI Agent Research System",
        border_style="green"
    ))
    
    if interactive_mode:
        console.print("\n[bold]ORCHESTRATOR INITIATION[/bold]: The ORCHESTRATOR is now initiating the multi-agent workflow with dynamic decision-making based on agent results.")
        input("\nPress Enter to start the research process...")
    
    # Initialize state
    state = {
        "original_query": query,
        "parsed_entities": [],
        "research_focus_areas": [],
        "research_data": {},
        "analysis_results": {},
        "validation_results": {},
        "final_report": "",
        "current_agent": "",
        "agent_messages": [],
        "iteration_count": 0,
        "max_iterations": 15,
        "research_context": {},
        "agent_call_counts": {"research_planner": 0, "data_collector": 0, "data_analyzer": 0, "quality_validator": 0, "report_synthesizer": 0}
    }
    
    # Dynamic workflow loop
    current_step = "query_parsing"
    last_result = ""
    
    while state["iteration_count"] < state["max_iterations"]:
        state["iteration_count"] += 1
        
        if current_step == "query_parsing":
            # Query Parsing Step - using proper agent class
            query_parser = QueryParserAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation)
            state, last_result = query_parser.execute(query, state, interactive_mode)
            
            show_state_info(state, interactive_mode)
            
            # Orchestrator decision
            console.print("\n[bold]ORCHESTRATOR DECISION MAKING[/bold]: Analyzing results and deciding next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"[bold]ORCHESTRATOR DECISION:[/bold] {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "research_planning":
                show_agent_transfer("Query Parser", "Research Planner", "Orchestrator decided to create research plan")
                current_step = "research_planning"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "data_collection":
                show_agent_transfer("Query Parser", "Data Collector", "Orchestrator decided to collect data")
                current_step = "data_collection"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "data_analysis":
                show_agent_transfer("Query Parser", "Data Analyzer", "Orchestrator decided to analyze data")
                current_step = "data_analysis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "report_synthesis":
                show_agent_transfer("Query Parser", "Report Synthesizer", "Orchestrator decided to synthesize report")
                current_step = "report_synthesis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "end":
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
                break
            else:
                show_agent_transfer("Query Parser", "Research Planner", "Orchestrator default decision")
                current_step = "research_planning"  # Default
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            
        elif current_step == "research_planning":
            # Research Planning Step - using proper agent class
            research_planner = ResearchPlannerAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation)
            state, last_result = research_planner.execute(state, interactive_mode)
            
            show_state_info(state, interactive_mode)
            
            # Orchestrator decision
            console.print("\n[bold]ORCHESTRATOR DECISION MAKING[/bold]: Analyzing results and deciding next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"[bold]ORCHESTRATOR DECISION:[/bold] {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "data_collection":
                show_agent_transfer("Research Planner", "Data Collector", "Orchestrator decided to collect data")
                current_step = "data_collection"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "data_analysis":
                show_agent_transfer("Research Planner", "Data Analyzer", "Orchestrator decided to analyze data")
                current_step = "data_analysis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "report_synthesis":
                show_agent_transfer("Research Planner", "Report Synthesizer", "Orchestrator decided to synthesize report")
                current_step = "report_synthesis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "end":
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
                break
            else:
                show_agent_transfer("Research Planner", "Data Collector", "Orchestrator default decision")
                current_step = "data_collection"  # Default
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            
        elif current_step == "data_collection":
            # Data Collection Step - using proper agent class
            data_collector = DataCollectorAgent(orchestrator, console, show_agent_working, pause_for_explanation, show_state_info)
            state, last_result = data_collector.execute(state, interactive_mode)
            
            # Orchestrator decision
            console.print("\n[bold]ORCHESTRATOR DECISION MAKING[/bold]: Analyzing results and deciding next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"[bold]ORCHESTRATOR DECISION:[/bold] {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "data_collection":
                show_agent_transfer("Data Collector", "Data Collector", "Orchestrator decided to collect more data")
                current_step = "data_collection"  # Loop back for more data collection
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "data_analysis":
                show_agent_transfer("Data Collector", "Data Analyzer", "Orchestrator decided to analyze collected data")
                current_step = "data_analysis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "additional_research":
                show_agent_transfer("Data Collector", "Data Collector", "Orchestrator decided to collect more data")
                current_step = "data_collection"  # Loop back for more research
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "report_synthesis":
                show_agent_transfer("Data Collector", "Report Synthesizer", "Orchestrator decided to synthesize report")
                current_step = "report_synthesis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "end":
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
                break
            else:
                show_agent_transfer("Data Collector", "Data Analyzer", "Orchestrator default decision")
                current_step = "data_analysis"  # Default
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            
        elif current_step == "data_analysis":
            # Data Analysis Step - using proper agent class
            data_analyzer = DataAnalyzerAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info)
            state, last_result = data_analyzer.execute(state, interactive_mode)
            
            # Orchestrator decision
            console.print("\n[bold]ORCHESTRATOR DECISION MAKING[/bold]: Analyzing results and deciding next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"[bold]ORCHESTRATOR DECISION:[/bold] {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "quality_validation":
                show_agent_transfer("Data Analyzer", "Quality Validator", "Orchestrator decided to validate quality")
                current_step = "quality_validation"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "enhance_analysis":
                show_agent_transfer("Data Analyzer", "Data Analyzer", "Orchestrator decided to enhance analysis")
                current_step = "data_analysis"  # Loop back for enhanced analysis
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "additional_research":
                show_agent_transfer("Data Analyzer", "Data Collector", "Orchestrator decided to collect more data")
                current_step = "data_collection"  # Loop back for more research
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "report_synthesis":
                show_agent_transfer("Data Analyzer", "Report Synthesizer", "Orchestrator decided to synthesize report")
                current_step = "report_synthesis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "end":
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
                break
            else:
                show_agent_transfer("Data Analyzer", "Quality Validator", "Orchestrator default decision")
                current_step = "quality_validation"  # Default to quality validation
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
        
        elif current_step == "quality_validation":
            # Quality Validation Step - using proper agent class
            quality_validator = QualityValidatorAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info)
            state, last_result = quality_validator.execute(state, interactive_mode)
            
            # Orchestrator decision
            console.print("\n[bold]ORCHESTRATOR DECISION MAKING[/bold]: Analyzing results and deciding next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"[bold]ORCHESTRATOR DECISION:[/bold] {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "report_synthesis":
                show_agent_transfer("Quality Validator", "Report Synthesizer", "Orchestrator decided to synthesize report")
                current_step = "report_synthesis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "data_collection":
                show_agent_transfer("Quality Validator", "Data Collector", "Orchestrator decided to collect more data")
                current_step = "data_collection"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "data_analysis":
                show_agent_transfer("Quality Validator", "Data Analyzer", "Orchestrator decided to enhance analysis")
                current_step = "data_analysis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "additional_research":
                show_agent_transfer("Quality Validator", "Data Collector", "Orchestrator decided to do additional research")
                current_step = "data_collection"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "quality_validation":
                show_agent_transfer("Quality Validator", "Quality Validator", "Orchestrator decided to re-validate quality")
                current_step = "quality_validation"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "end":
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
                break
            else:
                # Default to report synthesis
                show_agent_transfer("Quality Validator", "Report Synthesizer", "Orchestrator default decision")
                current_step = "report_synthesis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            
        elif current_step == "report_synthesis":
            # Report Synthesis Step - using proper agent class
            report_synthesizer = ReportSynthesizerAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info)
            state, last_result = report_synthesizer.execute(state, interactive_mode)
            
            show_state_info(state, interactive_mode)
            
            # Orchestrator decision
            console.print("\n[bold]ORCHESTRATOR DECISION MAKING[/bold]: Analyzing results and deciding next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"[bold]ORCHESTRATOR DECISION:[/bold] {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "enhance_analysis":
                show_agent_transfer("Report Synthesizer", "Data Analyzer", "Orchestrator decided to enhance analysis")
                current_step = "data_analysis"  # Loop back for enhanced analysis
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "additional_research":
                show_agent_transfer("Report Synthesizer", "Data Collector", "Orchestrator decided to collect more data")
                current_step = "data_collection"  # Loop back for more research
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            elif decision == "end":
                # End the research process
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
                break
            else:
                # Default to data collection for more back-and-forth
                show_agent_transfer("Report Synthesizer", "Data Collector", "Orchestrator default to data collection")
                current_step = "data_collection"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
    
    # Save results
    results_dir = Path("results")
    save_results(state, results_dir)
    
    # Show final summary
    console.print(f"\nResearch completed!")
    console.print(f"Total agent interactions: {len(state.get('agent_messages', []))}")
    console.print(f"Research entities: {len(state.get('parsed_entities', []))}")
    console.print(f"Analysis results: {len(state.get('analysis_results', {}))}")
    console.print(f"Report length: {len(state.get('final_report', ''))} characters")
    
    # Show agent communication log
    console.print(f"\nAgent Communication Log:")
    for i, message in enumerate(state.get('agent_messages', []), 1):
        console.print(f"  {i}. {message}")
    
    # Show complete agent transfer chain
    show_agent_transfer_chain(state.get('agent_messages', []))


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="AI Research System")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--query", type=str, default=ASSIGNMENT_QUERY, help="Research query")
    
    args = parser.parse_args()
    
    # Run the research
    run_research(args.query, args.interactive)


if __name__ == "__main__":
    main()
