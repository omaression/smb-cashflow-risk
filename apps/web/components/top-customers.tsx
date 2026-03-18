import Link from "next/link";

import { sampleCustomers } from "@/lib/customers";

export function TopCustomers({ customers }: { customers: string[] }) {
  return (
    <div className="panel">
      <h2>Top risky customers</h2>
      <p className="muted">Highest-priority counterparties based on current seeded data.</p>
      <ol>
        {customers.map((customer) => {
          const match = sampleCustomers.find((entry) => entry.name === customer);
          return (
            <li key={customer} style={{ marginBottom: 10 }}>
              {match ? <Link href={`/customers/${match.id}`}>{customer}</Link> : customer}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
