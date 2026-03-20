import Link from "next/link";

export function TopCustomers({ customers }: { customers: { id: string; name: string }[] }) {
  return (
    <div className="panel">
      <h2>Top risky customers</h2>
      <p className="muted">Highest-priority counterparties based on current receivables exposure.</p>
      <ol>
        {customers.map((customer) => (
          <li key={customer.id} style={{ marginBottom: 10 }}>
            <Link href={`/customers/${customer.id}`}>{customer.name}</Link>
          </li>
        ))}
      </ol>
    </div>
  );
}
