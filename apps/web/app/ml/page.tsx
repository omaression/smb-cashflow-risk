import Link from "next/link";

import { getMlOverview } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MlEvidencePage() {
  const overview = await getMlOverview();
  const runtime = overview.runtime_model;
  const native = overview.native_pipeline;

  return (
    <main>
      <div className="link-row" style={{ marginBottom: 16 }}>
        <Link className="link-chip" href="/">
          ← Back to dashboard
        </Link>
      </div>

      <section className="hero">
        <div>
          <div className="section-kicker">ML evidence</div>
          <h1>What is real ML here, and what is still deferred?</h1>
          <p>
            This project keeps the runtime scorer honest: the live product uses a rule-based baseline while
            benchmark artifacts and project-native readiness reports show what exists beyond the demo path.
          </p>
        </div>
      </section>

      <section className="grid cards">
        <div className="panel">
          <div className="muted">Runtime scorer</div>
          <div className="metric">{runtime.version}</div>
          <p className="muted" style={{ marginTop: 8 }}>
            {runtime.model_type} · target {runtime.target}
          </p>
        </div>
        <div className="panel">
          <div className="muted">Project-native ML</div>
          <div className="metric">{native.status === "deferred" ? "Deferred" : "Ready"}</div>
          <p className="muted" style={{ marginTop: 8 }}>
            {native.row_count} rows · {native.positive_count} positive labels
          </p>
        </div>
        <div className="panel">
          <div className="muted">External benchmarks</div>
          <div className="metric">{overview.external_benchmarks.length}</div>
          <p className="muted" style={{ marginTop: 8 }}>
            Reference artifacts for modeling behavior, not runtime replacement.
          </p>
        </div>
      </section>

      <section className="grid two-col" style={{ marginTop: 16 }}>
        <div className="panel">
          <div className="section-kicker">Current runtime model</div>
          <h2>Rule-based baseline stays in production for now</h2>
          <p className="muted" style={{ marginTop: 10 }}>
            {runtime.description}
          </p>
          <div className="ml-list" style={{ marginTop: 16 }}>
            {runtime.notes.map((note) => (
              <div key={note} className="ml-list-item">
                {note}
              </div>
            ))}
          </div>
        </div>

        <div className="panel callout-panel">
          <div className="section-kicker">Transfer recommendation</div>
          <h2>Use benchmarks as evidence, not as runtime proof</h2>
          <p className="muted" style={{ marginTop: 10 }}>
            {overview.transfer_recommendation.summary}
          </p>
          <div className="ml-note-card" style={{ marginTop: 16 }}>
            <strong>Approved runtime default</strong>
            <p className="muted" style={{ marginTop: 8 }}>
              Keep the live application on the interpretable rules model until native data volume clears the
              minimum training thresholds.
            </p>
          </div>
        </div>
      </section>

      <section className="panel" style={{ marginTop: 16 }}>
        <div className="section-kicker">Project-native readiness</div>
        <h2>Why learned native runtime is still deferred</h2>
        <p className="muted" style={{ marginTop: 10 }}>{native.reason}</p>
        <div className="ml-stat-grid" style={{ marginTop: 16 }}>
          <div className="ml-stat-card">
            <span className="muted">Rows available</span>
            <strong>{native.row_count}</strong>
            <span className="muted">Need {native.min_rows_required}</span>
          </div>
          <div className="ml-stat-card">
            <span className="muted">Positive labels</span>
            <strong>{native.positive_count}</strong>
            <span className="muted">Need {native.min_positive_rows_required}</span>
          </div>
        </div>
        {native.blockers.length > 0 ? (
          <div className="ml-list" style={{ marginTop: 16 }}>
            {native.blockers.map((blocker) => (
              <div key={blocker} className="ml-list-item warning">
                {blocker}
              </div>
            ))}
          </div>
        ) : null}
        <div className="ml-note-card" style={{ marginTop: 16 }}>
          <strong>Next unlock condition</strong>
          <p className="muted" style={{ marginTop: 8 }}>{native.next_unlock_condition}</p>
        </div>
      </section>

      <section className="panel" style={{ marginTop: 16 }}>
        <div className="section-kicker">Benchmark references</div>
        <h2>External datasets used as benchmark evidence</h2>
        <p className="muted" style={{ marginTop: 10 }}>
          These runs help compare modeling behavior and surface feature ideas. They do not validate direct
          runtime transfer into this app.
        </p>
        <div className="ml-benchmark-grid" style={{ marginTop: 16 }}>
          {overview.external_benchmarks.map((benchmark) => (
            <div key={benchmark.dataset_key} className="ml-benchmark-card">
              <div className="link-row" style={{ justifyContent: "space-between", gap: 8 }}>
                <strong>{benchmark.name}</strong>
                {benchmark.winner ? <span className="badge low">reference winner</span> : null}
              </div>
              <p className="muted" style={{ marginTop: 8 }}>{benchmark.description}</p>
              <div className="metric" style={{ fontSize: "1.5rem", marginTop: 14 }}>
                {benchmark.headline_metric?.toFixed(4) ?? "—"}
              </div>
              <p className="muted">headline comparison metric</p>
              <div className="ml-list" style={{ marginTop: 14 }}>
                {benchmark.caveats.map((caveat) => (
                  <div key={caveat} className="ml-list-item">
                    {caveat}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
