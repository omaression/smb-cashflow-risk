import Link from "next/link";
import { notFound } from "next/navigation";

import { EmptyState } from "@/components/empty-state";
import { ApiError, getCustomerDetail } from "@/lib/api";

export default async function CustomerDetailPage({ params }: { params: Promise<{ customerId: string }> }) {
  const { customerId } = await params;

  try {
    const customer = await getCustomerDetail(customerId);

    return (
      <main>
        <div className="link-row" style={{ marginBottom: 16 }}>
          <Link className="link-chip" href="/">
            ← Back to dashboard
          </Link>
        </div>

        <section className="hero">
          <div>
            <h1>{customer.customer_name}</h1>
            <p>
              {customer.industry ?? "Unknown industry"} · {customer.segment ?? "Unknown segment"} · Terms{" "}
              {customer.payment_terms_days ?? "n/a"} days
            </p>
          </div>
          <div className="panel" style={{ minWidth: 260 }}>
            <div className="muted">Top recommendation</div>
            <div style={{ marginTop: 10, fontWeight: 600 }}>{customer.top_recommendation}</div>
          </div>
        </section>

        <section className="grid cards">
          <div className="panel">
            <div className="muted">Open exposure</div>
            <div className="metric">${customer.open_exposure.toLocaleString()}</div>
          </div>
          <div className="panel">
            <div className="muted">Open invoices</div>
            <div className="metric">{customer.open_invoice_count}</div>
          </div>
          <div className="panel">
            <div className="muted">Overdue invoices</div>
            <div className="metric">{customer.overdue_invoice_count}</div>
          </div>
          <div className="panel">
            <div className="muted">Late-payment ratio</div>
            <div className="metric">{Math.round(customer.late_payment_ratio * 100)}%</div>
          </div>
        </section>

        <section style={{ marginTop: 16 }}>
          {customer.open_invoices.length > 0 ? (
            <div className="panel">
              <h2>Open invoices</h2>
              <table className="table">
                <thead>
                  <tr>
                    <th>Invoice</th>
                    <th>Total</th>
                    <th>Outstanding</th>
                    <th>Due</th>
                    <th>Status</th>
                    <th>Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {customer.open_invoices.map((invoice) => (
                    <tr key={invoice.invoice_id}>
                      <td>{invoice.invoice_id}</td>
                      <td>${invoice.total_amount.toLocaleString()}</td>
                      <td>${invoice.outstanding_amount.toLocaleString()}</td>
                      <td>{invoice.due_date}</td>
                      <td>{invoice.status}</td>
                      <td>
                        <span className={`badge ${invoice.risk_bucket}`}>{invoice.risk_bucket}</span>
                        <div className="muted">{Math.round(invoice.late_payment_probability * 100)}%</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <EmptyState
              title="No open invoices"
              body="This customer currently has no receivables exposure in the loaded portfolio."
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
