"""
Meta and Document structure checks:
- WCAG 2.4.2 Page Titled (Level A) - Operable
- WCAG 1.4.4 Resize Text / Viewport Scalability (Level AA) - Perceivable
"""

def check_meta(soup):
    issues = []
    
    # 1. Check <title> tag
    title = soup.find('title')
    if not title:
        issues.append({
            "rule_id": "PAGE_MISSING_TITLE",
            "wcag": "2.4.2",
            "level": "A",
            "pour": "Operable",
            "severity": "serious",
            "element": "head",
            "message": "Webpage is missing a <title> element",
            "html": "<head>...</head>",
            "suggestion": "Add a descriptive <title> inside the <head> element to summarize page topic for screen readers.",
            "remediation": "<title>Page Title - Website Name</title>"
        })
    elif not title.get_text(strip=True):
        issues.append({
            "rule_id": "PAGE_EMPTY_TITLE",
            "wcag": "2.4.2",
            "level": "A",
            "pour": "Operable",
            "severity": "serious",
            "element": "title",
            "message": "Webpage has an empty <title> element",
            "html": str(title),
            "suggestion": "Ensure the <title> contains informative text identifying the page topic.",
            "remediation": "<title>Descriptive Title Here</title>"
        })

    # 2. Check viewport meta tag for zoom disable
    viewport = soup.find('meta', attrs={"name": lambda v: v and v.lower() == "viewport"})
    if viewport:
        content = viewport.get("content", "").lower()
        if "user-scalable=no" in content or "user-scalable=0" in content or "maximum-scale=1" in content:
            issues.append({
                "rule_id": "VIEWPORT_ZOOM_DISABLED",
                "wcag": "1.4.4",
                "level": "AA",
                "pour": "Perceivable",
                "severity": "critical",
                "element": "meta",
                "message": "Viewport meta tag disables zoom or limits scaling",
                "html": str(viewport),
                "suggestion": "Remove 'user-scalable=no' and 'maximum-scale=1.0' from viewport content so low-vision users can zoom up to 200%.",
                "remediation": '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            })

    return issues
