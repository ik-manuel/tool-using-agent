import os
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew
from dotenv import load_dotenv
from tools import ListDirectoryTool, ReadFileTool, WebSearchTool, WriteReportTool
import time


load_dotenv()

@CrewBase
class ProjectAnalyzerCrew:
    """Project Analyzer Crew - analyses any project directory."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        self.llm = LLM(
            model=os.getenv("MODEL", "groq/llama-3.1-8b-instant"),
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.3,
        )

        self.ollama = LLM(
            model="ollama/qwen3-coder:480b-cloud",
            base_url="http://localhost:11434"
        )

    @agent
    def project_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["project_analyst"],
            tools=[
                ListDirectoryTool(),
                ReadFileTool(),
                WebSearchTool(),
                WriteReportTool(),
            ],
            llm=self.ollama,
            # llm=self.llm,
            verbose=True,
            max_iter=20, # file analysis needs more iterations
        )
    
    @task
    def analyze_project(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_project"],
            agent=self.project_analyst(),
        )
    
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=False,
            verbose=True,
        )
    


    # def run_with_retry(self, inputs: dict, max_retries: int = 3) -> str:
    #     for attempt in range(max_retries):
    #         try:
    #             return self.crew().kickoff(inputs=inputs)
    #         except Exception as e:
    #             if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
    #                 wait = 30 * (attempt + 1)
    #                 print(f"\n⏳ Rate limit hit. Waiting {wait}s before retry {attempt + 2}/{max_retries}...")
    #                 time.sleep(wait)
    #             else:
    #                 raise
    
