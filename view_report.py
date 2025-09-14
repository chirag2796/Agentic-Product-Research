"""
Simple script to open the latest HTML report in the browser
"""
import os
import webbrowser
import glob
from pathlib import Path

def find_latest_html_report():
    """Find the most recent HTML report"""
    # Look for HTML files in results folder
    html_files = glob.glob("results/run_*/langgraph_crm_report_*.html")
    
    if not html_files:
        # Try fallback HTML files
        html_files = glob.glob("results/run_*/fallback_crm_report_*.html")
    
    if not html_files:
        return None
    
    # Sort by modification time and get the latest
    latest_file = max(html_files, key=os.path.getmtime)
    return latest_file

def main():
    """Open the latest HTML report in browser"""
    latest_report = find_latest_html_report()
    
    if latest_report:
        print(f"🌐 Opening latest report: {latest_report}")
        # Convert to absolute path
        abs_path = os.path.abspath(latest_report)
        webbrowser.open(f"file://{abs_path}")
        print("✅ Report opened in your default browser!")
    else:
        print("❌ No HTML reports found. Run the research system first:")
        print("   python main_langgraph.py")
        print("   or")
        print("   python run_fallback.py")

if __name__ == "__main__":
    main()
