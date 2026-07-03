export default function LeaveList({ leaveRequests }) {
    const approved = leaveRequests.filter((r) => r.status === "approved");
    const byTeam = approved.reduce((acc, r) => {
        acc[r.team_id] = acc[r.team_id] || [];
        acc[r.team_id].push(r);
        return acc;
    }, {});

    return (
        <div>
            <h2>Approved Leave -- Next 30 Days</h2>
            {Object.entries(byTeam).map(([teamId, reqs]) => (
                <div key={teamId}>
                    <h3>Team {teamId}</h3>
                    <ul>
                        {reqs.map((r) => (
                            <li key={r.id}>
                                {r.employee_name}: {r.start_date} to {r.end_date}
                            </li>
                        ))}
                    </ul>
                </div>
            ))}
            {approved.length === 0 && <p>No approved leave in this window.</p>}
        </div>
    );
}
