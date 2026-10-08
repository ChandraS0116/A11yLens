from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from auditor import run_audit
from sarif import generate_sarif
from remediator import generate_remediation
from crawler import audit_entire_site

app = FastAPI(
    title="A11yLens API",
    description="Automated WCAG 2.2 Web Accessibility Intelligence & Remediation Platform",
    version="2.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AuditRequest(BaseModel):
    url: str
    engine: Optional[str] = "fast"  # 'fast' (Static HTTP) or 'dynamic' (Headless Chrome)

class SiteAuditRequest(BaseModel):
    url: str
    max_pages: Optional[int] = 4
    engine: Optional[str] = "fast"

class RemediateRequest(BaseModel):
    html: str
    rule_id: str
    wcag: str
    message: Optional[str] = ""
    suggestion: Optional[str] = ""

@app.get("/")
def read_root():
    return {
        "name": "A11yLens API",
        "version": "2.2.0",
        "status": "healthy",
        "engines": ["Static HTTP (<500ms)", "Headless Chromium (SPAs)"],
        "capabilities": ["Single-Page Audit", "Multi-Page Site Crawl", "POUR Radar", "SARIF 2.1", "AI Remediation"],
        "standards": ["WCAG 2.1", "WCAG 2.2", "ADA Title III", "Section 508", "EAA 2025"],
        "endpoints": {
            "audit": "/api/audit",
            "audit_site": "/api/audit/site",
            "sarif": "/api/audit/sarif",
            "remediate": "/api/remediate",
            "badge": "/api/badge",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "A11yLens Core Engine", "version": "2.2.0"}

@app.post("/api/audit")
async def audit_url(request: AuditRequest):
    url = request.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
        
    engine = request.engine or "fast"
    audit_data = run_audit(url, engine=engine)
    if audit_data is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch or parse target URL. Ensure the site is reachable and allows public requests."
        )
        
    return audit_data

@app.post("/api/audit/site")
async def audit_site_wide(request: SiteAuditRequest):
    url = request.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    engine = request.engine or "fast"
    max_pages = min(max(1, request.max_pages or 4), 10)
    
    site_data = audit_entire_site(url, max_pages=max_pages, engine=engine)
    if site_data is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to crawl or audit target domain."
        )

    return site_data

@app.post("/api/audit/sarif")
async def audit_url_sarif(request: AuditRequest):
    url = request.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    engine = request.engine or "fast"
    audit_data = run_audit(url, engine=engine)
    if audit_data is None:
        raise HTTPException(
            status_code=400,
            detail="Failed to fetch target URL for SARIF generation."
        )

    sarif_output = generate_sarif(audit_data, url)
    return sarif_output

@app.post("/api/remediate")
async def remediate_code(request: RemediateRequest):
    remediation = generate_remediation(
        html_snippet=request.html,
        rule_id=request.rule_id,
        wcag=request.wcag,
        message=request.message,
        suggestion=request.suggestion
    )
    return remediation

@app.get("/api/badge")
def generate_badge(score: int = 100, grade: str = "A"):
    """Generates an embeddable SVG compliance badge for GitHub READMEs"""
    if score >= 90:
        color = "#10b981"  # emerald
    elif score >= 75:
        color = "#f59e0b"  # amber
    else:
        color = "#ef4444"  # red

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="165" height="28" role="img" aria-label="A11yLens: {score}% ({grade})">
  <linearGradient id="b" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="a">
    <rect width="165" height="28" rx="4" fill="#fff"/>
  </clipPath>
  <g clip-path="url(#a)">
    <rect width="70" height="28" fill="#1e293b"/>
    <rect x="70" width="95" height="28" fill="{color}"/>
    <rect width="165" height="28" fill="url(#b)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="11">
    <text x="35" y="18" fill="#fff" font-weight="bold">a11y</text>
    <text x="117" y="18" fill="#fff" font-weight="bold">{score}% • {grade}</text>
  </g>
</svg>"""
    return Response(content=svg, media_type="image/svg+xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
