"""PDF Generator for CV Builder.

This module handles the generation of PDF files from CV data.
"""

from .models import CV, PersonalInfo, Education, CompanyExperience, Project, Skill, Output # Updated import
from pathlib import Path
from .styles import get_style
import os
from enum import Enum

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, ListFlowable, ListItem, Flowable
from typing import Callable, Iterable, Any, List, cast # Added cast
from .paser.yaml import parse_yaml_file,validate_cv_data
from .generate_summary import generate_summary



class PDFGenerator:
    """Class to generate PDF files from CV data."""

    def __init__(self, output_path : str, cv_data: CV, style: str = "classic",page_size: str = "A4"):
        """Initialize the PDF generator with CV data.
        
        Args:
            output_path (str): Path to save the generated PDF.
            cv_data (CV): CV data object containing all the information.
            style (str): Style of the CV (default is "classic").
            page_size (str): Size of the PDF page (default is "A4").
        """
        self.output_path = Path(output_path)
        self.cv_data = cv_data
        #applying the style
        try:
            self.cv_style = get_style(style)
            self.styles = self.cv_style.get_styles()
        except ValueError as e:
            print(f"Error applying style: {e}")
            self.cv_style = get_style("classic").get_styles()

        # Set page size
        if page_size.lower() == "a4":
            self.page_size = A4
        elif page_size.lower() == "letter":
            self.page_size = letter
        else: 
            raise ValueError(f"Invalid page size: {page_size}. Choose 'A4' or 'letter'.")
        
        os.makedirs(self.output_path.parent, exist_ok=True)

        self.doc = SimpleDocTemplate(
            str(self.output_path),
            pagesize=self.page_size,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Elements to be added to the PDF
        self.elements: List[Flowable] = []

    def generate(self):
        """Generate the PDF document."""
        # Add all sections
        self._add_content()
        
        # Build the document
        self.doc.build(self.elements)
        
        return self.output_path
    
    def _add_content(self):
        """Add all CV content to the PDF."""
        # Add personal info
        personal_info = self.cv_data.personal_info
        if personal_info:
            self._add_personal_info(personal_info)
        
        # Add experience
        experience = self.cv_data.experience
        if experience:
            self._add_section('Experience', experience, self._format_company_experience)

        
        # Add education
        education = self.cv_data.education
        if education:
            self._add_section('Education', education, self._format_education)
        
        # Add skills
        skills = self.cv_data.skills
        if skills:
            self._add_skills(skills)
        
        # Add projects
        projects = self.cv_data.projects
        if projects:
            self._add_section('Projects', projects, self._format_project)
    

    def _add_personal_info(self, personal_info: PersonalInfo):
        """Add personal information to the PDF."""
        # Add name
        if personal_info.name:
            self.elements.append(Paragraph(personal_info.name, self.styles['Name']))
        
        # Add title if present
        if personal_info.title:
            self.elements.append(Paragraph(personal_info.title, self.styles.get('ContactInfo', self.styles['Normal']))) # Use ContactInfo or fallback to Normal
        
        # Combine contact information
        contact_parts: List[str] = []
        if personal_info.email:
            contact_parts.append(f"Email: {personal_info.email}")
        if personal_info.phone:
            contact_parts.append(f"Phone: {personal_info.phone}")
        if personal_info.location:
            contact_parts.append(f"Location: {personal_info.location}")
        if personal_info.website:
            contact_parts.append(f"Website: {personal_info.website}")
        if personal_info.linkedin:
            contact_parts.append(f"LinkedIn: {personal_info.linkedin}")
        
        contact_info = " | ".join(contact_parts)
        self.elements.append(Paragraph(contact_info, self.styles['ContactInfo']))

        if personal_info.summary:
            self.elements.append(Paragraph("Summary", self.styles['SectionHeading'])) # Add a section heading for summary
            self.elements.append(Paragraph(personal_info.summary, self.styles['Normal']))
        # Add a spacer after personal info
        
    def _add_section(
        self,
        title: str,
        items: Iterable[Any],
        formatter: Callable[[Any], None]
    ) -> None:
        """Add a section to the PDF with formatted items."""
        self.elements.append(Paragraph(title, self.styles['SectionHeading']))
        
        for item in items:
            formatter(item)

    def _format_company_experience(self, company_exp: CompanyExperience):
        """Format a company experience entry, including all its roles."""
        # Company name and optional location
        company_text = company_exp.company
        if company_exp.location:
            company_text += f" ({company_exp.location})"
        self.elements.append(Paragraph(company_text, self.styles['ExperienceTitle'])) # Style for company name
        
        for role in company_exp.roles:
            # Role title
            self.elements.append(Paragraph(role.title, self.styles.get('RoleTitle', self.styles['ExperienceDetails']))) # Use RoleTitle or fallback to ExperienceDetails

            # Dates for the role
            dates = f"{role.start_date} - {role.end_date or 'Present'}"
            if role.location: # Role-specific location
                dates += f" | {role.location}"
            self.elements.append(Paragraph(dates, self.styles['ExperienceDetails']))
            
            # Description for the role
            if role.description:
                self.elements.append(Paragraph(role.description, self.styles['Normal']))
            
            # Achievements for the role
            if role.achievements:
                items: List[Flowable] = []
                for achievement in role.achievements:
                    items.append(cast(Flowable, ListItem(Paragraph(achievement, self.styles['Normal'])))) # Cast ListItem to Flowable
                self.elements.append(ListFlowable(items, bulletType='bullet', leftIndent=12, bulletFontName='Helvetica-Bold', bulletFontSize=self.styles['Normal'].fontSize))
    
    def _format_education(self, edu: Education):
        """Format an education entry."""
        # Degree and institution
        degree_text = f"{edu.degree} - {edu.institution}"
        self.elements.append(Paragraph(degree_text, self.styles['ExperienceTitle'])) # Reusing ExperienceTitle for consistency

        # Dates
        dates = f"{edu.start_date} - {edu.end_date or 'Present'}"
        if edu.location:
            dates += f" | {edu.location}"
        self.elements.append(Paragraph(dates, self.styles['ExperienceDetails']))

        # GPA/Details
        if edu.gpa:
            self.elements.append(Paragraph(f"GPA: {edu.gpa}", self.styles['Normal']))
        if edu.details:
            self.elements.append(Paragraph(edu.details, self.styles['Normal']))
    
    def _add_skills(self, skills: List[Skill]):
        """Add skills section to the PDF."""
        self.elements.append(Paragraph('Skills', self.styles['SectionHeading']))
        
        print("Skills:")
        for skill_item in skills:
            # Skill category (e.g., Programming Languages)
            self.elements.append(Paragraph(skill_item.category, self.styles.get('ExperienceTitle', self.styles['Normal']))) # Reusing ExperienceTitle or similar
            
            print("Category:", skill_item)
            print(skill_item.category)
            # List of skills in that category
            self.elements.append(Paragraph((skill_item.name), self.styles['Normal']))
    
    def _format_project(self, project: Project):
        """Format a project entry."""
        # Project name and optional link
        project_name_text = project.name
        if project.link:
            project_name_text += f" (Link: {project.link})" # Basic link display
        self.elements.append(Paragraph(project_name_text, self.styles['ExperienceTitle']))

        # Dates
        if project.start_date and project.end_date:
            dates = f"{project.start_date} - {project.end_date or 'Ongoing'}"
            self.elements.append(Paragraph(dates, self.styles['ExperienceDetails']))

        # Description
        if project.description:
            self.elements.append(Paragraph(project.description, self.styles['Normal']))

        # Technologies used
        if project.technologies:
            tech_text = "Technologies: " + ", ".join(project.technologies)
            self.elements.append(Paragraph(tech_text, self.styles['Normal']))

        # Achievements/Key Features
        if project.achievements:
            items: List[Flowable] = []
            for achievement in project.achievements:
                items.append(cast(Flowable, ListItem(Paragraph(achievement, self.styles['Normal'])))) # Cast ListItem to Flowable
            self.elements.append(ListFlowable(items, bulletType='bullet', leftIndent=12, bulletFontName='Helvetica-Bold', bulletFontSize=self.styles['Normal'].fontSize))

class JobCategory(Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    FULLSTACK = "fullstack"

def generate_pdf(cv_data: CV, output_path: str, style: str = "classic", page_size: str = "A4") -> str:
    """Generate a PDF CV from the provided data.
    
    Args:
        cv_data: CV model containing the CV data
        output_path: Path where the PDF will be saved
        style: Style name for the CV (e.g., 'classic', 'modern', 'minimal')
        page_size: Size of the page ('A4' or 'letter')
        
    Returns:
        Path to the generated PDF file
    """
    generator = PDFGenerator(output_path, cv_data, style, page_size)
    return str(generator.generate())

def generate_cv_pdf_from_yaml(job_category: JobCategory, style: str = "classic", page_size: str = "A4", vacancy: str = "") -> Output:
    """Generate a PDF CV from a YAML file based on job category.

    Args:
        job_category: The category of the job (e.g., backend, frontend, fullstack).
        output_path: Path where the PDF will be saved. If None, a default path is generated.
        style: Style name for the CV (e.g., 'classic', 'modern', 'minimal')
        page_size: Size of the page ('A4' or 'letter')
        vacancy: The job vacancy for which the CV is being tailored

    Returns:
        Path to the generated PDF file
    """
    yaml_file_name = f"{job_category.value}.yaml"
    yaml_path = os.path.join("generate_cv", "documents", "yaml", yaml_file_name)
    
    yaml_data = parse_yaml_file(yaml_path)
    cv_data = validate_cv_data(yaml_data)
    
    
    output_file_name = f"Muhamad_Wijayanto_{job_category.value}.pdf"
    output_path = os.path.join("generate_cv", "documents", "pdf", output_file_name)

    if vacancy:
        summary = generate_summary(cv_data, vacancy)
        # Optionally, you can attach the summary to the cv_data object if your PDFGenerator supports it
        cv_data.personal_info.summary = summary
        print(f"Generated summary: {summary}")
        print(f"Summary added to CV data: {cv_data.personal_info.summary}")
        # Add AI summary generation logic here

    # Generate the PDF
    pdf_path = generate_pdf(cv_data, output_path, style, page_size)
    output = Output(pdf_path=pdf_path, summary=cv_data.personal_info.summary or "")
    return output

def generate_cv_pdf(vacancy: str, roles: JobCategory) -> Output:
    """
    Generates a CV PDF based on vacancy and job role.
    Uses default style, page size, and output path generation.

    Args:
        vacancy: The job vacancy for which the CV is being tailored.
        roles: The job category (e.g., backend, frontend, fullstack).

    Returns:
        Path to the generated PDF file.
    """
    # Call the more detailed function with default values for other parameters
    output = generate_cv_pdf_from_yaml(
        job_category=roles,
        vacancy=vacancy
        # output_path, style, and page_size will use their defaults
        # from generate_cv_pdf_from_yaml
    )
    return output


