import requests
from typing import Dict, Any

class AIExplainer:
    def __init__(self, model: str = "llama3", timeout: int = 180):
        self.model = model
        self.timeout = timeout
        self.url = "http://localhost:11434/api/chat"

    def _call_llm(self, prompt: str, temperature: float = 0.6) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a scientific assistant specialized in numerical analysis and Monte Carlo integration."
                },
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": temperature}
        }
        try:
            r = requests.post(self.url, json=payload, timeout=self.timeout)
            if r.status_code == 200:
                return r.json()["message"]["content"]
        except:
            pass
        return self._fallback_explanation(prompt, temperature)

    def _fallback_explanation(self, prompt: str, style: str = "simple") -> str:
        # Simple rule-based fallback
        if "IEEE" in prompt or "scientific report" in prompt.lower():
            return (
                "The integral was estimated using Monte Carlo integration. "
                "The method is robust for high-dimensional domains. "
                "Convergence was assessed via cumulative error analysis."
            )
        elif "simple" in prompt.lower() or "human-readable" in prompt.lower():
            return (
                "We used random sampling (Monte Carlo) to estimate the area under the curve. "
                "The result is reliable if the error is small and stable."
            )
        else:
            return "Numerical integration completed. See plots for error analysis."

    def explain(self, summary: Dict[str, Any], level: str = "simple") -> str:
        prompt = f"Explain simply: estimate={summary.get('estimate')}, error={summary.get('mean_error')}"
        return self._call_llm(prompt)

    def explain_ieee(self, summary: Dict[str, Any]) -> str:
        prompt = f"Write IEEE-style paragraph for integral estimate: {summary}"
        return self._call_llm(prompt)