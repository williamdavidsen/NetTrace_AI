from support import frontend_text


def test_empty_dashboard_renders_without_data() -> None:
    html = frontend_text("/dashboard")

    assert "No activity yet" in html
    assert "No alerts" in html
    assert "No scans yet" in html
