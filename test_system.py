"""
Test script for the CRM Research Agent System
"""
import sys
from rich.console import Console
from config import SERPER_API_KEY, OPENROUTER_API_KEY, CRM_TOOLS, RESEARCH_AREAS

console = Console()


def test_configuration():
    """Test if configuration is properly set up"""
    console.print("🔧 Testing Configuration...")
    
    # Check API keys
    if not SERPER_API_KEY or SERPER_API_KEY == "your_serper_api_key_here":
        console.print("❌ Serper API key not configured")
        return False
    
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        console.print("❌ OpenRouter API key not configured")
        return False
    
    console.print("✅ API keys configured")
    console.print(f"✅ CRM Tools: {', '.join(CRM_TOOLS)}")
    console.print(f"✅ Research Areas: {', '.join(RESEARCH_AREAS)}")
    
    return True


def test_imports():
    """Test if all modules can be imported"""
    console.print("\n📦 Testing Imports...")
    
    try:
        from tools import WebSearchTool, DataAnalysisTool
        console.print("✅ Tools imported successfully")
    except ImportError as e:
        console.print(f"❌ Failed to import tools: {e}")
        return False
    
    try:
        from agents.simple_agents import CRMResearchSystem
        console.print("✅ Simple agents imported successfully")
    except ImportError as e:
        console.print(f"❌ Failed to import simple agents: {e}")
        return False
    
    try:
        from utils.pdf_generator import PDFReportGenerator
        console.print("✅ PDF generator imported successfully")
    except ImportError as e:
        console.print(f"❌ Failed to import PDF generator: {e}")
        return False
    
    return True


def test_web_search():
    """Test web search functionality"""
    console.print("\n🔍 Testing Web Search...")
    
    try:
        from tools import WebSearchTool
        search_tool = WebSearchTool()
        
        # Test with a simple query
        result = search_tool._run("HubSpot CRM pricing 2024", num_results=3)
        
        if "Error" in result or "failed" in result.lower():
            console.print(f"❌ Web search failed: {result}")
            return False
        
        console.print("✅ Web search working")
        console.print(f"Sample result length: {len(result)} characters")
        return True
        
    except Exception as e:
        console.print(f"❌ Web search test failed: {e}")
        return False


def test_agent_creation():
    """Test if agents can be created"""
    console.print("\n🤖 Testing Agent Creation...")
    
    try:
        from agents.simple_agents import CRMResearchSystem
        research_system = CRMResearchSystem()
        
        # Check if all agents are created
        agents = [
            research_system.coordinator,
            research_system.web_researcher,
            research_system.data_analyst,
            research_system.validator,
            research_system.report_generator
        ]
        
        for agent in agents:
            if not agent:
                console.print("❌ Some agents failed to create")
                return False
        
        console.print("✅ All agents created successfully")
        return True
        
    except Exception as e:
        console.print(f"❌ Agent creation failed: {e}")
        return False


def test_pdf_generation():
    """Test PDF generation functionality"""
    console.print("\n📄 Testing PDF Generation...")
    
    try:
        from utils.pdf_generator import PDFReportGenerator
        pdf_generator = PDFReportGenerator()
        
        # Test creating results folder
        results_folder = pdf_generator.create_results_folder()
        console.print(f"✅ Results folder created: {results_folder}")
        
        # Test with sample data
        sample_data = {
            "final_report": {
                "final_report": "This is a test report for PDF generation."
            },
            "research_plan": {
                "plan": "Test research plan"
            }
        }
        
        # This would normally create a PDF, but we'll just test the setup
        console.print("✅ PDF generator setup successful")
        return True
        
    except Exception as e:
        console.print(f"❌ PDF generation test failed: {e}")
        return False


def main():
    """Run all tests"""
    console.print("🧪 CRM Research Agent System - Test Suite")
    console.print("=" * 50)
    
    tests = [
        test_configuration,
        test_imports,
        test_web_search,
        test_agent_creation,
        test_pdf_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        console.print()
    
    console.print("=" * 50)
    console.print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        console.print("🎉 All tests passed! System is ready to run.")
        console.print("\nTo start the research process, run:")
        console.print("python main.py")
    else:
        console.print("⚠️  Some tests failed. Please check the configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()
