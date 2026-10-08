"""
SARIF (Static Analysis Results Interchange Format) 2.1.0 exporter for A11yLens.
Allows direct integration with GitHub Code Scanning (actions/upload-sarif) and CI/CD pipelines.
"""

def generate_sarif(audit_data: dict, target_url: str) -> dict:
    rules_dict = {}
    results_list = []

    level_map = {
        "critical": "error",
        "serious": "error",
        "moderate": "warning",
        "minor": "note"
    }

    raw_issues = audit_data.get("raw_issues", [])

    for idx, issue in enumerate(raw_issues):
        rule_id = issue.get("rule_id", "A11Y_RULE")
        wcag = issue.get("wcag", "2.1")
        pour = issue.get("pour", "General")
        
        # Build rule metadata in tool.driver.rules
        if rule_id not in rules_dict:
            rules_dict[rule_id] = {
                "id": rule_id,
                "name": rule_id.replace("_", " ").title(),
                "shortDescription": {
                    "text": issue.get("message", "Accessibility compliance issue")
                },
                "fullDescription": {
                    "text": f"{issue.get('message', '')} - Violates WCAG {wcag} ({pour} principle)."
                },
                "help": {
                    "text": f"Remediation Guidance: {issue.get('suggestion', '')}\nRecommended Code:\n{issue.get('remediation', '')}"
                },
                "properties": {
                    "wcag": wcag,
                    "pour": pour,
                    "level": issue.get("level", "AA")
                }
            }

        # Build result entry
        results_list.append({
            "ruleId": rule_id,
            "level": level_map.get(issue.get("severity", "minor"), "warning"),
            "message": {
                "text": f"{issue.get('message', '')} (WCAG {wcag})"
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": target_url
                        },
                        "region": {
                            "snippet": {
                                "text": issue.get("html", "")
                            }
                        }
                    }
                }
            ],
            "fixes": [
                {
                    "description": {
                        "text": issue.get("suggestion", "Remediation fix")
                    },
                    "replacement": issue.get("remediation", "")
                }
            ]
        })

    sarif_doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "A11yLens",
                        "organization": "A11yLens Open Source Project",
                        "semanticVersion": "2.0.0",
                        "informationUri": "https://a11ylens.org",
                        "rules": list(rules_dict.values())
                    }
                },
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "toolExecutionNotifications": []
                    }
                ],
                "results": results_list
            }
        ]
    }

    return sarif_doc
