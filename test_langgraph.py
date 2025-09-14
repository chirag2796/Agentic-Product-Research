"""
Test script for the LangGraph-based CRM Research System
"""
from rich.console import Console
from agents.langgraph_agents import CRMResearchOrchestrator

console = Console()

def test_langgraph_system():
    """Test the LangGraph system"""
    console.print("🧪 Testing LangGraph CRM Research System")
    console.print("=" * 50)
    
    try:
        # Initialize system
        console.print("🔧 Initializing LangGraph orchestrator...")
        orchestrator = CRMResearchOrchestrator()
        
        # Test with a simple query
        test_query = "Compare HubSpot and Zoho CRM for small businesses"
        console.print(f"🔍 Testing with query: {test_query}")
        
        # Run research
        console.print("🤖 Running agentic research...")
        results = orchestrator.run_research(test_query)
        
        # Check results
        if 'final_report' in results and results['final_report']:
            console.print("✅ LangGraph system working!")
            console.print(f"📊 Report length: {len(results['final_report'])} characters")
            console.print(f"🤖 Agent interactions: {len(results.get('agent_messages', []))}")
            
            # Show agent messages
            console.print("\n🤖 Agent Communication Log:")
            for i, message in enumerate(results.get('agent_messages', []), 1):
                console.print(f"  {i}. {message}")
            
            return True
        else:
            console.print("❌ LangGraph system failed - no report generated")
            return False
            
    except Exception as e:
        console.print(f"❌ LangGraph system test failed: {e}")
        import traceback
        console.print(f"Full error: {traceback.format_exc()}")
        return False

def main():
    """Run LangGraph test"""
    success = test_langgraph_system()
    
    if success:
        console.print("\n🎉 LangGraph system is working correctly!")
        console.print("You can now run the main system with:")
        console.print("python main_langgraph.py")
    else:
        console.print("\n⚠️  LangGraph system needs attention.")

if __name__ == "__main__":
    main()
