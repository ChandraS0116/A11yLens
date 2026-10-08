"""
Target Size (Minimum) check:
- WCAG 2.2 Success Criterion 2.5.8 Target Size (Minimum) (Level AA) - Operable
Checks inline and declared dimensions on interactive controls (buttons, links, inputs).
"""
import re

def check_target_size(soup):
    issues = []
    
    # Check buttons and links with explicitly small inline styles
    for el in soup.find_all(["button", "a", "input"]):
        style = el.get("style", "").lower()
        if not style:
            continue
            
        w_match = re.search(r"\bwidth:\s*(\d+)px", style)
        h_match = re.search(r"\bheight:\s*(\d+)px", style)
        
        width = int(w_match.group(1)) if w_match else None
        height = int(h_match.group(1)) if h_match else None
        
        # If explicitly sized smaller than 24x24px
        if (width and width < 24) or (height and height < 24):
            snippet = str(el)[:160] + ("..." if len(str(el)) > 160 else "")
            issues.append({
                "rule_id": "TARGET_SIZE_TOO_SMALL",
                "wcag": "2.5.8",
                "level": "AA",
                "pour": "Operable",
                "severity": "serious",
                "element": el.name,
                "message": f"Interactive control <{el.name}> has a target dimension smaller than the 24x24px minimum ({width or 'auto'}x{height or 'auto'}px)",
                "html": snippet,
                "suggestion": "Increase touch target size to at least 24x24 CSS pixels (or 44x44px for WCAG AAA 2.5.5) or add sufficient surrounding padding.",
                "remediation": f'style="{re.sub(r"(width|height):\s*\d+px", "", style).strip()} min-width: 24px; min-height: 24px; padding: 8px;"'
            })
            
    return issues
