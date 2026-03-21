"use client";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <main>
      <div className="panel" style={{ marginTop: 40 }}>
        <h1>Dashboard unavailable</h1>
        <p className="muted">
          The web app could not reach the API or received an invalid response. Make sure the FastAPI service is
          running and that <code>NEXT_PUBLIC_API_BASE_URL</code> points to the correct backend.
        </p>
        <details style={{ marginTop: 12 }}>
          <summary style={{ cursor: "pointer", color: "#888" }}>Error details</summary>
          <pre style={{ marginTop: 8, fontSize: "0.85rem", whiteSpace: "pre-wrap", wordBreak: "break-word", color: "#c44" }}>
            {error.message}
            {error.digest ? `\nDigest: ${error.digest}` : ""}
          </pre>
        </details>
        <button className="button" onClick={reset} type="button" style={{ marginTop: 16 }}>
          Retry
        </button>
      </div>
    </main>
  );
}
