function validateSearch() {
    const fromDate = document.querySelector('input[name="from_date"]').value;
    const toDate = document.querySelector('input[name="to_date"]').value;

    if (fromDate > toDate) {
        alert("From Date cannot be later than To Date");
        return false;
    }
    return true;
}
document.addEventListener("DOMContentLoaded", () => {
    loadProcesses();

    document.getElementById("process").addEventListener("change", loadSubProcesses);
});


function loadProcesses() {
    fetch("/api/processes/")
        .then(response => response.json())
        .then(data => {
            const processSelect = document.getElementById("process");
            processSelect.innerHTML = '<option value="">Select Process</option>';

            data.forEach(process => {
                processSelect.innerHTML += `<option value="${process}">${process}</option>`;
            });
        });
}


function loadSubProcesses() {
    const process = document.getElementById("process").value;
    const subSelect = document.getElementById("sub_process");

    subSelect.innerHTML = '<option value="">Loading...</option>';

    if (!process) return;

    fetch(`/api/subprocesses/?process=${encodeURIComponent(process)}`)
        .then(response => response.json())
        .then(data => {
            subSelect.innerHTML = '<option value="">Select Sub Process</option>';

            data.forEach(sub => {
                subSelect.innerHTML += `<option value="${sub}">${sub}</option>`;
            });
        });
}

