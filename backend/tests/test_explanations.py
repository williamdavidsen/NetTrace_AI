from app.services.explanations import FALLBACK_EXPLANATION, EXPLANATION_TEMPLATES, select_explanation_template


def test_select_explanation_template_uses_matching_rule_name() -> None:
    template = select_explanation_template("port_scan")

    assert template == EXPLANATION_TEMPLATES["port_scan"]


def test_port_scan_template_explains_pattern_and_action() -> None:
    template = select_explanation_template("port_scan")

    assert "many destination ports" in template["summary"]
    assert "probes multiple ports" in template["pattern"]
    assert "restrict" in template["recommended_action"]


def test_dns_spike_template_explains_pattern_and_action() -> None:
    template = select_explanation_template("dns_spike")

    assert "DNS traffic" in template["summary"]
    assert "malware" in template["pattern"]
    assert "DNS queries" in template["recommended_action"]


def test_suspicious_port_template_explains_pattern_and_action() -> None:
    template = select_explanation_template("suspicious_port")

    assert "sensitive" in template["summary"]
    assert "credential attacks" in template["pattern"]
    assert "trusted hosts" in template["recommended_action"]


def test_select_explanation_template_uses_fallback_for_unknown_rule_name() -> None:
    template = select_explanation_template("new_future_rule")

    assert template == FALLBACK_EXPLANATION


def test_fallback_template_explains_unknown_rules_and_action() -> None:
    template = select_explanation_template("new_future_rule")

    assert "detection rule" in template["summary"]
    assert "specialized explanation" in template["pattern"]
    assert "dedicated explanation template" in template["recommended_action"]


def test_all_main_alert_templates_include_recommended_action() -> None:
    for rule_name in ("port_scan", "dns_spike", "suspicious_port"):
        template = select_explanation_template(rule_name)

        assert template["recommended_action"]
