import Link from "next/link";

export default function NotFound() {
  return (
    <main>
      <div className="panel" style={{ marginTop: 40 }}>
        <h1>Record not found</h1>
        <p className="muted">
          The requested customer or invoice does not exist in the current dataset.
        </p>
        <Link className="link-chip" href="/">
          Back to dashboard
        </Link>
      </div>
    </main>
  );
}
