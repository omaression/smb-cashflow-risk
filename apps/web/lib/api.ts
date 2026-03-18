const browserApiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
const serverApiBaseUrl = process.env.INTERNAL_API_BASE_URL ?? process.env.API_BASE_URL;

const apiBaseUrl = serverApiBaseUrl ?? browserApiBaseUrl;

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

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

export type InvoicePaymentHistoryItem = {
  payment_date: string;
  amount: number;
  payment_method: string | null;
  reference: string | null;
};

export type InvoiceDetail = {
  invoice_id: string;
  customer_id: string;
  customer_name: string;
  invoice_date: string;
  due_date: string;
  currency: string;
  total_amount: number;
  outstanding_amount: number;
  amount_paid: number;
  status: string;
  overdue_days: number;
  payment_history: InvoicePaymentHistoryItem[];
  late_payment_probability: number;
  risk_bucket: "low" | "medium" | "high";
  top_reason_codes: string[];
  recommended_action: string;
};

export type CustomerOpenInvoice = {
  invoice_id: string;
  total_amount: number;
  outstanding_amount: number;
  due_date: string;
  status: string;
  late_payment_probability: number;
  risk_bucket: "low" | "medium" | "high";
};

export type CustomerDetail = {
  customer_id: string;
  customer_name: string;
  industry: string | null;
  segment: string | null;
  payment_terms_days: number | null;
  credit_limit: number | null;
  open_exposure: number;
  open_invoice_count: number;
  overdue_invoice_count: number;
  average_days_overdue: number;
  late_payment_ratio: number;
  top_recommendation: string;
  open_invoices: CustomerOpenInvoice[];
};

function getBrowserApiBaseUrl(): string | undefined {
  return browserApiBaseUrl;
}

async function fetchJson<T>(path: string): Promise<T> {
  if (!apiBaseUrl) {
    throw new Error("API base URL is not configured. Set INTERNAL_API_BASE_URL (server) or NEXT_PUBLIC_API_BASE_URL (browser).");
  }

  const response = await fetch(`${apiBaseUrl}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new ApiError(response.status, `API request failed for ${path}: ${response.status}`);
  }
  return (await response.json()) as T;
}

export function getBrowserApiLinks() {
  const docs = getBrowserApiBaseUrl() ? `${getBrowserApiBaseUrl()}/docs` : undefined;
  const summary = getBrowserApiBaseUrl() ? `${getBrowserApiBaseUrl()}/dashboard/summary` : undefined;

  return { docs, summary };
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return fetchJson<DashboardSummary>("/dashboard/summary");
}

export async function getInvoiceRisk(): Promise<InvoiceRiskItem[]> {
  return fetchJson<InvoiceRiskItem[]>("/invoices/risk");
}

export async function getInvoiceDetail(invoiceId: string): Promise<InvoiceDetail> {
  return fetchJson<InvoiceDetail>(`/invoices/${invoiceId}`);
}

export async function getCustomerDetail(customerId: string): Promise<CustomerDetail> {
  return fetchJson<CustomerDetail>(`/customers/${customerId}`);
}
