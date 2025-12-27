const form = document.getElementById("upload-form");
const loading = document.getElementById("loading");
const results = document.getElementById("results");

const totalTxEl = document.getElementById("totalTx");
const anomaliesEl = document.getElementById("anomalies");
const tableBody = document.querySelector("#preview-table tbody");

// ---------------- PAGINATION STATE ----------------
let currentPage = 1;
const pageSize = 20;
let totalRows = 0;

// ---------------- CHARTS ----------------
let categoryChart = null;
let anomalyChart = null;
let monthlyChart = null;
let forecastChart = null;

// -------------------- UPLOAD --------------------
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const file = document.getElementById("csvFile").files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    loading.classList.remove("hidden");
    results.classList.add("hidden");

    await fetch("http://127.0.0.1:8000/transactions/upload", {
        method: "POST",
        body: formData
        
    });
    await loadFilters();

    currentPage = 1;
    await applyFilters();

    loading.classList.add("hidden");
    results.classList.remove("hidden");
});

// -------------------- FILTER CHANGE --------------------
function onFilterChange() {
    currentPage = 1;
    applyFilters();
}

// -------------------- APPLY FILTERS (SQL) --------------------
async function applyFilters() {
    const params = new URLSearchParams();

    params.append("limit", pageSize);
    params.append("offset", (currentPage - 1) * pageSize);

    const start = document.getElementById("startDate").value;
    const end = document.getElementById("endDate").value;
    const category = document.getElementById("categoryFilter").value;
    const account = document.getElementById("accountFilter").value;

    if (start) params.append("start_date", start);
    if (end) params.append("end_date", end);
    if (category) params.append("category", category);
    if (account) params.append("account", account);

    const res = await fetch(
        `http://127.0.0.1:8000/transactions?${params.toString()}`
    );

    const result = await res.json();

    totalRows = result.total;
    totalTxEl.textContent = totalRows;

    updateDashboard(result.data);
    updatePaginationInfo();
}

// -------------------- DASHBOARD --------------------
function updateDashboard(data) {

    // --------- TABLE ---------
    tableBody.innerHTML = "";
    data.forEach(row => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${row.date}</td>
            <td>${row.description}</td>
            <td>${row.amount.toFixed(2)}</td>
            <td>${row.predicted_category}</td>
            <td>${row.is_anomaly ? "⚠️" : "✓"}</td>
        `;
        tableBody.appendChild(tr);
    });

    // --------- AGGREGATIONS ---------
    const categorySummary = {};
    const anomalySummary = { normal: 0, anomaly: 0 };
    const monthlySummary = {};

    data.forEach(row => {
        categorySummary[row.predicted_category] =
            (categorySummary[row.predicted_category] || 0) + row.amount;

        anomalySummary[row.is_anomaly ? "anomaly" : "normal"]++;

        const month = row.date.slice(0, 7);
        monthlySummary[month] =
            (monthlySummary[month] || 0) + row.amount;
    });

    anomaliesEl.textContent = anomalySummary.anomaly;

    renderCharts(categorySummary, anomalySummary, monthlySummary);
}

// -------------------- CHARTS --------------------
function renderCharts(categoryData, anomalyData, monthlyData) {

    if (categoryChart) categoryChart.destroy();
    if (anomalyChart) anomalyChart.destroy();
    if (monthlyChart) monthlyChart.destroy();

    categoryChart = new Chart("categoryChart", {
        type: "bar",
        data: {
            labels: Object.keys(categoryData),
            datasets: [{
                label: "Spending by Category",
                data: Object.values(categoryData)
            }]
        }
    });

    anomalyChart = new Chart("anomalyChart", {
        type: "doughnut",
        data: {
            labels: ["Normal", "Anomaly"],
            datasets: [{
                data: [
                    anomalyData.normal,
                    anomalyData.anomaly
                ]
            }]
        }
    });

    monthlyChart = new Chart("monthlyChart", {
        type: "line",
        data: {
            labels: Object.keys(monthlyData),
            datasets: [{
                label: "Monthly Spending",
                data: Object.values(monthlyData),
                tension: 0.3,
                fill: false
            }]
        }
    });
}

// -------------------- FORECAST --------------------
async function fetchForecast(monthlyData) {
    const response = await fetch(
        "http://127.0.0.1:8000/forecast/monthly",
        {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ monthly_spending: monthlyData })
        }
    );

    const data = await response.json();

    if (forecastChart) forecastChart.destroy();

    forecastChart = new Chart("forecastChart", {
        type: "line",
        data: {
            labels: Object.keys(data.forecast),
            datasets: [{
                label: "Forecasted Spending",
                data: Object.values(data.forecast),
                borderDash: [6, 6],
                tension: 0.3,
                fill: false
            }]
        }
    });
}

// -------------------- PAGINATION --------------------
function nextPage() {
    if (currentPage * pageSize < totalRows) {
        currentPage++;
        applyFilters();
    }
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        applyFilters();
    }
}

function updatePaginationInfo() {
    const totalPages = Math.ceil(totalRows / pageSize);
    document.getElementById("pageInfo").innerText =
        `Page ${currentPage} of ${totalPages}`;
}
function exportCSV() {
    const params = new URLSearchParams();

    const start = document.getElementById("startDate").value;
    const end = document.getElementById("endDate").value;
    const category = document.getElementById("categoryFilter").value;
    const account = document.getElementById("accountFilter").value;

    if (start) params.append("start_date", start);
    if (end) params.append("end_date", end);
    if (category) params.append("category", category);
    if (account) params.append("account", account);

    window.location.href =
        `http://127.0.0.1:8000/transactions/export?${params.toString()}`;
}
function populateSelect(id, values) {
    const select = document.getElementById(id);
    select.innerHTML = `<option value="">All</option>`;

    values.forEach(v => {
        const opt = document.createElement("option");
        opt.value = v;
        opt.textContent = v;
        select.appendChild(opt);
    });
}
async function loadFilters() {
    const res = await fetch("http://127.0.0.1:8000/transactions/filters");
    const data = await res.json();

    populateSelect("categoryFilter", data.categories);
    populateSelect("accountFilter", data.accounts);
}

// -------------------- FILTER EVENTS --------------------
["startDate", "endDate", "categoryFilter", "accountFilter"]
    .forEach(id =>
        document
            .getElementById(id)
            .addEventListener("change", onFilterChange)
    );
