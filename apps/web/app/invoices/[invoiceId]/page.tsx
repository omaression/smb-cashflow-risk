import Link from "next/link";
import { notFound } from "next/navigation";

import { EmptyState } from "@/components/empty-state";
import { getInvoiceDetail } from "@/lib/api";

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
          <div className="panel" style={{ minWidth: 260 }}>
            <div className="muted">Recommended action</div>
            <div style={{ marginTop: 10, fontWeight: 600 }}>{invoice.recommended_action}</div>
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
            <div className="muted">Risk</div>
            <div className="metric">{Math.round(invoice.late_payment_probability * 100)}%</div>
          </div>
        </section>

        <section className="grid two-col" style={{ marginTop: 16 }}>
          <div className="panel">
            <h2>Risk rationale</h2>
            <p>
              <span className={`badge ${invoice.risk_bucket}`}>{invoice.risk_bucket}</span>
            </p>
            <ul>
              {invoice.top_reason_codes.map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
            <p className="muted">Status: {invoice.status} · {invoice.overdue_days} days overdue</p>
          </div>
          {invoice.payment_history.length > 0 ? (
            <div className="panel">
              <h2>Payment history</h2>
              <table className="table">
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
                      <td>{payment.payment_date}</td>
                      <td>${payment.amount.toLocaleString()}</td>
                      <td>{payment.payment_method ?? "—"}</td>
                      <td>{payment.reference ?? "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              title="No payments recorded"
              body="This invoice has not received any payments yet, so collection action still matters."
            />
          )}
        </section>
      </main>
    );
  } catch {
    notFound();
  }
}
