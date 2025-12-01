"""
Web Search Tool for fetching real-time medical information
"""

import os
import requests
from typing import Dict, Any, Optional


class WebSearchTool:
    """Tool for searching the web for medical guidelines and information"""
    
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY", "")
        self.base_url = "https://google.serper.dev/search"
    
    async def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """
        Search the web for medical information
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            Dictionary with search results
        """
        if not self.api_key:
            # Fallback: return empty results if no API key
            return {
                "success": False,
                "results": [],
                "message": "SERPER_API_KEY not configured"
            }
        
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": num_results
            }
            
            response = requests.post(self.base_url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant information
            results = []
            if "organic" in data:
                for item in data["organic"][:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "link": item.get("link", ""),
                        "snippet": item.get("snippet", ""),
                        "position": item.get("position", 0)
                    })
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "total_results": len(results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "results": [],
                "error": str(e)
            }
    
    def search_medical_guidelines(self, symptom: str, year: int = 2024) -> Dict[str, Any]:
        """
        Search for medical guidelines for a specific symptom
        
        Args:
            symptom: Symptom or condition
            year: Year for guidelines (default: 2024)
            
        Returns:
            Search results
        """
        query = f"{symptom} medical guidelines {year} CDC WHO"
        return self.search(query, num_results=3)

