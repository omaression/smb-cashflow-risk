import Link from "next/link";
import { notFound } from "next/navigation";

import { EmptyState } from "@/components/empty-state";
import { RiskExplanationList } from "@/components/risk-explanation-list";
import { ApiError, getInvoiceDetail } from "@/lib/api";

export default async function InvoiceDetailPage({ params }: { params: Promise<{ invoiceId: string }> }) {
  const { invoiceId } = await params;

  try {
    const invoice = await getInvoiceDetail(invoiceId);

    return (
      <main>
        <div className="link-row" style={{ marginBottom: 16 }}>
          <Link className="link-chip" href="/">
            ← Back to dashboard
          </Link>
          <Link className="link-chip" href={`/customers/${invoice.customer_id}`}>
            View customer
          </Link>
        </div>

        <section className="hero">
          <div>
            <h1>{invoice.invoice_id}</h1>
            <p>
              {invoice.customer_name} · issued {invoice.invoice_date} · due {invoice.due_date}
            </p>
          </div>
          <div className="panel callout-panel" style={{ minWidth: 260 }}>
            <div className="muted">Recommended action</div>
            <div style={{ marginTop: 10, fontWeight: 700, fontSize: "1.05rem" }}>{invoice.recommended_action}</div>
            <p className="muted" style={{ marginTop: 10 }}>
              Focus this invoice if you want the biggest immediate collections signal for this customer.
            </p>
          </div>
        </section>

        <section className="grid cards">
          <div className="panel">
            <div className="muted">Total amount</div>
            <div className="metric">${invoice.total_amount.toLocaleString()}</div>
          </div>
          <div className="panel">
            <div className="muted">Outstanding</div>
            <div className="metric">${invoice.outstanding_amount.toLocaleString()}</div>
          </div>
          <div className="panel">
            <div className="muted">Amount paid</div>
            <div className="metric">${invoice.amount_paid.toLocaleString()}</div>
          </div>
          <div className="panel">
            <div className="muted">Late-payment risk</div>
            <div className="metric">{Math.round(invoice.late_payment_probability * 100)}%</div>
          </div>
        </section>

        <section className="grid two-col" style={{ marginTop: 16 }}>
          <div className="panel">
            <div className="section-kicker">Why this invoice is risky</div>
            <div className="ml-inline-meta" style={{ marginTop: 10 }}>
              <span className="badge medium">{invoice.score_type ?? "rule-based"}</span>
              {invoice.model_version ? <span className="ml-inline-text">Scored by {invoice.model_version}</span> : null}
              <Link className="ml-inline-link" href="/ml">
                How scoring works
              </Link>
            </div>
            <div style={{ marginTop: 10 }}>
              <span className={`badge ${invoice.risk_bucket}`}>{invoice.risk_bucket}</span>
            </div>
            <p className="muted" style={{ marginTop: 12 }}>
              Status: {invoice.status} · {invoice.overdue_days} days overdue
            </p>
            <RiskExplanationList reasons={invoice.top_reason_codes} />
          </div>
          {invoice.payment_history.length > 0 ? (
            <div className="panel">
              <div className="section-kicker">Payment history</div>
              <table className="table responsive-table" style={{ marginTop: 10 }}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Method</th>
                    <th>Reference</th>
                  </tr>
                </thead>
                <tbody>
                  {invoice.payment_history.map((payment) => (
                    <tr key={`${payment.payment_date}-${payment.reference ?? payment.amount}`}>
                      <td data-label="Date">{payment.payment_date}</td>
                      <td data-label="Amount">${payment.amount.toLocaleString()}</td>
                      <td data-label="Method">{payment.payment_method ?? "—"}</td>
                      <td data-label="Reference">{payment.reference ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              title="No payments recorded yet"
              body="This invoice has not received any payments so far, which makes collections timing especially important."
            />
          )}
        </section>
      </main>
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }
}
