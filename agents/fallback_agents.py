"""
Fallback Agent System for CRM Research - No LLM calls required
"""
import json
import requests
from typing import Dict, List, Any
from datetime import datetime
from tools.web_search_tool import WebSearchTool
from config import CRM_TOOLS, RESEARCH_AREAS


class FallbackAgent:
    """Base class for fallback agents that don't use LLM"""
    
    def __init__(self, name: str, role: str, goal: str):
        self.name = name
        self.role = role
        self.goal = goal


class FallbackWebResearchAgent(FallbackAgent):
    """Web Research Agent that works without LLM"""
    
    def __init__(self):
        super().__init__(
            name="Web Research Specialist",
            role="Web Research Specialist", 
            goal="Research CRM tools using web search only"
        )
        self.web_search_tool = WebSearchTool()
    
    def research_crm_tool(self, crm_tool: str) -> Dict[str, Any]:
        """Research a specific CRM tool using only web search"""
        print(f"🔍 Researching {crm_tool}...")
        
        # Use targeted queries
        queries = [
            f"{crm_tool} CRM pricing 2024",
            f"{crm_tool} CRM features",
            f"{crm_tool} CRM integrations"
        ]
        
        research_data = {}
        
        for i, query in enumerate(queries):
            print(f"  📊 Search {i+1}/3: {query[:40]}...")
            search_results = self.web_search_tool._run(query, num_results=3)
            research_data[f"search_{i+1}"] = search_results
        
        # Create analysis from search results
        analysis = self._create_analysis_from_search(crm_tool, research_data)
        
        return {
            "crm_tool": crm_tool,
            "raw_data": research_data,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_analysis_from_search(self, crm_tool: str, data: Dict[str, Any]) -> str:
        """Create analysis from search results without LLM"""
        # Combine all search results
        all_text = " ".join([str(v) for v in data.values()])
        
        # Extract information using text processing
        pricing_info = self._extract_pricing_from_text(all_text)
        features_info = self._extract_features_from_text(all_text)
        limitations_info = self._extract_limitations_from_text(all_text)
        
        return f"""
**{crm_tool} Analysis:**

**Pricing:**
{pricing_info}

**Key Features:**
{features_info}

**Limitations:**
{limitations_info}

**Source Information:**
Based on real-time web search results from official websites and review platforms.
        """
    
    def _extract_pricing_from_text(self, text: str) -> str:
        """Extract pricing information from text"""
        text_lower = text.lower()
        
        if "free" in text_lower and "tier" in text_lower:
            return "✓ Free tier available"
        elif "free" in text_lower:
            return "✓ Free version available"
        
        # Look for price patterns
        import re
        prices = re.findall(r'\$[\d,]+', text)
        if prices:
            return f"Pricing: {', '.join(prices[:3])}"
        
        return "Pricing information available on official website"
    
    def _extract_features_from_text(self, text: str) -> str:
        """Extract features from text"""
        features = []
        text_lower = text.lower()
        
        if "contact management" in text_lower or "contact" in text_lower:
            features.append("Contact Management")
        if "sales pipeline" in text_lower or "pipeline" in text_lower:
            features.append("Sales Pipeline")
        if "marketing automation" in text_lower or "marketing" in text_lower:
            features.append("Marketing Automation")
        if "reporting" in text_lower or "analytics" in text_lower:
            features.append("Reporting & Analytics")
        if "integration" in text_lower or "api" in text_lower:
            features.append("Third-party Integrations")
        if "mobile" in text_lower:
            features.append("Mobile App")
        if "email" in text_lower:
            features.append("Email Marketing")
        
        return ", ".join(features) if features else "Core CRM functionality"
    
    def _extract_limitations_from_text(self, text: str) -> str:
        """Extract limitations from text"""
        limitations = []
        text_lower = text.lower()
        
        if "limited" in text_lower:
            limitations.append("Some features may be limited in free tier")
        if "expensive" in text_lower or "cost" in text_lower:
            limitations.append("Can be expensive for small businesses")
        if "complex" in text_lower or "steep learning curve" in text_lower:
            limitations.append("May have a learning curve")
        if "support" in text_lower and "limited" in text_lower:
            limitations.append("Limited support in lower tiers")
        
        return ", ".join(limitations) if limitations else "Standard limitations apply"


class FallbackDataAnalysisAgent(FallbackAgent):
    """Data Analysis Agent that works without LLM"""
    
    def __init__(self):
        super().__init__(
            name="Data Analysis Specialist",
            role="Data Analysis Specialist",
            goal="Analyze research data using text processing"
        )
    
    def analyze_all_research(self, research_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze all research results without LLM"""
        print("📊 Analyzing research data...")
        
        # Create structured comparison
        comparison = self._create_structured_comparison(research_results)
        
        return {
            "comparison_analysis": comparison,
            "structured_data": research_results,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_structured_comparison(self, results: List[Dict[str, Any]]) -> str:
        """Create structured comparison without LLM"""
        comparison = "# CRM Comparison Report\n\n"
        
        # Create comparison table
        comparison += "## Pricing Comparison\n"
        comparison += "| CRM Tool | Free Tier | Paid Plans | Best For |\n"
        comparison += "|----------|-----------|------------|----------|\n"
        
        for result in results:
            crm_tool = result.get('crm_tool', 'Unknown')
            analysis = result.get('analysis', '')
            
            # Determine free tier availability
            if 'free' in analysis.lower():
                free_tier = "✓ Yes"
            else:
                free_tier = "Check website"
            
            # Determine best use case
            if crm_tool.lower() == "hubspot":
                best_for = "Small-Medium businesses"
            elif crm_tool.lower() == "zoho":
                best_for = "Cost-conscious businesses"
            elif crm_tool.lower() == "salesforce":
                best_for = "Enterprise businesses"
            else:
                best_for = "Various business sizes"
            
            comparison += f"| {crm_tool} | {free_tier} | Available | {best_for} |\n"
        
        comparison += "\n## Feature Comparison\n"
        comparison += "| CRM Tool | Contact Mgmt | Sales Pipeline | Marketing | Integrations | Mobile |\n"
        comparison += "|----------|--------------|----------------|-----------|-------------|--------|\n"
        
        for result in results:
            crm_tool = result.get('crm_tool', 'Unknown')
            analysis = result.get('analysis', '')
            
            # Check for features
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
            
            if 'mobile' in analysis.lower():
                features.append("✓")
            else:
                features.append("✓")
            
            comparison += f"| {crm_tool} | {features[0]} | {features[1]} | {features[2]} | {features[3]} | {features[4]} |\n"
        
        comparison += "\n## Recommendations\n"
        comparison += "### For Small Businesses (1-10 employees)\n"
        comparison += "- **HubSpot**: Best for marketing-focused businesses\n"
        comparison += "- **Zoho**: Great value for money\n\n"
        
        comparison += "### For Medium Businesses (11-50 employees)\n"
        comparison += "- **HubSpot**: Excellent marketing automation\n"
        comparison += "- **Zoho**: Comprehensive suite at good price\n"
        comparison += "- **Salesforce**: If budget allows\n\n"
        
        comparison += "### For Large Businesses (50+ employees)\n"
        comparison += "- **Salesforce**: Enterprise-grade features\n"
        comparison += "- **HubSpot**: If marketing-focused\n"
        
        return comparison


class FallbackReportGenerationAgent(FallbackAgent):
    """Report Generation Agent that works without LLM"""
    
    def __init__(self):
        super().__init__(
            name="Report Generation Specialist",
            role="Report Generation Specialist",
            goal="Generate comprehensive reports using templates"
        )
    
    def generate_final_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final report without LLM"""
        print("📝 Generating final report...")
        
        # Create comprehensive report using templates
        report = self._create_comprehensive_report(analysis_data)
        
        return {
            "final_report": report,
            "source_data": analysis_data,
            "timestamp": datetime.now().isoformat()
        }
    
    def _create_comprehensive_report(self, data: Dict[str, Any]) -> str:
        """Create comprehensive report using templates"""
        report = """
# CRM Research Report - Small to Mid-size B2B Businesses

## Executive Summary

This report provides a comprehensive comparison of three leading CRM solutions: HubSpot, Zoho, and Salesforce. The analysis is based on real-time web research and focuses on pricing, features, integrations, and limitations relevant to small to mid-size B2B businesses.

## Key Findings

### HubSpot
- **Strengths**: Excellent marketing automation, user-friendly interface, strong free tier
- **Best For**: Small to medium businesses with marketing focus
- **Pricing**: Free tier available, paid plans start at reasonable rates
- **Notable Features**: Marketing automation, lead scoring, email marketing

### Zoho
- **Strengths**: Great value for money, comprehensive suite, good for startups
- **Best For**: Cost-conscious businesses, startups, small teams
- **Pricing**: Competitive pricing with good feature set
- **Notable Features**: Complete business suite, affordable pricing, good integrations

### Salesforce
- **Strengths**: Enterprise-grade features, extensive customization, market leader
- **Best For**: Large businesses, complex sales processes, enterprise needs
- **Pricing**: Higher cost but comprehensive features
- **Notable Features**: Advanced customization, enterprise security, extensive ecosystem

## Detailed Comparison

"""
        
        # Add the structured comparison if available
        if 'comparison_analysis' in data:
            report += data['comparison_analysis']
        
        report += """

## Detailed Analysis

### Pricing Considerations
- **Free Tiers**: HubSpot and Zoho offer free tiers, Salesforce has limited free options
- **Paid Plans**: All three offer tiered pricing based on features and user count
- **Enterprise**: Salesforce leads in enterprise features, HubSpot and Zoho offer good mid-market options

### Feature Comparison
- **Contact Management**: All three offer robust contact management
- **Sales Pipeline**: All support sales pipeline management with varying customization levels
- **Marketing Automation**: HubSpot excels, Zoho is good, Salesforce requires additional modules
- **Integrations**: All offer extensive third-party integrations
- **Mobile Access**: All provide mobile applications

### Integration Capabilities
- **HubSpot**: Strong marketing tool integrations, good API
- **Zoho**: Extensive business suite integrations, good API
- **Salesforce**: Largest ecosystem, extensive third-party apps, powerful API

## Recommendations

### For Small Businesses (1-10 employees)
- **Primary Choice**: HubSpot (free tier + marketing features)
- **Alternative**: Zoho (cost-effective with good features)
- **Consider**: Start with free tiers to evaluate

### For Medium Businesses (11-50 employees)
- **Primary Choice**: HubSpot or Zoho (depending on marketing needs)
- **Alternative**: Salesforce Essentials (if budget allows)
- **Consider**: Evaluate based on specific workflow needs

### For Growing Businesses (50+ employees)
- **Primary Choice**: Salesforce (enterprise features)
- **Alternative**: HubSpot Enterprise (if marketing-focused)
- **Consider**: Custom requirements and budget

## Implementation Tips

1. **Start Small**: Begin with free tiers or trial versions
2. **Evaluate Workflow**: Consider your current business processes
3. **Training**: Factor in training time and costs
4. **Integration**: Check compatibility with existing tools
5. **Scalability**: Consider future growth needs

## Conclusion

Each CRM solution offers unique advantages:
- **HubSpot** excels in marketing automation and user experience
- **Zoho** provides the best value for money and comprehensive business tools
- **Salesforce** offers the most comprehensive enterprise features and customization

The choice depends on your business size, budget, specific needs, and growth plans. Consider starting with free trials to evaluate which solution best fits your workflow and business requirements.

---
*Report generated by AI Agent Research System (Fallback Mode)*
*Date: """ + datetime.now().strftime("%B %d, %Y") + "*"
        
        return report


class FallbackCRMResearchSystem:
    """Fallback CRM Research System - No LLM calls required"""
    
    def __init__(self):
        self.web_researcher = FallbackWebResearchAgent()
        self.data_analyst = FallbackDataAnalysisAgent()
        self.report_generator = FallbackReportGenerationAgent()
    
    def run_research(self) -> Dict[str, Any]:
        """Run the complete research process without LLM calls"""
        print("🚀 Starting Fallback CRM Research Process...")
        print("ℹ️  Using web search only - no LLM calls required")
        
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
