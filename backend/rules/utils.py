def is_element_accessible(element):
    if element.get_text(strip=True):
        return True
    if element.get("aria-label") or element.get("aria-labelledby") or element.get("title"):
        return True
    for img in element.find_all("img"):
        alt = img.get("alt")
        if alt and alt.strip():
            return True
    for svg in element.find_all("svg"):
        title = svg.find("title")
        if title and title.get_text(strip=True):
            return True
    return False
