from app.services.explanations import FALLBACK_EXPLANATION, EXPLANATION_TEMPLATES, select_explanation_template


def test_select_explanation_template_uses_matching_rule_name() -> None:
    template = select_explanation_template("port_scan")

    assert template == EXPLANATION_TEMPLATES["port_scan"]


def test_port_scan_template_explains_pattern_and_action() -> None:
    template = select_explanation_template("port_scan")

    assert "many destination ports" in template["summary"]
    assert "probes multiple ports" in template["pattern"]
    assert "restrict" in template["recommended_action"]


def test_select_explanation_template_uses_fallback_for_unknown_rule_name() -> None:
    template = select_explanation_template("new_future_rule")

    assert template == FALLBACK_EXPLANATION
