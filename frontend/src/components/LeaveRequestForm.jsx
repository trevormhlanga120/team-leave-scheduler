import  {useState} from "react";
import {submitLeave} from "../api";

export default function LeaveRequestForm({employees,onSubmitted}){
    const [employeeId,setEmployeeId] = useState("");
    const [startDate,setStartDate] = useState("");
    const [endDate,setEndDate] = useState("");
    const [error,setError] = useState("");

    async function handleSubmit(e){
        e.preventDefault();
        setError("");
        try{
            await submitLeave({
                employee_id: Number(employeeId),
                start_date : startDate,
                end_date : endDate
            });
            setEmployeeId("");
            setStartDate("");
            setEndDate("");
            onSubmitted();
        } catch(err){
            setError(err.message);
        }
    }

    return (
        <div>
            <h2> Submit Leave Request</h2>
            <form onSubmit = {handleSubmit}>
                    <select value = {employeeId} onChange = {(e)=> setEmployeeId(e.target.value)} required> 
                    <option value = "">Select employee</option>
                    {employees.map((emp)=>(
                       <option key={emp.id} value={emp.id}>{emp.name}</option> 
                    ))}
                </select>
                <input type = "date" value = {startDate} onChange = {(e)=> setStartDate(e.target.value)} required/>
                <input type = "date" value = {endDate} onChange = {(e)=> setEndDate(e.target.value)} required/>
                <button type= "submit">Submit</button>
            </form>
            {error && <p style = {{color:"red"}}>{error}</p>}
        </div>
    )
}