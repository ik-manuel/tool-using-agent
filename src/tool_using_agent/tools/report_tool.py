from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional 
import os
from datetime import datetime

class WriteReportInput(BaseModel):
    content: str = Field(..., description="Full markdown content of the analysis report")
    project_name: Optional[str] = Field(None, description="Optional project name for the report filename")

class WriteReportTool(BaseTool):
    name: str = "Write Report"
    description: str = "Saves the final analysis report as a timestamped markdown file in the 'reports' folder."
    args_schema: type[BaseModel] = WriteReportInput

    def _run(self, content: str, project_name: Optional[str] = None) -> str:
        try:
            # Create reports directory if it doesn't exist
            reports_dir = os.path.join(os.getcwd(), "reports")
            os.makedirs(reports_dir, exist_ok=True)

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = project_name.replace(" ", "_").lower() if project_name else "project"
            filename = f"analysis_{safe_name}_{timestamp}.md"
            filepath = os.path.join(reports_dir, filename)

            # Add metadata header to every report
            header = "# Project Analysis Report\n\n"
            header += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            header += f"**Project:** {project_name or 'Unknown'}\n\n---\n\n"

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header + content)

            return f"✅ Report successfully saved to: {filepath}"
        
        except Exception as e:
            return f"Failed to write report: {str(e)}"