"""
Web Search Tool using Serper API
"""
import requests
import json
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from config import SERPER_API_KEY, SERPER_BASE_URL


class WebSearchInput(BaseModel):
    """Input for web search tool"""
    query: str = Field(..., description="Search query to execute")
    num_results: int = Field(default=10, description="Number of results to return")


class WebSearchTool:
    name: str = "web_search"
    description: str = "Search the web for real-time information about CRM tools, pricing, features, and comparisons"
    args_schema: type[BaseModel] = WebSearchInput

    def _run(self, query: str, num_results: int = 10) -> str:
        """Execute web search using Serper API"""
        try:
            headers = {
                'X-API-KEY': SERPER_API_KEY,
                'Content-Type': 'application/json'
            }
            
            payload = {
                'q': query,
                'num': num_results
            }
            
            response = requests.post(
                f"{SERPER_BASE_URL}/search",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_search_results(data)
            else:
                return f"Search failed with status code: {response.status_code}"
                
        except Exception as e:
            return f"Error during web search: {str(e)}"

    def _format_search_results(self, data: Dict[str, Any]) -> str:
        """Format search results into readable text"""
        results = []
        
        if 'organic' in data:
            for item in data['organic'][:5]:  # Limit to top 5 results
                title = item.get('title', 'No title')
                snippet = item.get('snippet', 'No description')
                link = item.get('link', 'No link')
                
                results.append(f"""
**{title}**
{snippet}
Source: {link}
---""")
        
        if 'answerBox' in data and data['answerBox']:
            answer = data['answerBox']
            results.insert(0, f"""
**Quick Answer:**
{answer.get('answer', 'No answer available')}
---""")
        
        return "\n".join(results) if results else "No search results found"
