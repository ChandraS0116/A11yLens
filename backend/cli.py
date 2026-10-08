"""
A11yLens CLI: Enterprise Command-Line Automated WCAG Accessibility Auditor
Supports terminal reports, JSON, and SARIF output with CI/CD exit gates and dual-engine crawling.
"""
import sys
import json
import argparse
from auditor import run_audit
from sarif import generate_sarif

def print_banner():
    print("""
\033[1;36m======================================================================\033[0m
\033[1;35m       A11yLens — Enterprise WCAG 2.2 Accessibility Engine            \033[0m
\033[1;36m======================================================================\033[0m
""")

def main():
    parser = argparse.ArgumentParser(description="A11yLens Automated WCAG 2.2 Accessibility Auditor")
    parser.add_argument("url", help="Target URL to audit (e.g. https://example.com)")
    parser.add_argument("--engine", choices=["fast", "dynamic"], default="fast", help="Crawler engine: 'fast' (Static HTTP) or 'dynamic' (Headless Chromium)")
    parser.add_argument("--format", choices=["text", "json", "sarif"], default="text", help="Output format")
    parser.add_argument("--output", "-o", help="Save output to file")
    parser.add_argument("--min-score", type=int, default=0, help="Minimum acceptable score (0-100). Exits with 1 if lower.")
    parser.add_argument("--fail-on", choices=["critical", "serious", "moderate", "any"], help="Fail CI/CD exit code if violations of this severity exist.")
    
    args = parser.parse_args()

    url = args.url.strip()
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    if args.format == "text":
        print_banner()
        print(f"\033[1;33m[+] Auditing URL:\033[0m {url}")
        print(f"\033[1;34m[*] Engine:\033[0m       {'Headless Chromium (Dynamic)' if args.engine == 'dynamic' else 'Static HTTP (<500ms)'}")
        print("\033[1;30m[*] Running 13 WCAG 2.2 rule evaluators across POUR principles...\033[0m")

    result = run_audit(url, engine=args.engine)
    if not result:
        print("\033[1;31m[!] Error: Unable to fetch or parse target URL.\033[0m", file=sys.stderr)
        sys.exit(2)

    # Format outputs
    if args.format == "json":
        out_content = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out_content)
            print(f"JSON report written to {args.output}")
        else:
            print(out_content)

    elif args.format == "sarif":
        sarif_data = generate_sarif(result, url)
        out_content = json.dumps(sarif_data, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out_content)
            print(f"SARIF report written to {args.output}")
        else:
            print(out_content)

    else:
        # Beautiful text output
        score = result["score"]
        grade = result["grade"]
        stats = result["stats"]
        pour = result["pour_scores"]
        reg = result.get("regulatory", {})

        score_color = "\033[1;32m" if score >= 85 else ("\033[1;33m" if score >= 70 else "\033[1;31m")

        print(f"\n\033[1mTarget Title:\033[0m {result['page_title']}")
        print(f"\033[1mEngine Used:\033[0m  {result.get('engine_used', 'Static HTTP')}")
        print(f"\033[1mAudit Time:\033[0m   {stats['duration_ms']} ms ({stats['total_elements_scanned']} DOM nodes scanned)\n")

        print(f"===================== AUDIT SUMMARY =====================")
        print(f" Overall Score:     {score_color}{score}/100\033[0m [Grade: {grade}]")
        print(f" Compliance Status: {result['status']}")
        print(f" ADA Title III:     {reg.get('ada_risk', 'Unknown')}")
        print(f" Section 508:       {reg.get('section_508', 'Unknown')}")
        print(f" EAA 2025:          {reg.get('eaa_2025', 'Unknown')}")
        print(f"---------------------------------------------------------")
        print(f" Perceivable:       {pour['perceivable']}/100")
        print(f" Operable:          {pour['operable']}/100")
        print(f" Understandable:    {pour['understandable']}/100")
        print(f" Robust:            {pour['robust']}/100")
        print(f"---------------------------------------------------------")
        print(f" Violations:        \033[1;31mCritical: {stats['severity']['critical']}\033[0m | \033[1;33mSerious: {stats['severity']['serious']}\033[0m | Moderate: {stats['severity']['moderate']} | Minor: {stats['severity']['minor']}")
        print(f" WCAG Levels:       Level A: {stats['levels']['A']} | Level AA: {stats['levels']['AA']} | Level AAA: {stats['levels']['AAA']}")
        print(f"=========================================================\n")

        # Top violations
        raw_issues = result["raw_issues"]
        if raw_issues:
            print("\033[1;37m[!] Top Identified Issues:\033[0m")
            for i, issue in enumerate(raw_issues[:10], 1):
                sev = issue['severity'].upper()
                c = "\033[1;31m" if sev == "CRITICAL" else ("\033[1;33m" if sev == "SERIOUS" else "\033[0;37m")
                print(f"  {i}. {c}[{sev}]\033[0m {issue['message']} (WCAG {issue['wcag']} - {issue['pour']})")
                print(f"     Fix: {issue['suggestion']}")
            if len(raw_issues) > 10:
                print(f"\n  ... and {len(raw_issues) - 10} more issues found.")
        else:
            print("\033[1;32m[✓] Zero accessibility violations detected! Outstanding.\033[0m")

    # CI/CD Gate check
    fail = False
    if args.min_score > 0 and result["score"] < args.min_score:
        print(f"\n\033[1;31m[FAIL] Score {result['score']} is below required minimum threshold {args.min_score}\033[0m", file=sys.stderr)
        fail = True

    if args.fail_on:
        sev_counts = result["stats"]["severity"]
        if args.fail_on == "critical" and sev_counts["critical"] > 0:
            print(f"\n\033[1;31m[FAIL] {sev_counts['critical']} critical violations found.\033[0m", file=sys.stderr)
            fail = True
        elif args.fail_on == "serious" and (sev_counts["critical"] > 0 or sev_counts["serious"] > 0):
            print(f"\n\033[1;31m[FAIL] Serious or critical violations found.\033[0m", file=sys.stderr)
            fail = True
        elif args.fail_on == "any" and result["stats"]["total_issues"] > 0:
            print(f"\n\033[1;31m[FAIL] Accessibility violations found.\033[0m", file=sys.stderr)
            fail = True

    if fail:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
