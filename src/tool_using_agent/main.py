import crewai.llms.cache as _crewai_cache
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

from crew import ProjectAnalyzerCrew
import os
import sys
from dotenv import load_dotenv

load_dotenv()



if __name__ == "__main__":
    print("=== Project Analyzer CrewAI ===\n")
    
    project_path = input("Enter project path: ").strip()
    
    if not os.path.exists(project_path):
        print(f"❌ Error: Path '{project_path}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(project_path):
        print(f"❌ Error: '{project_path}' is a file, not a directory.")
        sys.exit(1)

    analysis_goal = input("What do you want to analyze? (suggest improvements / code review / security audit / etc): ").strip()

    print("\n🚀 Starting analysis with CrewAI...\n")

    inputs = {
        "project_path": project_path,
        "analysis_goal": analysis_goal or "suggest improvements"
    }

    try:
        result = ProjectAnalyzerCrew().crew().kickoff(inputs=inputs)
        # result = ProjectAnalyzerCrew().run_with_retry(inputs=inputs)
        
        print("\n" + "="*100)
        print(result)
        print("="*100)
        print("\n✅ Analysis completed! Check the 'reports/' folder for the saved report.")
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")