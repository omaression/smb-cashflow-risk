import { CashForecastChart } from "@/components/cash-forecast-chart";
import { EmptyState } from "@/components/empty-state";
import { InvoiceRiskTable } from "@/components/invoice-risk-table";
import { SummaryCards } from "@/components/summary-cards";
import { TopCustomers } from "@/components/top-customers";
import { getBrowserApiLinks, getDashboardSummary, getInvoiceRisk } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [summary, invoices] = await Promise.all([getDashboardSummary(), getInvoiceRisk()]);
  const links = getBrowserApiLinks();

  return (
    <main>
      <section className="hero">
        <div>
          <h1>SMB cash flow risk cockpit</h1>
          <p>
            Early warning dashboard for short-term liquidity pressure, receivables risk, and collections
            prioritization. Built to tell a reviewer what matters in under two minutes.
          </p>
        </div>
        <div className="link-row">
          <a className="link-chip" href="/ml">
            ML evidence
          </a>
          {links.docs ? (
            <a className="link-chip" href={links.docs} target="_blank" rel="noreferrer">
              API docs
            </a>
          ) : null}
          {links.summary ? (
            <a className="link-chip" href={links.summary} target="_blank" rel="noreferrer">
              Summary JSON
            </a>
          ) : null}
        </div>
      </section>

      <SummaryCards summary={summary} />

      <section style={{ marginTop: 16 }}>
        <div className="panel ml-banner">
          <div>
            <div className="section-kicker">Scoring status</div>
            <h2>Runtime scoring is intentionally conservative</h2>
            <p className="muted" style={{ marginTop: 8 }}>
              The live invoice queue is powered by <strong>{summary.runtime_model_version ?? "the current rules model"}</strong>. External benchmarks and project-native readiness are surfaced separately so the app stays honest about what is live versus experimental.
            </p>
          </div>
          <div className="link-row" style={{ marginTop: 12 }}>
            <span className="badge medium">{summary.ml_status_badge ?? "rules-only"}</span>
            <a className="link-chip" href="/ml">
              Inspect ML evidence
            </a>
          </div>
        </div>
      </section>

      <section className="grid two-col" style={{ marginTop: 16 }}>
        {Object.keys(summary.projected_cash_balances).length > 0 ? (
          <CashForecastChart balances={summary.projected_cash_balances} />
        ) : (
          <EmptyState title="No forecast available" body="Load snapshots and invoices to generate a short-term cash view." />
        )}

        {summary.top_risky_customers.length > 0 ? (
          <TopCustomers customers={summary.top_risky_customers} />
        ) : (
          <EmptyState
            title="No risky customers yet"
            body="Once receivables are loaded, counterparties with meaningful exposure will appear here."
          />
        )}
      </section>

      <section style={{ marginTop: 16 }}>
        {invoices.length > 0 ? (
          <InvoiceRiskTable invoices={invoices} />
        ) : (
          <EmptyState
            title="No invoices loaded"
            body="Import customer, invoice, and payment CSVs to populate the collections queue."
          />
        )}
      </section>
    </main>
  );
}
