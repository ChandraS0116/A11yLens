"""
Table accessibility checks:
- WCAG 1.3.1 Info and Relationships (Level A) - Understandable
"""

def check_tables(soup):
    issues = []
    
    for table in soup.find_all("table"):
        role = table.get("role", "").lower()
        if role in ["presentation", "none"]:
            continue
            
        ths = table.find_all("th")
        table_snippet = str(table).split(">")[0] + ">"
        
        # 1. Missing header cells
        if not ths:
            issues.append({
                "rule_id": "TABLE_MISSING_TH",
                "wcag": "1.3.1",
                "level": "A",
                "pour": "Understandable",
                "severity": "serious",
                "element": "table",
                "message": "Data table contains no header cells (<th>)",
                "html": table_snippet,
                "suggestion": "Use <th> elements for column and row headers to give data context to screen readers.",
                "remediation": "<table>\n  <thead>\n    <tr><th scope=\"col\">Column 1</th><th scope=\"col\">Column 2</th></tr>\n  </thead>\n  <tbody>...</tbody>\n</table>"
            })
            continue
            
        # 2. Scope attributes on th
        for th in ths:
            scope = th.get("scope")
            if not scope or scope not in ["row", "col", "rowgroup", "colgroup"]:
                snippet = str(th)[:160] + ("..." if len(str(th)) > 160 else "")
                issues.append({
                    "rule_id": "TABLE_TH_MISSING_SCOPE",
                    "wcag": "1.3.1",
                    "level": "A",
                    "pour": "Understandable",
                    "severity": "moderate",
                    "element": "th",
                    "message": "Table header cell (<th>) lacks an explicit 'scope' attribute (col/row)",
                    "html": snippet,
                    "suggestion": "Add scope=\"col\" or scope=\"row\" to associate headers with data cells.",
                    "remediation": f'<th scope="col">{th.get_text(strip=True) or "Header"}</th>'
                })
                
        # 3. Table missing caption
        if not table.find("caption"):
            issues.append({
                "rule_id": "TABLE_MISSING_CAPTION",
                "wcag": "1.3.1",
                "level": "AA",
                "pour": "Understandable",
                "severity": "minor",
                "element": "table",
                "message": "Data table is missing an explanatory <caption> summary element",
                "html": table_snippet,
                "suggestion": "Provide a <caption> inside the table describing its contents.",
                "remediation": "<table>\n  <caption>Quarterly Financial Performance Overview</caption>\n  ..."
            })
            
    return issues
