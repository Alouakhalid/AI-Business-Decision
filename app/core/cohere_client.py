import requests
from typing import List, Dict, Any
from app.config import config

class CohereRerankClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.COHERE_API_KEY
        self.v2_url = "https://api.cohere.com/v2/rerank"
        self.v1_url = "https://api.cohere.ai/v1/rerank"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        """Reranks a list of document strings based on relevance to query using Cohere Rerank API."""
        if not documents:
            return []
        
        # Limit top_n to len(documents)
        top_n = min(top_n, len(documents))
        
        payload = {
            "model": "rerank-v3.5",
            "query": query,
            "documents": documents,
            "top_n": top_n
        }

        try:
            res = requests.post(self.v2_url, json=payload, headers=self.headers, timeout=15)
            if res.status_code == 200:
                results_data = res.json().get("results", [])
                output = []
                for item in results_data:
                    idx = item.get("index")
                    score = item.get("relevance_score", 0.0)
                    output.append({
                        "document": documents[idx],
                        "index": idx,
                        "relevance_score": round(score, 4)
                    })
                return output
            else:
                # Fallback to v1 API
                res_v1 = requests.post(self.v1_url, json=payload, headers=self.headers, timeout=15)
                if res_v1.status_code == 200:
                    results_data = res_v1.json().get("results", [])
                    output = []
                    for item in results_data:
                        idx = item.get("index")
                        score = item.get("relevance_score", 0.0)
                        output.append({
                            "document": documents[idx],
                            "index": idx,
                            "relevance_score": round(score, 4)
                        })
                    return output
                else:
                    print(f"Cohere rerank error ({res.status_code}): {res.text[:150]}")
                    return [{"document": doc, "index": i, "relevance_score": 0.5} for i, doc in enumerate(documents[:top_n])]
        except Exception as e:
            print(f"Exception during Cohere rerank: {e}")
            return [{"document": doc, "index": i, "relevance_score": 0.5} for i, doc in enumerate(documents[:top_n])]

cohere_client = CohereRerankClient()
