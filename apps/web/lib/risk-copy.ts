const REASON_COPY: Record<string, { label: string; detail: string }> = {
  invoice_overdue_days: {
    label: "Invoice is already overdue",
    detail: "This receivable has passed its due date, which is the strongest immediate indicator of delayed cash arrival.",
  },
  extended_payment_terms: {
    label: "Customer has extended payment terms",
    detail: "Longer payment terms usually stretch cash conversion and make delayed settlement less surprising.",
  },
  customer_concentration_risk: {
    label: "Large invoice exposure",
    detail: "A larger outstanding amount increases concentration risk and can materially affect short-term cash position.",
  },
  no_partial_payments_recorded: {
    label: "No partial payments recorded",
    detail: "There is no sign of incremental repayment yet, so collections follow-up may need to start sooner.",
  },
  customer_historical_late_ratio: {
    label: "Customer has a late-payment history",
    detail: "This counterparty has a pattern of paying late, which raises the chance of another delayed settlement.",
  },
};

export function explainReasonCode(code: string) {
  return REASON_COPY[code] ?? {
    label: code.replaceAll("_", " "),
    detail: "This signal contributed to the current risk assessment.",
  };
}
