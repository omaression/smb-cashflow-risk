import { explainReasonCode } from "@/lib/risk-copy";

export function RiskExplanationList({ reasons }: { reasons: string[] }) {
  const uniqueReasons = Array.from(new Set(reasons));

  return (
    <div className="risk-reasons">
      {uniqueReasons.map((reason, index) => {
        const item = explainReasonCode(reason);
        return (
          <div className="risk-reason" key={`${reason}-${index}`}>
            <div className="risk-reason-title">{item.label}</div>
            <div className="risk-reason-detail">{item.detail}</div>
          </div>
        );
      })}
    </div>
  );
}
