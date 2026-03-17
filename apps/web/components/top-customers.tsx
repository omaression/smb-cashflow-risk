export function TopCustomers({ customers }: { customers: string[] }) {
  return (
    <div className="panel">
      <h2>Top risky customers</h2>
      <p className="muted">Highest-priority counterparties based on current seeded data.</p>
      <ol>
        {customers.map((customer) => (
          <li key={customer} style={{ marginBottom: 10 }}>{customer}</li>
        ))}
      </ol>
    </div>
  );
}
