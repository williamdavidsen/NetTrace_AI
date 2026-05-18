"use client";

import { ErrorPanel } from "@/components/status-panels";

export default function ScansError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <ErrorPanel title="Scans unavailable" onRetry={reset} />;
}
