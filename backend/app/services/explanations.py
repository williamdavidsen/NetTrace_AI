from app.models import Alert


EXPLANATION_TEMPLATES = {
    "port_scan": {
        "summary": "A single source contacted many destination ports in a short time window.",
        "pattern": (
            "This pattern is commonly associated with port scanning, where a host probes multiple ports "
            "to discover exposed services before a possible follow-up attempt."
        ),
        "recommended_action": (
            "Review the source host, check whether the activity was expected scanning, and restrict or "
            "firewall unnecessary exposed services."
        ),
    },
    "dns_spike": {
        "summary": "A single source generated an unusual burst of DNS traffic in a short time window.",
        "pattern": (
            "DNS spikes can happen during normal resolver activity, but they can also point to malware "
            "lookups, domain discovery, tunneling attempts, or a misconfigured application."
        ),
        "recommended_action": (
            "Review the source host's DNS queries, look for repeated or unexpected domains, and verify "
            "whether the traffic matches normal application behavior."
        ),
    },
    "suspicious_port": {
        "summary": "Traffic was observed to a sensitive administrative or legacy service port.",
        "pattern": (
            "Ports such as SSH, Telnet, SMB, and RDP are often targeted for probing, credential attacks, "
            "or lateral movement attempts."
        ),
        "recommended_action": (
            "Confirm the connection is expected, review authentication logs for the service, and limit "
            "access to trusted hosts or management networks."
        ),
    },
    "large_packet": {
        "summary": "This alert shows packet metadata above the large-packet threshold.",
        "pattern": "Very large packets can be normal in some environments, but may deserve review when unexpected.",
        "recommended_action": "Check whether the source and destination normally exchange high-volume traffic.",
    },
    "unknown_protocol": {
        "summary": "This alert shows a protocol outside the expected TCP, UDP, and ICMP set.",
        "pattern": "Unexpected protocol values may indicate unusual tooling, malformed metadata, or unsupported traffic.",
        "recommended_action": "Verify the collector output and inspect the source host if the protocol is unexpected.",
    },
}

FALLBACK_EXPLANATION = {
    "summary": "A detection rule matched network metadata that may require review.",
    "pattern": (
        "This rule does not have a specialized explanation yet, so the alert should be interpreted from "
        "its title, description, severity, source, and scan context."
    ),
    "recommended_action": (
        "Review the alert details, compare the source host activity with expected behavior, and document "
        "whether this rule needs a dedicated explanation template."
    ),
}


def select_explanation_template(rule_name: str) -> dict[str, str]:
    return EXPLANATION_TEMPLATES.get(rule_name, FALLBACK_EXPLANATION)


def explain_alert(alert: Alert) -> dict[str, str]:
    template = select_explanation_template(alert.rule_name)
    return {
        "alert_id": alert.id,
        "rule_name": alert.rule_name,
        **template,
    }
