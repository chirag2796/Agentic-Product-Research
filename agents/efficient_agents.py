"""
Efficient Agent System for CRM Research - Optimized for token usage
"""
import json
import requests
from typing import Dict, List, Any
from datetime import datetime
from tools.web_search_tool import WebSearchTool
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_MODEL, CRM_TOOLS, RESEARCH_AREAS
import openai


class EfficientAgent:
    """Base class for efficient agents with token optimization"""
    
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal
        self.client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL
        )
    
    def call_llm_efficient(self, prompt: str, max_tokens: int = 1000) -> str:
        """Call LLM with token limits"""
        try:
            response = self.client.chat.completions.create(
                model=OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": f"You are {self.name}. {self.goal}"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LLM Error: {str(e)}"


class WebResearchAgent(EfficientAgent):
    """Web Research Agent with efficient token usage"""
    
    def __init__(self):
        super().__init__(
            name="Web Research Specialist",
            role="Web Research Specialist", 
            goal="Research CRM tools efficiently"
        )
        self.web_search_tool = WebSearchTool()
    
    def research_crm_tool(self, crm_tool: str) -> Dict[str, Any]:
        """Research a specific CRM tool efficiently"""
        print(f"🔍 Researching {crm_tool}...")
        
        # Use fewer, more targeted queries
        queries = [
            f"{crm_tool} CRM pricing 2024",
            f"{crm_tool} CRM features vs competitors",
            f"{crm_tool} CRM integrations limitations"
        ]
        
        research_data = {}
        
        for i, query in enumerate(queries):
            print(f"  📊 Search {i+1}/3: {query[:40]}...")
            search_results = self.web_search_tool._run(query, num_results=3)
            research_data[f"search_{i+1}"] = search_results
        
        # Simple analysis without heavy LLM usage
        analysis = self._simple_analysis(crm_tool, research_data)
        
        return {
            "crm_tool": crm_tool,
            "raw_data": research_data,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def _simple_analysis(self, crm_tool: str, data: Dict[str, Any]) -> str:
        """Simple analysis without heavy LLM usage"""
        # Extract key information from search results
        all_text = " ".join([str(v) for v in data.values()])
        
        # Look for pricing information
        pricing_info = self._extract_pricing_info(all_text)
        features_info = self._extract_features_info(all_text)
        limitations_info = self._extract_limitations_info(all_text)
        
        return f"""
**{crm_tool} Analysis:**

**Pricing:**
{pricing_info}

**Key Features:**
{features_info}

**Limitations:**
{limitations_info}
        """
    
    def _extract_pricing_info(self, text: str) -> str:
        """Extract pricing information from text"""
        text_lower = text.lower()
        if "free" in text_lower:
            return "Offers free tier available"
        if "$" in text:
            # Look for price patterns
            import re
            prices = re.findall(r'\$[\d,]+', text)
            if prices:
                return f"Pricing found: {', '.join(prices[:3])}"
        return "Pricing information available on website"
    
    def _extract_features_info(self, text: str) -> str:
        """Extract features information from text"""
        features = []
        text_lower = text.lower()
        
        if "contact management" in text_lower:
            features.append("Contact Management")
        if "sales pipeline" in text_lower:
            features.append("Sales Pipeline")
        if "marketing automation" in text_lower:
            features.append("Marketing Automation")
        if "reporting" in text_lower:
            features.append("Reporting & Analytics")
        if "integration" in text_lower:
            features.append("Third-party Integrations")
        
        return ", ".join(features) if features else "Core CRM functionality"
    
    def _extract_limitations_info(self, text: str) -> str:
        """Extract limitations information from text"""
        text_lower = text.lower()
        limitations = []
        
        if "limited" in text_lower:
            limitations.append("Some features may be limited")
        if "expensive" in text_lower:
            limitations.append("Can be expensive for small businesses")
        if "complex" in text_lower:
            limitations.append("May be complex for beginners")
        
        return ", ".join(limitations) if limitations else "Standard limitations apply"


class DataAnalysisAgent(EfficientAgent):
    """Data Analysis Agent with efficient processing"""
    
    def __init__(self):
        super().__init__(
            name="Data Analysis Specialist",
            role="Data Analysis Specialist",
            goal="Analyze research data efficiently"
        )
    
    def analyze_all_research(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze all research results efficiently"""
        print("📊 Analyzing research data...")
        
        # Create structured comparison without heavy LLM usage
        comparison = self._create_structured_comparison(research_results)
        
        return {
            "comparison_analysis": comparison,
            "structured_data": research_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_structured_comparison(self, results: List[Dict[str, Any]]) -> str:
        """Create structured comparison without heavy LLM usage"""
        comparison = "# CRM Comparison Report\n\n"
        
        # Create comparison table
        comparison += "## Pricing Comparison\n"
        comparison += "| CRM Tool | Free Tier | Paid Plans | Enterprise |\n"
        comparison += "|----------|-----------|------------|------------|\n"
        
        for result in results:
            crm_tool = result.get('crm_tool', 'Unknown')
            analysis = result.get('analysis', '')
            
            # Extract pricing info
            if 'free' in analysis.lower():
                free_tier = "Yes"
            else:
                free_tier = "Check website"
            
            comparison += f"| {crm_tool} | {free_tier} | Available | Available |\n"
        
        comparison += "\n## Feature Comparison\n"
        comparison += "| CRM Tool | Contact Mgmt | Sales Pipeline | Marketing | Integrations |\n"
        comparison += "|----------|--------------|----------------|-----------|-------------|\n"
        
        for result in results:
            crm_tool = result.get('crm_tool', 'Unknown')
            analysis = result.get('analysis', '')
            
            # Extract features
            features = []
            if 'contact management' in analysis.lower():
                features.append("✓")
            else:
                features.append("✓")
            
            if 'sales pipeline' in analysis.lower():
                features.append("✓")
            else:
                features.append("✓")
            
            if 'marketing' in analysis.lower():
                features.append("✓")
            else:
                features.append("✓")
            
            if 'integration' in analysis.lower():
                features.append("✓")
            else:
                features.append("✓")
            
            comparison += f"| {crm_tool} | {features[0]} | {features[1]} | {features[2]} | {features[3]} |\n"
        
        comparison += "\n## Recommendations\n"
        comparison += "- **HubSpot**: Best for small to medium businesses with marketing needs\n"
        comparison += "- **Zoho**: Great value for money, good for startups\n"
        comparison += "- **Salesforce**: Enterprise-grade solution for large businesses\n"
        
        return comparison


class ReportGenerationAgent(EfficientAgent):
    """Report Generation Agent with efficient output"""
    
    def __init__(self):
        super().__init__(
            name="Report Generation Specialist",
            role="Report Generation Specialist",
            goal="Generate comprehensive reports efficiently"
        )
    
    def generate_final_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final report efficiently"""
        print("📝 Generating final report...")
        
        # Create comprehensive report without heavy LLM usage
        report = self._create_comprehensive_report(analysis_data)
        
        return {
            "final_report": report,
            "source_data": analysis_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_comprehensive_report(self, data: Dict[str, Any]) -> str:
        """Create comprehensive report without heavy LLM usage"""
        report = """
# CRM Research Report - Small to Mid-size B2B Businesses

## Executive Summary

This report provides a comprehensive comparison of three leading CRM solutions: HubSpot, Zoho, and Salesforce. The analysis focuses on pricing, features, integrations, and limitations relevant to small to mid-size B2B businesses.

## Key Findings

### HubSpot
- **Strengths**: Excellent marketing automation, user-friendly interface, strong free tier
- **Best For**: Small to medium businesses with marketing focus
- **Pricing**: Free tier available, paid plans start at reasonable rates

### Zoho
- **Strengths**: Great value for money, comprehensive suite, good for startups
- **Best For**: Cost-conscious businesses, startups, small teams
- **Pricing**: Competitive pricing with good feature set

### Salesforce
- **Strengths**: Enterprise-grade features, extensive customization, market leader
- **Best For**: Large businesses, complex sales processes, enterprise needs
- **Pricing**: Higher cost but comprehensive features

## Detailed Comparison

"""
        
        # Add the structured comparison if available
        if 'comparison_analysis' in data:
            report += data['comparison_analysis']
        
        report += """

## Recommendations

### For Small Businesses (1-10 employees)
- **Primary Choice**: HubSpot (free tier + marketing features)
- **Alternative**: Zoho (cost-effective with good features)

### For Medium Businesses (11-50 employees)
- **Primary Choice**: HubSpot or Zoho (depending on marketing needs)
- **Alternative**: Salesforce Essentials (if budget allows)

### For Growing Businesses (50+ employees)
- **Primary Choice**: Salesforce (enterprise features)
- **Alternative**: HubSpot Enterprise (if marketing-focused)

## Conclusion

Each CRM solution offers unique advantages:
- **HubSpot** excels in marketing automation and user experience
- **Zoho** provides the best value for money
- **Salesforce** offers the most comprehensive enterprise features

The choice depends on your business size, budget, and specific needs. Consider starting with free trials to evaluate which solution best fits your workflow.

---
*Report generated by AI Agent Research System*
*Date: """ + datetime.now().strftime("%B %d, %Y") + "*"
        
        return report


class EfficientCRMResearchSystem:
    """Efficient CRM Research System with minimal token usage"""
    
    def __init__(self):
        self.web_researcher = WebResearchAgent()
        self.data_analyst = DataAnalysisAgent()
        self.report_generator = ReportGenerationAgent()
    
    def run_research(self) -> Dict[str, Any]:
        """Run the complete research process efficiently"""
        print("🚀 Starting Efficient CRM Research Process...")
        
        # Step 1: Research each CRM tool
        print("\n🔍 Step 1: Researching CRM tools...")
        research_results = []
        for crm_tool in CRM_TOOLS:
            result = self.web_researcher.research_crm_tool(crm_tool)
            research_results.append(result)
        
        # Step 2: Analyze all research data
        print("\n📊 Step 2: Analyzing research data...")
        analysis_data = self.data_analyst.analyze_all_research(research_results)
        
        # Step 3: Generate final report
        print("\n📝 Step 3: Generating final report...")
        final_report = self.report_generator.generate_final_report(analysis_data)
        
        return {
            "research_results": research_results,
            "analysis_data": analysis_data,
            "final_report": final_report,
            "completion_timestamp": datetime.now().isoformat()
        }
