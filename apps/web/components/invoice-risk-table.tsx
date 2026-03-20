import Link from "next/link";

import type { InvoiceRiskItem } from "@/lib/api";
import { explainReasonCode } from "@/lib/risk-copy";

export function InvoiceRiskTable({ invoices }: { invoices: InvoiceRiskItem[] }) {
  return (
    <div className="panel">
      <h2>Invoice risk queue</h2>
      <p className="muted">Decision-oriented receivables view for the next collections pass.</p>
      <table className="table responsive-table" style={{ marginTop: 10 }}>
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
              <td data-label="Invoice">
                <Link href={`/invoices/${invoice.invoice_id}`}>{invoice.invoice_id}</Link>
              </td>
              <td data-label="Customer">{invoice.customer_name}</td>
              <td data-label="Amount">${invoice.amount.toLocaleString()}</td>
              <td data-label="Due">
                {invoice.due_date}
                <div className="muted">{invoice.overdue_days} days overdue</div>
              </td>
              <td data-label="Risk">
                <span className={`badge ${invoice.risk_bucket}`}>{invoice.risk_bucket}</span>
                <div className="muted">{Math.round(invoice.late_payment_probability * 100)}% probability</div>
              </td>
              <td data-label="Why">{invoice.top_reason_codes.map((code) => explainReasonCode(code).label).join(", ")}</td>
              <td data-label="Action">{invoice.recommended_action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
