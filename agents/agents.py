import json
from typing import Dict, Any
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from tools.web_search_tool import WebSearchTool
from config import OPENROUTER_BASE_URL, OPENROUTER_MODEL, OPENROUTER_API_KEY


class GenericResearchOrchestrator:
    """Research orchestrator that provides LLM and web search capabilities"""
    
    def __init__(self):
        # Initialize LLM using config
        self.llm = ChatOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
            model=OPENROUTER_MODEL,
            temperature=0.1
        )
        
        # Initialize web search tool
        self.web_search_tool = WebSearchTool()


class GenericAgentState:
    """Generic agent state class for compatibility"""
    pass


class QueryParserAgent:
    """Query Parser Agent - extracts entities and focus areas from research queries"""
    
    def __init__(self, orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation):
        self.orchestrator = orchestrator
        self.console = console
        self.show_agent_working = show_agent_working
        self.show_llm_call = show_llm_call
        self.pause_for_explanation = pause_for_explanation
    
    def execute(self, query: str, state: dict, interactive_mode: bool):
        """Execute query parsing - EXACT same code from main.py"""
        # Query Parsing Step
        self.pause_for_explanation(
            "QUERY PARSING",
            "Analyzing research query and extracting entities, focus areas, and context.",
            interactive_mode
        )
        
        self.show_agent_working("Query Parser Agent", "Analyzing research query...")
        
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
            response = self.orchestrator.llm.invoke([{"role": "user", "content": parse_prompt}])
            
            # Show full LLM call
            self.show_llm_call(parse_prompt, response.content, "Query Parser")
            
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
            
            self.console.print(f"✅ Query parsed successfully!")
            self.console.print(f"   • Entities: {', '.join(state['parsed_entities'])}")
            self.console.print(f"   • Focus Areas: {', '.join(state['research_focus_areas'])}")
            self.console.print(f"   • Research Type: {state['research_context']['research_type']}")
            
            last_result = f"Query parsed successfully - {len(state['parsed_entities'])} entities, {len(state['research_focus_areas'])} focus areas"
            
        except Exception as e:
            self.console.print(f"❌ Query parsing failed: {e}")
            # Fallback parsing
            state["parsed_entities"] = ["Unknown"]
            state["research_focus_areas"] = ["general"]
            state["research_context"] = {"research_type": "analysis", "output_format": "report", "original_query": query}
            state["current_agent"] = "query_parser"
            state["agent_messages"].append(f"Query Parser: Fallback parsing due to error: {e}")
            last_result = f"Query parsing failed, using fallback"
        
        return state, last_result


class ResearchPlannerAgent:
    """Research Planner Agent - creates research strategy and search queries"""
    
    def __init__(self, orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation):
        self.orchestrator = orchestrator
        self.console = console
        self.show_agent_working = show_agent_working
        self.show_llm_call = show_llm_call
        self.pause_for_explanation = pause_for_explanation
    
    def execute(self, state: dict, interactive_mode: bool):
        """Execute research planning - EXACT same code from main.py"""
        # Research Planning Step
        self.pause_for_explanation(
            "RESEARCH PLANNING",
            "Creating research strategy and search queries for comprehensive data collection.",
            interactive_mode
        )
        
        self.show_agent_working("Research Planner Agent", "Creating research strategy...")
        
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
            response = self.orchestrator.llm.invoke([{"role": "user", "content": planning_prompt}])
            
            # Show full LLM call
            self.show_llm_call(planning_prompt, response.content, "Research Planner")
            
            # Clean the response to extract JSON
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Remove any non-printable characters that might cause JSON parsing issues
            content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
            
            # Find the JSON object boundaries more carefully
            start_idx = content.find('{')
            if start_idx != -1:
                brace_count = 0
                end_idx = start_idx
                for i, char in enumerate(content[start_idx:], start_idx):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break
                content = content[start_idx:end_idx]
            
            plan_data = json.loads(content)
            
            state["research_context"]["research_plan"] = plan_data
            state["current_agent"] = "research_planner"
            state["agent_call_counts"]["research_planner"] += 1
            state["agent_messages"].append(f"Research Planner: Created research plan with {len(plan_data.get('search_queries', []))} search queries")
            
            self.console.print(f"✅ Research plan created successfully!")
            self.console.print(f"   • Search queries: {len(plan_data.get('search_queries', []))}")
            self.console.print(f"   • Methodology: {plan_data.get('methodology', 'N/A')}")
            self.console.print(f"   • Quality criteria: {len(plan_data.get('quality_criteria', []))}")
            
            last_result = f"Research plan created with {len(plan_data.get('search_queries', []))} search queries"
            
        except Exception as e:
            self.console.print(f"❌ Research planning failed: {e}")
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
        
        return state, last_result


