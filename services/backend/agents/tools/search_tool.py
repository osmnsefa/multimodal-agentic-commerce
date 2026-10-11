from typing import List, Dict, Any

class SearchTool:
    """
    Tool used by AI agents to perform real-time catalog queries and similarity search.
    """
    def execute_search(self, query: str) -> List[Dict[str, Any]]:
        return [
            {"id": "prod-101", "name": "Aegis Pro Headset", "price": 199.99}
        ]
