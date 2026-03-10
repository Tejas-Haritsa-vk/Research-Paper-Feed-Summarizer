"""
Newsletter generation for research papers.

Creates modern, attractive HTML and text newsletters.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict


# Source color scheme
SOURCE_COLORS = {
    'arXiv': '#B31B1B',
    'HuggingFace': '#FFD21E',
    'Google DeepMind': '#4285F4',  # Special blue for DeepMind
    'Google AI Blog': '#0F9D58',   # Google green
    'Google Research': '#0F9D58',  # Same Google green
    'Meta AI Blog': '#0668E1',
    'OpenReview': '#8B5CF6'
}


def get_source_badge_color(source: str) -> str:
    """Get color for source badge."""
    return SOURCE_COLORS.get(source, '#6B7280')


def group_by_source(papers: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """Group papers by source."""
    grouped = defaultdict(list)
    for paper in papers:
        source = paper.get('source', 'Unknown')
        grouped[source].append(paper)
    return dict(grouped)


def generate_html_newsletter(papers: List[Dict[str, Any]], title: str = "AI Research Digest", tldr: Optional[str] = None) -> str:
    """
    Generate modern HTML newsletter.
    
    Args:
        papers: List of papers
        title: Newsletter title
        tldr: LLM-generated summary for the top section (optional)
        
    Returns:
        HTML string
    """
    if not papers:
        return "<html><body><h1>No papers found</h1></body></html>"
    
    # Group papers by source
    grouped_papers = group_by_source(papers)
    sources_count = len(grouped_papers)
    papers_count = len(papers)
    
    # Get current date
    current_date = datetime.now().strftime("%B %d, %Y")

    # Parse tldr
    if tldr:
        tldr_summary = tldr.get("summary", "")
        tldr_overview = tldr.get("overview", "")
    else:
        tldr_summary = ""
        tldr_overview = ""
    
    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 20px 30px;
            border-bottom: 1px solid #dee2e6;
            
            /* Force the container to fill the card */
            width: 100%;
            display: flex;
            
            /* Align items to the center */
            justify-content: center; 
            align-items: center;
            
            /* Space between the two blocks */
            gap: 60px; 
            
            /* Fallback for older renderers */
            text-align: center;
        }}
        .stat {{
            /* Ensures items stay side-by-side but centered */
            display: inline-block;
            vertical-align: middle;
            padding: 10px;
        }}
        .stat-number {{
            font-size: 28px;
            font-weight: 700;
            color: #495057;
        }}
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .content {{
            padding: 30px;
        }}
        .source-section {{
            margin-bottom: 40px;
        }}
        .source-header {{
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e9ecef;
        }}
        .source-badge {{
            display: inline-block;
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            color: white;
            margin-right: 12px;
        }}
        .source-count {{
            color: #6c757d;
            font-size: 14px;
        }}
        .paper-card {{
            background: #ffffff;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
        }}
        .paper-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        .paper-title {{
            font-size: 18px;
            font-weight: 600;
            color: #212529;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        .paper-title a {{
            color: #212529;
            text-decoration: none;
        }}
        .paper-title a:hover {{
            color: #667eea;
        }}
        .paper-meta {{
            font-size: 13px;
            color: #6c757d;
            margin-bottom: 12px;
        }}
        .paper-summary {{
            font-size: 14px;
            color: #495057;
            line-height: 1.6;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
            border-top: 1px solid #dee2e6;
        }}
        .tldr-section {{
            background: #fdf2f2;
            border-left: 4px solid #f87171;
            padding: 20px 30px;
            margin: 20px 30px 0 30px;
            border-radius: 4px;
        }}
        .tldr-title {{
            font-weight: 700;
            color: #b91c1c;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }}
        .tldr-summary-title {{
            font-weight: 700;
            color: #b91c1c;
            margin-bottom: 8px;
            margin-left: 20px;
            display: flex;
            align-items: center;
        }}
        .tldr-overview-title {{
            font-weight: 700;
            color: #b91c1c;
            margin-bottom: 8px;
            margin-left: 20px;
            display: flex;
            align-items: center;
        }}
        .tldr-content {{
            font-size: 15px;
            color: #4b5563;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>{current_date}</p>
        </div>
        
        <!-- DASHBOARD STATS SECTION (Gmail Optimized) -->
        <div style="background-color: #ffffff; padding: 30px 0; border-bottom: 1px solid #edf2f7; text-align: center;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto; width: 100%; max-width: 450px;">
                <tr>
                    <!-- Papers Stat -->
                    <td width="49%" style="text-align: center; padding: 0 20px;">
                        <div style="font-size: 36px; font-weight: 800; color: #2d3748; line-height: 1;">{papers_count}</div>
                        <div style="font-size: 11px; font-weight: 700; color: #a0aec0; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 10px;">Papers Found</div>
                    </td>
                    <!-- Vertical Divider -->
                    <td width="1" style="background-color: #e2e8f0; padding: 0;">
                        <div style="width: 1px; height: 50px; background-color: #e2e8f0; margin: 0 auto;"></div>
                    </td>
                    <!-- Sources Stat -->
                    <td width="49%" style="text-align: center; padding: 0 20px;">
                        <div style="font-size: 36px; font-weight: 800; color: #2d3748; line-height: 1;">{sources_count}</div>
                        <div style="font-size: 11px; font-weight: 700; color: #a0aec0; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 10px;">Unique Sources</div>
                    </td>
                </tr>
            </table>
        </div>
        
        {f'''<div class="tldr-section">
            <div class="tldr-title">🚀 TL;DR (1-2 min read)</div>
            <div class="tldr-content">{tldr_summary}<br><br></div>
            <div class="tldr-content">{tldr_overview}</div>
        </div>''' if tldr_summary and tldr_overview else ""}
        
        <div class="content">
"""
    
    # Add each source section
    for source, source_papers in grouped_papers.items():
        source_color = get_source_badge_color(source)
        html += f"""
            <div class="source-section">
                <div class="source-header">
                    <span class="source-badge" style="background-color: {source_color};">{source}</span>
                    <span class="source-count">{len(source_papers)} paper{"s" if len(source_papers) != 1 else ""}</span>
                </div>
"""
        
        # Add papers
        for paper in source_papers:
            title_text = paper.get('title', 'Untitled')
            link = paper.get('link', '#')
            published = paper.get('published', 'N/A')
            summary = paper.get('summary', '')[:300]
            topics = paper.get('topics', [])
            
            topics_html = ""
            if topics:
                topics_html = '<div style="margin-top: 10px;">'
                for topic in topics:
                    topics_html += f'<span style="display: inline-block; background: #e9ecef; color: #495057; font-size: 11px; padding: 2px 8px; border-radius: 4px; margin-right: 5px; margin-bottom: 5px;">{topic}</span>'
                topics_html += '</div>'
            
            html += f"""
                <div class="paper-card">
                    <div class="paper-title">
                        <a href="{link}" target="_blank">{title_text}</a>
                    </div>
                    <div class="paper-meta">Published: {published}</div>
                    <div class="paper-summary">{summary}...</div>
                    {topics_html}
                </div>
"""
        
        html += "            </div>\n"
    
    # Add footer
    html += f"""
        </div>
        
        <div class="footer">
            Generated by AI Research Agent • {current_date}
        </div>
    </div>
</body>
</html>
"""
    
    return html


