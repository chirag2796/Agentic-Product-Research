"""
HTML Report Generator for CRM Research Results
Creates beautiful, responsive HTML reports with CSS styling
"""
import os
from datetime import datetime
from typing import Dict, Any


class HTMLReportGenerator:
    """Generate beautiful HTML reports for CRM research results"""
    
    def __init__(self):
        self.css_styles = self._get_css_styles()
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report"""
        return """
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f8f9fa;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: white;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                border-radius: 10px;
                margin-top: 20px;
                margin-bottom: 20px;
            }
            
            .header {
                text-align: center;
                padding: 30px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 30px;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .header .subtitle {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .timestamp {
                text-align: center;
                color: #666;
                font-style: italic;
                margin-bottom: 30px;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            
            .section {
                margin-bottom: 40px;
                padding: 25px;
                background-color: #fff;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.05);
                border-left: 4px solid #667eea;
            }
            
            .section h2 {
                color: #667eea;
                font-size: 1.8em;
                margin-bottom: 20px;
                display: flex;
                align-items: center;
            }
            
            .section h2::before {
                content: "📊";
                margin-right: 10px;
                font-size: 1.2em;
            }
            
            .section h3 {
                color: #495057;
                font-size: 1.4em;
                margin: 20px 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #e9ecef;
            }
            
            .crm-comparison {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 25px;
                margin: 20px 0;
            }
            
            .crm-card {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: 1px solid #dee2e6;
            }
            
            .crm-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            
            .crm-card h4 {
                color: #495057;
                font-size: 1.5em;
                margin-bottom: 15px;
                text-align: center;
                padding: 10px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            
            .crm-card .feature {
                margin: 12px 0;
                padding: 8px 12px;
                background-color: white;
                border-radius: 6px;
                border-left: 3px solid #28a745;
            }
            
            .crm-card .feature strong {
                color: #495057;
                display: block;
                margin-bottom: 5px;
            }
            
            .comparison-table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            .comparison-table th {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }
            
            .comparison-table td {
                padding: 12px 15px;
                border-bottom: 1px solid #e9ecef;
            }
            
            .comparison-table tr:nth-child(even) {
                background-color: #f8f9fa;
            }
            
            .comparison-table tr:hover {
                background-color: #e3f2fd;
            }
            
            .agent-log {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }
            
            .agent-log h3 {
                color: #667eea;
                margin-bottom: 15px;
            }
            
            .agent-message {
                background-color: white;
                padding: 12px 15px;
                margin: 8px 0;
                border-radius: 6px;
                border-left: 4px solid #28a745;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .agent-message .agent-name {
                font-weight: bold;
                color: #495057;
            }
            
            .recommendations {
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }
            
            .recommendations h3 {
                color: #1976d2;
                margin-bottom: 15px;
            }
            
            .recommendations ul {
                list-style: none;
                padding: 0;
            }
            
            .recommendations li {
                background-color: white;
                margin: 8px 0;
                padding: 12px 15px;
                border-radius: 6px;
                border-left: 4px solid #1976d2;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            .recommendations li::before {
                content: "💡";
                margin-right: 8px;
            }
            
            .footer {
                text-align: center;
                padding: 30px;
                background-color: #495057;
                color: white;
                border-radius: 8px;
                margin-top: 40px;
            }
            
            .footer p {
                margin: 5px 0;
            }
            
            .badge {
                display: inline-block;
                padding: 4px 8px;
                background-color: #28a745;
                color: white;
                border-radius: 4px;
                font-size: 0.8em;
                font-weight: bold;
                margin-left: 8px;
            }
            
            .badge.warning {
                background-color: #ffc107;
                color: #212529;
            }
            
            .badge.info {
                background-color: #17a2b8;
            }
            
            @media (max-width: 768px) {
                .container {
                    margin: 10px;
                    padding: 15px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .crm-comparison {
                    grid-template-columns: 1fr;
                }
                
                .comparison-table {
                    font-size: 0.9em;
                }
            }
        </style>
        """
    
    def generate_html_report(self, research_data: Dict[str, Any], filename: str = None, custom_folder: str = None) -> str:
        """Generate comprehensive HTML report"""
        # Use custom folder if provided, otherwise create results folder
        if custom_folder:
            results_folder = custom_folder
        else:
            results_folder = self.create_results_folder()
        
        # Generate filename with timestamp if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crm_research_report_{timestamp}.html"
        
        filepath = os.path.join(results_folder, filename)
        
        # Generate HTML content
        html_content = self._generate_html_content(research_data)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def _generate_html_content(self, research_data: Dict[str, Any]) -> str:
        """Generate the HTML content"""
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CRM Research Report - {timestamp}</title>
            {self.css_styles}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🤖 AI Agent CRM Research Report</h1>
                    <div class="subtitle">Comprehensive Analysis for Small to Mid-size B2B Businesses</div>
                </div>
                
                <div class="timestamp">
                    Generated on {timestamp}
                </div>
        """
        
        # Add executive summary
        if 'final_report' in research_data:
            html += self._generate_executive_summary(research_data['final_report'])
        
        # Add research methodology
        html += self._generate_methodology_section()
        
        # Add CRM comparison
        if 'analysis_results' in research_data:
            html += self._generate_crm_comparison(research_data['analysis_results'])
        
        # Add comparison table
        html += self._generate_comparison_table()
        
        # Add recommendations
        html += self._generate_recommendations_section()
        
        # Add agent communication log
        if 'agent_messages' in research_data:
            html += self._generate_agent_log(research_data['agent_messages'])
        
        # Add validation results
        if 'validation_results' in research_data:
            html += self._generate_validation_section(research_data['validation_results'])
        
        # Add footer
        html += self._generate_footer()
        
        html += """
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_executive_summary(self, final_report: str) -> str:
        """Generate executive summary section"""
        # Extract key parts from the report
        lines = final_report.split('\n')
        summary_lines = []
        
        for line in lines[:10]:  # Take first 10 lines
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
        
        summary_text = ' '.join(summary_lines)
        
        return f"""
        <div class="section">
            <h2>Executive Summary</h2>
            <p>{summary_text}</p>
        </div>
        """
    
    def _generate_methodology_section(self) -> str:
        """Generate research methodology section"""
        return """
        <div class="section">
            <h2>Research Methodology</h2>
            <div class="crm-comparison">
                <div class="crm-card">
                    <h4>🔬 Framework</h4>
                    <div class="feature">
                        <strong>Agentic AI System</strong>
                        LangGraph StateGraph with 7 autonomous agents
                    </div>
                </div>
                <div class="crm-card">
                    <h4>🌐 Data Sources</h4>
                    <div class="feature">
                        <strong>Real-time Research</strong>
                        Official websites, review platforms, comparison articles
                    </div>
                </div>
                <div class="crm-card">
                    <h4>✅ Validation</h4>
                    <div class="feature">
                        <strong>Quality Assurance</strong>
                        Multi-agent validation and quality control
                    </div>
                </div>
            </div>
        </div>
        """
    
    def _generate_crm_comparison(self, analysis_results: Dict[str, Any]) -> str:
        """Generate CRM comparison cards"""
        html = """
        <div class="section">
            <h2>CRM Tool Analysis</h2>
            <div class="crm-comparison">
        """
        
        for crm_tool, analysis in analysis_results.items():
            html += f"""
                <div class="crm-card">
                    <h4>{crm_tool}</h4>
                    <div class="feature">
                        <strong>💰 Pricing</strong>
                        {analysis.get('pricing', 'Information available on website')}
                    </div>
                    <div class="feature">
                        <strong>⚡ Key Features</strong>
                        {analysis.get('features', 'Core CRM functionality')}
                    </div>
                    <div class="feature">
                        <strong>🔗 Integrations</strong>
                        {analysis.get('integrations', 'Integration capabilities available')}
                    </div>
                    <div class="feature">
                        <strong>⚠️ Limitations</strong>
                        {analysis.get('limitations', 'Standard limitations apply')}
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_comparison_table(self) -> str:
        """Generate comparison table"""
        return """
        <div class="section">
            <h2>Quick Comparison</h2>
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>CRM Tool</th>
                        <th>Free Tier</th>
                        <th>Key Strengths</th>
                        <th>Best For</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>HubSpot</strong></td>
                        <td><span class="badge">Yes</span></td>
                        <td>Marketing automation, user-friendly</td>
                        <td>Small-medium businesses</td>
                        <td>⭐⭐⭐⭐⭐</td>
                    </tr>
                    <tr>
                        <td><strong>Zoho</strong></td>
                        <td><span class="badge">Yes</span></td>
                        <td>Value for money, comprehensive suite</td>
                        <td>Cost-conscious businesses</td>
                        <td>⭐⭐⭐⭐</td>
                    </tr>
                    <tr>
                        <td><strong>Salesforce</strong></td>
                        <td><span class="badge warning">Limited</span></td>
                        <td>Enterprise features, customization</td>
                        <td>Large businesses</td>
                        <td>⭐⭐⭐⭐⭐</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
    
    def _generate_recommendations_section(self) -> str:
        """Generate recommendations section"""
        return """
        <div class="section">
            <h2>Recommendations</h2>
            <div class="recommendations">
                <h3>🎯 Business Size Recommendations</h3>
                <ul>
                    <li><strong>Small Businesses (1-10 employees):</strong> HubSpot (free tier + marketing features) or Zoho (cost-effective)</li>
                    <li><strong>Medium Businesses (11-50 employees):</strong> HubSpot or Zoho (depending on marketing needs)</li>
                    <li><strong>Growing Businesses (50+ employees):</strong> Salesforce (enterprise features) or HubSpot Enterprise</li>
                </ul>
            </div>
        </div>
        """
    
    def _generate_agent_log(self, agent_messages: list) -> str:
        """Generate agent communication log"""
        html = """
        <div class="section">
            <h2>Agent Communication Log</h2>
            <div class="agent-log">
                <h3>🤖 Agent Interactions</h3>
        """
        
        for i, message in enumerate(agent_messages, 1):
            # Extract agent name and message
            if ':' in message:
                agent_name, message_text = message.split(':', 1)
                html += f"""
                <div class="agent-message">
                    <span class="agent-name">{agent_name.strip()}</span>: {message_text.strip()}
                </div>
                """
            else:
                html += f"""
                <div class="agent-message">
                    {message}
                </div>
                """
        
        html += f"""
                <p><strong>Total agent interactions:</strong> {len(agent_messages)}</p>
            </div>
        </div>
        """
        
        return html
    
    def _generate_validation_section(self, validation_results: Dict[str, Any]) -> str:
        """Generate validation section"""
        html = """
        <div class="section">
            <h2>Validation Results</h2>
            <div class="recommendations">
                <h3>✅ Quality Assurance</h3>
                <ul>
        """
        
        if 'recommendations' in validation_results:
            for rec in validation_results['recommendations']:
                html += f"<li>{rec}</li>"
        
        html += """
                </ul>
            </div>
        </div>
        """
        
        return html
    
    def _generate_footer(self) -> str:
        """Generate footer"""
        return """
        <div class="footer">
            <p><strong>🤖 AI Agent Research System</strong></p>
            <p>Powered by LangGraph StateGraph Framework</p>
            <p>Generated by autonomous AI agents for business intelligence</p>
        </div>
        """
    
    def create_results_folder(self) -> str:
        """Create results folder if it doesn't exist"""
        results_folder = "results"
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        return results_folder
