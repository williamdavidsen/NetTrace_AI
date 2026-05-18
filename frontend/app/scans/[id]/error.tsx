"use client";

import { ErrorPanel } from "@/components/status-panels";

export default function ScanDetailError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <ErrorPanel title="Scan detail unavailable" onRetry={reset} />;
}
