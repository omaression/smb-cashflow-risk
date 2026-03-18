export default function Loading() {
  return (
    <main>
      <section className="hero">
        <div>
          <h1>Loading SMB cash flow risk cockpit…</h1>
          <p>Fetching receivables, forecast, and customer risk signals.</p>
        </div>
      </section>

      <section className="grid cards">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="panel skeleton" style={{ minHeight: 132 }} />
        ))}
      </section>

      <section className="grid two-col" style={{ marginTop: 16 }}>
        <div className="panel skeleton" style={{ minHeight: 280 }} />
        <div className="panel skeleton" style={{ minHeight: 280 }} />
      </section>

      <section style={{ marginTop: 16 }}>
        <div className="panel skeleton" style={{ minHeight: 340 }} />
      </section>
    </main>
  );
}
