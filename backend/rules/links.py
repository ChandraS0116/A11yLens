"""
Link accessibility checks:
- WCAG 2.4.4 Link Purpose (In Context) (Level A) - Operable
- WCAG 4.1.2 Name, Role, Value (Level A) - Robust
"""
import re
from .utils import is_element_accessible

GENERIC_LINK_TEXTS = {
    "click here", "click", "here", "read more", "learn more", "more",
    "details", "link", "this link", "go", "view", "continue", "info"
}

ICON_MAPPINGS = [
    (["facebook", "fa-facebook"], "Facebook", "Follow on Facebook"),
    (["twitter", "fa-twitter", "x-twitter"], "Twitter / X", "Follow on Twitter / X"),
    (["instagram", "fa-instagram"], "Instagram", "Follow on Instagram"),
    (["linkedin", "fa-linkedin"], "LinkedIn", "Connect on LinkedIn"),
    (["youtube", "fa-youtube"], "YouTube", "Subscribe on YouTube"),
    (["pinterest", "fa-pinterest"], "Pinterest", "Follow on Pinterest"),
    (["whatsapp", "fa-whatsapp"], "WhatsApp", "Chat on WhatsApp"),
    (["envelope", "mail", "email"], "Email Contact", "Send Email Inquiry"),
    (["phone", "tel", "call"], "Telephone", "Call Contact Number"),
    (["map-marker", "location", "marker", "map"], "Campus Map Location", "View Location on Map"),
    (["search", "magnifying-glass"], "Search", "Search Website"),
    (["bars", "navicon", "hamburger", "menu"], "Navigation Menu", "Toggle Navigation Menu"),
    (["close", "times", "cross"], "Close", "Close Dialog"),
    (["chevron", "angle", "arrow-right", "arrow-left", "arrow"], "Direction Arrow", "Go to Next Section"),
    (["user", "account", "login", "profile"], "User Account", "User Account / Login"),
    (["cart", "shopping", "basket"], "Shopping Cart", "View Shopping Cart"),
    (["globe", "language"], "Language / Region", "Select Language / Region"),
    (["pdf", "file-pdf", "download"], "Download Document", "Download File / Document"),
]

