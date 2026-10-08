"""
Obsolete / Deprecated HTML Elements:
- WCAG 4.1.2 Name, Role, Value / Parsing (Level A) - Robust
- Modern Web Standards compliance
"""

def check_obsolete(soup):
    issues = []
    deprecated_tags = {
        "marquee": ("<marquee> creates auto-scrolling content that confuses screen readers and cannot be paused easily.", "Use CSS animations with @media (prefers-reduced-motion) instead."),
        "blink": ("<blink> causes flashing that triggers vestibular disorders and seizures (WCAG 2.3.1).", "Avoid flashing/blinking elements entirely; use styled text."),
        "font": ("<font> is obsolete and separates presentation from CSS.", "Use semantic CSS font styling classes instead."),
        "center": ("<center> is obsolete non-semantic presentation HTML.", "Use CSS text-align: center or flexbox/grid layout."),
        "strike": ("<strike> is obsolete presentation markup.", "Use <del> or <s> with appropriate ARIA or CSS styling."),
        "applet": ("<applet> is deprecated and completely unsupported.", "Use modern standards-compliant web technologies.")
    }
    
    for tag_name, (msg, fix) in deprecated_tags.items():
        found = soup.find_all(tag_name)
        for el in found:
            issues.append({
                "rule_id": f"OBSOLETE_{tag_name.upper()}",
                "wcag": "4.1.2",
                "level": "A",
                "pour": "Robust",
                "severity": "critical" if tag_name in ["marquee", "blink"] else "moderate",
                "element": tag_name,
                "message": f"Deprecated/obsolete HTML element <{tag_name}> detected: {msg}",
                "html": str(el)[:160] + ("..." if len(str(el)) > 160 else ""),
                "suggestion": fix,
                "remediation": f"<!-- Replace <{tag_name}> with modern semantic HTML and CSS -->"
            })
            
    return issues
