document.addEventListener("DOMContentLoaded", () => {
    loadProcesses();
    document.getElementById("process").addEventListener("change", loadSubProcesses);
});

function loadProcesses() {
    fetch("/api/processes/")
        .then(res => res.json())
        .then(data => {
            const p = document.getElementById("process");
            p.innerHTML = '<option value="">Select Process</option>';
            data.forEach(item => {
                p.innerHTML += `<option value="${item}">${item}</option>`;
            });
        })
        .catch(err => console.error("Error loading processes:", err));
}

function loadSubProcesses() {
    const campaign = document.getElementById("process").value;
    const sub = document.getElementById("sub_process");
    sub.innerHTML = '<option value="">Loading...</option>';

    if (!campaign) {
        sub.innerHTML = '<option value="">Select Sub Process</option>';
        return;
    }

    fetch(`/api/subprocesses/?process=${encodeURIComponent(campaign)}`)
        .then(res => res.json())
        .then(data => {
            sub.innerHTML = '<option value="">Select Sub Process</option>';
            data.forEach(item => {
                sub.innerHTML += `<option value="${item}">${item}</option>`;
            });
            if (data.length > 0) sub.value = data[0];
        })
        .catch(err => console.error("Error loading sub processes:", err));
}
