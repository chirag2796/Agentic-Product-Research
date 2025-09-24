"""
Dynamic Generic AI Agent Research System - LangGraph Implementation
"""
import argparse
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from typing_extensions import NotRequired
import operator

from agents.agents import GenericResearchOrchestrator
from utils.html_generator import HTMLReportGenerator
from config import ASSIGNMENT_QUERY
from agents.agents import (
    QueryParserAgent, ResearchPlannerAgent, DataCollectorAgent, 
    DataAnalyzerAgent, QualityValidatorAgent, ReportSynthesizerAgent
)

console = Console()


# LangGraph State Definition
class AgentState(TypedDict):
    original_query: str
    parsed_entities: list
    research_focus_areas: list
    research_context: dict
    research_data: dict
    analysis_results: dict
    validation_results: NotRequired[dict]
    final_report: NotRequired[str]
    current_agent: str
    agent_messages: Annotated[list, operator.add]
    agent_call_counts: dict
    iteration_count: int
    max_iterations: int
    interactive_mode: NotRequired[bool]
    research_queries: NotRequired[list]


def pause_for_explanation(title: str, explanation: str, interactive_mode: bool):
    """Pause for user input in interactive mode"""
    if interactive_mode:
        console.print(f"\n[bold blue]STAGE: {title}[/bold blue]")
        console.print(Panel(explanation, title="Explanation", border_style="blue"))
        input("\nPress Enter to continue: ")


def show_agent_working(message: str, show: bool = True):
    """Show agent working status"""
    if show:
        console.print(f"[cyan]{message}[/cyan]")


def show_llm_call(prompt: str, response: str, show: bool = True):
    """Show LLM call details"""
    if show:
        console.print(f"\n[yellow]LLM CALL:[/yellow]")
        console.print(f"[dim]INPUT PROMPT:[/dim] {prompt[:200]}...")
        console.print(f"[dim]LLM RESPONSE:[/dim] {response[:200]}...")


def show_state_info(state: dict, show: bool = True):
    """Show current system state"""
    if show:
        console.print(f"\n[bold]Current System State:[/bold]")
        console.print(f"  • Entities: {', '.join(state.get('parsed_entities', []))}")
        console.print(f"  • Focus Areas: {', '.join(state.get('research_focus_areas', []))}")
        console.print(f"  • Current Agent: {state.get('current_agent', 'None')}")
        console.print(f"  • Agent Messages: {len(state.get('agent_messages', []))}")
        console.print(f"  • Iteration Count: {state.get('iteration_count', 0)}/{state.get('max_iterations', 15)}")
        console.print(f"  • Research Data: {len(state.get('research_data', {}))} entities")
        console.print(f"  • Analysis Results: {len(state.get('analysis_results', {}))} entities")
        console.print(f"  • Validation Status: {'Complete' if state.get('validation_results') else 'Pending'}")


def show_agent_transfer(from_agent: str, to_agent: str, reason: str):
    """Show agent transfer"""
    console.print(f"\n[bold]CONTROL TRANSFER:[/bold] {from_agent} → {to_agent}")
    console.print(f"   Reason: {reason}")


def show_agent_transfer_chain(agent_messages: list):
    """Show complete agent transfer chain"""
    if agent_messages:
        # Remove duplicates while preserving order
        unique_messages = []
        seen = set()
        for message in agent_messages:
            if message not in seen:
                unique_messages.append(message)
                seen.add(message)
        
        console.print(f"\n[bold]COMPLETE AGENT TRANSFER CHAIN:[/bold]")
        for i, message in enumerate(unique_messages):
            if i == 0:
                console.print(f"   {message}")
            else:
                console.print(f" → {message}")


