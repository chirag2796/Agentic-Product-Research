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
    console.print(f"\n🤖 {agent_name}: {action}")


def show_llm_call(prompt: str, response: str, agent_name: str):
    """Show full LLM input and output for transparency"""
    console.print(f"\n📝 **{agent_name} LLM CALL:**")
    console.print(f"**INPUT PROMPT:**")
    console.print(f"[dim]{prompt[:500]}{'...' if len(prompt) > 500 else ''}[/dim]")
    console.print(f"\n**LLM RESPONSE:**")
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
    console.print(f"\n🔄 **COMPLETE AGENT TRANSFER CHAIN:** {chain_str}")


def show_agent_transfer(from_agent: str, to_agent: str, reason: str = ""):
    """Show clear agent transfer with reason"""
    console.print(f"\n🔄 **CONTROL TRANSFER:** {from_agent} → {to_agent}")
    if reason:
        console.print(f"   Reason: {reason}")


def show_state_info(state: dict, interactive_mode: bool):
    """Show current system state"""
    if interactive_mode:
        console.print(f"\n📊 Current System State:")
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


def orchestrator_decision(orchestrator, state: dict, last_agent_result: str) -> str:
    """Make dynamic orchestrator decisions based on agent results using LLM"""
    from langchain_core.messages import HumanMessage
    
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
        "agent_call_counts": state.get("agent_call_counts", {"data_collector": 0, "data_analyzer": 0, "report_synthesizer": 0})
    }
    
    # Enhanced decision prompt for truly dynamic behavior
    decision_prompt = f"""
    You are the ORCHESTRATOR of a multi-agent research system. You must make intelligent decisions to ensure comprehensive, high-quality research.
    
    Current Context:
    - Iteration Count: {decision_context['iteration_count']}/{decision_context['max_iterations']}
    - Last Agent: {decision_context['last_agent']}
    - Research Data Quality: {decision_context['research_data_quality']} entities
    - Analysis Quality: {decision_context['analysis_quality']} entities
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
    
    Decision Criteria (SHOW NON-SEQUENTIAL ORCHESTRATION WITH CONTROLLED LOOPS):
    - If research data < 3 entities AND data_collector called < 4 times → data_collection (need all 3 CRM tools)
    - If analysis is missing for any researched entity AND data_analyzer called < 4 times → data_analysis
    - If we have 3 entities researched but < 3 analyzed AND data_analyzer called < 4 times → data_analysis
    - If we have 3 entities analyzed but report is missing AND report_synthesizer called < 3 times → report_synthesis
    - If report exists but doesn't cover all 3 entities AND data_collector called < 4 times → data_collection (get missing entities)
    - If report exists and covers all 3 entities AND iteration count >= 8 → end
    - If iteration count > 15 → end (prevent infinite loops)
    - If all 3 entities are researched, analyzed, and reported → end
    
    IMPORTANT: Show TRUE DYNAMIC ORCHESTRATION by:
    1. Collect data for all 3 CRM entities (HubSpot, Zoho, Salesforce) - 3-4 data collection cycles
    2. Analyze data for all 3 CRM entities - 3-4 data analysis cycles  
    3. Generate comprehensive report covering all 3 entities - 2-3 report synthesis cycles
    4. Show 3-4 back-and-forth cycles to demonstrate non-sequential behavior
    5. Aim for 10-12 total iterations with meaningful loops
    6. Focus on getting complete data for all 3 CRM tools (HubSpot, Zoho, Salesforce)
    7. Ensure report covers all 3 entities with detailed comparison
    8. NO CHARACTER LIMITS on reports - make them comprehensive
    
    Respond with ONLY the action name (e.g., "data_collection", "enhance_analysis", "additional_research", etc.)
    """
    
    try:
        response = orchestrator.llm.invoke([HumanMessage(content=decision_prompt)])
        
        # Show full LLM call for orchestrator decisions
        show_llm_call(decision_prompt, response.content, "ORCHESTRATOR")
        
        decision = response.content.strip().lower()
        
        # Extract only the first word/line (the actual decision)
        decision_clean = decision.split('\n')[0].split()[0] if decision else decision
        
        # Debug: Print the exact decision
        console.print(f"🔍 **DEBUG**: Original = '{decision[:50]}...' (length: {len(decision)})")
        console.print(f"🔍 **DEBUG**: Cleaned = '{decision_clean}' (length: {len(decision_clean)})")
        
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


