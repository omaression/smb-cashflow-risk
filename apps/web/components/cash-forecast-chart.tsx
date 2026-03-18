export function CashForecastChart({ balances }: { balances: Record<string, number> }) {
  const entries = Object.entries(balances).sort((a, b) => Number(a[0]) - Number(b[0]));
  const maxValue = Math.max(...entries.map(([, value]) => value), 1);

  return (
    <div className="panel">
      <h2>Cash forecast</h2>
      <p className="muted">Projected closing cash balances across the primary MVP horizons.</p>
      <div className="chart">
        {entries.map(([horizon, value]) => {
          const height = Math.max((value / maxValue) * 180, 20);
          return (
            <div key={horizon} className="bar-wrap">
              <div className="bar" style={{ height }} />
              <div className="bar-label">{horizon}d · ${value.toLocaleString()}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
