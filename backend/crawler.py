"""
Multi-Page Site Crawler & Domain-Wide Audit Engine for A11yLens.
High-speed internal route discovery and aggregate domain accessibility health calculations.
Optimized with single-session Headless Chromium reuse and concurrent static threads.
"""
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from auditor import (
    run_audit,
    normalize_target_url,
    fetch_static_html,
    get_headless_driver
)

def extract_internal_links(base_url: str, html: str, max_links: int = 5) -> list:
    """Extracts unique internal links residing on the exact same domain."""
    if not html:
        return [base_url]

    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc.lower()
    
    soup = BeautifulSoup(html, "html.parser")
    found_links = set()
    found_links.add(base_url)
    
    for a in soup.find_all("a", href=True):
        href = a.get("href").strip()
        if not href or href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.startswith("javascript:"):
            continue
            
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        # Verify same domain
        if parsed.netloc.lower() == base_domain:
            clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")
            if not clean_url:
                clean_url = f"{parsed.scheme}://{parsed.netloc}"
                
            # Avoid downloading binary or media assets
            if not clean_url.lower().endswith((".pdf", ".zip", ".png", ".jpg", ".jpeg", ".svg", ".gif", ".webp", ".mp4", ".mp3", ".css", ".js")):
                found_links.add(clean_url)
                if len(found_links) >= max_links:
                    break
                    
    return list(found_links)[:max_links]

def audit_entire_site(base_url: str, max_pages: int = 4, engine: str = "fast") -> dict:
    """
    Crawls internal pages on a domain and runs comprehensive audits.
    Reuses a single Headless Chromium session in dynamic mode (5x-8x speedup)
    and uses concurrent workers in fast mode (<1s response).
    """
    url = normalize_target_url(base_url)
    max_pages = min(max(1, max_pages), 10)

    page_results = []
    total_score = 0
    issue_frequency = {}

    def record_audit(audit_res):
        nonlocal total_score
        if not audit_res:
            return
        total_score += audit_res["score"]
        page_results.append({
            "url": audit_res["url"],
            "page_title": audit_res["page_title"],
            "score": audit_res["score"],
            "grade": audit_res["grade"],
            "total_issues": audit_res["stats"]["total_issues"],
            "pour_scores": audit_res["pour_scores"],
            "severity": audit_res["stats"]["severity"]
        })
        for issue in audit_res["raw_issues"]:
            rid = issue["rule_id"]
            if rid not in issue_frequency:
                issue_frequency[rid] = {
                    "rule_id": rid,
                    "message": issue["message"],
                    "wcag": issue["wcag"],
                    "pour": issue["pour"],
                    "count": 0
                }
            issue_frequency[rid]["count"] += 1

    # DYNAMIC HEADLESS CHROMIUM ENGINE: Reuse a single browser instance!
    if engine == "dynamic":
        driver = None
        try:
            driver = get_headless_driver()
        except Exception as e:
            print(f"[A11yLens Crawler] Headless Chrome driver initialization failed: {e}. Falling back to Fast engine...")
            engine = "fast"

        if driver:
            try:
                driver.set_page_load_timeout(8)
                try:
                    driver.get(url)
                    time.sleep(0.3)
                    home_html = driver.page_source
                except Exception as e:
                    print(f"[A11yLens Crawler] Initial dynamic navigation failed on {url}: {e}")
                    home_html = fetch_static_html(url)

                # Extract internal links from the live rendered DOM (supports React / Vue SPAs)
                internal_urls = extract_internal_links(url, home_html or "", max_links=max_pages)

                # 1. Audit homepage immediately using home_html (0s extra network delay)
                home_audit = run_audit(url, engine="dynamic", existing_html=home_html)
                record_audit(home_audit)

                # 2. Sequentially audit remaining internal pages within the same browser session
                for p_url in internal_urls:
                    if p_url == url:
                        continue
                    try:
                        driver.get(p_url)
                        time.sleep(0.2)
                        p_html = driver.page_source
                    except Exception:
                        p_html = fetch_static_html(p_url)

                    p_audit = run_audit(p_url, engine="dynamic", existing_html=p_html)
                    record_audit(p_audit)
            finally:
                try:
                    driver.quit()
                except Exception:
                    pass

    # FAST STATIC HTTP ENGINE: Concurrent ThreadPool (<1s)
    if engine == "fast" or not page_results:
        home_html = fetch_static_html(url)
        internal_urls = extract_internal_links(url, home_html or "", max_links=max_pages)

        # Audit home page first
        home_audit = run_audit(url, engine="fast", existing_html=home_html)
        record_audit(home_audit)

        remaining_urls = [u for u in internal_urls if u != url]
        if remaining_urls:
            with ThreadPoolExecutor(max_workers=min(4, len(remaining_urls))) as executor:
                futures = [executor.submit(run_audit, p_url, "fast") for p_url in remaining_urls]
                for fut in futures:
                    try:
                        res = fut.result(timeout=12)
                        record_audit(res)
                    except Exception as e:
                        print(f"[A11yLens Crawler] Parallel audit error: {e}")

    if not page_results:
        return None

    site_avg_score = round(total_score / len(page_results))
    
    # Assign Site Grade
    if site_avg_score >= 95:
        site_grade = "A+"
    elif site_avg_score >= 85:
        site_grade = "A"
    elif site_avg_score >= 70:
        site_grade = "B"
    elif site_avg_score >= 50:
        site_grade = "C"
    else:
        site_grade = "F"

    # Sort systemic issues by frequency
    systemic_issues = sorted(issue_frequency.values(), key=lambda x: x["count"], reverse=True)

    return {
        "base_url": url,
        "engine": engine,
        "site_average_score": site_avg_score,
        "site_grade": site_grade,
        "pages_audited_count": len(page_results),
        "pages": page_results,
        "systemic_violations": systemic_issues[:8]
    }
