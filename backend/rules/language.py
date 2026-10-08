"""
Language accessibility checks:
- WCAG 3.1.1 Language of Page (Level A) - Understandable
"""

def check_language(soup):
    issues = []
    html_tag = soup.find('html')
    
    if not html_tag:
        issues.append({
            "rule_id": "LANG_MISSING_HTML_TAG",
            "wcag": "3.1.1",
            "level": "A",
            "pour": "Understandable",
            "severity": "critical",
            "element": "html",
            "message": "Document root <html> tag was not found",
            "html": "<html>",
            "suggestion": "Ensure the document has a root <html> element with a valid 'lang' attribute.",
            "remediation": '<html lang="en">'
        })
        return issues
        
    lang = html_tag.get('lang')
    if not lang:
        issues.append({
            "rule_id": "LANG_MISSING",
            "wcag": "3.1.1",
            "level": "A",
            "pour": "Understandable",
            "severity": "critical",
            "element": "html",
            "message": "Root <html> element is missing the 'lang' attribute",
            "html": "<html" + (" ...>" if html_tag.attrs else ">"),
            "suggestion": "Add a primary BCP 47 language tag (e.g., lang=\"en\" or lang=\"es\") so screen readers apply correct pronunciation rules.",
            "remediation": '<html lang="en">'
        })
    elif not lang.strip():
        issues.append({
            "rule_id": "LANG_EMPTY",
            "wcag": "3.1.1",
            "level": "A",
            "pour": "Understandable",
            "severity": "critical",
            "element": "html",
            "message": "Root <html> element has an empty 'lang' attribute",
            "html": '<html lang="">',
            "suggestion": "Specify a valid BCP 47 language code (e.g., lang=\"en\").",
            "remediation": '<html lang="en">'
        })
        
    return issues
