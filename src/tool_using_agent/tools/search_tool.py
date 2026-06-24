import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query string optimised for web search")

class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = """Search the internet for current information, best practices,
    documentation, trends, or any topic that requires up-to-date knowledge.
    Use for: best practices, security advice, library docs, industry trends, research topics."""
    args_schema: type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        try:
            client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

            response = client.search(
                query=query,
                max_results=3,
                search_depth="basic",
                include_answer=True,    # Tavily generates a direct answer
            )

            output = f'Search results for "{query}":\n\n'

            # Include Tavily's direct answer if available
            if response.get("answer"):
                output += f"Quick Answer: {response['answer']}\n\n"

                # Include top results
                for i, result in enumerate(response.get("results", [], 1)):
                    output += f"{i}. {result.get('title', 'No title')}\n"
                    output += f"   URL: {result.get('url', '')}\n"
                    output += f"   {result.get('content', '')[:300]}\n\n"

                return output.strip() if output.strip() else f"No results found for {query}"
            
        except Exception as e:
            return f"Search failed: {str(e)}"