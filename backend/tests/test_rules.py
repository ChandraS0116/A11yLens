"""
Unit tests for A11yLens WCAG 2.2 Rule Evaluators.
"""
import pytest
from bs4 import BeautifulSoup

from rules.images import check_images
from rules.contrast import check_contrast, contrast_ratio, parse_color
from rules.links import check_links
from rules.buttons import check_buttons
from rules.forms import check_forms
from rules.keyboard import check_keyboard
from rules.headings import check_headings
from rules.language import check_language
from rules.aria import check_aria
from rules.tables import check_tables
from rules.meta import check_meta
from rules.media import check_media
from rules.obsolete import check_obsolete


def test_images_missing_alt():
    html = '<div><img src="avatar.jpg"></div>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_images(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "IMG_ALT_MISSING"
    assert issues[0]["pour"] == "Perceivable"
    assert issues[0]["severity"] == "critical"
    assert "alt=" in issues[0]["remediation"]


def test_images_suspicious_alt():
    html = '<div><img src="logo.png" alt="logo"></div>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_images(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "IMG_ALT_SUSPICIOUS"


def test_images_valid_alt():
    html = '<div><img src="chart.png" alt="Quarterly sales increase of 25 percent"></div>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_images(soup)
    assert len(issues) == 0


def test_contrast_calculation():
    # Pure black (#000000) on pure white (#ffffff) ratio is 21:1
    ratio = contrast_ratio((0, 0, 0), (255, 255, 255))
    assert pytest.approx(ratio, 0.1) == 21.0

    # Low contrast gray (#999999) on white (#ffffff)
    c1 = parse_color("#999999")
    c2 = parse_color("#ffffff")
    low_ratio = contrast_ratio(c1, c2)
    assert low_ratio < 4.5


def test_contrast_rule_evaluation():
    html = '<p style="color: #999999; background-color: #ffffff;">Subtle text</p>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_contrast(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "CONTRAST_LOW"
    assert issues[0]["wcag"] == "1.4.3"


def test_links_empty_and_generic():
    html = '''
    <div>
        <a href="/target"></a>
        <a href="/about">Click Here</a>
        <a href="/valid">Contact Us for Support</a>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    issues = check_links(soup)
    rule_ids = [i["rule_id"] for i in issues]
    assert "LINK_EMPTY" in rule_ids
    assert "LINK_GENERIC_TEXT" in rule_ids
    assert len(issues) == 2


def test_buttons_empty():
    html = '<button type="button"></button>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_buttons(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "BUTTON_EMPTY"
    assert issues[0]["pour"] == "Robust"


def test_forms_unlabeled_inputs():
    html = '''
    <form>
        <input type="text" id="username">
        <label for="email">Email</label>
        <input type="email" id="email">
    </form>
    '''
    soup = BeautifulSoup(html, "html.parser")
    issues = check_forms(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "FORM_MISSING_LABEL"
    assert issues[0]["pour"] == "Understandable"


def test_keyboard_navigation_and_tabindex():
    html = '''
    <div>
        <div onclick="doSomething()">Clickable Div</div>
        <button tabindex="3">Tab 3 Button</button>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    issues = check_keyboard(soup)
    rule_ids = [i["rule_id"] for i in issues]
    assert "KEYBOARD_NON_INTERACTIVE_CLICK" in rule_ids
    assert "KEYBOARD_POSITIVE_TABINDEX" in rule_ids


def test_headings_skips_and_missing_h1():
    html = '''
    <div>
        <h2>First Section</h2>
        <h4>Skipped Sub-section</h4>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    issues = check_headings(soup)
    rule_ids = [i["rule_id"] for i in issues]
    assert "HEADING_MISSING_H1" in rule_ids
    assert "HEADING_LEVEL_SKIP" in rule_ids


def test_language_missing():
    html = '<html><head><title>Test</title></head><body>Hello</body></html>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_language(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "LANG_MISSING"


def test_aria_invalid_and_hidden_focusable():
    html = '''
    <div>
        <div role="fake-super-role">Custom item</div>
        <button aria-hidden="true">Hidden action</button>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    issues = check_aria(soup)
    rule_ids = [i["rule_id"] for i in issues]
    assert "ARIA_INVALID_ROLE" in rule_ids
    assert "ARIA_HIDDEN_FOCUSABLE" in rule_ids


def test_tables_missing_th_and_scope():
    html = '''
    <table>
        <tr><td>Data 1</td><td>Data 2</td></tr>
    </table>
    '''
    soup = BeautifulSoup(html, "html.parser")
    issues = check_tables(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "TABLE_MISSING_TH"


def test_meta_viewport_and_title():
    html = '''
    <html>
        <head>
            <meta name="viewport" content="width=device-width, user-scalable=no">
        </head>
        <body>No title test</body>
    </html>
    '''
    soup = BeautifulSoup(html, "html.parser")
    issues = check_meta(soup)
    rule_ids = [i["rule_id"] for i in issues]
    assert "PAGE_MISSING_TITLE" in rule_ids
    assert "VIEWPORT_ZOOM_DISABLED" in rule_ids


def test_media_missing_captions():
    html = '<video src="demo.mp4" autoplay></video>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_media(soup)
    rule_ids = [i["rule_id"] for i in issues]
    assert "VIDEO_MISSING_CAPTIONS" in rule_ids
    assert "MEDIA_AUTOPLAY_UNMUTED" in rule_ids


def test_obsolete_tags():
    html = '<div><marquee>Scrolling Notice</marquee><center>Centered</center></div>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_obsolete(soup)
    assert len(issues) == 2
    rule_ids = [i["rule_id"] for i in issues]
    assert "OBSOLETE_MARQUEE" in rule_ids
    assert "OBSOLETE_CENTER" in rule_ids


def test_target_size():
    from rules.target_size import check_target_size
    html = '<button style="width: 16px; height: 16px;">Tiny</button>'
    soup = BeautifulSoup(html, "html.parser")
    issues = check_target_size(soup)
    assert len(issues) == 1
    assert issues[0]["rule_id"] == "TARGET_SIZE_TOO_SMALL"
    assert issues[0]["wcag"] == "2.5.8"