def analyze_link_main_cause(a, href):
    """
    Determines the precise main cause, screen reader impact, and contextual fix for an inaccessible link.
    """
    # 1. Check if link wraps an image
    imgs = a.find_all("img")
    if imgs:
        img = imgs[0]
        src = img.get("src") or img.get("data-src") or "image"
        filename = src.split("/")[-1].split("?")[0] if "/" in src else src
        clean_name = filename.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title() if "." in filename else "Image"
        alt = img.get("alt")
        
        if alt == "":
            main_cause = f"The <a> link wraps an image ('{filename}') with an explicit empty alt attribute (alt=\"\"). Because the link has no text and the image has alt=\"\", the entire link is completely silent to assistive technologies."
        elif alt is None:
            main_cause = f"The <a> link wraps an image ('{filename}') which lacks an alt attribute entirely. Screen readers cannot tell users what this visual link represents."
        else:
            main_cause = f"The <a> link wraps an image ('{filename}') with non-descriptive alt text ('{alt}')."

        screen_reader_impact = f'Screen readers announce "Link, graphic" or speak the raw image URL without explaining where the link leads.'
        target_detail = f"Image Asset: {filename}"
        suggested_label = f"Go to {clean_name}"
        remediation_code = f'<a href="{href or "#"}">\n  <img src="{src}" alt="{clean_name}" />\n</a>'
        message = f"Image Link: Wraps image '{filename}' without accessible alternative text"
        cause_badge = "Image Missing Alt"

        return {
            "main_cause": main_cause,
            "screen_reader_impact": screen_reader_impact,
            "target_detail": target_detail,
            "target_href": href,
            "suggested_label": suggested_label,
            "remediation_code": remediation_code,
            "message": message,
            "cause_badge": cause_badge,
            "category_type": "image_link"
        }

    # 2. Check for visual icon inside (i, span, svg, em)
    icon_tags = a.find_all(["i", "span", "svg", "em"])
    icon_classes = []
    for it in icon_tags:
        cls = it.get("class", [])
        if isinstance(cls, list):
            icon_classes.extend(cls)
        elif cls:
            icon_classes.append(str(cls))

    icon_str = " ".join(icon_classes).lower()
    href_str = (href or "").lower()

    icon_detected = None
    suggested_label = None

    # Check href patterns first
    if "mailto:" in href_str:
        icon_detected = "Email Contact"
        email_addr = href.replace("mailto:", "").split("?")[0]
        suggested_label = f"Send email to {email_addr}" if email_addr else "Send Email Inquiry"
    elif "tel:" in href_str:
        icon_detected = "Telephone"
        phone_num = href.replace("tel:", "").split("?")[0]
        suggested_label = f"Call {phone_num}" if phone_num else "Call Contact Number"
    elif "facebook.com" in href_str:
        icon_detected = "Facebook"
        suggested_label = "Follow on Facebook"
    elif "instagram.com" in href_str:
        icon_detected = "Instagram"
        suggested_label = "Follow on Instagram"
    elif "twitter.com" in href_str or "x.com" in href_str:
        icon_detected = "Twitter / X"
        suggested_label = "Follow on Twitter / X"
    elif "linkedin.com" in href_str:
        icon_detected = "LinkedIn"
        suggested_label = "Connect on LinkedIn"
    elif "youtube.com" in href_str:
        icon_detected = "YouTube"
        suggested_label = "Watch on YouTube"
    elif "pinterest.com" in href_str:
        icon_detected = "Pinterest"
        suggested_label = "Follow on Pinterest"

    # Check icon classes if not yet detected
    if not icon_detected:
        for patterns, name, default_label in ICON_MAPPINGS:
            if any(p in icon_str for p in patterns):
                icon_detected = name
                suggested_label = default_label
                break

    if icon_detected:
        class_snippet = f"class=\"{' '.join(icon_classes[:2])}\"" if icon_classes else "inline graphic"
        main_cause = f"The <a> link is an icon-only element displaying a visual {icon_detected} icon (<i {class_snippet}>), but contains NO readable text, aria-label, or title."
        screen_reader_impact = f'Screen readers announce only "Link" into silence. Visually impaired users cannot determine that this is the {icon_detected} link.'
        message = f"Icon-Only Link: {icon_detected} icon has no accessible text or aria-label"
        return {
            "main_cause": main_cause,
            "screen_reader_impact": screen_reader_impact,
            "target_detail": f"Visual Icon: {icon_detected} ({', '.join(icon_classes[:2]) if icon_classes else 'svg'})",
            "target_href": href,
            "suggested_label": suggested_label or f"Activate {icon_detected}",
            "remediation_code": f'<a href="{href or "#"}" aria-label="{suggested_label or icon_detected}">\n  <i {class_snippet}></i>\n</a>',
            "message": message,
            "cause_badge": "Icon Without Label",
            "category_type": "icon_link"
        }

    # 3. Check inline SVG
    svgs = a.find_all("svg")
    if svgs:
        return {
            "main_cause": "The <a> link wraps an inline <svg> graphic without an internal <title> tag, aria-label, or readable text.",
            "screen_reader_impact": 'Screen readers ignore the graphical vector and announce an unnamed empty link.',
            "target_detail": "Vector SVG Graphic",
            "target_href": href,
            "suggested_label": "Interactive Graphic Link",
            "remediation_code": f'<a href="{href or "#"}" aria-label="Interactive Action Description">\n  <svg ...>...</svg>\n</a>',
            "message": "SVG Link: Vector graphic link lacks an accessible <title> or aria-label",
            "cause_badge": "SVG Without Title",
            "category_type": "svg_link"
        }

    # 4. Completely empty anchor tag
    clean_target = href.strip("/").split("/")[-1].replace("-", " ").replace("_", " ").title() if href and not href.startswith("#") else "Page Action"
    if href in ["#", "", "javascript:void(0)", "javascript:;"]:
        main_cause = f"The <a> tag has href=\"{href}\" and contains no text, icons, or images. It functions as an empty phantom node in the keyboard focus order."
        screen_reader_impact = 'Screen readers announce "Link" followed by dead silence. Keyboard users tabbing through will land on an invisible phantom element that triggers nothing.'
        message = f"Empty Phantom Link: Anchor tag has no content (href=\"{href}\")"
        suggested_label = "Perform Page Action"
        cause_badge = "Empty Ghost Link"
    else:
        main_cause = f"The <a> link points to \"{href}\" but is completely blank with no visible text, aria-label, or inner elements."
        screen_reader_impact = f'Screen readers announce "Link" into silence. Blind users cannot know this navigates to {href}.'
        message = f"Blank Link: Navigates to '{href}' but contains no text or label"
        suggested_label = f"Go to {clean_target}"
        cause_badge = "Blank Link"

    return {
        "main_cause": main_cause,
        "screen_reader_impact": screen_reader_impact,
        "target_detail": f"Destination: {href or '#'}",
        "target_href": href,
        "suggested_label": suggested_label,
        "remediation_code": f'<a href="{href or "#"}" aria-label="{suggested_label}">{clean_target}</a>',
        "message": message,
        "cause_badge": cause_badge,
        "category_type": "empty_link"
    }

