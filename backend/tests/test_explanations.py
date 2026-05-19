from app.services.explanations import FALLBACK_EXPLANATION, EXPLANATION_TEMPLATES, select_explanation_template


def test_select_explanation_template_uses_matching_rule_name() -> None:
    template = select_explanation_template("port_scan")

    assert template == EXPLANATION_TEMPLATES["port_scan"]


def test_select_explanation_template_uses_fallback_for_unknown_rule_name() -> None:
    template = select_explanation_template("new_future_rule")

    assert template == FALLBACK_EXPLANATION
