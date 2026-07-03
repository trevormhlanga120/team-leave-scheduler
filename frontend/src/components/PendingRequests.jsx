import { approveLeave, rejectLeave } from "../api";

export default function PendingRequests({ leaveRequests, onChanged }) {
  const pending = leaveRequests.filter((r) => r.status === "pending");

  async function handleApprove(id) {
    try {
      await approveLeave(id);
      onChanged();
    } catch (err) {
      alert(err.message); // surfaces the 30% cap breach message from the API
    }
  }

  async function handleReject(id) {
    await rejectLeave(id);
    onChanged();
  }

  return (
    <div>
      <h2>Pending Requests</h2>
      {pending.length === 0 && <p>No pending requests.</p>}
      <ul>
        {pending.map((r) => (
          <li key={r.id}>
            {r.employee_name}: {r.start_date} to {r.end_date}{" "}
            <button onClick={() => handleApprove(r.id)}>Approve</button>
            <button onClick={() => handleReject(r.id)}>Reject</button>
          </li>
        ))}
      </ul>
    </div>
  );
}