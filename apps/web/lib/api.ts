export type DashboardSummary = {
  total_ar: number;
  overdue_ar: number;
  open_invoice_count: number;
  risky_invoice_count: number;
  top_risky_customers: string[];
  projected_cash_balances: Record<string, number>;
};

export type InvoiceRiskItem = {
  invoice_id: string;
  customer_name: string;
  amount: number;
  due_date: string;
  overdue_days: number;
  late_payment_probability: number;
  risk_bucket: "low" | "medium" | "high";
  top_reason_codes: string[];
  recommended_action: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`API request failed for ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return fetchJson<DashboardSummary>("/dashboard/summary");
}

export async function getInvoiceRisk(): Promise<InvoiceRiskItem[]> {
  return fetchJson<InvoiceRiskItem[]>("/invoices/risk");
}
