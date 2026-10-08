"""
Color contrast accessibility checks:
- WCAG 1.4.3 Contrast (Minimum) (Level AA) - Perceivable
"""
import re

NAMED_COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 0, 0),
    "lime": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "silver": (192, 192, 192),
    "maroon": (128, 0, 0),
    "navy": (0, 0, 128),
    "teal": (0, 128, 128),
    "purple": (128, 0, 128),
    "orange": (255, 165, 0),
    "darkgray": (169, 169, 169),
    "lightgray": (211, 211, 211),
}

def parse_color(color_str):
    if not color_str:
        return None
    c = color_str.strip().lower()
    
    # Check named color
    if c in NAMED_COLORS:
        return NAMED_COLORS[c]
        
    # Check hex
    if c.startswith("#"):
        hex_val = c.lstrip("#")
        if len(hex_val) == 3:
            hex_val = "".join(ch + ch for ch in hex_val)
        if len(hex_val) >= 6:
            try:
                return (int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16))
            except ValueError:
                return None
                
    # Check rgb / rgba
    rgb_match = re.match(r"rgba?\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)", c)
    if rgb_match:
        try:
            return (int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3)))
        except ValueError:
            return None
            
    return None

def luminance(r, g, b):
    rgb = [r / 255.0, g / 255.0, b / 255.0]
    for i in range(3):
        if rgb[i] <= 0.03928:
            rgb[i] /= 12.92
        else:
            rgb[i] = ((rgb[i] + 0.055) / 1.055) ** 2.4
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

def contrast_ratio(rgb1, rgb2):
    l1 = luminance(*rgb1)
    l2 = luminance(*rgb2)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

def check_contrast(soup):
    issues = []
    for tag in soup.find_all(style=True):
        style = tag["style"]
        
        color_match = re.search(r"(?<!-)\bcolor:\s*([^;]+)", style, re.IGNORECASE)
        bg_match = re.search(r"\bbackground(?:-color)?:\s*([^;]+)", style, re.IGNORECASE)
        
        if color_match and bg_match:
            c1 = parse_color(color_match.group(1))
            c2 = parse_color(bg_match.group(1))
            
            if c1 and c2:
                try:
                    ratio = contrast_ratio(c1, c2)
                    if ratio < 4.5:
                        snippet = str(tag)[:160] + ("..." if len(str(tag)) > 160 else "")
                        fg = color_match.group(1).strip()
                        bg = bg_match.group(1).strip()
                        main_cause = f"Low Color Contrast Ratio: Foreground text color '{fg}' on background '{bg}' yields a contrast ratio of {ratio:.2f}:1, failing the WCAG AA minimum threshold of 4.5:1."
                        screen_reader_impact = "Users with low vision, contrast sensitivity loss, or color blindness, as well as users under direct sunlight glare, cannot comfortably read or discern this text."
                        issues.append({
                            "rule_id": "CONTRAST_LOW",
                            "wcag": "1.4.3",
                            "level": "AA",
                            "pour": "Perceivable",
                            "severity": "critical" if ratio < 3.0 else "serious",
                            "element": tag.name,
                            "message": f"Insufficient color contrast ratio ({ratio:.2f}:1, minimum is 4.5:1)",
                            "html": snippet,
                            "suggestion": f"Increase the contrast between foreground color '{fg}' and background '{bg}' to at least 4.5:1 (or 3:1 for large text).",
                            "remediation": f'style="color: #0f172a; background-color: #ffffff; /* Contrast 18.2:1 */"',
                            "main_cause": main_cause,
                            "screen_reader_impact": screen_reader_impact,
                            "target_detail": f"Colors: {fg} on {bg} ({ratio:.2f}:1)",
                            "recommended_fix": f"Adjust {fg} on {bg} to reach ≥ 4.5:1",
                            "cause_badge": "Contrast Below 4.5:1",
                            "fg_color": fg,
                            "bg_color": bg,
                            "contrast_ratio": round(ratio, 2)
                        })
                except Exception:
                    pass
    return issues