def save_results(state: dict, results_dir: Path):
    """Save research results to files"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = results_dir / f"run_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON data
    json_file = run_dir / "research_data.json"
    json_data = {
        "original_query": state.get("original_query", ""),
        "parsed_entities": state.get("parsed_entities", []),
        "research_focus_areas": state.get("research_focus_areas", []),
        "research_data": state.get("research_data", {}),
        "analysis_results": state.get("analysis_results", {}),
        "validation_results": state.get("validation_results", {}),
        "agent_messages": state.get("agent_messages", [])
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    
    # Save text report
    report_content = state.get("final_report", "No report generated")
    txt_file = run_dir / "research_report.txt"
    md_file = run_dir / "research_report.md"
    
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # Generate HTML report
    html_file = run_dir / "research_report.html"
    try:
        html_generator = HTMLReportGenerator()
        # Create research data structure expected by HTMLReportGenerator
        research_data_for_html = {
            "original_query": state.get("original_query", ""),
            "parsed_entities": state.get("parsed_entities", []),
            "research_data": state.get("research_data", {}),
            "analysis_results": state.get("analysis_results", {}),
            "final_report": report_content,
            "agent_messages": state.get("agent_messages", [])
        }
        html_content = html_generator.generate_html_report(research_data_for_html)
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
    except Exception as e:
        console.print(f"Warning: Could not generate HTML report: {e}")
    
    console.print(f"\nResults saved to: {run_dir.name}")
    console.print(f"  • JSON: {json_file.name}")
    console.print(f"  • TXT: {txt_file.name}")
    console.print(f"  • MD: {md_file.name}")
    console.print(f"  • HTML: {html_file.name}")


# LangGraph Node Functions
def query_parser_node(state: AgentState) -> AgentState:
    """LangGraph node for query parsing"""
    # Only run if this is the first iteration or if we haven't parsed yet
    if state.get("parsed_entities") and len(state.get("parsed_entities", [])) > 0:
        return state  # Skip if already parsed
        
    orchestrator = GenericResearchOrchestrator()
    agent = QueryParserAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation)
    
    # Get interactive mode from state
    interactive_mode = state.get("interactive_mode", False)
    new_state, last_result = agent.execute(state["original_query"], state, interactive_mode)
    
    # Update iteration count
    new_state["iteration_count"] = state.get("iteration_count", 0) + 1
    new_state["interactive_mode"] = interactive_mode  # Preserve interactive mode
    
    return new_state


def research_planner_node(state: AgentState) -> AgentState:
    """LangGraph node for research planning"""
    # Only run if we haven't planned yet or need to replan
    if state.get("research_queries") and len(state.get("research_queries", [])) > 0:
        return state  # Skip if already planned
        
    orchestrator = GenericResearchOrchestrator()
    agent = ResearchPlannerAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation)
    
    interactive_mode = state.get("interactive_mode", False)
    new_state, last_result = agent.execute(state, interactive_mode)
    
    new_state["iteration_count"] = state.get("iteration_count", 0) + 1
    new_state["interactive_mode"] = interactive_mode
    
    return new_state


def data_collector_node(state: AgentState) -> AgentState:
    """LangGraph node for data collection"""
    orchestrator = GenericResearchOrchestrator()
    agent = DataCollectorAgent(orchestrator, console, show_agent_working, pause_for_explanation, show_state_info)
    
    interactive_mode = state.get("interactive_mode", False)
    new_state, last_result = agent.execute(state, interactive_mode)
    
    new_state["iteration_count"] = state.get("iteration_count", 0) + 1
    new_state["interactive_mode"] = interactive_mode
    
    return new_state


def data_analyzer_node(state: AgentState) -> AgentState:
    """LangGraph node for data analysis"""
    orchestrator = GenericResearchOrchestrator()
    agent = DataAnalyzerAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info)
    
    interactive_mode = state.get("interactive_mode", False)
    new_state, last_result = agent.execute(state, interactive_mode)
    
    new_state["iteration_count"] = state.get("iteration_count", 0) + 1
    new_state["interactive_mode"] = interactive_mode
    
    return new_state


def quality_validator_node(state: AgentState) -> AgentState:
    """LangGraph node for quality validation"""
    orchestrator = GenericResearchOrchestrator()
    agent = QualityValidatorAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info)
    
    interactive_mode = state.get("interactive_mode", False)
    new_state, last_result = agent.execute(state, interactive_mode)
    
    new_state["iteration_count"] = state.get("iteration_count", 0) + 1
    new_state["interactive_mode"] = interactive_mode
    
    return new_state


def report_synthesizer_node(state: AgentState) -> AgentState:
    """LangGraph node for report synthesis"""
    orchestrator = GenericResearchOrchestrator()
    agent = ReportSynthesizerAgent(orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info)
    
    interactive_mode = state.get("interactive_mode", False)
    new_state, last_result = agent.execute(state, interactive_mode)
    
    new_state["iteration_count"] = state.get("iteration_count", 0) + 1
    new_state["interactive_mode"] = interactive_mode
    
    return new_state


def orchestrator_routing(state: AgentState) -> str:
    """LangGraph routing function using our intelligent orchestrator"""
    from agents.agents import orchestrator_decision
    
    orchestrator = GenericResearchOrchestrator()
    
    # Determine last result based on current agent
    current_agent = state.get("current_agent", "")
    last_result = ""
    
    if current_agent == "query_parser":
        last_result = "Query parsed successfully"
    elif current_agent == "research_planner":
        last_result = "Research plan created"
    elif current_agent == "data_collector":
        last_result = f"Data collection completed for {len(state.get('research_data', {}))} entities"
    elif current_agent == "data_analyzer":
        last_result = f"Data analysis completed for {len(state.get('analysis_results', {}))} entities"
    elif current_agent == "quality_validator":
        validation_results = state.get("validation_results", {})
        overall_score = validation_results.get("overall_score", 0)
        validation_status = validation_results.get("validation_status", "unknown")
        if overall_score >= 8:
            last_result = "quality_validated_good"
        elif overall_score >= 6:
            last_result = "quality_validated_needs_improvement"
        else:
            last_result = "quality_validated_poor"
    elif current_agent == "report_synthesizer":
        last_result = "Report synthesis completed"
    
    # Show orchestrator decision making
    console.print("\n[bold]ORCHESTRATOR DECISION MAKING[/bold]: Analyzing results and deciding next action...")
    
    # Get orchestrator decision
    decision = orchestrator_decision(orchestrator, state, last_result)
    
    console.print(f"[bold]ORCHESTRATOR DECISION:[/bold] {decision.upper()}")
    console.print(f"   Based on: {current_agent} result")
    console.print(f"   Iteration: {state.get('iteration_count', 0)}/{state.get('max_iterations', 15)}")
    console.print(f"   Raw decision: '{decision}'")
    
    # Show state info if interactive
    if state.get("interactive_mode", False):
        show_state_info(state, True)
    
    # Map orchestrator decisions to LangGraph node names
    next_node = ""
    if decision == "research_planning":
        next_node = "research_planner"
    elif decision == "data_collection":
        next_node = "data_collector"
    elif decision == "data_analysis":
        next_node = "data_analyzer"
    elif decision == "quality_validation":
        next_node = "quality_validator"
    elif decision == "report_synthesis":
        next_node = "report_synthesizer"
    elif decision == "end":
        next_node = END
    else:
        next_node = "report_synthesizer"  # Default fallback
    
    # Show agent transfer
    if next_node != END:
        current_agent_name = current_agent.replace("_", " ").title() if current_agent else "System"
        next_agent_name = next_node.replace("_", " ").title()
        show_agent_transfer(current_agent_name, next_agent_name, f"Orchestrator decided to proceed with {decision}")
        
        # Pause for explanation if interactive
        if state.get("interactive_mode", False):
            pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", True)
    
    return next_node


def create_langgraph_workflow() -> StateGraph:
    """Create the LangGraph workflow"""
    # Create the StateGraph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("query_parser", query_parser_node)
    workflow.add_node("research_planner", research_planner_node)
    workflow.add_node("data_collector", data_collector_node)
    workflow.add_node("data_analyzer", data_analyzer_node)
    workflow.add_node("quality_validator", quality_validator_node)
    workflow.add_node("report_synthesizer", report_synthesizer_node)
    
    # Set entry point
    workflow.set_entry_point("query_parser")
    
    # Add conditional edges using our intelligent orchestrator
    workflow.add_conditional_edges(
        "query_parser",
        orchestrator_routing,
        {
            "research_planner": "research_planner",
            "data_collector": "data_collector",
            "data_analyzer": "data_analyzer",
            "quality_validator": "quality_validator",
            "report_synthesizer": "report_synthesizer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "research_planner",
        orchestrator_routing,
        {
            "research_planner": "research_planner",
            "data_collector": "data_collector",
            "data_analyzer": "data_analyzer",
            "quality_validator": "quality_validator",
            "report_synthesizer": "report_synthesizer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "data_collector",
        orchestrator_routing,
        {
            "research_planner": "research_planner",
            "data_collector": "data_collector",
            "data_analyzer": "data_analyzer",
            "quality_validator": "quality_validator",
            "report_synthesizer": "report_synthesizer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "data_analyzer",
        orchestrator_routing,
        {
            "research_planner": "research_planner",
            "data_collector": "data_collector",
            "data_analyzer": "data_analyzer",
            "quality_validator": "quality_validator",
            "report_synthesizer": "report_synthesizer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "quality_validator",
        orchestrator_routing,
        {
            "research_planner": "research_planner",
            "data_collector": "data_collector",
            "data_analyzer": "data_analyzer",
            "quality_validator": "quality_validator",
            "report_synthesizer": "report_synthesizer",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "report_synthesizer",
        orchestrator_routing,
        {
            "research_planner": "research_planner",
            "data_collector": "data_collector",
            "data_analyzer": "data_analyzer",
            "quality_validator": "quality_validator",
            "report_synthesizer": "report_synthesizer",
            END: END
        }
    )
    
    return workflow


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
    """Run dynamic research with LangGraph orchestration"""
    console.print("Starting AI Research System...")
    console.print("Initializing LangGraph Multi-Agent Workflow...")
    
    # Show system capabilities
    console.print(Panel(
        f"""
