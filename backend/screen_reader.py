"""
Screen Reader Announcement Synthesizer for A11yLens.
Generates linear auditory announcement sequences mimicking VoiceOver, NVDA, and JAWS.
"""
from bs4 import BeautifulSoup

def simulate_screen_reader_stream(soup: BeautifulSoup, page_title: str) -> dict:
    announcements = []
    
    # 1. Page Load Announcement
    announcements.append({
        "type": "document",
        "announcement": f"Web page loaded: {page_title or 'Untitled Page'}",
        "accessible": True
    })

    html_tag = soup.find("html")
    lang = html_tag.get("lang") if html_tag else None
    if lang:
        announcements.append({
            "type": "language",
            "announcement": f"Document language: {lang}",
            "accessible": True
        })
    else:
        announcements.append({
            "type": "language",
            "announcement": "Warning: Document language not specified, default system synthesizer active",
            "accessible": False
        })

    # Traverse major semantic nodes in document order
    for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "a", "button", "input", "img", "table", "p"]):
        # Headings
        if tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = tag.name[1]
            text = tag.get_text(strip=True)
            if text:
                announcements.append({
                    "type": "heading",
                    "announcement": f"Heading level {level}, {text}",
                    "accessible": True,
                    "html": str(tag)[:120]
                })

        # Links
        elif tag.name == "a":
            text = tag.get_text(strip=True)
            aria = tag.get("aria-label") or tag.get("title")
            eff = aria or text
            if eff:
                is_generic = eff.lower() in ["click here", "read more", "here", "more"]
                announcements.append({
                    "type": "link",
                    "announcement": f"Link, {eff}",
                    "accessible": not is_generic,
                    "html": str(tag)[:120]
                })
            else:
                announcements.append({
                    "type": "link",
                    "announcement": "Link, unlabelled link",
                    "accessible": False,
                    "html": str(tag)[:120]
                })

        # Buttons
        elif tag.name == "button":
            text = tag.get_text(strip=True)
            aria = tag.get("aria-label")
            eff = aria or text
            if eff:
                announcements.append({
                    "type": "button",
                    "announcement": f"Button, {eff}",
                    "accessible": True,
                    "html": str(tag)[:120]
                })
            else:
                announcements.append({
                    "type": "button",
                    "announcement": "Button, unlabelled button",
                    "accessible": False,
                    "html": str(tag)[:120]
                })

        # Inputs
        elif tag.name == "input":
            inp_type = tag.get("type", "text").lower()
            if inp_type in ["hidden", "submit"]:
                continue
            aria = tag.get("aria-label")
            inp_id = tag.get("id")
            label_tag = soup.find("label", attrs={"for": inp_id}) if inp_id else None
            label_text = aria or (label_tag.get_text(strip=True) if label_tag else None)
            
            if label_text:
                announcements.append({
                    "type": "input",
                    "announcement": f"Edit text, {label_text}",
                    "accessible": True,
                    "html": str(tag)[:120]
                })
            else:
                announcements.append({
                    "type": "input",
                    "announcement": f"Edit text, unlabelled input field",
                    "accessible": False,
                    "html": str(tag)[:120]
                })

        # Images
        elif tag.name == "img":
            alt = tag.get("alt")
            if alt is None:
                announcements.append({
                    "type": "image",
                    "announcement": "Graphic, unlabelled image",
                    "accessible": False,
                    "html": str(tag)[:120]
                })
            elif alt.strip() == "":
                # Purely decorative, screen readers omit
                continue
            else:
                announcements.append({
                    "type": "image",
                    "announcement": f"Graphic, {alt.strip()}",
                    "accessible": True,
                    "html": str(tag)[:120]
                })

        # Limit announcement stream to first 40 major elements
        if len(announcements) >= 40:
            break

    # Build plain speech script
    full_speech_script = ". ".join(item["announcement"] for item in announcements) + "."

    return {
        "full_speech": full_speech_script,
        "items": announcements,
        "total_announced": len(announcements)
    }
