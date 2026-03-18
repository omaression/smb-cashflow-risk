"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main>
      <div className="panel" style={{ marginTop: 40 }}>
        <h1>Dashboard unavailable</h1>
        <p className="muted">
          The web app could not reach the API or received an invalid response. Make sure the FastAPI service is
          running and that <code>NEXT_PUBLIC_API_BASE_URL</code> points to the correct backend.
        </p>
        <button className="button" onClick={reset} type="button">
          Retry
        </button>
      </div>
    </main>
  );
}
