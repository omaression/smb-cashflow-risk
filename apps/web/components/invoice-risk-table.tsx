import type { InvoiceRiskItem } from "@/lib/api";

export function InvoiceRiskTable({ invoices }: { invoices: InvoiceRiskItem[] }) {
  return (
    <div className="panel">
      <h2>Invoice risk queue</h2>
      <p className="muted">Decision-oriented receivables view for the next collections pass.</p>
      <table className="table">
        <thead>
          <tr>
            <th>Invoice</th>
            <th>Customer</th>
            <th>Amount</th>
            <th>Due</th>
            <th>Risk</th>
            <th>Why</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {invoices.map((invoice) => (
            <tr key={invoice.invoice_id}>
              <td>{invoice.invoice_id}</td>
              <td>{invoice.customer_name}</td>
              <td>${invoice.amount.toLocaleString()}</td>
              <td>
                {invoice.due_date}
                <div className="muted">{invoice.overdue_days} days overdue</div>
              </td>
              <td>
                <span className={`badge ${invoice.risk_bucket}`}>{invoice.risk_bucket}</span>
                <div className="muted">{Math.round(invoice.late_payment_probability * 100)}% probability</div>
              </td>
              <td>{invoice.top_reason_codes.join(", ")}</td>
              <td>{invoice.recommended_action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
