"""
Unit tests for POUR calculations, scoring, and regulatory risk matrix.
"""
from auditor import calculate_pour_scores
from sarif import generate_sarif


def test_perfect_score_calculation():
    score_data = calculate_pour_scores([])
    assert score_data["overall"] == 100
    assert score_data["grade"] == "A+"
    assert score_data["pour"]["perceivable"] == 100
    assert score_data["pour"]["operable"] == 100
    assert score_data["pour"]["understandable"] == 100
    assert score_data["pour"]["robust"] == 100
    assert score_data["regulatory"]["ada_risk"] == "Low Risk"


def test_weighted_deductions_and_grade():
    issues = [
        {"severity": "critical", "pour": "Perceivable"},
        {"severity": "serious", "pour": "Operable"},
        {"severity": "moderate", "pour": "Understandable"},
        {"severity": "minor", "pour": "Robust"},
    ]
    # Total deduction: 10 + 6 + 3 + 1 = 20 pts
    score_data = calculate_pour_scores(issues)
    assert score_data["overall"] == 80
    assert score_data["grade"] == "B"
    assert score_data["pour"]["perceivable"] == 80  # 100 - (10 * 2)
    assert score_data["pour"]["operable"] == 88     # 100 - (6 * 2)
    assert score_data["pour"]["understandable"] == 94 # 100 - (3 * 2)
    assert score_data["pour"]["robust"] == 98        # 100 - (1 * 2)


def test_sarif_generation():
    fake_audit = {
        "score": 90,
        "grade": "A",
        "raw_issues": [
            {
                "rule_id": "IMG_ALT_MISSING",
                "wcag": "1.1.1",
                "pour": "Perceivable",
                "severity": "critical",
                "message": "Image is missing alternative text",
                "html": '<img src="sample.jpg">',
                "suggestion": "Add alt text",
                "remediation": '<img alt="Sample" src="sample.jpg">'
            }
        ]
    }
    sarif = generate_sarif(fake_audit, "https://example.com")
    assert sarif["version"] == "2.1.0"
    assert len(sarif["runs"]) == 1
    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "A11yLens"
    assert len(run["results"]) == 1
    assert run["results"][0]["ruleId"] == "IMG_ALT_MISSING"
    assert run["results"][0]["level"] == "error"
