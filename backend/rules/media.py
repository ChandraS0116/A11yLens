"""
Media checks:
- WCAG 1.2.2 Captions (Prerecorded) (Level A) - Perceivable
- WCAG 1.4.2 Audio Control (Level A) - Perceivable
"""

def check_media(soup):
    issues = []
    
    # 1. Videos missing captions tracks
    for video in soup.find_all("video"):
        tracks = video.find_all("track")
        has_captions = any(t.get("kind") in ["captions", "subtitles"] for t in tracks)
        if not has_captions:
            issues.append({
                "rule_id": "VIDEO_MISSING_CAPTIONS",
                "wcag": "1.2.2",
                "level": "A",
                "pour": "Perceivable",
                "severity": "critical",
                "element": "video",
                "message": "Video element is missing captions or subtitles (<track kind='captions'>)",
                "html": str(video)[:160] + ("..." if len(str(video)) > 160 else ""),
                "suggestion": "Provide closed captions or subtitles using the <track kind='captions'> element for deaf and hard-of-hearing users.",
                "remediation": f'<video src="..." controls>\n  <track kind="captions" src="captions_en.vtt" srclang="en" label="English">\n</video>'
            })
            
        # Check autoplay with sound
        if video.has_attr("autoplay") and not video.has_attr("muted"):
            issues.append({
                "rule_id": "MEDIA_AUTOPLAY_UNMUTED",
                "wcag": "1.4.2",
                "level": "A",
                "pour": "Perceivable",
                "severity": "serious",
                "element": "video",
                "message": "Video element autoplays audio without being muted by default",
                "html": str(video)[:160] + ("..." if len(str(video)) > 160 else ""),
                "suggestion": "Do not autoplay audio automatically, or add the 'muted' attribute to preserve accessibility.",
                "remediation": '<video autoplay muted controls ...>'
            })

    # 2. Audios with autoplay
    for audio in soup.find_all("audio"):
        if audio.has_attr("autoplay"):
            issues.append({
                "rule_id": "MEDIA_AUTOPLAY_AUDIO",
                "wcag": "1.4.2",
                "level": "A",
                "pour": "Perceivable",
                "severity": "serious",
                "element": "audio",
                "message": "Audio element autoplays without user interaction",
                "html": str(audio)[:160] + ("..." if len(str(audio)) > 160 else ""),
                "suggestion": "Ensure audio does not play automatically for more than 3 seconds without a visible control to stop it.",
                "remediation": '<audio controls ...>'
            })

    return issues
