"use client";

export function LoadingPanel({ title }: { title: string }) {
  return (
    <section className="status-panel" aria-live="polite">
      <div className="loader" />
      <h1>{title}</h1>
    </section>
  );
}

export function ErrorPanel({ title, onRetry }: { title: string; onRetry: () => void }) {
  return (
    <section className="status-panel">
      <h1>{title}</h1>
      <p>The backend API could not be reached or returned an unexpected response.</p>
      <button type="button" onClick={onRetry}>
        Retry
      </button>
    </section>
  );
}
