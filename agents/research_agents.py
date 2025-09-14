"""
Research Agents for CRM Comparison System
"""
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools import WebSearchTool, DataAnalysisTool
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, CRM_TOOLS, RESEARCH_AREAS
import json


class CRMResearchAgents:
    def __init__(self):
        # Initialize LLM
        self.llm = ChatOpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            model=OPENROUTER_MODEL,
            temperature=0.1
        )
        
        # Initialize tools
        self.web_search_tool = WebSearchTool()
        self.data_analysis_tool = DataAnalysisTool()
        
        # Create agents
        self.coordinator_agent = self._create_coordinator_agent()
        self.web_research_agent = self._create_web_research_agent()
        self.data_analysis_agent = self._create_data_analysis_agent()
        self.validation_agent = self._create_validation_agent()
        self.report_agent = self._create_report_agent()

    def _create_coordinator_agent(self) -> Agent:
        """Research Coordinator Agent - Orchestrates the research process"""
        return Agent(
            role='Research Coordinator',
            goal='Orchestrate and coordinate the CRM research process, ensuring comprehensive coverage of all tools and aspects',
            backstory="""You are an experienced research coordinator with deep expertise in B2B software evaluation. 
            You excel at breaking down complex research tasks, delegating work to specialized agents, and ensuring 
            comprehensive coverage of all research areas. You make decisions about when to request additional research, 
            when to validate findings, and when to move forward with report generation.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[self.web_search_tool, self.data_analysis_tool]
        )

    def _create_web_research_agent(self) -> Agent:
        """Web Research Agent - Gathers real-time data from web sources"""
        return Agent(
            role='Web Research Specialist',
            goal='Conduct thorough web research on CRM tools, focusing on current pricing, features, integrations, and limitations',
            backstory="""You are a meticulous web researcher specializing in B2B software research. You have access to 
            real-time web search capabilities and excel at finding the most current and accurate information about 
            software products. You know how to craft effective search queries and extract relevant information from 
            various sources including official websites, review sites, and comparison platforms.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.web_search_tool]
        )

    def _create_data_analysis_agent(self) -> Agent:
        """Data Analysis Agent - Processes and structures information"""
        return Agent(
            role='Data Analysis Specialist',
            goal='Analyze, structure, and organize research data into meaningful comparisons and insights',
            backstory="""You are a data analysis expert with strong skills in information processing and structuring. 
            You excel at taking raw research data and transforming it into organized, comparable formats. You can 
            identify patterns, extract key insights, and present information in clear, structured ways that facilitate 
            decision-making.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.data_analysis_tool]
        )

    def _create_validation_agent(self) -> Agent:
        """Validation Agent - Cross-checks and validates findings"""
        return Agent(
            role='Research Validation Specialist',
            goal='Validate research findings, cross-check information, and ensure data accuracy and completeness',
            backstory="""You are a quality assurance specialist with a keen eye for detail and accuracy. You excel at 
            validating research findings by cross-referencing multiple sources, identifying inconsistencies, and 
            ensuring that all information is current and accurate. You know when to request additional research or 
            clarification to maintain high standards of data quality.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[self.web_search_tool, self.data_analysis_tool]
        )

    def _create_report_agent(self) -> Agent:
        """Report Generation Agent - Creates the final comparison"""
        return Agent(
            role='Report Generation Specialist',
            goal='Create comprehensive, well-structured comparison reports and summaries',
            backstory="""You are a technical writer and analyst with expertise in creating clear, comprehensive 
            comparison reports. You excel at synthesizing complex information into digestible formats, creating 
            side-by-side comparisons, and highlighting key differentiators. You ensure that reports are well-organized, 
            accurate, and actionable for decision-makers.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.data_analysis_tool]
        )

    def create_research_tasks(self) -> list[Task]:
        """Create research tasks for the agents"""
        tasks = []
        
        # Task 1: Initial Research Coordination
        coordination_task = Task(
            description=f"""
            As the Research Coordinator, create a comprehensive research plan for comparing {', '.join(CRM_TOOLS)} 
            for small to mid-size B2B businesses. Focus on: {', '.join(RESEARCH_AREAS)}.
            
            Your plan should:
            1. Break down the research into specific areas for each CRM tool
            2. Identify potential information gaps that need additional research
            3. Set quality standards for the research data
            4. Create a timeline for the research process
            
            Delegate specific research tasks to the Web Research Specialist for each CRM tool.
            """,
            agent=self.coordinator_agent,
            expected_output="A detailed research plan with delegated tasks for each CRM tool and research area"
        )
        tasks.append(coordination_task)

        # Task 2: Web Research for each CRM tool
        for crm_tool in CRM_TOOLS:
            research_task = Task(
                description=f"""
                Conduct comprehensive web research on {crm_tool} focusing on:
                - Current pricing plans and costs for small to mid-size B2B businesses
                - Key features and capabilities
                - Available integrations with other business tools
                - Known limitations and drawbacks
                - Recent updates and changes
                
                Use multiple search queries to gather comprehensive information from:
                - Official {crm_tool} website
                - Review sites (G2, Capterra, TrustRadius)
                - Comparison articles and blogs
                - User forums and communities
                
                Ensure you gather the most current information available.
                """,
                agent=self.web_research_agent,
                expected_output=f"Comprehensive research data on {crm_tool} covering all specified areas"
            )
            tasks.append(research_task)

        # Task 3: Data Analysis and Structuring
        analysis_task = Task(
            description=f"""
            Analyze and structure all the research data collected for {', '.join(CRM_TOOLS)}.
            
            For each CRM tool, extract and organize:
            1. Pricing information (free tier, paid plans, enterprise pricing)
            2. Feature matrix (core features, advanced features, unique capabilities)
            3. Integration capabilities (popular integrations, API access, third-party tools)
            4. Limitations and drawbacks (user complaints, missing features, technical issues)
            
            Create structured data that can be easily compared across all three tools.
            Identify any gaps in the research data that need additional investigation.
            """,
            agent=self.data_analysis_agent,
            expected_output="Structured, comparable data for all three CRM tools with identified research gaps"
        )
        tasks.append(analysis_task)

        # Task 4: Validation and Cross-checking
        validation_task = Task(
            description=f"""
            Validate the research findings for {', '.join(CRM_TOOLS)} by:
            1. Cross-checking pricing information from multiple sources
            2. Verifying feature claims against official documentation
            3. Confirming integration capabilities
            4. Validating limitation claims with user reviews
            
            If you find inconsistencies or gaps in the data, request additional research 
            from the Web Research Specialist for specific areas.
            
            Ensure all information is current (within the last 6 months) and accurate.
            """,
            agent=self.validation_agent,
            expected_output="Validated research data with any additional research requests for gaps or inconsistencies"
        )
        tasks.append(validation_task)

        # Task 5: Final Report Generation
        report_task = Task(
            description=f"""
            Create a comprehensive comparison report for {', '.join(CRM_TOOLS)} for small to mid-size B2B businesses.
            
            The report should include:
            1. Executive Summary
            2. Side-by-side comparison table covering:
               - Pricing (free tier, starter plans, professional plans, enterprise)
               - Key Features (contact management, sales pipeline, marketing automation, reporting)
               - Integrations (popular business tools, API access, marketplace)
               - Limitations (user complaints, missing features, technical constraints)
            3. Recommendations based on business size and needs
            4. Conclusion with key differentiators
            
            Format the output as both a structured JSON object and a markdown table for easy comparison.
            """,
            agent=self.report_agent,
            expected_output="Comprehensive comparison report in both JSON and markdown formats"
        )
        tasks.append(report_task)

        return tasks

    def run_research(self) -> str:
        """Execute the research process"""
        tasks = self.create_research_tasks()
        
        crew = Crew(
            agents=[
                self.coordinator_agent,
                self.web_research_agent,
                self.data_analysis_agent,
                self.validation_agent,
                self.report_agent
            ],
            tasks=tasks,
            process=Process.hierarchical,
            manager_agent=self.coordinator_agent,
            verbose=True
        )
        
        result = crew.kickoff()
        return result
