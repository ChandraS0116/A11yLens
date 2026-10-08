"""
ARIA accessibility checks:
- WCAG 4.1.2 Name, Role, Value (Level A) - Robust
"""

VALID_ARIA_ROLES = {
    "alert", "alertdialog", "application", "article", "banner", "button", "cell", "checkbox",
    "columnheader", "combobox", "complementary", "contentinfo", "definition", "dialog", "directory",
    "document", "feed", "figure", "form", "grid", "gridcell", "group", "heading", "img", "link",
    "list", "listbox", "listitem", "log", "main", "marquee", "math", "menu", "menubar", "menuitem",
    "menuitemcheckbox", "menuitemradio", "navigation", "none", "note", "option", "presentation",
    "progressbar", "radio", "radiogroup", "region", "row", "rowgroup", "rowheader", "scrollbar",
    "search", "searchbox", "separator", "slider", "spinbutton", "status", "switch", "tab", "table",
    "tablist", "tabpanel", "term", "textbox", "timer", "toolbar", "tooltip", "tree", "treegrid", "treeitem"
}

def check_aria(soup):
    issues = []
    
    # 1. Redundant ARIA roles (e.g. <button role="button">)
    redundant_roles = {
        "button": "button",
        "link": "a",
        "form": "form",
        "navigation": "nav",
        "article": "article",
        "heading": ["h1", "h2", "h3", "h4", "h5", "h6"],
        "list": ["ul", "ol"],
        "listitem": "li",
        "table": "table",
    }
    
    for tag in soup.find_all(True):
        role = tag.get("role")
        if role:
            role = role.lower().strip()
            
            # Check invalid / fabricated ARIA role
            if role not in VALID_ARIA_ROLES:
                snippet = str(tag)[:160] + ("..." if len(str(tag)) > 160 else "")
                issues.append({
                    "rule_id": "ARIA_INVALID_ROLE",
                    "wcag": "4.1.2",
                    "level": "A",
                    "pour": "Robust",
                    "severity": "critical",
                    "element": tag.name,
                    "message": f"Non-standard or invalid ARIA role '{role}' detected",
                    "html": snippet,
                    "suggestion": f"Use an official W3C ARIA landmark or widget role.",
                    "remediation": str(tag).replace(f'role="{role}"', '')[:200]
                })

            # Check redundant role
            if role in redundant_roles:
                native = redundant_roles[role]
                if tag.name == native or (isinstance(native, list) and tag.name in native):
                    snippet = str(tag)[:160] + ("..." if len(str(tag)) > 160 else "")
                    issues.append({
                        "rule_id": "ARIA_REDUNDANT_ROLE",
                        "wcag": "4.1.2",
                        "level": "AA",
                        "pour": "Robust",
                        "severity": "minor",
                        "element": tag.name,
                        "message": f"Redundant ARIA role '{role}' on native <{tag.name}> element",
                        "html": snippet,
                        "suggestion": "Remove the role attribute, as assistive technology natively understands semantic HTML elements.",
                        "remediation": str(tag).replace(f'role="{role}"', '')[:200]
                    })
                    
    # 2. aria-hidden="true" on focusable elements
    focusable_tags = ["a", "button", "input", "select", "textarea"]
    for tag in soup.find_all(focusable_tags, attrs={"aria-hidden": "true"}):
        if tag.get("tabindex") != "-1":
            snippet = str(tag)[:160] + ("..." if len(str(tag)) > 160 else "")
            main_cause = f"Interactive Element Hidden from Assistive Tech: The focusable <{tag.name}> has aria-hidden=\"true\" applied, but is still reachable via keyboard Tab key (missing tabindex=\"-1\")."
            screen_reader_impact = "When a keyboard user tabs to this element, the screen reader becomes completely silent, stranding the user on a non-communicative ghost element."
            issues.append({
                "rule_id": "ARIA_HIDDEN_FOCUSABLE",
                "wcag": "4.1.2",
                "level": "A",
                "pour": "Robust",
                "severity": "critical",
                "element": tag.name,
                "message": f"Interactive <{tag.name}> has aria-hidden=\"true\" but remains in the keyboard tab order",
                "html": snippet,
                "suggestion": "Focusable elements must not be hidden from screen readers. Either remove aria-hidden or add tabindex=\"-1\".",
                "remediation": str(tag).replace('aria-hidden="true"', '')[:200],
                "main_cause": main_cause,
                "screen_reader_impact": screen_reader_impact,
                "target_detail": f"Element: <{tag.name} aria-hidden=\"true\">",
                "recommended_fix": 'Remove aria-hidden="true" or add tabindex="-1"',
                "cause_badge": "Silent Ghost Element"
            })
            
    return issues
