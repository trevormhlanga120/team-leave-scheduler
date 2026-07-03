const BASE_URL =  "http://localhost:8000";


export async function getEmployees(){
    const  res = await  fetch(`${BASE_URL}/employees`);
    return res.json();
}


export async function getLeave(days = 30){
    const res = await fetch(`${BASE_URL}/leave/?days=${days}`);
    return res.json();
}


export async function submitLeave({employee_id,start_date,end_date}){
    const res = await fetch(`${BASE_URL}/leave/`,{

        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({employee_id,start_date,end_date}),

    });
    if (!res.ok){
        const err = await res.json().catch(()=>null);
        const msg = err?.detail ?? err?.message ?? JSON.stringify(err) ?? "Request failed";
        throw new Error(msg);
    }
    return res.json();
}


export async function rejectLeave(id){
    const res = await fetch(`${BASE_URL}/leave/${id}/reject`,{method:"PUT"});
    if (!res.ok){
        const err = await res.json().catch(()=>null);
        throw new Error(err?.detail ?? JSON.stringify(err) ?? 'Request failed');
    }
    return res.json();
}

export async function approveLeave(id){
    const res = await fetch(`${BASE_URL}/leave/${id}/approve`,{method:"PUT"});
    if (!res.ok){
        const err = await res.json().catch(()=>null);
        throw new Error(err?.detail ?? JSON.stringify(err) ?? 'Request failed');
    }
    return res.json();
}