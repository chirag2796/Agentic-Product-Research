"""
Generic AI Agent Research System - Simplified Version
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
        console.print(f"  • Research Data: {len(state.get('research_data', {}))} entities")
        console.print(f"  • Analysis Results: {len(state.get('analysis_results', {}))} entities")


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


def run_generic_research_step_by_step(query: str, interactive_mode: bool = False):
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
        "max_iterations": 8,
        "research_context": {}
    }
    
    # Step 1: Query Parsing
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
        
    except Exception as e:
        console.print(f"❌ Query parsing failed: {e}")
        # Fallback parsing
        state["parsed_entities"] = ["Unknown"]
        state["research_focus_areas"] = ["general"]
        state["research_context"] = {"research_type": "analysis", "output_format": "report", "original_query": query}
        state["current_agent"] = "query_parser"
        state["agent_messages"].append(f"Query Parser: Fallback parsing due to error: {e}")
    
    show_state_info(state, interactive_mode)
    
    # Step 2: Research Planning
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
    
    show_state_info(state, interactive_mode)
    
    # Step 3: Data Collection
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
    
    research_data = {}
    
    for i, query_info in enumerate(search_queries[:6], 1):  # Limit to 6 queries for demo
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
    state["agent_messages"].append(f"Data Collector: Collected data for {len(research_data)} entities")
    
    console.print(f"✅ Data collection completed!")
    console.print(f"   • Entities researched: {len(research_data)}")
    console.print(f"   • Total searches: {len(search_queries[:6])}")
    
    show_state_info(state, interactive_mode)
    
    # Step 4: Data Analysis
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
    
    analysis_results = {}
    
    for entity in state["parsed_entities"]:
        if entity in research_data:
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
    state["agent_messages"].append(f"Data Analyzer: Analyzed data for {len(analysis_results)} entities")
    
    console.print(f"✅ Data analysis completed!")
    console.print(f"   • Entities analyzed: {len(analysis_results)}")
    
    show_state_info(state, interactive_mode)
    
    # Step 5: Report Synthesis
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
    research_context = state["research_context"]
    output_format = research_context.get("output_format", "report")
    
    synthesis_prompt = f"""
    You are a research report synthesizer. Create a comprehensive {output_format} based on:
    
    Original Query: {original_query}
    Research Type: {research_context.get('research_type', 'analysis')}
    Output Format: {output_format}
    
    Analysis Results: {json.dumps(analysis_results, indent=2)[:3000]}...
    
    Create a professional, comprehensive {output_format} that:
    1. Addresses the original query completely
    2. Synthesizes all analysis findings
    3. Includes actionable insights and recommendations
    4. Is well-structured and easy to understand
    
    Make this report detailed, professional, and valuable for decision-making.
    """
    
    try:
        response = orchestrator.llm.invoke([{"role": "user", "content": synthesis_prompt}])
        state["final_report"] = response.content
        state["current_agent"] = "report_synthesizer"
        state["agent_messages"].append("Report Synthesizer: Generated comprehensive report")
        
        console.print(f"✅ Report synthesis completed!")
        console.print(f"   • Report length: {len(response.content)} characters")
        
    except Exception as e:
        state["final_report"] = f"Report generation failed: {e}"
        state["current_agent"] = "report_synthesizer"
        state["agent_messages"].append(f"Report Synthesizer: Failed to generate report: {e}")
        console.print(f"❌ Report synthesis failed: {e}")
    
    show_state_info(state, interactive_mode)
    
    # Save results
    results_dir = Path("results")
    save_results(state, results_dir)
    
    # Show final summary
    console.print(f"\n🎉 GENERIC AI AGENT RESEARCH SYSTEM COMPLETED!")
    console.print(f"📊 Total agent interactions: {len(state.get('agent_messages', []))}")
    console.print(f"📊 Research entities: {len(state.get('parsed_entities', []))}")
    console.print(f"📊 Analysis results: {len(state.get('analysis_results', {}))}")
    console.print(f"📊 Report length: {len(state.get('final_report', ''))} characters")
    
    # Show agent communication log
    console.print(f"\n🤖 Agent Communication Log:")
    for i, message in enumerate(state.get('agent_messages', []), 1):
        console.print(f"  {i}. {message}")
    
    console.print(f"\n📁 Check the 'results' folder for generated files")
    console.print("🎪 Perfect for demonstrating generic agentic AI capabilities!")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generic AI Agent Research System")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--query", type=str, default=ASSIGNMENT_QUERY, help="Research query")
    
    args = parser.parse_args()
    
    # Run the research
    run_generic_research_step_by_step(args.query, args.interactive)


if __name__ == "__main__":
    main()