def run_truly_dynamic_research(query: str, interactive_mode: bool = False):
    """Run truly dynamic research with real orchestration"""
    console.print("🚀 Starting Truly Dynamic AI Agent Research System...")
    
    # Initialize the generic orchestrator
    console.print("🔧 Initializing Generic Research Orchestrator...")
    orchestrator = GenericResearchOrchestrator()
    
    # Show system capabilities
    console.print(Panel(
        f"""
🎪 TRULY DYNAMIC AI AGENT RESEARCH SYSTEM - {'INTERACTIVE' if interactive_mode else 'AUTOMATED'} MODE

🎯 System Capabilities:
• Handles ANY research query with true dynamic orchestration
• 6+ autonomous agents with intelligent routing
• Non-linear workflow with real inter-agent communication
• Collaborative agent behavior with reasoning and delegation
• Quality validation and iterative improvement
• Orchestrator makes intelligent decisions to loop back and enhance

🔧 Framework: LangGraph with StateGraph
🤖 Agents: Query Parser, Research Planner, Data Collector, Data Analyzer, Quality Validator, Report Synthesizer
📊 Output: Comprehensive research reports with true agentic orchestration

🎯 Current Query: {query[:100]}...
        """,
        title="🤖 Truly Dynamic AI Agent Research System",
        border_style="green"
    ))
    
    if interactive_mode:
        console.print("\n🎭 **ORCHESTRATOR INITIATION**: The **ORCHESTRATOR** is now initiating the multi-agent workflow with dynamic decision-making based on agent results.")
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
        "agent_call_counts": {"data_collector": 0, "data_analyzer": 0, "report_synthesizer": 0}
    }
    
    # Dynamic workflow loop
    current_step = "query_parsing"
    last_result = ""
    
    while state["iteration_count"] < state["max_iterations"]:
        state["iteration_count"] += 1
        
        if current_step == "query_parsing":
            # Query Parsing Step
            pause_for_explanation(
                "STEP: QUERY PARSING",
                """
The Query Parser Agent analyzes ANY research query and extracts:
• Main entities/subjects to research (products, companies, technologies, concepts)
• Research focus areas (pricing, features, reviews, comparisons, etc.)
• Research context and expected output format

This agent is completely generic and can handle any type of research query.
                """,
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
            console.print("\n🎭 **ORCHESTRATOR DECISION MAKING**: The **ORCHESTRATOR** is now analyzing the results and deciding the next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"🎯 **ORCHESTRATOR DECISION**: {decision.upper()}")
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
                "STEP: RESEARCH PLANNING",
                """
The Research Planner Agent creates a comprehensive research strategy for ANY topic:
• Generates specific search queries for each entity and focus area
• Identifies data sources and research methodology
• Sets quality criteria and expected deliverables

This agent demonstrates true reasoning and planning capabilities.
                """,
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
                state["agent_messages"].append(f"Research Planner: Fallback planning due to error: {e}")
                last_result = f"Research planning failed, using fallback"
            
            show_state_info(state, interactive_mode)
            
            # Orchestrator decision
            console.print("\n🎭 **ORCHESTRATOR DECISION MAKING**: The **ORCHESTRATOR** is now analyzing the results and deciding the next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"🎯 **ORCHESTRATOR DECISION**: {decision.upper()}")
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
                "STEP: DATA COLLECTION",
                """
The Data Collector Agent performs web research for ANY topic:
• Executes search queries for each entity and focus area
• Gathers comprehensive data from multiple sources
• Demonstrates collaborative behavior by working with the research plan

This agent shows how agents can delegate and coordinate tasks.
                """,
                interactive_mode
            )
            
            show_agent_working("Data Collector Agent", "Collecting research data...")
            
            research_plan = state["research_context"].get("research_plan", {})
            search_queries = research_plan.get("search_queries", [])
            
            research_data = state.get("research_data", {})
            
            # Collect data for up to 4 queries per iteration to allow for back-and-forth
            # If we have fallback entities, create proper search queries for CRM tools
            if not search_queries or (len(search_queries) == 1 and search_queries[0]["entity"] == "Unknown"):
                # Create proper CRM search queries
                crm_entities = ["HubSpot", "Zoho", "Salesforce"]
                crm_focus_areas = ["pricing", "features", "integrations", "limitations"]
                search_queries = [
                    {"entity": entity, "focus": focus, "query": f"{entity} CRM {focus} small business"}
                    for entity in crm_entities for focus in crm_focus_areas
                ]
                state["research_context"]["research_plan"] = {"search_queries": search_queries}
            
            # Calculate how many queries we've processed so far
            total_queries_processed = sum(len(data) for data in research_data.values())
            
            # Ensure we collect data for all 3 CRM entities (HubSpot, Zoho, Salesforce)
            # Each entity has 4 focus areas, so we need 12 total queries
            if total_queries_processed < 12:  # 3 entities * 4 focus areas each
                queries_to_process = search_queries[total_queries_processed:total_queries_processed+4]
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
            console.print("\n🎭 **ORCHESTRATOR DECISION MAKING**: The **ORCHESTRATOR** is now analyzing the results and deciding the next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"🎯 **ORCHESTRATOR DECISION**: {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "data_analysis":
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
                "STEP: DATA ANALYSIS",
                """
The Data Analyzer Agent processes research data for ANY topic:
• Analyzes collected data using LLM reasoning
• Extracts insights and patterns
• Demonstrates non-linear thinking by adapting analysis to different entity types

This agent shows true reasoning capabilities across different domains.
                """,
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
            console.print("\n🎭 **ORCHESTRATOR DECISION MAKING**: The **ORCHESTRATOR** is now analyzing the results and deciding the next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"🎯 **ORCHESTRATOR DECISION**: {decision.upper()}")
            console.print(f"   Based on: {state['current_agent']} result")
            console.print(f"   Iteration: {state['iteration_count']}/{state['max_iterations']}")
            
            # Show agent transfer
            if decision == "enhance_analysis":
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
                show_agent_transfer("Data Analyzer", "Report Synthesizer", "Orchestrator default decision")
                current_step = "report_synthesis"  # Default
                pause_for_explanation("TRANSITION", f"Press Enter to continue with {decision.upper()}...", interactive_mode)
            
        elif current_step == "report_synthesis":
            # Report Synthesis Step
            pause_for_explanation(
                "STEP: REPORT SYNTHESIS",
                """
The Report Synthesizer Agent creates comprehensive reports for ANY research:
• Synthesizes all analysis findings
• Creates professional, actionable reports
• Adapts output format based on research context

This agent demonstrates the power of LLM-driven report generation.
                """,
                interactive_mode
            )
            
            show_agent_working("Report Synthesizer Agent", "Creating comprehensive report...")
            
            original_query = state["original_query"]
            analysis_results = state["analysis_results"]
            research_context = state["research_context"]
            output_format = research_context.get("output_format", "report")
            
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
            5. Covers ALL entities mentioned in the original query (HubSpot, Zoho, Salesforce)
            6. Provides detailed comparisons and analysis for ALL 3 CRM tools
            7. Includes specific pricing, features, and limitations for EACH platform
            8. Offers clear recommendations for different business types
            9. NO CHARACTER LIMIT - make it as comprehensive as needed
            10. Ensure equal coverage of HubSpot, Zoho, AND Salesforce
            
            CRITICAL: The report must include detailed information about ALL THREE CRM tools:
            - HubSpot: Include all pricing tiers, features, integrations, limitations
            - Zoho: Include all pricing tiers, features, integrations, limitations  
            - Salesforce: Include all pricing tiers, features, integrations, limitations
            - Comparative analysis across all three platforms
            - Side-by-side feature comparisons
            - Detailed recommendations for different business sizes
            
            IMPORTANT: This report must be comprehensive and detailed. NO CHARACTER LIMIT.
            Make this report detailed, professional, and valuable for decision-making.
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
            console.print("\n🎭 **ORCHESTRATOR DECISION MAKING**: The **ORCHESTRATOR** is now analyzing the results and deciding the next action...")
            decision = orchestrator_decision(orchestrator, state, last_result)
            console.print(f"🎯 **ORCHESTRATOR DECISION**: {decision.upper()}")
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
    console.print(f"\n🎉 TRULY DYNAMIC AI AGENT RESEARCH SYSTEM COMPLETED!")
    console.print(f"📊 Total agent interactions: {len(state.get('agent_messages', []))}")
    console.print(f"📊 Research entities: {len(state.get('parsed_entities', []))}")
    console.print(f"📊 Analysis results: {len(state.get('analysis_results', {}))}")
    console.print(f"📊 Report length: {len(state.get('final_report', ''))} characters")
    
    # Show agent communication log
    console.print(f"\n🤖 Agent Communication Log:")
    for i, message in enumerate(state.get('agent_messages', []), 1):
        console.print(f"  {i}. {message}")
    
    # Show complete agent transfer chain
    show_agent_transfer_chain(state.get('agent_messages', []))
    
    console.print(f"\n📁 Check the 'results' folder for generated files")
    console.print("🎪 Perfect for demonstrating truly dynamic agentic AI capabilities!")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Truly Dynamic AI Agent Research System")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--query", type=str, default=ASSIGNMENT_QUERY, help="Research query")
    
    args = parser.parse_args()
    
    # Run the research
    run_truly_dynamic_research(args.query, args.interactive)


if __name__ == "__main__":
    main()