def generate_text_newsletter(papers: List[Dict[str, Any]], title: str = "AI Research Digest", tldr: Optional[str] = None) -> str:
    """
    Generate plain text newsletter.
    
    Args:
        papers: List of papers
        title: Newsletter title
        tldr: LLM-generated summary (optional)
        
    Returns:
        Plain text string
    """
    if not papers:
        return "No papers found."
    
    # Group by source
    grouped_papers = group_by_source(papers)
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Build text
    text = f"{title}\n"
    text += f"{current_date}\n"
    text += "=" * 70 + "\n\n"

    tldr_summary = tldr.get("summary", "")
    tldr_overview = tldr.get("overview", "")
    
    if tldr_summary and tldr_overview:
        text += "TL;DR:\n"
        text += f"{tldr_summary}\n"
        text += "\n"
        text += "Overview:\n"
        text += f"{tldr_overview}\n"
        text += "-" * 70 + "\n\n"
        
    text += f"Total: {len(papers)} papers from {len(grouped_papers)} sources\n\n"
    
    for source, source_papers in grouped_papers.items():
        text += f"\n{'=' * 70}\n"
        text += f"{source} ({len(source_papers)} papers)\n"
        text += f"{'=' * 70}\n\n"
        
        for i, paper in enumerate(source_papers, 1):
            title_text = paper.get('title', 'Untitled')
            link = paper.get('link', '')
            published = paper.get('published', 'N/A')
            summary = paper.get('summary', '')[:200]
            
            text += f"{i}. {title_text}\n"
            text += f"   Published: {published}\n"
            text += f"   Link: {link}\n"
            text += f"   Summary: {summary}...\n\n"
    
    text += f"\n{'=' * 70}\n"
    text += f"End of newsletter • {current_date}\n"
    
    return text
