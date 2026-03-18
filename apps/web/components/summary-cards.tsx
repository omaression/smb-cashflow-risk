import type { DashboardSummary } from "@/lib/api";

export function SummaryCards({ summary }: { summary: DashboardSummary }) {
  const cards = [
    { label: "Total AR", value: `$${summary.total_ar.toLocaleString()}` },
    { label: "Overdue AR", value: `$${summary.overdue_ar.toLocaleString()}` },
    { label: "Open invoices", value: summary.open_invoice_count.toString() },
    { label: "Risky invoices", value: summary.risky_invoice_count.toString() },
  ];

  return (
    <section className="grid cards">
      {cards.map((card) => (
        <div key={card.label} className="panel">
          <div className="muted">{card.label}</div>
          <div className="metric">{card.value}</div>
        </div>
      ))}
    </section>
  );
}
