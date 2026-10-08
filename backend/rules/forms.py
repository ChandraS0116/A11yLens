"""
Form control accessibility checks:
- WCAG 1.3.1 Info and Relationships (Level A) - Understandable
- WCAG 3.3.2 Labels or Instructions (Level A) - Understandable
"""

def check_forms(soup):
    issues = []
    ignore_types = {"hidden", "submit", "button", "reset", "image"}
    for inp in soup.find_all(["input", "textarea", "select"]):
        if inp.name == "input" and inp.get("type", "").lower() in ignore_types:
            continue
        if inp.get("aria-label") or inp.get("aria-labelledby") or inp.get("title"):
            continue
        if inp.find_parent("label"):
            continue
        input_id = inp.get("id")
        if input_id and soup.find("label", attrs={"for": input_id}):
            continue
            
        snippet = str(inp)[:160] + ("..." if len(str(inp)) > 160 else "")
        target_id = input_id or f"{inp.name}_{inp.get('name', 'field')}"
        placeholder = inp.get("placeholder", "").strip()
        inp_type = inp.get("type", "text") if inp.name == "input" else inp.name
        clean_name = (inp.get("name") or input_id or placeholder or inp_type).replace("-", " ").replace("_", " ").title()

        if placeholder:
            main_cause = f"Input Relies Solely on Placeholder: The <{inp.name} type=\"{inp_type}\"> uses placeholder=\"{placeholder}\" without an associated <label> or aria-label. Placeholders disappear once text is typed and are frequently ignored or misread by screen readers."
            screen_reader_impact = f'Screen readers announce "Edit text, {placeholder}" without persistent context. Once a user types anything, the placeholder vanishes completely.'
            message = f"Form Field Missing Label: <{inp.name}> relies solely on placeholder ('{placeholder}')"
            suggested_label = placeholder
            cause_badge = "Placeholder Is Not A Label"
        else:
            main_cause = f"Unlabelled Form Input: The <{inp.name} type=\"{inp_type}\"> has no linked <label for=\"...\">, aria-label, or title. Assistive tools cannot announce what data is expected."
            screen_reader_impact = 'Screen readers announce only "Edit text, blank". Blind users cannot tell whether to type their Name, Email, Password, or Search query.'
            message = f"Form Field Missing Label: <{inp.name}> ({inp_type}) has no label or accessible name"
            suggested_label = f"Enter {clean_name}"
            cause_badge = "Unlabelled Form Control"

        name_attr = f' name="{inp.get("name")}"' if inp.get("name") else ""
        remediation = f'<label for="{target_id}">{suggested_label}</label>\n<{inp.name} id="{target_id}"{name_attr} />'

        issues.append({
            "rule_id": "FORM_MISSING_LABEL",
            "wcag": "3.3.2",
            "level": "A",
            "pour": "Understandable",
            "severity": "critical",
            "element": inp.name,
            "message": message,
            "html": snippet,
            "suggestion": f'Associate a semantic <label for="{target_id}">{suggested_label}</label> or add aria-label="{suggested_label}".',
            "remediation": remediation,
            "main_cause": main_cause,
            "screen_reader_impact": screen_reader_impact,
            "target_detail": f"Field: <{inp.name}> ({clean_name})",
            "recommended_fix": f'aria-label="{suggested_label}"',
            "cause_badge": cause_badge
        })
    return issues
