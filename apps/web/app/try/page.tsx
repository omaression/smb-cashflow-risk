import Link from "next/link";

export default function TryPage() {
  return (
    <main>
      <section className="hero">
        <div>
          <div className="section-kicker">Bring your own data</div>
          <h1>Upload messy receivables data without guessing what the app trusts</h1>
          <p>
            The v0.5.0 onboarding flow starts with a preview step: detect likely file roles, suggest column
            mappings, surface quality risks, and only then materialize a trial workspace for scoring and cash
            forecasting.
          </p>
        </div>
        <div className="link-row">
          <Link className="link-chip" href="/">
            Back to dashboard
          </Link>
          <a className="link-chip" href="/ml">
            ML evidence
          </a>
        </div>
      </section>

      <section className="grid cards">
        <div className="panel">
          <div className="muted">Step 1</div>
          <div className="metric">Upload</div>
          <p className="muted" style={{ marginTop: 8 }}>
            Drop one unpaid-invoice export or multiple customer / invoice / payment / cash files.
          </p>
        </div>
        <div className="panel">
          <div className="muted">Step 2</div>
          <div className="metric">Review mapping</div>
          <p className="muted" style={{ marginTop: 8 }}>
            Confirm inferred roles and canonical column mappings before import proceeds.
          </p>
        </div>
        <div className="panel">
          <div className="muted">Step 3</div>
          <div className="metric">Preview trust</div>
          <p className="muted" style={{ marginTop: 8 }}>
            See validation issues, reliability grade, and concrete recommendations to improve confidence.
          </p>
        </div>
        <div className="panel">
          <div className="muted">Step 4</div>
          <div className="metric">Import & score</div>
          <p className="muted" style={{ marginTop: 8 }}>
            Materialize a trial workspace and run the existing rule-based scoring and forecast stack.
          </p>
        </div>
      </section>

      <section style={{ marginTop: 16 }}>
        <div className="panel">
          <div className="section-kicker">Current status</div>
          <h2>Foundation slice in progress</h2>
          <div className="ml-list" style={{ marginTop: 12 }}>
            <div className="ml-list-item">Preview/import workflow contract is being added first.</div>
            <div className="ml-list-item">Trial workspaces will isolate uploaded data from the demo dataset.</div>
            <div className="ml-list-item">Mapping review, validation preview, and reliability scoring come next.</div>
          </div>
        </div>
      </section>
    </main>
  );
}
