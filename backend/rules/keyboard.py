"""
Keyboard navigation and focus checks:
- WCAG 2.1.1 Keyboard Accessible (Level A) - Operable
- WCAG 2.4.3 Focus Order (Level A) - Operable
"""

def check_keyboard(soup):
    issues = []
    interactive_roles = {"button", "link", "checkbox", "menuitem", "menuitemcheckbox", "menuitemradio", "option", "radio", "searchbox", "switch", "textbox", "treeitem"}
    
    for t in soup.find_all(True):
        # 1. Click handlers on non-interactive elements without keyboard access
        if t.name not in ["a", "button", "input", "select", "textarea"] and t.has_attr("onclick"):
            if not t.has_attr("tabindex") and t.get("role") not in interactive_roles:
                snippet = str(t)[:160] + ("..." if len(str(t)) > 160 else "")
                main_cause = f"Non-Interactive Element With Click Listener: The <{t.name}> element has an onclick listener but cannot receive keyboard focus (missing tabindex=\"0\") and cannot be activated via Enter or Space."
                screen_reader_impact = "Keyboard-only and switch-control users cannot tab to or trigger this action, blocking them from accessing this functionality."
                issues.append({
                    "rule_id": "KEYBOARD_NON_INTERACTIVE_CLICK",
                    "wcag": "2.1.1",
                    "level": "A",
                    "pour": "Operable",
                    "severity": "critical",
                    "element": t.name,
                    "message": f"Non-interactive element <{t.name}> has a click handler but cannot be reached via keyboard",
                    "html": snippet,
                    "suggestion": "Replace with a native <button>, or add tabindex=\"0\", role=\"button\", and an onKeyDown handler.",
                    "remediation": f'<button type="button" class="{t.get("class", ["action"])[0] if isinstance(t.get("class"), list) else "action"}">\n  {t.get_text(strip=True) or "Perform Action"}\n</button>',
                    "main_cause": main_cause,
                    "screen_reader_impact": screen_reader_impact,
                    "target_detail": f"Element: <{t.name} onclick=\"...\">",
                    "recommended_fix": f'<button type="button">Action</button>',
                    "cause_badge": "Inaccessible Click Handler"
                })

        # 2. Positive tabindex anti-pattern (disrupts natural tab navigation order)
        tabindex = t.get("tabindex")
        if tabindex is not None:
            try:
                ti_val = int(tabindex)
                if ti_val > 0:
                    snippet = str(t)[:160] + ("..." if len(str(t)) > 160 else "")
                    main_cause = f"Positive Tabindex Anti-Pattern: Element specifies tabindex=\"{ti_val}\". Any positive tabindex pulls this element ahead of the natural visual page flow, breaking the expected top-to-bottom tab order."
                    screen_reader_impact = f"Pressing the Tab key suddenly teleports focus to tabindex=\"{ti_val}\" before reaching earlier page elements, disorienting keyboard navigators."
                    issues.append({
                        "rule_id": "KEYBOARD_POSITIVE_TABINDEX",
                        "wcag": "2.4.3",
                        "level": "A",
                        "pour": "Operable",
                        "severity": "serious",
                        "element": t.name,
                        "message": f"Element uses positive tabindex=\"{ti_val}\", which disrupts natural keyboard focus flow",
                        "html": snippet,
                        "suggestion": "Avoid positive tabindex values. Use tabindex=\"0\" to place elements in the natural tab flow, or tabindex=\"-1\" for programmatic focus.",
                        "remediation": str(t).replace(f'tabindex="{tabindex}"', 'tabindex="0"')[:200],
                        "main_cause": main_cause,
                        "screen_reader_impact": screen_reader_impact,
                        "target_detail": f"tabindex=\"{ti_val}\"",
                        "recommended_fix": 'tabindex="0" or remove tabindex',
                        "cause_badge": "Disruptive Positive Tabindex"
                    })
            except ValueError:
                pass

    return issues