class DataCollectorAgent:
    """Data Collector Agent - performs web research and data collection"""
    
    def __init__(self, orchestrator, console, show_agent_working, pause_for_explanation, show_state_info):
        self.orchestrator = orchestrator
        self.console = console
        self.show_agent_working = show_agent_working
        self.pause_for_explanation = pause_for_explanation
        self.show_state_info = show_state_info
    
    def execute(self, state: dict, interactive_mode: bool):
        """Execute data collection - EXACT same code from main.py"""
        # Data Collection Step
        self.pause_for_explanation(
            "DATA COLLECTION",
            "Performing web research and gathering comprehensive data from multiple sources.",
            interactive_mode
        )
        
        self.show_agent_working("Data Collector Agent", "Collecting research data...")
        
        research_plan = state["research_context"].get("research_plan", {})
        search_queries = research_plan.get("search_queries", [])
        
        research_data = state.get("research_data", {})
        
        # Extract target entities from parsed entities (filter out generic terms)
        parsed_entities = state.get("parsed_entities", [])
        generic_terms = [
            "tools", "businesses", "small to mid-size B2B businesses", "small to mid-size businesses", 
            "B2B businesses", "software", "platforms", "solutions", "systems", "applications", 
            "products", "services", "companies", "organizations"
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
        
        # If no search queries available, create simple fallback
        if not search_queries or (len(search_queries) == 1 and search_queries[0]["entity"] == "Unknown"):
            # Simple fallback - assume Research Planner will provide proper queries in normal operation
            search_queries = [
                {"entity": entity, "focus": focus, "query": f"{entity} {focus}"}
                for entity in target_entities for focus in focus_areas
            ]
            state["research_context"]["research_plan"] = {"search_queries": search_queries}
        
        # Calculate how many queries we've processed so far by counting unique entities with data
        entities_with_data = set(research_data.keys())
        
        # Process entities one at a time - find the next entity that needs data collection
        queries_to_process = []
        for entity in target_entities:
            if entity not in entities_with_data:
                # This entity needs data - collect all focus areas for this entity
                entity_queries = [q for q in search_queries if q["entity"] == entity]
                queries_to_process = entity_queries[:4]  # Limit to 4 queries per iteration
                break
        
        # If all main entities have data, check if any need more focus areas
        if not queries_to_process:
            for entity in target_entities:
                if entity in research_data:
                    entity_focus_areas = set(research_data[entity].keys())
                    missing_focus_areas = set(focus_areas) - entity_focus_areas
                    if missing_focus_areas:
                        # This entity needs more focus areas
                        for focus in missing_focus_areas:
                            matching_queries = [q for q in search_queries if q["entity"] == entity and q["focus"] == focus]
                            if matching_queries:
                                queries_to_process.append(matching_queries[0])
                                if len(queries_to_process) >= 8:
                                    break
                        if len(queries_to_process) >= 8:  # Break outer loop when we have enough queries
                            break
        
        # If still no queries (quality improvement cycle), collect additional depth for all entities
        quality_validator_count = state["agent_call_counts"].get("quality_validator", 0)
        if not queries_to_process and quality_validator_count > 0:
            self.console.print("   🔍 Quality improvement cycle - collecting comprehensive additional data...")
            # Create enhanced search queries for deeper research on ALL entities
            improvement_queries = [
                f"{entity} detailed user reviews and ratings",
                f"{entity} real world implementation case studies small business", 
                f"{entity} pros and cons comparison small to medium business",
                f"{entity} cost total ownership analysis",
                f"{entity} customer support and training resources"
            ]
            
            for entity in target_entities:
                for query_template in improvement_queries[:4]:
                    enhanced_query = query_template.format(entity=entity) if "{entity}" in query_template else query_template.replace(entity.split()[0], entity)
                    queries_to_process.append({"entity": entity, "focus": "quality_enhancement", "query": enhanced_query})
                    if len(queries_to_process) >= 12:
                        break
                if len(queries_to_process) >= 12:
                    break
        
        for i, query_info in enumerate(queries_to_process, 1):
            entity = query_info["entity"]
            focus = query_info["focus"]
            query = query_info["query"]
            
            self.console.print(f"   🔍 Executing search {i}: {query}")
            
            if entity not in research_data:
                research_data[entity] = {}
            
            try:
                # Perform web search
                search_results = self.orchestrator.web_search_tool._run(query)
                research_data[entity][focus] = search_results
                self.console.print(f"   📥 Search {i} completed: {len(search_results)} characters")
                
            except Exception as e:
                research_data[entity][focus] = f"Search failed for {query}: {e}"
                self.console.print(f"   ❌ Search {i} failed: {e}")
        
        state["research_data"] = research_data
        state["current_agent"] = "data_collector"
        state["agent_call_counts"]["data_collector"] += 1
        state["agent_messages"].append(f"Data Collector: Collected data for {len(research_data)} entities")
        
        self.console.print(f"✅ Data collection completed!")
        self.console.print(f"   • Entities researched: {len(research_data)}")
        self.console.print(f"   • Total searches: {len(queries_to_process)}")
        
        last_result = f"Data collection completed for {len(research_data)} entities"
        
        self.show_state_info(state, interactive_mode)
        
        return state, last_result


class DataAnalyzerAgent:
    """Data Analyzer Agent - analyzes collected research data"""
    
    def __init__(self, orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info):
        self.orchestrator = orchestrator
        self.console = console
        self.show_agent_working = show_agent_working
        self.show_llm_call = show_llm_call
        self.pause_for_explanation = pause_for_explanation
        self.show_state_info = show_state_info
    
    def execute(self, state: dict, interactive_mode: bool):
        """Execute data analysis - EXACT same code from main.py"""
        # Data Analysis Step
        self.pause_for_explanation(
            "DATA ANALYSIS",
            "Analyzing collected data and extracting insights using advanced reasoning.",
            interactive_mode
        )
        
        self.show_agent_working("Data Analyzer Agent", "Analyzing research data...")
        
        research_data = state["research_data"]
        entities = state["parsed_entities"]
        focus_areas = state["research_focus_areas"]
        research_type = state["research_context"].get("research_type", "analysis")
        
        analysis_results = state.get("analysis_results", {})
        
        # Analyze all entities in research data (re-analyze if new data available)
        for entity in research_data:
            # Check if this is a re-analysis cycle (more than 3 data collector calls)
            is_reanalysis = state["agent_call_counts"]["data_collector"] > 3
            
            if entity not in analysis_results or is_reanalysis:
                entity_data = research_data[entity]
                
                self.console.print(f"   🔍 Analyzing {entity}...")
                
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
                    response = self.orchestrator.llm.invoke([{"role": "user", "content": analysis_prompt}])
                    
                    # Show full LLM call
                    self.show_llm_call(analysis_prompt, response.content, f"Data Analyzer ({entity})")
                    
                    analysis_results[entity] = {
                        "analysis": response.content,
                        "focus_areas_covered": list(entity_data.keys()),
                        "data_quality": "high" if len(combined_data) > 1000 else "medium"
                    }
                    self.console.print(f"   ✅ {entity} analysis completed: {len(response.content)} characters")
                    
                except Exception as e:
                    analysis_results[entity] = {
                        "analysis": f"Analysis failed: {e}",
                        "focus_areas_covered": list(entity_data.keys()),
                        "data_quality": "low"
                    }
                    self.console.print(f"   ❌ {entity} analysis failed: {e}")
        
        state["analysis_results"] = analysis_results
        state["current_agent"] = "data_analyzer"
        state["agent_call_counts"]["data_analyzer"] += 1
        state["agent_messages"].append(f"Data Analyzer: Analyzed data for {len(analysis_results)} entities")
        
        self.console.print(f"✅ Data analysis completed!")
        self.console.print(f"   • Entities analyzed: {len(analysis_results)}")
        
        last_result = f"Data analysis completed for {len(analysis_results)} entities"
        
        self.show_state_info(state, interactive_mode)
        
        return state, last_result


class QualityValidatorAgent:
    """Quality Validator Agent - validates research quality and completeness"""
    
    def __init__(self, orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info):
        self.orchestrator = orchestrator
        self.console = console
        self.show_agent_working = show_agent_working
        self.show_llm_call = show_llm_call
        self.pause_for_explanation = pause_for_explanation
        self.show_state_info = show_state_info
    
    def execute(self, state: dict, interactive_mode: bool):
        """Execute quality validation - EXACT same code from main.py"""
        # Quality Validation Step
        self.pause_for_explanation(
            "QUALITY VALIDATION",
            "Validating research quality and ensuring completeness before report generation.",
            interactive_mode
        )
        
        self.show_agent_working("Quality Validator Agent", "Validating research quality...")
        
        # Validate research quality
        # Prepare context-rich information for quality assessment
        research_data = state.get('research_data', {})
        analysis_results = state.get('analysis_results', {})
        target_entities = [entity for entity in state['parsed_entities'] if entity not in ['tools', 'businesses', 'software', 'platforms', 'solutions']]
        
        # Build detailed context about what has been researched and analyzed
        research_context = []
        for entity in target_entities:
            if entity in research_data:
                focus_areas_covered = list(research_data[entity].keys())
                research_context.append(f"{entity}: Data collected for {focus_areas_covered}")
            else:
                research_context.append(f"{entity}: No data collected")
        
        analysis_context = []
        for entity in target_entities:
            if entity in analysis_results:
                analysis_preview = analysis_results[entity][:200] + "..." if len(analysis_results[entity]) > 200 else analysis_results[entity]
                analysis_context.append(f"{entity}: Analysis completed - {analysis_preview}")
            else:
                analysis_context.append(f"{entity}: No analysis available")
        
        validation_prompt = f"""
        You are a quality validator assessing research comprehensiveness and depth for:
        
        Original Query: {state['original_query']}
        Target Entities: {target_entities}
        Focus Areas: {state['research_focus_areas']}
        
        CURRENT RESEARCH STATUS:
        {chr(10).join(research_context)}
        
        ANALYSIS CONTENT OVERVIEW:
        {chr(10).join(analysis_context)}
        
        QUALITY ASSESSMENT CONTEXT:
        - Total entities with data: {len(research_data)} of {len(target_entities)} target entities
        - Total entities analyzed: {len(analysis_results)} entities
        - Focus areas defined: {len(state['research_focus_areas'])}
        - Research depth varies by entity based on data availability
        
        Evaluate the research quality considering:
        1. Entity Coverage: Are all target entities represented with meaningful data?
        2. Focus Area Completeness: Do entities have data across the specified focus areas?
        3. Analysis Depth: Are the analyses substantive and provide actionable insights?
        4. Comparative Readiness: Is there sufficient information for meaningful comparison?
        5. Gap Identification: What specific improvements would enhance research value?
        
        INTELLIGENT SCORING (1-10):
        - Consider both breadth (entity coverage) and depth (analysis quality)
        - 6-7: Solid foundation with some gaps that could be improved
        - 8-9: Comprehensive coverage with good analytical depth
        - 10: Exceptional research with comprehensive insights across all dimensions
        
        Provide specific, actionable recommendations based on actual content gaps, not just numerical deficiencies.
        
        Return as JSON format:
        {{
            "data_completeness": {{
                "score": 8,
                "details": "assessment based on entity and focus area coverage"
            }},
            "analysis_quality": {{
                "score": 7,
                "details": "assessment based on analytical depth and insight quality"
            }},
            "research_gaps": ["specific gap1", "specific gap2"],
            "overall_score": 7.5,
            "recommendations": ["specific actionable recommendation1", "specific actionable recommendation2"],
            "validation_status": "pass|needs_improvement|fail"
        }}
        """
        
        try:
            response = self.orchestrator.llm.invoke([{"role": "user", "content": validation_prompt}])
            
            # Show full LLM call
            self.show_llm_call(validation_prompt, response.content, "Quality Validator")
            
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
            
            # Show different detail levels based on validation count for better presentation
            current_validation_count = state["agent_call_counts"]["quality_validator"]
            
            if current_validation_count == 0:  # First validation - show full details
                self.console.print(f"✅ Quality validation completed!")
                self.console.print(f"   • Overall Score: {validation_data.get('overall_score', 'N/A')}/10")
                self.console.print(f"   • Validation Status: {validation_data.get('validation_status', 'N/A')}")
                self.console.print(f"   • Research Gaps: {len(validation_data.get('research_gaps', []))}")
            else:  # Subsequent validations - simplified display
                self.console.print(f"✅ Quality validation completed!")
            
            state["agent_call_counts"]["quality_validator"] += 1
            state["current_agent"] = "quality_validator"  # CRITICAL: Set current agent
            
            # Determine next action based on quality score and recommendations
            overall_score = validation_data.get('overall_score', 0)
            validation_status = validation_data.get('validation_status', 'fail')
            recommendations = validation_data.get('recommendations', [])
            
            if overall_score >= 8 or validation_status == 'pass':
                last_result = "quality_validated_good"
                if current_validation_count == 0:
                    self.console.print(f"   🎯 Quality is sufficient - ready for report synthesis")
            elif overall_score >= 6:
                last_result = "quality_validated_needs_improvement"
                if current_validation_count == 0:
                    self.console.print(f"   ⚠️  Quality needs improvement - recommendations provided")
            else:
                last_result = "quality_validated_poor"
                if current_validation_count == 0:
                    self.console.print(f"   ❌ Quality insufficient - significant improvements needed")
            
            state["agent_messages"].append(f"Quality Validator: Validated research")

        except Exception as e:
            self.console.print(f"❌ Quality validation failed: {e}")
            state["validation_results"] = {
                "data_completeness": {"score": 7, "details": "Good coverage"},
                "analysis_quality": {"score": 7, "details": "Solid analysis"},
                "research_gaps": [],
                "overall_score": 7,
                "recommendations": ["Continue with current approach"],
                "validation_status": "pass"
            }
            state["agent_call_counts"]["quality_validator"] += 1
            state["current_agent"] = "quality_validator"  # CRITICAL: Set current agent
            last_result = "quality_validated_fallback"
            state["agent_messages"].append(f"Quality Validator: Using fallback validation due to validation error")
        
        return state, last_result


class ReportSynthesizerAgent:
    """Report Synthesizer Agent - creates comprehensive final reports"""
    
    def __init__(self, orchestrator, console, show_agent_working, show_llm_call, pause_for_explanation, show_state_info):
        self.orchestrator = orchestrator
        self.console = console
        self.show_agent_working = show_agent_working
        self.show_llm_call = show_llm_call
        self.pause_for_explanation = pause_for_explanation
        self.show_state_info = show_state_info
    
    def execute(self, state: dict, interactive_mode: bool):
        """Execute report synthesis - EXACT same code from main.py"""
        # Report Synthesis Step
        self.pause_for_explanation(
            "REPORT SYNTHESIS",
            "Creating comprehensive report with analysis findings and recommendations.",
            interactive_mode
        )
        
        self.show_agent_working("Report Synthesizer Agent", "Creating comprehensive report...")
        
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
        
        WRITING STYLE: Use detailed, narrative paragraphs with thorough explanations. 
        Write like a business analyst with flowing text rather than simple bullet points. 
        Provide context and reasoning behind recommendations.
        
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
            response = self.orchestrator.llm.invoke([{"role": "user", "content": synthesis_prompt}])
            
            # Show full LLM call
            self.show_llm_call(synthesis_prompt, response.content, "Report Synthesizer")
            
            state["final_report"] = response.content
            state["current_agent"] = "report_synthesizer"
            state["agent_call_counts"]["report_synthesizer"] += 1
            state["agent_messages"].append("Report Synthesizer: Generated comprehensive report")
            
            self.console.print(f"✅ Report synthesis completed!")
            self.console.print(f"   • Report length: {len(response.content)} characters")
            
            last_result = f"Report synthesis completed - {len(response.content)} characters"
            
        except Exception as e:
            state["final_report"] = f"Report generation failed: {e}"
            state["current_agent"] = "report_synthesizer"
            state["agent_call_counts"]["report_synthesizer"] += 1
            state["agent_messages"].append(f"Report Synthesizer: Failed to generate report: {e}")
            self.console.print(f"❌ Report synthesis failed: {e}")
            last_result = f"Report synthesis failed: {e}"
        
        return state, last_result


# Orchestrator functions - EXACT same code from main.py
def orchestrator_decision(orchestrator, state: dict, last_agent_result: str) -> str:
    """Make dynamic orchestrator decisions based on agent results using LLM"""
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
    
    # HYBRID ORCHESTRATOR: LLM Intelligence + Quality-Driven Rules
    iteration_count = decision_context['iteration_count']
    agent_counts = decision_context['agent_call_counts']
    research_data_quality = decision_context['research_data_quality']
    target_entities_count = decision_context['target_entities_count']
    
    # Enhanced decision prompt with STRONG quality validation emphasis
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
    
    RESEARCH ORCHESTRATION GUIDANCE:
    
    The research_planning agent creates a strategic foundation 
    by developing detailed search queries and methodology. This transforms raw query understanding into 
    actionable research steps, establishing the roadmap for comprehensive data collection.
    
    The data_collection agent executes systematic information gathering based on the research plan. 
    It works iteratively to ensure all target entities receive adequate coverage. When research_data_quality 
    shows fewer entities than target_entities_count, more collection is needed to achieve comprehensive coverage.
    
    The data_analysis agent processes and synthesizes the gathered information. This agent transforms raw research data into structured insights, creating 
    the analytical foundation necessary for quality assessment.
    
    The quality_validation agent serves as the research quality gatekeeper. When validation results indicate 
    "quality_validated_good", the research meets standards for final reporting. However, if validation shows 
    "quality_validated_needs_improvement" or "quality_validated_poor", the system should intelligently 
    choose improvement strategies - additional data collection for breadth, enhanced analysis for depth, 
    or targeted research for specific gaps.
    
    The report_synthesis agent creates the final deliverable when research quality is sufficient or when 
    multiple improvement cycles have been completed (typically after 2 quality validations to prevent 
    endless iteration).
    
    CONTEXTUAL DECISION FACTORS:
    - Research completeness: Does research_data_quality match target_entities_count?
    - Analysis depth: Are analysis_quality results comprehensive for the entities collected?
    - Quality feedback: What specific improvements does quality validation suggest?
    - Iteration efficiency: Have we reached reasonable iteration limits for practical completion?
    
    Available Actions and Their Purpose:
    • "research_planning" - Develops strategic approach and detailed search methodology
    • "data_collection" - Gathers comprehensive information across all target entities  
    • "data_analysis" - Processes data into structured insights and comparative analysis
    • "quality_validation" - Assesses research comprehensiveness and identifies improvement areas
    • "report_synthesis" - Creates final deliverable when quality standards are met
    • "additional_research" - Targeted information gathering for specific improvement needs
    • "end" - Completes the research process when objectives are fully satisfied
    
    SAFETY RULES:
    - If iteration count >= 12 → choose "report_synthesis"
    - If iteration count > 15 → choose "end"
    
    Respond with ONLY the action name (e.g., "data_collection", "data_analysis", "quality_validation", etc.)
    """
    
    try:
        response = orchestrator.llm.invoke([HumanMessage(content=decision_prompt)])
        decision = response.content.strip().lower()
        
        # Extract only the first word/line (the actual decision)
        decision_clean = decision.split('\n')[0].split()[0] if decision else decision
        
        # CRITICAL: Enforce quality validation rules if LLM ignores them
        if "quality_validated_good" in last_agent_result:
            return "report_synthesis"
        elif "quality_validated_needs_improvement" in last_agent_result:
            if agent_counts.get("quality_validator", 0) < 2:
                return "data_collection"  # FORCE improvement - override LLM
            else:
                return "report_synthesis"  # Force report after 2 quality checks
        elif "quality_validated_poor" in last_agent_result:
            if agent_counts.get("quality_validator", 0) < 2:
                return "data_collection"  # FORCE improvement - override LLM
            else:
                return "report_synthesis"  # Force report after 2 quality checks
        
        # Safety rules
        if iteration_count >= 12:
            return "report_synthesis"
        elif iteration_count > 15:
            return "end"
        
        return decision_clean
        
    except Exception as e:
        print(f"❌ Orchestrator decision failed: {e}")
        # Fallback to quality-aware logic
        if "quality_validated_good" in last_agent_result:
            return "report_synthesis"
        elif "quality_validated_needs_improvement" in last_agent_result:
            return "data_collection" if agent_counts.get("quality_validator", 0) < 2 else "report_synthesis"
        elif "quality_validated_poor" in last_agent_result:
            return "data_collection" if agent_counts.get("quality_validator", 0) < 2 else "report_synthesis"
        elif iteration_count < 5:
            return "data_collection"
        elif iteration_count < 8:
            return "data_analysis"
        else:
            return "report_synthesis"


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
