import { useState, useEffect, useCallback } from "react";
import { getEmployees, getLeave } from "./api";
import LeaveList from "./components/LeaveList";
import LeaveRequestForm from "./components/LeaveRequestForm";
import PendingRequests from "./components/PendingRequests";

export default function App() {
  const [employees, setEmployees] = useState([]);
  const [leaveRequests, setLeaveRequests] = useState([]);

  const refresh = useCallback(async () => {
    setLeaveRequests(await getLeave(30));
  }, []);

  useEffect(() => {
    async function loadInitialData() {
      const [employeesData, leaveData] = await Promise.all([
        getEmployees(),
        getLeave(30),
      ]);
      setEmployees(employeesData);
      setLeaveRequests(leaveData);
    }

    loadInitialData();
  }, []);

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", fontFamily: "sans-serif" }}>
      <h1>Team Leave Scheduler</h1>
      <LeaveList leaveRequests={leaveRequests} />
      <hr />
      <LeaveRequestForm employees={employees} onSubmitted={refresh} />
      <hr />
      <PendingRequests leaveRequests={leaveRequests} onChanged={refresh} />
    </div>
  );
}
