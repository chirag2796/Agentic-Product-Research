"""
Test script for the Fallback CRM Research System
"""
from rich.console import Console
from agents.fallback_agents import FallbackCRMResearchSystem

console = Console()

def test_fallback_system():
    """Test the fallback system"""
    console.print("🧪 Testing Fallback CRM Research System")
    console.print("=" * 50)
    
    try:
        # Initialize fallback system
        console.print("🔧 Initializing fallback system...")
        research_system = FallbackCRMResearchSystem()
        
        # Run research
        console.print("🔍 Running research...")
        results = research_system.run_research()
        
        # Check results
        if 'final_report' in results and 'final_report' in results['final_report']:
            final_report = results['final_report']['final_report']
            console.print("✅ Fallback system working!")
            console.print(f"📊 Report length: {len(final_report)} characters")
            
            # Show a snippet
            snippet = final_report[:200] + "..." if len(final_report) > 200 else final_report
            console.print(f"📝 Report snippet: {snippet}")
            
            return True
        else:
            console.print("❌ Fallback system failed - no report generated")
            return False
            
    except Exception as e:
        console.print(f"❌ Fallback system test failed: {e}")
        return False

def main():
    """Run fallback test"""
    success = test_fallback_system()
    
    if success:
        console.print("\n🎉 Fallback system is working correctly!")
        console.print("You can now run the main system and it will automatically")
        console.print("switch to fallback mode if LLM credits are exhausted.")
    else:
        console.print("\n⚠️  Fallback system needs attention.")

if __name__ == "__main__":
    main()
