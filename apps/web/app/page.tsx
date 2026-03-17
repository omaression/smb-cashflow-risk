import { CashForecastChart } from "@/components/cash-forecast-chart";
import { InvoiceRiskTable } from "@/components/invoice-risk-table";
import { SummaryCards } from "@/components/summary-cards";
import { TopCustomers } from "@/components/top-customers";
import { getDashboardSummary, getInvoiceRisk } from "@/lib/api";

export default async function DashboardPage() {
  const [summary, invoices] = await Promise.all([getDashboardSummary(), getInvoiceRisk()]);

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
          <a className="link-chip" href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">
            API docs
          </a>
          <a className="link-chip" href="http://127.0.0.1:8000/api/v1/dashboard/summary" target="_blank" rel="noreferrer">
            Summary JSON
          </a>
        </div>
      </section>

      <SummaryCards summary={summary} />

      <section className="grid two-col" style={{ marginTop: 16 }}>
        <CashForecastChart balances={summary.projected_cash_balances} />
        <TopCustomers customers={summary.top_risky_customers} />
      </section>

      <section style={{ marginTop: 16 }}>
        <InvoiceRiskTable invoices={invoices} />
      </section>
    </main>
  );
}
