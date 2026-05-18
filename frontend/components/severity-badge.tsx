const severityLabels: Record<string, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  critical: "Critical",
};

export function SeverityBadge({ severity }: { severity: string }) {
  const normalized = severity.toLowerCase();

  return (
    <span className={`severity-badge severity-${normalized}`}>
      {severityLabels[normalized] ?? severity}
    </span>
  );
}
