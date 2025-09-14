"""
PDF Generation utility for CRM Research Results
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from typing import Dict, Any


class PDFReportGenerator:
    """Generate PDF reports from research results"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
        
        # Timestamp style
        self.styles.add(ParagraphStyle(
            name='Timestamp',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
    
    def create_results_folder(self) -> str:
        """Create results folder if it doesn't exist"""
        results_folder = "results"
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        return results_folder
    
    def generate_pdf_report(self, research_data: Dict[str, Any], filename: str = None) -> str:
        """Generate PDF report from research data"""
        # Create results folder
        results_folder = self.create_results_folder()
        
        # Generate filename with timestamp if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crm_research_report_{timestamp}.pdf"
        
        filepath = os.path.join(results_folder, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("CRM Research Report", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Timestamp
        timestamp_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"Generated on {timestamp_str}", self.styles['Timestamp']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        if 'final_report' in research_data:
            final_report = research_data['final_report']
            if 'final_report' in final_report:
                story.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
                story.append(Paragraph(final_report['final_report'], self.styles['CustomBody']))
                story.append(Spacer(1, 20))
        
        # Research Plan
        if 'research_plan' in research_data:
            story.append(Paragraph("Research Plan", self.styles['CustomSubtitle']))
            plan = research_data['research_plan']
            if 'plan' in plan:
                story.append(Paragraph(plan['plan'], self.styles['CustomBody']))
            story.append(Spacer(1, 20))
        
        # Individual CRM Research Results
        if 'research_results' in research_data:
            story.append(Paragraph("Research Results", self.styles['CustomSubtitle']))
            
            for result in research_data['research_results']:
                crm_tool = result.get('crm_tool', 'Unknown CRM')
                story.append(Paragraph(f"{crm_tool} Analysis", self.styles['Heading3']))
                
                if 'analysis' in result:
                    story.append(Paragraph(result['analysis'], self.styles['CustomBody']))
                
                story.append(Spacer(1, 12))
        
        # Analysis Data
        if 'analysis_data' in research_data:
            story.append(PageBreak())
            story.append(Paragraph("Comparative Analysis", self.styles['CustomSubtitle']))
            
            analysis = research_data['analysis_data']
            if 'comparison_analysis' in analysis:
                story.append(Paragraph(analysis['comparison_analysis'], self.styles['CustomBody']))
        
        # Validation Results
        if 'validated_data' in research_data:
            story.append(PageBreak())
            story.append(Paragraph("Validation Results", self.styles['CustomSubtitle']))
            
            validation = research_data['validated_data']
            if 'validation_results' in validation:
                story.append(Paragraph(validation['validation_results'], self.styles['CustomBody']))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def generate_summary_pdf(self, research_data: Dict[str, Any], filename: str = None) -> str:
        """Generate a concise summary PDF"""
        results_folder = self.create_results_folder()
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crm_research_summary_{timestamp}.pdf"
        
        filepath = os.path.join(results_folder, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Title
        story.append(Paragraph("CRM Research Summary", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Timestamp
        timestamp_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"Generated on {timestamp_str}", self.styles['Timestamp']))
        story.append(Spacer(1, 20))
        
        # Extract key information for summary
        if 'final_report' in research_data:
            final_report = research_data['final_report']
            if 'final_report' in final_report:
                # Try to extract key sections
                report_text = final_report['final_report']
                
                # Split into sections and take the most important parts
                sections = report_text.split('\n\n')
                for section in sections[:5]:  # Take first 5 sections
                    if section.strip():
                        story.append(Paragraph(section.strip(), self.styles['CustomBody']))
                        story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        
        return filepath
