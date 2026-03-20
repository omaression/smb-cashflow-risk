export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="panel empty-state">
      <div className="section-kicker">Empty state</div>
      <h2>{title}</h2>
      <p className="muted">{body}</p>
    </div>
  );
}
