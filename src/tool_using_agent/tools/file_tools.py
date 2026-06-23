from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class FileToolInput(BaseModel):
    """Input schema for FileToolInput"""
    argument: str = Field(..., description="File directory/folder path.")

class FileTools(BaseTool):
    name: str = "File Tools"
    description: str = (
        "File operational agent, Should read and analize filesystem"
    )
    args_schema = Type[BaseModel] = FileToolInput

    def _run(self, argument: str) -> str:
        return "This an example of file path"