"""
Image accessibility checks:
- WCAG 1.1.1 Non-text Content (Level A) - Perceivable
"""

def extract_img_source(img):
    """Extracts genuine image source, supporting lazy-loading and responsive srcset."""
    for attr in ["src", "data-src", "data-original", "data-lazy-src", "data-url"]:
        val = img.get(attr)
        if val and str(val).strip() and str(val).strip().lower() != "none":
            return str(val).strip()
    srcset = img.get("srcset")
    if srcset and str(srcset).strip():
        first = str(srcset).split(",")[0].strip().split()[0]
        if first:
            return first
    return None

def infer_suggested_alt(filename, element_id, class_list):
    """Infers human-readable contextual alternative text based on asset naming."""
    if not filename or filename.startswith("#") or filename.startswith("."):
        if element_id:
            return element_id.replace("-", " ").replace("_", " ").title()
        return "Descriptive label of visual content"
    clean = filename.rsplit(".", 1)[0] if "." in filename else filename
    clean = clean.replace("-", " ").replace("_", " ").title()
    if clean.lower() in ["image", "picture", "photo", "img", "logo"]:
        if element_id:
            clean = element_id.replace("-", " ").replace("_", " ").title()
        elif class_list:
            clean = " ".join(class_list).replace("-", " ").replace("_", " ").title()
        else:
            clean = "Organization Brand Logo"
    return clean

def check_images(soup):
    issues = []
    for img in soup.find_all("img"):
        alt = img.get("alt")
        img_str = str(img)
        if len(img_str) > 180:
            img_snippet = img_str[:180] + "...>"
        else:
            img_snippet = img_str

        src = extract_img_source(img)
        element_id = img.get("id", "")
        classes = img.get("class", [])
        if isinstance(classes, list):
            classes_str = " ".join(classes)
        else:
            classes_str = str(classes)

        if src:
            filename = src.split("/")[-1].split("?")[0] or "image"
            is_dynamic = False
        else:
            is_dynamic = True
            filename = f"#{element_id}" if element_id else f".{classes_str}" if classes_str else "Dynamic Image Element"
            src = None

        suggested_alt = infer_suggested_alt(filename if not is_dynamic else "", element_id, classes if isinstance(classes, list) else [classes_str])

        if alt is None:
            if is_dynamic:
                message = f"Dynamic image element ({filename}) is rendered without an alt attribute"
                main_cause = f"Dynamic Image Without Alt: The image node ({filename}) is injected or rendered in the DOM without an alt attribute. Assistive technologies cannot describe what will be rendered."
            else:
                message = f"Image '{filename}' is missing alternative text (alt attribute)"
                main_cause = f"Missing Alternative Text: The image asset '{filename}' lacks an alt attribute. Screen readers have no text to announce to blind and low-vision users."

            screen_reader_impact = f"Screen readers announce either the full cryptographic URL file path ('{filename}') or remain silent, leaving visually impaired users unaware of visual page content."

            issues.append({
                "rule_id": "IMG_ALT_MISSING",
                "wcag": "1.1.1",
                "level": "A",
                "pour": "Perceivable",
                "severity": "critical",
                "element": "img",
                "message": message,
                "html": img_snippet,
                "suggestion": f'Add a descriptive alt attribute (e.g. alt="{suggested_alt}"), or use alt="" if purely decorative.',
                "remediation": f'<img alt="{suggested_alt}" ... />',
                "main_cause": main_cause,
                "screen_reader_impact": screen_reader_impact,
                "target_detail": f"Asset: {filename}",
                "recommended_fix": f'alt="{suggested_alt}"',
                "cause_badge": "Missing Alt Attribute",
                "img_src": src,
                "img_alt": "",
                "img_filename": filename,
                "suggested_alt": suggested_alt,
                "is_dynamic": is_dynamic,
                "width": img.get("width", ""),
                "height": img.get("height", "")
            })
        elif alt.strip().lower() in ["image", "picture", "photo", "logo", "icon", "img", "graphic"]:
            message = f"Image uses non-descriptive filler alt text ('{alt.strip()}')"
            main_cause = f"Non-Descriptive Filler Alt Text: The image uses generic text ('{alt.strip()}') instead of describing the specific content or entity shown."
            screen_reader_impact = f"Screen readers announce only '{alt.strip()}', forcing users to guess which organization, icon, or photo is on screen."
            issues.append({
                "rule_id": "IMG_ALT_SUSPICIOUS",
                "wcag": "1.1.1",
                "level": "A",
                "pour": "Perceivable",
                "severity": "serious",
                "element": "img",
                "message": message,
                "html": img_snippet,
                "suggestion": f'Replace filler words with a descriptive label (recommended: "{suggested_alt}").',
                "remediation": f'<img alt="{suggested_alt}" ... />',
                "main_cause": main_cause,
                "screen_reader_impact": screen_reader_impact,
                "target_detail": f"Asset: {filename}",
                "recommended_fix": f'alt="{suggested_alt}"',
                "cause_badge": "Generic Placeholder Alt",
                "img_src": src,
                "img_alt": alt.strip(),
                "img_filename": filename,
                "suggested_alt": suggested_alt,
                "is_dynamic": is_dynamic,
                "width": img.get("width", ""),
                "height": img.get("height", "")
            })
    return issues
