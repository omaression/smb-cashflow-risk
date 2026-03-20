import { explainReasonCode } from "@/lib/risk-copy";

export function RiskExplanationList({ reasons }: { reasons: string[] }) {
  return (
    <div className="risk-reasons">
      {reasons.map((reason) => {
        const item = explainReasonCode(reason);
        return (
          <div className="risk-reason" key={reason}>
            <div className="risk-reason-title">{item.label}</div>
            <div className="risk-reason-detail">{item.detail}</div>
          </div>
        );
      })}
    </div>
  );
}
