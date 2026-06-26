from crewai.tools import BaseTool
from pydantic import BaseModel, Field
# from typing import List, Optional
import os
# from datetime import datetime

# ====================== SAFETY CONSTRAINTS ======================
BLOCKED_PATHS = ['.env', '.git', 'node_modules', '__pycache__', '.venv', 'venv', 'vendor']
MAX_FILE_SIZE_KB = 50
ALLOWED_EXTENSIONS = ['.py', '.php', '.js', '.ts', '.md', '.css', '.json', '.yaml', '.txt']

# helper function
def is_path_blocked(path: str) -> bool:
    """Check if path contains any blocked keywords."""
    path_lower = path.lower()
    return any(blocked in path_lower for blocked in BLOCKED_PATHS)

def is_allowed_extension(file_path: str) -> bool:
    """Check if file has allowed extension."""
    return any(file_path.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def get_file_size_kb(file_path: str) -> float:
    """Return file size in KB."""
    try:
        return os.path.getsize(file_path) / 1024
    except:
        return 0


# ====================== LIST DIRECTORY TOOL ======================
class ListDirectoryInput(BaseModel):
    """Input schema for FileToolInput"""
    folder_path: str = Field(..., description="Path to the project folder")

class ListDirectoryTool(BaseTool):
    name: str = "List Directory"
    description: str = """Safely lists the directory structure of a project.
    Respects blocked paths and only show allowed file types."""
    args_schema: type[BaseModel] = ListDirectoryInput

    def _run(self, folder_path: str) -> str:
        try:
            abs_path = os.path.abspath(folder_path)
            if not os.path.exists(abs_path):
                return f"Error: Path '{abs_path}' does not exist."
            
            if not os.path.isdir(abs_path):
                return f"Error: '{abs_path}' is not a directory."
            
            structure = []
            structure.append(f"Projects Root: {abs_path}\n")

            for root, dirs, files in os.walk(abs_path):
                # Skip blocked directories
                dirs[:] = [d for d in dirs if not is_path_blocked(d)]

                level = root.replace(abs_path, '').count(os.sep)
                indent = ' ' * 4 * level
                relative_root = os.path.relpath(root, abs_path)

                if relative_root == '.':
                    structure.append("📁 .")
                else:
                    structure.append(f"{indent}📁 {os.path.basename(root)}")

                # Show files (limited depth for cleanliness)
                if level <= 4:  # Limit depth to avoid huge output
                    for file in sorted(files):
                        file_path = os.path.join(root, file)
                        if is_allowed_extension(file_path) and not is_path_blocked(file):
                            structure.append(f"{indent}    📄 {file} → FULL PATH: {os.path.join(root, file)}")

            return "\n".join(structure[:300]) # Limit total lines
        
        except Exception as e:
            return f"Directory listing error: {str(e)}"
    

# ====================== READ FILE TOOL ======================
class ReadFileInput(BaseModel):
    file_path: str = Field(..., description="Full absolute path to the file you want to read")

class ReadFileTool(BaseTool):
    name: str = "Read File"
    description: str = """Reads the content of a single file with strict safety checks.
     Only allowed extensions, size limit, and allowed paths are permitted."""
    args_schema: type[BaseModel] = ReadFileInput

    def _run(self, file_path: str) -> str:
        try:
            abs_path = os.path.abspath(file_path)

            # Safety checks
            if is_path_blocked(abs_path):
                return "Access denied: Path contains blocked keyword."
            
            if not os.path.exists(abs_path):
                return f"Error: File '{abs_path}' does not exist."
            
            if not os.path.isfile(abs_path):
                return f"Error: '{abs_path}' is not a file."
            
            if not is_allowed_extension(abs_path):
                return f"Error: file type not allowed. Allowed: {ALLOWED_EXTENSIONS}"
            
            size_kb = get_file_size_kb(abs_path)
            if size_kb > MAX_FILE_SIZE_KB:
                return f"Error: File too large ({size_kb:.1f} KB) . Maximum allowed: {MAX_FILE_SIZE_KB} KB."
            
            with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            rel_path = os.path.relpath(abs_path, start=os.getcwd())
            return f"--- File: {rel_path} ---\n\n{content}"
        
        except Exception as e:
            return f"Failed to read file: {str(e)}"
        