"""
Unit tests for multi-page crawler and link extraction.
"""
from crawler import extract_internal_links

def test_extract_internal_links():
    base_url = "https://example.com"
    html = '''
    <html>
        <body>
            <a href="/about">About Us</a>
            <a href="/pricing">Pricing Plans</a>
            <a href="https://external.com">External Site</a>
            <a href="https://example.com/contact">Contact</a>
            <a href="mailto:info@example.com">Email</a>
            <a href="#section">Hash link</a>
        </body>
    </html>
    '''
    links = extract_internal_links(base_url, html, max_links=5)
    assert "https://example.com" in links
    assert "https://example.com/about" in links
    assert "https://example.com/pricing" in links
    assert "https://example.com/contact" in links
    assert "https://external.com" not in links
    assert len(links) <= 5
