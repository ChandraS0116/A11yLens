"""
Button accessibility checks:
- WCAG 4.1.2 Name, Role, Value (Level A) - Robust
"""
from .utils import is_element_accessible

ICON_BUTTON_MAPPINGS = [
    (["search", "magnifying-glass"], "Search", "Search"),
    (["bars", "navicon", "hamburger", "menu"], "Navigation Menu", "Toggle navigation menu"),
    (["close", "times", "cross"], "Close", "Close dialog"),
    (["chevron", "angle", "arrow-right", "arrow-left", "arrow"], "Direction Arrow", "Next slide / section"),
    (["user", "account", "profile"], "User Account", "User profile"),
    (["cart", "shopping", "basket"], "Shopping Cart", "View cart"),
    (["filter"], "Filter", "Filter results"),
    (["settings", "gear", "cog"], "Settings", "Open settings"),
    (["plus", "add"], "Add New", "Add item"),
    (["minus", "remove", "trash", "delete"], "Delete", "Delete item"),
    (["play"], "Play Video", "Play media"),
    (["pause"], "Pause Video", "Pause media"),
]

def check_buttons(soup):
    issues = []
    for b in soup.find_all("button"):
        if not is_element_accessible(b):
            snippet = str(b)[:160] + ("..." if len(str(b)) > 160 else "")
            
            # Detect icons inside button
            icon_tags = b.find_all(["i", "span", "svg", "em"])
            icon_classes = []
            for it in icon_tags:
                cls = it.get("class", [])
                if isinstance(cls, list):
                    icon_classes.extend(cls)
                elif cls:
                    icon_classes.append(str(cls))
            icon_str = " ".join(icon_classes).lower()
            btn_id = b.get("id", "")
            btn_classes = " ".join(b.get("class", [])) if isinstance(b.get("class"), list) else b.get("class", "")

            detected_action = None
            suggested_label = None

            for patterns, name, default_label in ICON_BUTTON_MAPPINGS:
                if any(p in icon_str or p in btn_id.lower() or p in btn_classes.lower() for p in patterns):
                    detected_action = name
                    suggested_label = default_label
                    break

            if detected_action:
                main_cause = f"Icon-Only Button: The <button> displays a visual {detected_action} icon ({', '.join(icon_classes[:2]) or 'svg'}), but contains no readable text or aria-label."
                screen_reader_impact = f'Screen readers announce only "Button". Blind and low-vision users cannot tell that this button performs the {detected_action} action.'
                message = f"Icon-Only Button: {detected_action} button lacks an accessible name or aria-label"
                suggested_label = suggested_label or detected_action
                cause_badge = "Icon-Only Button"
            else:
                main_cause = "Empty Unlabelled Button: The <button> element contains no readable text, accessible label, or embedded graphic title."
                screen_reader_impact = 'Screen readers announce "Button, unlabelled". Assistive technology users cannot determine what action will occur when activated.'
                message = "Empty Button: <button> has no accessible name or readable text"
                suggested_label = "Submit Action"
                cause_badge = "Empty Button"

            class_attr = f' class="{btn_classes}"' if btn_classes else ""
            id_attr = f' id="{btn_id}"' if btn_id else ""
            remediation = f'<button{id_attr}{class_attr} aria-label="{suggested_label}">\n  {b.decode_contents().strip() or suggested_label}\n</button>'

            issues.append({
                "rule_id": "BUTTON_EMPTY",
                "wcag": "4.1.2",
                "level": "A",
                "pour": "Robust",
                "severity": "critical",
                "element": "button",
                "message": message,
                "html": snippet,
                "suggestion": f'Add aria-label="{suggested_label}" or provide visible button text.',
                "remediation": remediation,
                "main_cause": main_cause,
                "screen_reader_impact": screen_reader_impact,
                "target_detail": f"Button ({detected_action or 'Action'})",
                "recommended_fix": f'aria-label="{suggested_label}"',
                "cause_badge": cause_badge
            })
    return issues
