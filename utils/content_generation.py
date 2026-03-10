import re
from typing import List, Dict, Optional
from utils.jsonify_llm_response import jsonify_llm_response
from utils.scraper import scrape_article_content

def generate_tldr(papers: List[Dict], llm_agent, max_papers: int = 25) -> Optional[Dict]:
    """
    Generate a TL;DR summary using the provided LLM agent.
    
    Args:
        papers: List of paper dictionaries.
        llm_agent: Initialized LLM agent instance (e.g., OllamaAgent).
        max_papers: Max papers to include in context to avoid context window issues.
        
    Returns:
        Dictionary with 'summary' and 'overview' keys, or None if generation fails.
    """
    if not papers:
        return None
        
    try:
        # Prepare context for TL;DR
        # Limit the number of papers in context to avoid token limits if necessary, 
        # though the agent handles context window, it's good to be explicit for summary relevance.
        subset_papers = papers[:max_papers]
        
        paper_titles = [f"- {p['title']}: {p['summary'][:1500]}..." for p in subset_papers]
        context = "\n".join(paper_titles)
        
        tldr_prompt = """
        You are a senior AI research analyst. Provide a high-level TL;DR synthesis of the following research papers.
        
        Focus on:
        - Connecting the dots: What are the recurring themes or significant shifts in the field?
        - High-level trends: How do these papers collectively move the needle?
        - Meta-observations: What are the broader architectural or deployment implications?
        
        Format your response as a JSON object with two keys:
        1. "summary": A 1-2 paragraph professional synthesis of the "State of the Sweep".
        2. "overview": A JSON array of 3-5 concise bullet points, each describing a high-level trend or technical insight observed across these papers.
        
        CRITICAL: The "overview" must NOT just list individual papers. It must describe trends (e.g., "Emergence of sparse architectures for real-time edge deployment" instead of "Paper X uses sparse models").
        
        Provide ONLY valid JSON.
        """
        
        tldr_response = llm_agent.chat(user_query=tldr_prompt, context=context)
        parsed = jsonify_llm_response(tldr_response)
        
        if not parsed:
            # Fallback for plain text response
            return {
                "summary": tldr_response,
                "overview": "Theme identification in progress..."
            }
        return parsed

    except Exception as e:
        print(f"Error generating TL;DR: {e}")
        return {
            "summary": "AI sweep completed. Statistical analysis of new papers available below.",
            "overview": "The field continues to move at a high velocity across multiple modalities."
        }

def generate_insights(papers: List[Dict], llm_agent, batch_size: int = 5) -> List[Dict]:
    """
    Generate a 'Radar Insight' for each paper using the provided LLM agent.
    
    Args:
        papers: List of paper dictionaries.
        llm_agent: Initialized LLM agent instance.
        batch_size: Number of papers to process in each LLM call.
        
    Returns:
        The updated list of papers with an 'insight' field added to each.
    """
    if not papers:
        return []
        
    all_papers = papers.copy()
    
    for i in range(0, len(all_papers), batch_size):
        batch = all_papers[i:i + batch_size]
        
        try:
            # Prepare context for the batch
            paper_contexts = []
            for j, p in enumerate(batch):
                paper_contexts.append(f"Paper {j+1}:\nTitle: {p['title']}\nSummary: {p['summary'][:1000]}...")
            
            context = "\n\n".join(paper_contexts)
            
            insight_prompt = f"""
            For each of the following {len(batch)} research papers, provide a 1-2 sentence "Radar Insight".
            Focus on the architectural implications, potential for deployment, 
            or a unique technical contribution.
            
            IMPORTANT: Do NOT include any prefixes like "Paper 1:" or "Insight:". 
            Just provide the direct insight text.
            
            Format your response as a JSON object with a key "insights" containing a list of strings.
            The length of the "insights" list MUST be exactly {len(batch)}.
            """
            
            response = llm_agent.chat(user_query=insight_prompt, context=context)
            json_response = jsonify_llm_response(response)
            
            if json_response and "insights" in json_response:
                batch_insights = json_response["insights"]
                # Match insights back to papers in the batch
                for k, insight in enumerate(batch_insights):
                    if k < len(batch):
                        # Clean up any remaining prefixes just in case
                        cleaned_insight = re.sub(r"^(Paper \d+:|Insight:)\s*", "", insight, flags=re.IGNORECASE).strip()
                        batch[k]['insight'] = cleaned_insight
            else:
                # Fallback if JSON parsing fails or format is wrong
                for p in batch:
                    p['insight'] = "Analyzing architectural implications for deployment..."
                    
        except Exception as e:
            print(f"Error generating insights for batch {i//batch_size}: {e}")
            for p in batch:
                if 'insight' not in p:
                    p['insight'] = "Technical sweep in progress..."
                    
    return all_papers

def enrich_summaries(papers: List[Dict], llm_agent, min_length: int = 400) -> List[Dict]:
    """
    Enrich short summaries by scraping original content and using LLM to summarize.
    """
    if not papers:
        return []
        
    for paper in papers:
        summary = paper.get('summary', '')
        if len(summary) < min_length:
            url = paper.get('link')
            if not url:
                continue
                
            print(f"Enriching short summary for: {paper.get('title')}...")
            full_content = scrape_article_content(url)
            
            if full_content and len(full_content) > len(summary):
                enrich_prompt = """
                You are a world-class AI research analyst. Your task is to write a highly informative, technical, and engaging summary of the research paper or blog post provided below.
                
                The summary should:
                - Be exactly 2-3 paragraphs.
                - Use a professional, academic tone but be accessible to practitioners.
                - Highlight the specific "state-of-the-art" (SOTA) improvements or novel architectures introduced.
                - Explain the "Why it matters" in a clear, impactful way.
                - Avoid generic fluff or meta-talk (like "This paper discusses..."). Jump straight into the content.
                - Format using professional language suitable for a high-end newsletter.
                
                CONTENT TO SUMMARIZE:
                """
                
                try:
                    enriched_summary = llm_agent.chat(user_query=enrich_prompt, context=full_content)
                    # Clean up prefixes
                    enriched_summary = re.sub(r"^(Detailed Summary:|Summary:|Abstract:)\s*", "", enriched_summary, flags=re.IGNORECASE)
                    # Ensure no weird formatting or leftover prompt text
                    enriched_summary = enriched_summary.strip()
                    if len(enriched_summary) > 100: # Sanity check
                        paper['summary'] = enriched_summary
                        print(f"Successfully enriched summary for {paper.get('title')}.")
                    else:
                        print(f"LLM returned too short enrichment for {paper.get('title')}.")
                except Exception as e:
                    print(f"Error enriching summary for {paper.get('title')}: {e}")
            else:
                print(f"Could not fetch enough content to enrich {paper.get('title')}.")
                
    return papers