def check_links(soup):
    issues = []
    for a in soup.find_all("a"):
        href = a.get("href")
        text = a.get_text(strip=True).lower()
        aria_label = (a.get("aria-label") or "").strip().lower()
        effective_name = aria_label or text

        # 1. Empty / non-accessible link
        if not is_element_accessible(a) and href:
            analysis = analyze_link_main_cause(a, href)
            snippet = str(a)[:160] + ("..." if len(str(a)) > 160 else "")
            issues.append({
                "rule_id": "LINK_EMPTY",
                "wcag": "2.4.4",
                "level": "A",
                "pour": "Operable",
                "severity": "critical",
                "element": "a",
                "message": analysis["message"],
                "html": snippet,
                "suggestion": f"Add an aria-label=\"{analysis['suggested_label']}\" or provide visible link text.",
                "remediation": analysis["remediation_code"],
                "main_cause": analysis["main_cause"],
                "screen_reader_impact": analysis["screen_reader_impact"],
                "target_detail": analysis["target_detail"],
                "target_href": analysis["target_href"],
                "recommended_fix": f'aria-label="{analysis["suggested_label"]}"',
                "cause_badge": analysis["cause_badge"]
            })
            continue

        # 2. Generic non-descriptive link text
        if effective_name in GENERIC_LINK_TEXTS:
            clean_dest = href.strip("/").split("/")[-1].replace("-", " ").replace("_", " ").title() if href and not href.startswith("#") else "Target Section"
            suggested_phrase = f"Read more about {clean_dest}" if "more" in text or "read" in text else f"Go to {clean_dest}"
            snippet = str(a)[:160] + ("..." if len(str(a)) > 160 else "")
            main_cause = f"Ambiguous Generic Text: The link text is simply \"{text}\". In WCAG guidelines, link destination must be clear from the anchor text alone or programmatic context. Screen reader users browsing a list of page links hear repetitive '{text}' with zero indication of where this link navigates."
            sr_impact = f"Screen reader users browsing links hear only \"{text}, link\", making it impossible to identify which article or section will be opened."
            issues.append({
                "rule_id": "LINK_GENERIC_TEXT",
                "wcag": "2.4.4",
                "level": "A",
                "pour": "Operable",
                "severity": "serious",
                "element": "a",
                "message": f"Ambiguous Link Text: Generic phrase '{text}' lacks destination context",
                "html": snippet,
                "suggestion": f"Replace generic phrase '{text}' with specific destination details (e.g., '{suggested_phrase}').",
                "remediation": f'<a href="{href or "#"}">{suggested_phrase}</a>',
                "main_cause": main_cause,
                "screen_reader_impact": sr_impact,
                "target_detail": f'Anchor Text: "{text}"',
                "target_href": href,
                "recommended_fix": f'Replace "{text}" with "{suggested_phrase}"',
                "cause_badge": "Ambiguous Link Text"
            })

        # 3. Dummy href or pseudo-button (href="#" or href="javascript:...")
        if href in ["#", "javascript:void(0)", "javascript:;", ""]:
            if a.has_attr("onclick") or a.get("role") == "button":
                snippet = str(a)[:160] + ("..." if len(str(a)) > 160 else "")
                main_cause = f"Anchor Tag Acting as Scripted Button: The <a> tag has dummy href=\"{href}\" with a JavaScript handler. In standard HTML, hyperlinks are for navigation to resources; action triggers should be native <button> elements."
                sr_impact = 'Screen readers announce "Link" instead of "Button", confusing users expecting navigation rather than an interactive page state change.'
                issues.append({
                    "rule_id": "LINK_AS_BUTTON",
                    "wcag": "4.1.2",
                    "level": "A",
                    "pour": "Operable",
                    "severity": "moderate",
                    "element": "a",
                    "message": f"Anchor as Button: <a> with href=\"{href}\" is used as an interactive button",
                    "html": snippet,
                    "suggestion": "Use a native <button type='button'> instead of an anchor tag for interactive scripted triggers.",
                    "remediation": f'<button type="button" class="{a.get("class", ["btn"])[0] if isinstance(a.get("class"), list) else "btn"}">{a.get_text(strip=True) or "Action"}</button>',
                    "main_cause": main_cause,
                    "screen_reader_impact": sr_impact,
                    "target_detail": f"Dummy href: {href}",
                    "target_href": href,
                    "recommended_fix": '<button type="button">...</button>',
                    "cause_badge": "Improper Anchor as Button"
                })

    return issues
