from langchain_ollama import OllamaLLM
from typing import Optional, List
import requests

class OllamaAgent(OllamaLLM):
    model: str = "gemma3"
    host: str = "http://127.0.0.1:11434"

    @property
    def _llm_type(self) -> str:
        return "ollama"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Send a completion request to the Ollama API."""
        url = f"{self.host}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")

    def chat(self, user_query: str, context: Optional[List[str]] = None) -> str:
        """Generate a response given a user query and optional context."""
        context = context or []
        # prompt = f"Use the following context to answer concisely. \n Include the follwing in answer as a json for each item in list: title: original title from item, summary: brief summary, overview: brief overview on its impact. \n Question: {user_query}\nContext: {context}"
        prompt = f"Use the following context to answer concisely. \n Include the follwing in answer as a json: summary: brief summary, overview: brief overview on its impact. \n Question: {user_query}\nContext: {context}. Do not include explanations, commentary, or follow-up phrases. Always respond in English."
        return self.invoke(prompt)