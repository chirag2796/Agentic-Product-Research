"""
Simple Agent System for CRM Research without CrewAI dependencies
"""
import json
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from tools.web_search_tool import WebSearchTool
from tools.data_analysis_tool import DataAnalysisTool
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, CRM_TOOLS, RESEARCH_AREAS
import openai
import os


class SimpleAgent:
    """Base class for simple agents"""
    
    def __init__(self, name: str, role: str, goal: str, backstory: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
    
    def call_llm(self, prompt: str, temperature: float = 0.1) -> str:
        """Call the LLM with a prompt"""
        try:
            response = self.client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": f"You are {self.name}, {self.backstory}"},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            # Re-raise the exception so it can be caught by the main system
            raise e


class ResearchCoordinator(SimpleAgent):
    """Research Coordinator Agent"""
    
    def __init__(self):
        super().__init__(
            name="Research Coordinator",
            role="Research Coordinator",
            goal="Orchestrate and coordinate the CRM research process",
            backstory="""You are an experienced research coordinator with deep expertise in B2B software evaluation. 
            You excel at breaking down complex research tasks, delegating work to specialized agents, and ensuring 
            comprehensive coverage of all research areas."""
        )
        self.web_search_tool = WebSearchTool()
        self.data_analysis_tool = DataAnalysisTool()
    
    def create_research_plan(self) -> Dict[str, Any]:
        """Create a comprehensive research plan"""
        prompt = f"""
        Create a detailed research plan for comparing {', '.join(CRM_TOOLS)} for small to mid-size B2B businesses.
        Focus on: {', '.join(RESEARCH_AREAS)}.
        
        Your plan should include:
        1. Specific research tasks for each CRM tool
        2. Information sources to target
        3. Quality standards for the research data
        4. Timeline for the research process
        
        Return your response as a structured plan.
        """
        
        plan = self.call_llm(prompt)
        return {
            "plan": plan,
            "crm_tools": CRM_TOOLS,
            "research_areas": RESEARCH_AREAS,
            "timestamp": datetime.now().isoformat()
        }


class WebResearchAgent(SimpleAgent):
    """Web Research Agent"""
    
    def __init__(self):
        super().__init__(
            name="Web Research Specialist",
            role="Web Research Specialist",
            goal="Conduct thorough web research on CRM tools",
            backstory="""You are a meticulous web researcher specializing in B2B software research. You have access to 
            real-time web search capabilities and excel at finding the most current and accurate information about 
            software products."""
        )
        self.web_search_tool = WebSearchTool()
    
    def research_crm_tool(self, crm_tool: str) -> Dict[str, Any]:
        """Research a specific CRM tool"""
        print(f"🔍 Researching {crm_tool}...")
        
        # Create search queries for different aspects
        queries = [
            f"{crm_tool} CRM pricing plans 2024 small business",
            f"{crm_tool} CRM features comparison B2B",
            f"{crm_tool} CRM integrations third party tools",
            f"{crm_tool} CRM limitations drawbacks reviews",
            f"{crm_tool} CRM vs competitors small business"
        ]
        
        research_data = {}
        
        for i, query in enumerate(queries):
            print(f"  📊 Search {i+1}/5: {query[:50]}...")
            search_results = self.web_search_tool._run(query, num_results=5)
            research_data[f"search_{i+1}"] = search_results
        
        # Analyze the research data
        analysis_prompt = f"""
        Analyze the following research data for {crm_tool} and extract key information about:
        1. Pricing (free tier, paid plans, enterprise pricing)
        2. Key features and capabilities
        3. Available integrations
        4. Limitations and drawbacks
        
        Research Data:
        {json.dumps(research_data, indent=2)}
        
        Provide a structured analysis focusing on small to mid-size B2B businesses.
        """
        
        analysis = self.call_llm(analysis_prompt)
        
        return {
            "crm_tool": crm_tool,
            "raw_data": research_data,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }


class DataAnalysisAgent(SimpleAgent):
    """Data Analysis Agent"""
    
    def __init__(self):
        super().__init__(
            name="Data Analysis Specialist",
            role="Data Analysis Specialist",
            goal="Analyze and structure research data into meaningful comparisons",
            backstory="""You are a data analysis expert with strong skills in information processing and structuring. 
            You excel at taking raw research data and transforming it into organized, comparable formats."""
        )
        self.data_analysis_tool = DataAnalysisTool()
    
    def analyze_all_research(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze all research results and create structured comparison"""
        print("📊 Analyzing research data...")
        
        # Combine all research data
        combined_data = {
            "research_results": research_results,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        analysis_prompt = f"""
        Analyze the following research data for {', '.join(CRM_TOOLS)} and create a comprehensive comparison.
        
        Research Data:
        {json.dumps(combined_data, indent=2)}
        
        Create a structured comparison that includes:
        1. Executive Summary
        2. Side-by-side comparison table for:
           - Pricing (free tier, starter plans, professional plans, enterprise)
           - Key Features (contact management, sales pipeline, marketing automation, reporting)
           - Integrations (popular business tools, API access, marketplace)
           - Limitations (user complaints, missing features, technical constraints)
        3. Recommendations for small to mid-size B2B businesses
        4. Key differentiators
        
        Format the output as both a structured analysis and a markdown table.
        """
        
        analysis = self.call_llm(analysis_prompt)
        
        return {
            "comparison_analysis": analysis,
            "structured_data": combined_data,
            "timestamp": datetime.now().isoformat()
        }


class ValidationAgent(SimpleAgent):
    """Validation Agent"""
    
    def __init__(self):
        super().__init__(
            name="Research Validation Specialist",
            role="Research Validation Specialist",
            goal="Validate research findings and ensure data accuracy",
            backstory="""You are a quality assurance specialist with a keen eye for detail and accuracy. You excel at 
            validating research findings by cross-referencing multiple sources and ensuring information accuracy."""
        )
        self.web_search_tool = WebSearchTool()
    
    def validate_findings(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the research findings"""
        print("✅ Validating research findings...")
        
        validation_prompt = f"""
        Review the following CRM comparison analysis and identify any areas that need validation or additional research:
        
        Analysis Data:
        {json.dumps(analysis_data, indent=2)}
        
        Check for:
        1. Pricing accuracy and currency
        2. Feature claims verification
        3. Integration availability
        4. Limitation accuracy
        5. Data completeness
        
        Provide validation results and any recommendations for additional research.
        """
        
        validation = self.call_llm(validation_prompt)
        
        return {
            "validation_results": validation,
            "original_data": analysis_data,
            "timestamp": datetime.now().isoformat()
        }


class ReportGenerationAgent(SimpleAgent):
    """Report Generation Agent"""
    
    def __init__(self):
        super().__init__(
            name="Report Generation Specialist",
            role="Report Generation Specialist",
            goal="Create comprehensive comparison reports and summaries",
            backstory="""You are a technical writer and analyst with expertise in creating clear, comprehensive 
            comparison reports. You excel at synthesizing complex information into digestible formats."""
        )
    
    def generate_final_report(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate the final comparison report"""
        print("📝 Generating final report...")
        
        report_prompt = f"""
        Create a comprehensive final report for CRM comparison based on the validated research data.
        
        Validated Data:
        {json.dumps(validated_data, indent=2)}
        
        The report should include:
        1. Executive Summary
        2. Detailed comparison in both JSON and markdown formats
        3. Recommendations for small to mid-size B2B businesses
        4. Conclusion with key differentiators
        
        Format the output as a professional business report.
        """
        
        report = self.call_llm(report_prompt)
        
        return {
            "final_report": report,
            "source_data": validated_data,
            "timestamp": datetime.now().isoformat()
        }


class CRMResearchSystem:
    """Main CRM Research System"""
    
    def __init__(self):
        self.coordinator = ResearchCoordinator()
        self.web_researcher = WebResearchAgent()
        self.data_analyst = DataAnalysisAgent()
        self.validator = ValidationAgent()
        self.report_generator = ReportGenerationAgent()
    
    def run_research(self) -> Dict[str, Any]:
        """Run the complete research process"""
        print("🚀 Starting CRM Research Process...")
        
        # Step 1: Create research plan
        print("\n📋 Step 1: Creating research plan...")
        research_plan = self.coordinator.create_research_plan()
        
        # Step 2: Research each CRM tool
        print("\n🔍 Step 2: Researching CRM tools...")
        research_results = []
        for crm_tool in CRM_TOOLS:
            result = self.web_researcher.research_crm_tool(crm_tool)
            research_results.append(result)
        
        # Step 3: Analyze all research data
        print("\n📊 Step 3: Analyzing research data...")
        analysis_data = self.data_analyst.analyze_all_research(research_results)
        
        # Step 4: Validate findings
        print("\n✅ Step 4: Validating findings...")
        validated_data = self.validator.validate_findings(analysis_data)
        
        # Step 5: Generate final report
        print("\n📝 Step 5: Generating final report...")
        final_report = self.report_generator.generate_final_report(validated_data)
        
        return {
            "research_plan": research_plan,
            "research_results": research_results,
            "analysis_data": analysis_data,
            "validated_data": validated_data,
            "final_report": final_report,
            "completion_timestamp": datetime.now().isoformat()
        }
