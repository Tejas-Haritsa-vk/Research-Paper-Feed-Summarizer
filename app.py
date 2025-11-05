import uvicorn
import threading
from agents.ollama_agent import OllamaAgent
from langchain_core.output_parsers import JsonOutputParser
import requests
import json

def run_server():
    print("Starting server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8080)

if __name__ == "__main__": 
    # Start server in a background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # MCP server URL
    BASE_URL = "http://127.0.0.1:8080"
    
    #AI Agent
    llm = OllamaAgent(model="gemma3:4b")

    print("Processing Query...")
    # 🔍 Example query
    query = "Summarize the document"
    context_query = query or None
    params = {"query": query, "context_query": context_query}
    url = f"{BASE_URL}/fetch_all_sources"
    response = requests.get(url, params=params)
    contexts = response.json()
    json_parser = JsonOutputParser()

    for source in contexts:
        context_query = contexts[source]
        params = {"query": query, "query_context": context_query}
        url = f"{BASE_URL}/summarize_with_llm"
        response = requests.post(url, params=params)
        llm_response = response.json()['llm_response']
        llm_response_json = json_parser.parse(llm_response)
        print(f"llm_response : {llm_response}")

    # Shut down gracefully
    print("Shutting down...")
    
