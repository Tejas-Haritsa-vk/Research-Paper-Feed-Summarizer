from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

# Source color scheme for the Research Radar aesthetic
SOURCE_COLORS = {
    'arXiv': '#B31B1B',
    'HuggingFace': '#FFD21E',
    'DeepMind': '#764ba2',
    'Google DeepMind': '#764ba2',
    'Google AI': '#4285F4',
    'Google Research': '#0F9D58',
    'Google AI Blog': '#0F9D58',
    'Meta AI': '#0668E1',
    'Meta AI Blog': '#0668E1',
    'OpenReview': '#8B5CF6'
}

def get_source_badge_color(source: str) -> str:
    """Returns the hex color code for a given research source."""
    return SOURCE_COLORS.get(source, '#64748b')

def group_by_source(papers: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """Groups the list of paper dictionaries by their source field."""
    grouped = defaultdict(list)
    for paper in papers:
        source = paper.get('source', 'Unknown Signal')
        grouped[source].append(paper)
    return dict(grouped)

def generate_html_newsletter(
    papers: List[Dict[str, Any]], 
    title: str = "The Research Radar", 
    tldr: Optional[Dict[str, Any]] = None,
    horizon_items: Optional[List[Dict[str, str]]] = None,
    signal_vs_noise: Optional[Dict[str, Any]] = None,
    issue_number: str = "000"
) -> str:
    """
    Generates a high-fidelity, interactive HTML newsletter (Web view).
    Matches test_newsletter_v2.html exactly.
    """
    if not papers:
        return "<html><body style='font-family:sans-serif; text-align:center; padding:50px;'><h1>No signals detected in the current sweep.</h1></body></html>"
    
    current_date = datetime.now().strftime("%b %d, %Y")
    papers_count = len(papers)
    grouped_papers = group_by_source(papers)
    sources_count = len(grouped_papers)
    signal_quality = "92%"

    # --- TL;DR Content Processing ---
    tldr_summary = tldr.get("summary", "") if tldr else ""
    tldr_overview = tldr.get("overview", "") if tldr else ""
    
    tldr_inner_html = ""
    if tldr_summary:
        tldr_inner_html += f"<div class='tldr-content'>{tldr_summary}<br></br></div>"
    
    if isinstance(tldr_overview, list):
        items = "".join([f"<li>{item}</li>" for item in tldr_overview])
        tldr_inner_html += f"<div class='tldr-section-list'><ul>{items}</ul></div>"
    elif tldr_overview:
        tldr_inner_html += f"<div class='tldr-content'>{tldr_overview}</div>"

    # --- Hits Processing ---
    hits_html = ""
    for source, source_papers in grouped_papers.items():
        badge_color = get_source_badge_color(source)
        hits_html += f"""
        <div class="source-group">
            <div class="source-header">
                <span class="source-badge" style="background:{badge_color};">{source}</span>
                <span class="source-label">Signal Detected</span>
            </div>
        """
        for p in source_papers:
            link = p.get('link', '#')
            p_title = p.get('title', 'Untitled')
            summary = p.get('summary', 'No summary provided.')
            insight = p.get('insight', 'Analyzing architectural implications for deployment...')
            hits_html += f"""
            <article class="paper-card">
                <h2 class="paper-title"><a href="{link}">{p_title}</a></h2>
                <div class="paper-summary">{summary}</div>
                <div class="analysis-box">
                    <strong>Radar Insight</strong>
                    {insight}
                </div>
            </article>
            """
        hits_html += "</div>"

    # --- Template Assembly ---
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #020617;
            --accent: #22d3ee;
            --text: #334155;
            --bg-dark: #020617;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: #f1f5f9;
            padding: 2vw; 
            color: var(--text);
            line-height: 1.5;
        }}
        .container {{
            width: 100%;
            max-width: 900px; 
            min-width: 320px;
            margin: 0 auto;
            background: white;
            border-radius: 24px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid #e2e8f0;
        }}
        
        .header {{
            background: var(--bg-dark);
            color: white;
            padding: 30px 40px; 
            text-align: center;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 140px;
        }}
        .radar-box {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            max-width: 500px;
            aspect-ratio: 1 / 1;
            pointer-events: none;
        }}
        .radar-ring {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border: 1px solid rgba(34, 211, 238, 0.25); 
            border-radius: 50%;
        }}
        .ring-1 {{ width: 30%; height: 30%; }}
        .ring-2 {{ width: 60%; height: 60%; }}
        .ring-3 {{ width: 90%; height: 90%; }}
        
        .radar-sweep {{
            position: absolute;
            top: 5%;
            left: 5%;
            width: 90%;
            height: 90%;
            border-radius: 50%;
            background: conic-gradient(from 0deg, transparent 0%, transparent 40%, var(--accent) 100%);
            opacity: 0.6;
            animation: sweep-rotate 3s linear infinite;
            -webkit-mask-image: radial-gradient(circle, transparent 20%, black 100%);
            mask-image: radial-gradient(circle, transparent 20%, black 100%);
        }}
        
        .ping {{
            position: absolute;
            width: 6px;
            height: 6px;
            background: var(--accent);
            border-radius: 50%;
            box-shadow: 0 0 12px var(--accent);
            opacity: 0;
            animation: ping-fade 4s ease-out infinite;
        }}
        .ping-1 {{ top: 35%; left: 65%; animation-delay: 0.5s; }}
        .ping-2 {{ top: 60%; left: 30%; animation-delay: 1.8s; }}
        .ping-3 {{ top: 20%; left: 40%; animation-delay: 2.9s; }}
        .ping-4 {{ top: 75%; left: 70%; animation-delay: 1.2s; }}

        @keyframes sweep-rotate {{
            from {{ transform: rotate(0deg); }}
            to {{ transform: rotate(360deg); }}
        }}
        @keyframes ping-fade {{
            0% {{ opacity: 0; transform: scale(0.5); }}
            45% {{ opacity: 0; }}
            50% {{ opacity: 1; transform: scale(1.5); }}
            60% {{ opacity: 0; transform: scale(2); }}
            100% {{ opacity: 0; }}
        }}

        .header-content {{ position: relative; z-index: 5; }}
        .issue-tag {{ 
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            color: var(--accent);
            display: inline;
        }}
        .header h1 {{ font-size: clamp(24px, 5vw, 36px); font-weight: 800; letter-spacing: -1.5px; margin-bottom: 5px; text-transform: uppercase; }}
        .header p {{ color: var(--accent); font-size: 10px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; white-space: nowrap; }}
        
        .stat-bar {{
            display: flex;
            justify-content: space-around;
            background: #ffffff;
            padding: 25px 20px;
            border-bottom: 1px solid #f1f5f9;
            text-align: center;
        }}
        .stat-item h4 {{ font-size: clamp(20px, 4vw, 26px); color: var(--primary); font-weight: 800; line-height: 1; }}
        .stat-item span {{ font-size: 9px; color: #94a3b8; text-transform: uppercase; font-weight: 700; letter-spacing: 1px; display: block; margin-top: 5px; }}
        .stat-item.highlight h4 {{ color: #0891b2; }}
        .stat-badge {{
            display: inline-block;
            font-size: 10px;
            font-weight: 800;
            color: #0891b2;
            background: rgba(34, 211, 238, 0.15);
            padding: 2px 8px;
            border-radius: 4px;
            margin-top: 6px;
            text-transform: uppercase;
            border: 1px solid rgba(34, 211, 238, 0.3);
        }}

        .operator-note {{
            background: #f8fafc;
            padding: 20px 8%;
            text-align: center;
            border-bottom: 1px solid #e2e8f0;
            color: #64748b;
            font-size: 14px;
            font-style: italic;
            line-height: 1.6;
        }}

        .tldr-box {{
            margin: 30px 4% 0;
            padding: 25px;
            background: rgba(34, 211, 238, 0.15);
            border-radius: 16px;
            border: 1px dashed #cbd5e1;
        }}
        .tldr-label {{ font-size: 14px; font-weight: 800; text-transform: uppercase; 
            color: #0891b2; letter-spacing: 1px; margin-bottom: 15px; display: block; }}
        
        .tldr-section {{ padding: 0 3%; }}
        .tldr-content {{ font-size: 14px; color: var(--text); line-height: 1.6; text-align: justify; }}
        .tldr-section-list ul {{ 
            margin-top: 10px; padding-left: 20px; color: var(--text); font-size: 14px; 
            line-height: 1.6; list-style-type: disc; text-align: justify;
        }}
        .tldr-section-list li {{ margin-bottom: 8px; }}

        .main-content {{ padding: 30px 4% 50px; }}
        .section-heading {{
            font-size: 12px; font-weight: 900; text-transform: uppercase; letter-spacing: 2px;
            color: var(--primary); margin-bottom: 25px; display: flex; align-items: center;
        }}
        .section-heading::before {{ content: ''; width: 12px; height: 2px; background: var(--accent); margin-right: 12px; }}

        .source-group {{ margin-bottom: 45px; }}
        .source-header {{ display: flex; align-items: center; margin-bottom: 15px; }}
        .source-badge {{ padding: 4px 10px; border-radius: 6px; font-size: 10px; font-weight: 800; color: white; text-transform: uppercase; }}
        .source-label {{ font-size: 9px; color: #94a3b8; font-weight: 800; text-transform: uppercase; margin-left: 12px; }}

        .paper-card {{
            background: white; border: 1px solid #f1f5f9; border-radius: 16px;
            padding: 25px; margin-bottom: 18px;
        }}
        .paper-title {{ font-size: 20px; font-weight: 700; color: var(--primary); margin-bottom: 10px; line-height: 1.3; }}
        .paper-title a {{ color: inherit; text-decoration: none; }}
        
        .paper-summary {{ font-size: 14px; color: #475569; margin-bottom: 12px; text-align: justify; }}
        .paper-summary img {{ display: block; max-width: 100%; height: auto; margin: 12px auto; border-radius: 8px; }}

        .analysis-box {{
            background: #f0fdfa; border-left: 4px solid var(--accent);
            padding: 16px; font-size: 14px; margin-top: 20px; border-radius: 4px 12px 12px 4px;
            color: #334155; text-align: justify;
        }}
        .analysis-box strong {{ display: block; font-size: 9px; text-transform: uppercase; color: #0891b2; margin-bottom: 4px; }}
        
        footer {{ background: #020617; padding: 60px 40px; text-align: center; color: #475569; font-size: 11px; }}
        .footer-logo {{ color: var(--accent); font-weight: 800; letter-spacing: 2px; margin-top: 10px; display: block; }}

        @media (max-width: 640px) {{
            body {{ padding: 0; }}
            .container {{ border-radius: 0; border: none; }}
            .stat-bar {{ flex-direction: column; gap: 20px; }}
            .operator-note {{ padding: 20px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <div class="radar-box">
                <div class="radar-ring ring-1"></div>
                <div class="radar-ring ring-2"></div>
                <div class="radar-ring ring-3"></div>
                <div class="radar-sweep"></div>
                <div class="ping ping-1"></div>
                <div class="ping ping-2"></div>
                <div class="ping ping-3"></div>
                <div class="ping ping-4"></div>
            </div>
            <div class="header-content">
                <h1>{title}</h1>
                <p>Establishing Connection • <span class="issue-tag">Issue #{issue_number} // {current_date}</span></p>
            </div>
        </header>

        <div class="stat-bar">
            <div class="stat-item"><h4>{papers_count}</h4><span>Papers Scanned</span></div>
            <div class="stat-item"><h4>{sources_count}</h4><span>Signals Found</span></div>
            <div class="stat-item highlight">
                <h4>{signal_quality}</h4>
                <span>Signal Quality</span>
                <span class="stat-badge">Low Noise Detected</span>
            </div>
        </div>

        <div class="operator-note">
            "We scanned <strong>{papers_count} blips</strong> this week. The following <strong>Direct Hits</strong> are the highest-fidelity signals on the horizon."
        </div>

        <div class="tldr-box">
            <span class="tldr-label">🚀 The Weekly Sweep:  TL;DR (1-2 min read)</span>
            <div class='tldr-section'>{tldr_inner_html}</div>
        </div>

        <main class="main-content">
            <div class="section-heading">Direct Signal Hits</div>
            {hits_html}
        </main>
        
        <footer>
            <p>© 2025 {title} • Intelligence distilled for practitioners.</p>
            <span class="footer-logo">SIGNAL ENCRYPTED</span>
        </footer>
    </div>
</body>
</html>"""
    return full_html


def generate_email_newsletter(
    papers: List[Dict[str, Any]], 
    title: str = "The Research Radar", 
    tldr: Optional[Dict[str, Any]] = None,
    issue_number: str = "000"
) -> str:
    """
    Generates a GMAIL-FRIENDLY HTML newsletter.
    Uses nested tables and inline CSS. Strips animations.
    """
    if not papers:
        return "<html><body><h1>No signals detected.</h1></body></html>"
    
    current_date = datetime.now().strftime("%b %d, %Y")
    papers_count = len(papers)
    grouped_papers = group_by_source(papers)
    sources_count = len(grouped_papers)

    # TL;DR
    tldr_summary = tldr.get("summary", "") if tldr else ""
    tldr_overview = tldr.get("overview", "") if tldr else ""
    overview_html = ""
    if isinstance(tldr_overview, list):
        items = "".join([f"<li style='margin-bottom:8px;'>{item}</li>" for item in tldr_overview])
        overview_html = f"<ul style='margin-top:10px; padding-left:20px; font-size:14px; line-height:1.6; color:#334155; list-style-type:disc; text-align:justify;'>{items}</ul>"
    elif tldr_overview:
        overview_html = f"<div style='margin-top:10px; font-size:14px; color:#334155; line-height:1.6; text-align:justify;'>{tldr_overview}</div>"

    hits_html = ""
    for source, source_papers in grouped_papers.items():
        badge_color = get_source_badge_color(source)
        hits_html += f"""
        <tr>
            <td style="padding: 30px 0 15px 0;">
                <table border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="background:{badge_color}; color:white; padding:4px 10px; border-radius:6px; font-size:10px; font-weight:800; text-transform:uppercase; font-family:sans-serif;">{source}</td>
                        <td style="font-size:9px; color:#94a3b8; font-weight:800; text-transform:uppercase; padding-left:12px; font-family:sans-serif; letter-spacing:1px;">Signal Detected</td>
                    </tr>
                </table>
            </td>
        </tr>
        """
        for p in source_papers:
            link = p.get('link', '#')
            p_title = p.get('title', 'Untitled')
            summary = p.get('summary', 'No summary provided.')
            insight = p.get('insight', 'Analyzing architectural implications for deployment...')
            hits_html += f"""
            <tr>
                <td style="background-color: #ffffff; border: 1px solid #f1f5f9; border-radius: 16px; padding: 25px;">
                    <h2 style="margin: 0 0 10px 0; font-size: 20px; font-weight: 700; line-height: 1.3; font-family: sans-serif;">
                        <a href="{link}" style="color: #020617; text-decoration: none;">{p_title}</a>
                    </h2>
                    <p style="margin: 0 0 20px 0; font-size: 14px; color: #475569; line-height: 1.5; font-family: sans-serif; text-align: justify;">{summary}</p>
                    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0fdfa; border-left: 4px solid #22d3ee; border-radius: 4px 12px 12px 4px;">
                        <tr>
                            <td style="padding: 16px;">
                                <strong style="display: block; font-size: 9px; text-transform: uppercase; color: #0891b2; margin-bottom: 4px; font-family: sans-serif; letter-spacing: 1px;">Radar Insight</strong>
                                <div style="font-size: 14px; color: #334155; font-family: sans-serif; line-height: 1.4; text-align: justify;">{insight}</div>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr><td height="15"></td></tr>
            """

    full_html = f"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: sans-serif;">
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f1f5f9; padding: 20px 0;">
        <tr>
            <td align="center">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 900px; background-color: #ffffff; border-radius: 24px; overflow: hidden; border: 1px solid #e2e8f0;">
                    <tr>
                        <td align="center" style="background-color: #020617; padding: 30px 20px;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 800; letter-spacing: -1px; text-transform: uppercase;">{title}</h1>
                            <p style="margin: 8px 0 0 0; color: #22d3ee; font-size: 10px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; white-space: nowrap;">Establishing Connection • <span style="font-family: monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 2px; color: #22d3ee;">Issue #{issue_number} // {current_date}</span></p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 25px 20px; border-bottom: 1px solid #f1f5f9;">
                            <table width="100%" border="0" cellpadding="0" cellspacing="0" style="text-align: center;">
                                <tr>
                                    <td width="33%">
                                        <div style="font-size: 22px; color: #020617; font-weight: 800;">{papers_count}</div>
                                        <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Papers Scanned</div>
                                    </td>
                                    <td width="33%" style="border-left: 1px solid #f1f5f9; border-right: 1px solid #f1f5f9;">
                                        <div style="font-size: 22px; color: #020617; font-weight: 800;">{sources_count}</div>
                                        <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Signals Found</div>
                                    </td>
                                    <td width="33%">
                                        <div style="font-size: 22px; color: #0891b2; font-weight: 800;">92%</div>
                                        <div style="font-size: 9px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Signal Quality</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px 30px 0 30px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f0fdfa; border: 1px dashed #cbd5e1; border-radius: 16px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <span style="font-size: 14px; font-weight: 800; text-transform: uppercase; color: #0891b2; display: block; margin-bottom: 10px;">🚀 The Weekly Sweep:  TL;DR (1-2 min read)</span>
                                        <div style="font-size: 14px; color: #334155; line-height: 1.6; text-align: justify; padding: 0 3%;">{tldr_summary}<br></br></div>
                                        {overview_html}
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px 30px 50px 30px;">
                            <table width="100%" border="0" cellpadding="0" cellspacing="0">
                                {hits_html}
                            </table>
                        </td>
                    </tr>
                    <tr>
                        <td align="center" style="background-color: #020617; padding: 40px; color: #475569;">
                            <p style="margin: 0; font-size: 11px;">© 2025 {title} • Intelligence distilled for practitioners.</p>
                            <p style="margin: 8px 0 0 0; color: #22d3ee; font-size: 10px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; white-space: nowrap;">SIGNAL ENCRYPTED</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    return full_html
