"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

const DEFAULT_POLL_INTERVAL_MS = 5000;

export function RealtimeRefresh({
  intervalMs = DEFAULT_POLL_INTERVAL_MS,
}: {
  intervalMs?: number;
}) {
  const router = useRouter();

  useEffect(() => {
    const timerId = window.setInterval(() => {
      router.refresh();
    }, intervalMs);

    return () => {
      window.clearInterval(timerId);
    };
  }, [intervalMs, router]);

  return null;
}