DYNAMIC AI AGENT RESEARCH SYSTEM - {'INTERACTIVE' if interactive_mode else 'AUTOMATED'} MODE

System Capabilities:
• Handles ANY research query with true dynamic orchestration
• 6+ autonomous agents with intelligent routing
• Non-linear workflow with real inter-agent communication
• Collaborative agent behavior with reasoning and delegation
• Quality validation and iterative improvement
• Orchestrator makes intelligent decisions to loop back and enhance

Framework: LangGraph with StateGraph
Agents: Query Parser, Research Planner, Data Collector, Data Analyzer, Quality Validator, Report Synthesizer
Output: Comprehensive research reports with true agentic orchestration

Current Query: {query[:100]}...
        """,
        title="Truly Dynamic AI Agent Research System",
        border_style="green"
    ))
    
    if interactive_mode:
        console.print("\n[bold]LANGGRAPH ORCHESTRATION[/bold]: The LANGGRAPH WORKFLOW is now managing the multi-agent research with dynamic decision-making.")
        input("\nPress Enter to start the research process...")
    
    # Initialize state for LangGraph
    initial_state: AgentState = {
        "original_query": query,
        "parsed_entities": [],
        "research_focus_areas": [],
        "research_context": {},
        "research_data": {},
        "analysis_results": {},
        "current_agent": "",
        "agent_messages": [],
        "agent_call_counts": {
            "research_planner": 0,
            "data_collector": 0,
            "data_analyzer": 0,
            "quality_validator": 0,
            "report_synthesizer": 0
        },
        "iteration_count": 0,
        "max_iterations": 15,
        "interactive_mode": interactive_mode,  # Pass through interactive mode
        "research_queries": []
    }
    
    # Create and compile the LangGraph workflow
    workflow = create_langgraph_workflow()
    app = workflow.compile()
    
    # Execute the LangGraph workflow
    console.print("Executing LangGraph Multi-Agent Workflow...")
    
    try:
        # Run the workflow - use invoke instead of stream to prevent looping
        final_state = app.invoke(initial_state)
        state = final_state
        
    except Exception as e:
        console.print(f"LangGraph execution error: {e}")
        # Print more details for debugging
        import traceback
        console.print(f"Error details: {traceback.format_exc()}")
        state = initial_state
    
    # Save results
    results_dir = Path("results")
    save_results(state, results_dir)
    
    # Show final summary
    console.print(f"\nResearch completed!")
    
    # Remove duplicates for counting
    unique_messages = []
    seen = set()
    for message in state.get('agent_messages', []):
        if message not in seen:
            unique_messages.append(message)
            seen.add(message)
    
    console.print(f"Total agent interactions: {len(unique_messages)}")
    console.print(f"Research entities: {len(state.get('parsed_entities', []))}")
    console.print(f"Analysis results: {len(state.get('analysis_results', {}))}")
    console.print(f"Report length: {len(state.get('final_report', ''))} characters")
    
    # Show agent communication log
    console.print(f"\nAgent Communication Log:")
    for i, message in enumerate(unique_messages, 1):
        console.print(f"  {i}. {message}")
    
    # Show complete agent transfer chain
    show_agent_transfer_chain(unique_messages)


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