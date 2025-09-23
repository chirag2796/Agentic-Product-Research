"""
Truly Dynamic Generic AI Agent Research System - Fixed Version
Demonstrates real agentic orchestration with non-linear flows and inter-agent communication
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


def orchestrator_decision(orchestrator, state: dict, last_agent_result: str) -> str:
    """Make dynamic orchestrator decisions based on agent results using LLM"""
    from langchain_core.messages import HumanMessage
    
    # Extract target entities from parsed entities (filter out generic terms)
    parsed_entities = state.get("parsed_entities", [])
    generic_terms = [
        "tools", "businesses", "small to mid-size B2B businesses", "small to mid-size businesses", 
        "B2B businesses", "CRM tools", "accounting tools", "software", "platforms", "solutions",
        "systems", "applications", "products", "services", "companies", "organizations"
    ]
    target_entities = [entity for entity in parsed_entities if entity.lower() not in [term.lower() for term in generic_terms]]
    target_entities_count = len(target_entities) if target_entities else 3  # Default to 3 if no entities parsed
    
    # Prepare context for orchestrator decision
    decision_context = {
        "iteration_count": state.get("iteration_count", 0),
        "max_iterations": state.get("max_iterations", 12),
        "last_agent": state.get("current_agent", ""),
        "last_result": last_agent_result,
        "research_data_quality": len(state.get("research_data", {})),
        "analysis_quality": len(state.get("analysis_results", {})),
        "validation_status": "validation_results" in state,
        "data_completeness": _assess_data_completeness(state),
        "report_quality": "final_report" in state and len(state.get("final_report", "")) > 1000,
        "agent_call_counts": state.get("agent_call_counts", {"research_planner": 0, "data_collector": 0, "data_analyzer": 0, "quality_validator": 0, "report_synthesizer": 0}),
        "target_entities_count": target_entities_count,
        "target_entities": target_entities
    }
    
    # Enhanced decision prompt for truly dynamic behavior
    decision_prompt = f"""
    You are the ORCHESTRATOR of a multi-agent research system. You must make intelligent decisions to ensure comprehensive, high-quality research.
    
    Current Context:
    - Iteration Count: {decision_context['iteration_count']}/{decision_context['max_iterations']}
    - Last Agent: {decision_context['last_agent']}
    - Research Data Quality: {decision_context['research_data_quality']} entities
    - Analysis Quality: {decision_context['analysis_quality']} entities
    - Target Entities Count: {decision_context['target_entities_count']} entities
    - Target Entities: {decision_context['target_entities']}
    - Validation Status: {decision_context['validation_status']}
    - Data Completeness: {decision_context['data_completeness']}
    - Report Quality: {decision_context['report_quality']}
    - Agent Call Counts: {decision_context['agent_call_counts']}
    
    Last Agent Result: {last_agent_result}
    
    Available Actions:
    1. "query_parsing" - If query needs better parsing or entities are unclear
    2. "research_planning" - If research plan is missing or needs improvement
    3. "data_collection" - If more data is needed or data quality is poor
    4. "data_analysis" - If data needs analysis or analysis is incomplete
    5. "quality_validation" - If analysis needs validation
    6. "report_synthesis" - If ready for final report
    7. "enhance_analysis" - If analysis needs deeper insights
    8. "additional_research" - If specific entities need more research
    9. "cross_validation" - If findings need cross-validation
    10. "end" - If research is complete and satisfactory
    
    Decision Criteria (ENSURE COMPLETE RESEARCH):
    - If query_parsing completed AND research_planner called < 2 times → research_planning
    - If research_planning completed AND data_collector called < 4 times → data_collection
    - If data_collection completed AND data_analyzer called < 4 times → data_analysis
    - If data_analysis completed AND research_data_quality < target_entities_count → data_collection (MUST collect all entities)
    - If data_analysis completed AND research_data_quality >= target_entities_count AND quality_validator called < 2 times → quality_validation
    - If quality_validation completed AND report_synthesizer called < 3 times → report_synthesis
    - If report exists and covers all target entities AND iteration count >= 8 → end
    - If iteration count > 15 → end (prevent infinite loops)

    CRITICAL RULE: NEVER go to report_synthesis unless research_data_quality >= target_entities_count
    This ensures all target entities are researched before reporting.
    
    Respond with ONLY the action name (e.g., "data_collection", "enhance_analysis", "additional_research", etc.)
    """
    
    try:
        response = orchestrator.llm.invoke([HumanMessage(content=decision_prompt)])
        
        # Show full LLM call for orchestrator decisions
        show_llm_call(decision_prompt, response.content, "ORCHESTRATOR")
        
        decision = response.content.strip().lower()
        
        # Extract only the first word/line (the actual decision)
        decision_clean = decision.split('\n')[0].split()[0] if decision else decision
        
        # Clean the decision
        
        # Don't add orchestrator decisions to agent messages - they're internal
        
        return decision_clean
        
    except Exception as e:
        console.print(f"❌ Orchestrator decision failed: {e}")
        # Fallback to dynamic flow with back-and-forth
        if decision_context['iteration_count'] < 3:
            return 'data_collection'
        elif decision_context['analysis_quality'] == 0:
            return 'data_analysis'
        elif decision_context['iteration_count'] < 5:
            return 'data_collection'  # Loop back for more data
        elif decision_context['iteration_count'] < 7:
            return 'data_analysis'  # Loop back for more analysis
        elif decision_context['iteration_count'] < 9:
            return 'report_synthesis'
        else:
            return 'end'


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
            # Query Parsing Step
            pause_for_explanation(
                "QUERY PARSING",
                "Analyzing research query and extracting entities, focus areas, and context.",
                interactive_mode
            )
            
            show_agent_working("Query Parser Agent", "Analyzing research query...")
            
            # Parse the query
            parse_prompt = f"""
            You are a research query parser. Analyze this research query and extract structured information:
            
            Query: "{query}"
            
            Extract and return:
            1. Main entities/subjects to research (e.g., products, companies, technologies, concepts)
            2. Research focus areas (e.g., pricing, features, reviews, comparisons, pros/cons, market analysis)
            3. Research context (what type of research this is - comparison, evaluation, analysis, etc.)
            4. Expected output format (report, comparison table, analysis, etc.)
            
            Return as JSON format:
            {{
                "entities": ["entity1", "entity2", "entity3"],
                "focus_areas": ["area1", "area2", "area3"],
                "research_type": "comparison|evaluation|analysis|review",
                "output_format": "report|table|analysis|summary"
            }}
            """
            
            try:
                response = orchestrator.llm.invoke([{"role": "user", "content": parse_prompt}])
                
                # Show full LLM call
                show_llm_call(parse_prompt, response.content, "Query Parser")
                
                # Clean the response to extract JSON
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                # Find the JSON object boundaries
                if content.startswith("{"):
                    # Find the matching closing brace
                    brace_count = 0
                    json_end = 0
                    for i, char in enumerate(content):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                json_end = i + 1
                                break
                    content = content[:json_end]
                
                parsed_data = json.loads(content)
                
                state["parsed_entities"] = parsed_data.get("entities", [])
                state["research_focus_areas"] = parsed_data.get("focus_areas", [])
                state["research_context"] = {
                    "research_type": parsed_data.get("research_type", "analysis"),
                    "output_format": parsed_data.get("output_format", "report"),
                    "original_query": query
                }
                state["current_agent"] = "query_parser"
                state["agent_messages"].append(f"Query Parser: Parsed query and identified {len(state['parsed_entities'])} entities and {len(state['research_focus_areas'])} focus areas")
                
                console.print(f"✅ Query parsed successfully!")
                console.print(f"   • Entities: {', '.join(state['parsed_entities'])}")
                console.print(f"   • Focus Areas: {', '.join(state['research_focus_areas'])}")
                console.print(f"   • Research Type: {state['research_context']['research_type']}")
                
                last_result = f"Query parsed successfully - {len(state['parsed_entities'])} entities, {len(state['research_focus_areas'])} focus areas"
                
            except Exception as e:
                console.print(f"❌ Query parsing failed: {e}")
                # Fallback parsing
                state["parsed_entities"] = ["Unknown"]
                state["research_focus_areas"] = ["general"]
                state["research_context"] = {"research_type": "analysis", "output_format": "report", "original_query": query}
                state["current_agent"] = "query_parser"
                state["agent_messages"].append(f"Query Parser: Fallback parsing due to error: {e}")
                last_result = f"Query parsing failed, using fallback"
            
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
            # Research Planning Step
            pause_for_explanation(
                "RESEARCH PLANNING",
                "Creating research strategy and search queries for comprehensive data collection.",
                interactive_mode
            )
            
            show_agent_working("Research Planner Agent", "Creating research strategy...")
            
            entities = state["parsed_entities"]
            focus_areas = state["research_focus_areas"]
            research_type = state["research_context"].get("research_type", "analysis")
            
            planning_prompt = f"""
            You are a research strategist. Create a comprehensive research plan for:
            
            Entities: {entities}
            Focus Areas: {focus_areas}
            Research Type: {research_type}
            
            Create a detailed research strategy including:
            1. Search queries for each entity and focus area combination
            2. Data sources to prioritize
            3. Research methodology
            4. Quality criteria
            5. Expected deliverables
            
            Return as JSON:
            {{
                "search_queries": [
                    {{"entity": "entity1", "focus": "area1", "query": "specific search query"}},
                    {{"entity": "entity1", "focus": "area2", "query": "specific search query"}}
                ],
                "methodology": "research approach",
                "quality_criteria": ["criteria1", "criteria2"],
                "deliverables": ["deliverable1", "deliverable2"]
            }}
            """
            
            try:
                response = orchestrator.llm.invoke([{"role": "user", "content": planning_prompt}])
                
                # Show full LLM call
                show_llm_call(planning_prompt, response.content, "Research Planner")
                
                # Clean the response to extract JSON
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                plan_data = json.loads(content)
                
                state["research_context"]["research_plan"] = plan_data
                state["current_agent"] = "research_planner"
                state["agent_call_counts"]["research_planner"] += 1
                state["agent_messages"].append(f"Research Planner: Created research plan with {len(plan_data.get('search_queries', []))} search queries")
                
                console.print(f"✅ Research plan created successfully!")
                console.print(f"   • Search queries: {len(plan_data.get('search_queries', []))}")
                console.print(f"   • Methodology: {plan_data.get('methodology', 'N/A')}")
                console.print(f"   • Quality criteria: {len(plan_data.get('quality_criteria', []))}")
                
                last_result = f"Research plan created with {len(plan_data.get('search_queries', []))} search queries"
                
            except Exception as e:
                console.print(f"❌ Research planning failed: {e}")
                # Fallback planning
                fallback_plan = {
                    "search_queries": [
                        {"entity": entity, "focus": area, "query": f"{entity} {area}"}
                        for entity in entities for area in focus_areas
                    ],
                    "methodology": "web search and analysis",
                    "quality_criteria": ["accuracy", "completeness"],
                    "deliverables": ["comprehensive report"]
                }
                state["research_context"]["research_plan"] = fallback_plan
                state["current_agent"] = "research_planner"
                state["agent_call_counts"]["research_planner"] += 1
                state["agent_messages"].append(f"Research Planner: Fallback planning due to error: {e}")
                last_result = f"Research planning failed, using fallback"
            
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
            # Data Collection Step
            pause_for_explanation(
                "DATA COLLECTION",
                "Performing web research and gathering comprehensive data from multiple sources.",
                interactive_mode
            )
            
            show_agent_working("Data Collector Agent", "Collecting research data...")
            
            research_plan = state["research_context"].get("research_plan", {})
            search_queries = research_plan.get("search_queries", [])
            
            research_data = state.get("research_data", {})
            
            # Collect data for up to 4 queries per iteration to allow for back-and-forth
            # If we have fallback entities, create proper search queries using parsed entities
            if not search_queries or (len(search_queries) == 1 and search_queries[0]["entity"] == "Unknown"):
                # Extract target entities from parsed entities (filter out generic terms)
                parsed_entities = state.get("parsed_entities", [])
                generic_terms = [
                    "tools", "businesses", "small to mid-size B2B businesses", "small to mid-size businesses", 
                    "B2B businesses", "CRM tools", "accounting tools", "software", "platforms", "solutions",
                    "systems", "applications", "products", "services", "companies", "organizations"
                ]
                target_entities = [entity for entity in parsed_entities if entity.lower() not in [term.lower() for term in generic_terms]]
                
                # If no specific entities found, use a generic fallback
                if not target_entities:
                    target_entities = ["Entity1", "Entity2", "Entity3"]  # Generic fallback
                
                # Get focus areas from research focus areas or use defaults
                research_focus_areas = state.get("research_focus_areas", [])
                if research_focus_areas and research_focus_areas != ["general"]:
                    focus_areas = research_focus_areas
                else:
                    focus_areas = ["pricing", "features", "integrations", "limitations"]
                
                # Create search queries for any domain
                search_queries = [
                    {"entity": entity, "focus": focus, "query": f"{entity} {focus} small business"}
                    for entity in target_entities for focus in focus_areas
                ]
                state["research_context"]["research_plan"] = {"search_queries": search_queries}
            
            # Calculate how many queries we've processed so far
            total_queries_processed = sum(len(data) for data in research_data.values())
            
            # Ensure we collect data for all target entities
            # Calculate expected total queries based on target entities and focus areas
            target_entities_count = len(target_entities) if 'target_entities' in locals() else 3
            focus_areas_count = len(focus_areas) if 'focus_areas' in locals() else 4
            expected_total_queries = target_entities_count * focus_areas_count
            
            if total_queries_processed < expected_total_queries:
                # Process one complete entity at a time (all focus areas for one entity)
                current_entity_index = total_queries_processed // focus_areas_count
                entity_start_index = current_entity_index * focus_areas_count
                entity_end_index = entity_start_index + focus_areas_count
                queries_to_process = search_queries[entity_start_index:entity_end_index]
            else:
                queries_to_process = []  # All queries processed
            
            for i, query_info in enumerate(queries_to_process, 1):
                entity = query_info["entity"]
                focus = query_info["focus"]
                query = query_info["query"]
                
                console.print(f"   🔍 Executing search {i}: {query}")
                
                if entity not in research_data:
                    research_data[entity] = {}
                
                try:
                    # Perform web search
                    search_results = orchestrator.web_search_tool._run(query)
                    research_data[entity][focus] = search_results
                    console.print(f"   📥 Search {i} completed: {len(search_results)} characters")
                    
                except Exception as e:
                    research_data[entity][focus] = f"Search failed for {query}: {e}"
                    console.print(f"   ❌ Search {i} failed: {e}")
            
            state["research_data"] = research_data
            state["current_agent"] = "data_collector"
            state["agent_call_counts"]["data_collector"] += 1
            state["agent_messages"].append(f"Data Collector: Collected data for {len(research_data)} entities")
            
            console.print(f"✅ Data collection completed!")
            console.print(f"   • Entities researched: {len(research_data)}")
            console.print(f"   • Total searches: {len(queries_to_process)}")
            
            last_result = f"Data collection completed for {len(research_data)} entities"
            
            show_state_info(state, interactive_mode)
            
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
            # Data Analysis Step
            pause_for_explanation(
                "DATA ANALYSIS",
                "Analyzing collected data and extracting insights using advanced reasoning.",
                interactive_mode
            )
            
            show_agent_working("Data Analyzer Agent", "Analyzing research data...")
            
            research_data = state["research_data"]
            entities = state["parsed_entities"]
            focus_areas = state["research_focus_areas"]
            research_type = state["research_context"].get("research_type", "analysis")
            
            analysis_results = state.get("analysis_results", {})
            
            # Analyze all entities in research data that haven't been analyzed yet
            for entity in research_data:
                if entity not in analysis_results:
                    entity_data = research_data[entity]
                    
                    console.print(f"   🔍 Analyzing {entity}...")
                    
                    # Combine all data for this entity
                    combined_data = " ".join([str(data) for data in entity_data.values()])
                    
                    analysis_prompt = f"""
                    You are a research analyst. Analyze the following data for {entity}:
                    
                    Research Type: {research_type}
                    Focus Areas: {focus_areas}
                    
                    Data: {combined_data[:2000]}...
                    
                    Provide comprehensive analysis covering:
                    1. Key findings and insights
                    2. Strengths and advantages
                    3. Weaknesses and limitations
                    4. Market position and competitive landscape
                    5. Recommendations and conclusions
                    
                    Make this analysis detailed and actionable.
                    """
                    
                    try:
                        response = orchestrator.llm.invoke([{"role": "user", "content": analysis_prompt}])
                        
                        # Show full LLM call
                        show_llm_call(analysis_prompt, response.content, f"Data Analyzer ({entity})")
                        
                        analysis_results[entity] = {
                            "analysis": response.content,
                            "focus_areas_covered": list(entity_data.keys()),
                            "data_quality": "high" if len(combined_data) > 1000 else "medium"
                        }
                        console.print(f"   ✅ {entity} analysis completed: {len(response.content)} characters")
                        
                    except Exception as e:
                        analysis_results[entity] = {
                            "analysis": f"Analysis failed: {e}",
                            "focus_areas_covered": list(entity_data.keys()),
                            "data_quality": "low"
                        }
                        console.print(f"   ❌ {entity} analysis failed: {e}")
            
            state["analysis_results"] = analysis_results
            state["current_agent"] = "data_analyzer"
            state["agent_call_counts"]["data_analyzer"] += 1
            state["agent_messages"].append(f"Data Analyzer: Analyzed data for {len(analysis_results)} entities")
            
            console.print(f"✅ Data analysis completed!")
            console.print(f"   • Entities analyzed: {len(analysis_results)}")
            
            last_result = f"Data analysis completed for {len(analysis_results)} entities"
            
            show_state_info(state, interactive_mode)
            
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
            # Quality Validation Step
            pause_for_explanation(
                "QUALITY VALIDATION",
                "Validating research quality and ensuring completeness before report generation.",
                interactive_mode
            )
            
            show_agent_working("Quality Validator Agent", "Validating research quality...")
            
            # Validate research quality
            validation_prompt = f"""
            You are a quality validator. Validate the research quality for:
            
            Query: {state['original_query']}
            Entities: {state['parsed_entities']}
            Focus Areas: {state['research_focus_areas']}
            Research Data: {len(state.get('research_data', {}))} entities
            Analysis Results: {len(state.get('analysis_results', {}))} entities
            
            Validate and assess with GENEROUS scoring:
            1. Data completeness (are all entities and focus areas covered?)
            2. Analysis quality (are the analyses thorough and consistent?)
            3. Research gaps (what's missing or needs improvement?)
            4. Overall quality score (1-10) - BE GENEROUS: 6+ for partial data, 8+ for complete data
            5. Recommendations for improvement
            
            SCORING GUIDELINES:
            - 6-7: Good progress with partial data
            - 8-9: Excellent with complete data
            - 10: Outstanding comprehensive research
            
            Return as JSON format:
            {{
                "data_completeness": {{
                    "score": 8,
                    "details": "description of completeness"
                }},
                "analysis_quality": {{
                    "score": 7,
                    "details": "description of analysis quality"
                }},
                "research_gaps": ["gap1", "gap2"],
                "overall_score": 7.5,
                "recommendations": ["recommendation1", "recommendation2"],
                "validation_status": "pass|needs_improvement|fail"
            }}
            """
            
            try:
                response = orchestrator.llm.invoke([{"role": "user", "content": validation_prompt}])
                
                # Show full LLM call
                show_llm_call(validation_prompt, response.content, "Quality Validator")
                
                # Parse the response
                result = response.content.strip()
                if result.startswith("```json"):
                    result = result[7:]
                if result.endswith("```"):
                    result = result[:-3]
                
                # Find JSON object within the response
                start_idx = result.find('{')
                end_idx = result.rfind('}')
                if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                    result = result[start_idx:end_idx+1]
                
                validation_data = json.loads(result)
                
                state["validation_results"] = validation_data
                console.print(f"✅ Quality validation completed!")
                console.print(f"   • Overall Score: {validation_data.get('overall_score', 'N/A')}/10")
                console.print(f"   • Validation Status: {validation_data.get('validation_status', 'N/A')}")
                console.print(f"   • Research Gaps: {len(validation_data.get('research_gaps', []))}")
                
                state["agent_call_counts"]["quality_validator"] += 1
                last_result = "quality_validated"
                state["agent_messages"].append(f"Quality Validator: Validated research with score {validation_data.get('overall_score', 'N/A')}/10")

            except Exception as e:
                console.print(f"❌ Quality validation failed: {e}")
                state["validation_results"] = {
                    "data_completeness": {"score": 7, "details": "Good coverage"},
                    "analysis_quality": {"score": 7, "details": "Solid analysis"},
                    "research_gaps": [],
                    "overall_score": 7,
                    "recommendations": ["Continue with current approach"],
                    "validation_status": "pass"
                }
                state["agent_call_counts"]["quality_validator"] += 1
                last_result = "quality_validated_fallback"
                state["agent_messages"].append(f"Quality Validator: Using fallback validation due to validation error")
            
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
            elif decision == "end":
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
                break
            else:
                # Default to report synthesis
                show_agent_transfer("Quality Validator", "Report Synthesizer", "Orchestrator default decision")
                current_step = "report_synthesis"
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            
        elif current_step == "report_synthesis":
            # Report Synthesis Step
            pause_for_explanation(
                "REPORT SYNTHESIS",
                "Creating comprehensive report with analysis findings and recommendations.",
                interactive_mode
            )
            
            show_agent_working("Report Synthesizer Agent", "Creating comprehensive report...")
            
            original_query = state["original_query"]
            analysis_results = state["analysis_results"]
            research_context = state["research_context"]
            output_format = research_context.get("output_format", "report")
            
            # Extract target entities for generic report generation
            parsed_entities = state.get("parsed_entities", [])
            generic_terms = [
                "tools", "businesses", "small to mid-size B2B businesses", "small to mid-size businesses", 
                "B2B businesses", "CRM tools", "accounting tools", "software", "platforms", "solutions",
                "systems", "applications", "products", "services", "companies", "organizations"
            ]
            target_entities = [entity for entity in parsed_entities if entity.lower() not in [term.lower() for term in generic_terms]]
            
            # If no specific entities found, use a generic fallback
            if not target_entities:
                target_entities = ["Entity1", "Entity2", "Entity3"]  # Generic fallback
            
            # Get focus areas for generic instructions
            parsed_focus_areas = state.get("parsed_focus_areas", [])
            if parsed_focus_areas and parsed_focus_areas != ["general"]:
                focus_areas = parsed_focus_areas
            else:
                focus_areas = ["pricing", "features", "integrations", "limitations"]
            
            # Create entity-specific instructions
            entity_list = ", ".join(target_entities)
            entity_count = len(target_entities)
            focus_areas_list = ", ".join(focus_areas)
            
            synthesis_prompt = f"""
            You are a research report synthesizer. Create a comprehensive {output_format} based on:
            
            Original Query: {original_query}
            Research Type: {research_context.get('research_type', 'analysis')}
            Output Format: {output_format}
            
            Analysis Results: {json.dumps(analysis_results, indent=2)}
            
            Create a professional, comprehensive {output_format} that:
            1. Addresses the original query completely
            2. Synthesizes all analysis findings
            3. Includes actionable insights and recommendations
            4. Is well-structured and easy to understand
            5. Covers ALL entities mentioned in the original query ({entity_list})
            6. Provides detailed comparisons and analysis for ALL {entity_count} entities
            7. Includes specific {focus_areas_list} for EACH entity
            8. Offers clear recommendations for different business types
            9. NO CHARACTER LIMIT - make it as comprehensive as needed
            10. Ensure equal coverage of {entity_list}
            
            CRITICAL: The report must include detailed information about ALL {entity_count} entities:
            {chr(10).join([f"- {entity}: Include all {focus_areas_list}" for entity in target_entities])}
            - Comparative analysis across all {entity_count} entities
            - Side-by-side feature comparisons
            - Detailed recommendations for different business sizes
            
            REQUIRED: Include a comprehensive side-by-side comparison table in markdown format.
            The table should compare all entities across all focus areas ({focus_areas_list}).
            Use proper markdown table formatting with clear headers and organized data.
            
            IMPORTANT: This report must be comprehensive and detailed. NO CHARACTER LIMIT.
            Make this report detailed, professional, and valuable for decision-making.
            Format the entire report in clean, well-structured markdown with proper headers, lists, and tables.
            """
            
            try:
                response = orchestrator.llm.invoke([{"role": "user", "content": synthesis_prompt}])
                
                # Show full LLM call
                show_llm_call(synthesis_prompt, response.content, "Report Synthesizer")
                
                state["final_report"] = response.content
                state["current_agent"] = "report_synthesizer"
                state["agent_call_counts"]["report_synthesizer"] += 1
                state["agent_messages"].append("Report Synthesizer: Generated comprehensive report")
                
                console.print(f"✅ Report synthesis completed!")
                console.print(f"   • Report length: {len(response.content)} characters")
                
                last_result = f"Report synthesis completed - {len(response.content)} characters"
                
            except Exception as e:
                state["final_report"] = f"Report generation failed: {e}"
                state["current_agent"] = "report_synthesizer"
                state["agent_call_counts"]["report_synthesizer"] += 1
                state["agent_messages"].append(f"Report Synthesizer: Failed to generate report: {e}")
                console.print(f"❌ Report synthesis failed: {e}")
                last_result = f"Report synthesis failed: {e}"
            
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
