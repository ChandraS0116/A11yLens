"""
Heading hierarchy and semantic structure checks:
- WCAG 1.3.1 Info and Relationships (Level A) - Understandable
- WCAG 2.4.6 Headings and Labels (Level AA) - Operable
"""

def check_headings(soup):
    issues = []
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    if not headings:
        issues.append({
            "rule_id": "HEADING_NONE_FOUND",
            "wcag": "1.3.1",
            "level": "A",
            "pour": "Understandable",
            "severity": "serious",
            "element": "body",
            "message": "Webpage does not contain any heading elements (<h1>-<h6>)",
            "html": "<body>...</body>",
            "suggestion": "Structure your page with semantic headings starting from an <h1>.",
            "remediation": "<h1>Main Page Heading</h1>\n<p>Section intro...</p>"
        })
        return issues
        
    # Check for missing H1
    h1s = soup.find_all('h1')
    if len(h1s) == 0:
        issues.append({
            "rule_id": "HEADING_MISSING_H1",
            "wcag": "1.3.1",
            "level": "A",
            "pour": "Understandable",
            "severity": "serious",
            "element": "body",
            "message": "Page is missing a primary level-one heading (<h1>)",
            "html": "<main>...</main>",
            "suggestion": "Include exactly one <h1> element describing the main topic of the page.",
            "remediation": "<h1>Primary Page Title</h1>",
            "main_cause": "Missing Primary <h1>: The webpage does not have an <h1> element. In accessibility hierarchy, an <h1> serves as the essential main title introducing the document content.",
            "screen_reader_impact": "Screen reader users commonly jump directly to the <h1> heading upon landing to confirm page identity; without it, orientation is significantly delayed.",
            "target_detail": "Missing Element: <h1>",
            "recommended_fix": "<h1>Page Title</h1>",
            "cause_badge": "Missing <h1> Landmark"
        })
    elif len(h1s) > 1:
        issues.append({
            "rule_id": "HEADING_MULTIPLE_H1",
            "wcag": "1.3.1",
            "level": "AA",
            "pour": "Understandable",
            "severity": "moderate",
            "element": "h1",
            "message": f"Page contains {len(h1s)} <h1> headings; standard convention recommends a single primary <h1>",
            "html": str(h1s[1])[:160] + ("..." if len(str(h1s[1])) > 160 else ""),
            "suggestion": "Demote secondary <h1> headings to <h2> to maintain a consistent hierarchical tree.",
            "remediation": f"<h2>{h1s[1].get_text(strip=True)}</h2>",
            "main_cause": f"Multiple Top-Level <h1> Headings: Found {len(h1s)} <h1> tags on a single page. Having more than one top-level heading dilutes document structure.",
            "screen_reader_impact": "Screen reader heading navigation lists show multiple primary titles, confusing users about which section is the actual top-level content.",
            "target_detail": f"Count: {len(h1s)} <h1> tags",
            "recommended_fix": "Demote secondary <h1> to <h2>",
            "cause_badge": "Multiple <h1> Headings"
        })
        
    # Check for heading level skips
    previous_level = 0
    for h in headings:
        level = int(h.name[1])
        if previous_level > 0 and level > previous_level + 1:
            snippet = str(h)[:160] + ("..." if len(str(h)) > 160 else "")
            issues.append({
                "rule_id": "HEADING_LEVEL_SKIP",
                "wcag": "1.3.1",
                "level": "A",
                "pour": "Understandable",
                "severity": "moderate",
                "element": h.name,
                "message": f"Heading hierarchy level skipped: jumped from <h{previous_level}> to <h{level}>",
                "html": snippet,
                "suggestion": f"Nest headings hierarchically without skipping levels (change <h{level}> to <h{previous_level + 1}>).",
                "remediation": f"<h{previous_level + 1}>{h.get_text(strip=True)}</h{previous_level + 1}>",
                "main_cause": f"Heading Level Skip: Hierarchy jumped from <h{previous_level}> directly to <h{level}>, skipping <h{previous_level + 1}>. Headings must reflect a nested document outline.",
                "screen_reader_impact": "Screen reader users navigating via heading keys (e.g. 'H' or '2'/'3') assume missing content or broken structure when levels are skipped.",
                "target_detail": f"Skipped: <h{previous_level}> → <h{level}>",
                "recommended_fix": f"Change <h{level}> to <h{previous_level + 1}>",
                "cause_badge": "Broken Heading Tree"
            })
        previous_level = level
        
    return issues
