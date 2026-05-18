"use client";

import { ErrorPanel } from "@/components/status-panels";

export default function DashboardError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <ErrorPanel title="Dashboard unavailable" onRetry={reset} />;
}
