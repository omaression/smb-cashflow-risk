export function EmptyState({ title, body, kicker = "No data" }: { title: string; body: string; kicker?: string }) {
  return (
    <div className="panel empty-state">
      <div className="section-kicker">{kicker}</div>
      <h2>{title}</h2>
      <p className="muted">{body}</p>
    </div>
  );
}
