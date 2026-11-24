document.addEventListener("DOMContentLoaded", () => {
  const riskCanvas = document.getElementById("riskDistributionChart");
  if (riskCanvas && window.RISK_DIST_DATA) {
    new Chart(riskCanvas, {
      type: "doughnut",
      data: {
        labels: ["Low Risk (0–30)", "Medium Risk (31–60)", "High Risk (61–100)"],
        datasets: [
          {
            data: [
              window.RISK_DIST_DATA.low,
              window.RISK_DIST_DATA.medium,
              window.RISK_DIST_DATA.high,
            ],
            backgroundColor: ["#059669", "#d97706", "#dc2626"],
            borderWidth: 2,
            borderColor: "#ffffff",
          },
        ],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: "bottom" },
        },
      },
    });
  }

  const catCanvas = document.getElementById("categoryFundingChart");
  if (catCanvas && window.CATEGORY_DATA) {
    new Chart(catCanvas, {
      type: "bar",
      data: {
        labels: window.CATEGORY_DATA.labels,
        datasets: [
          {
            label: "Total Raised ($)",
            data: window.CATEGORY_DATA.totals,
            backgroundColor: "#4f46e5",
            borderRadius: 6,
          },
        ],
      },
      options: {
        responsive: true,
        scales: {
          y: { beginAtZero: true },
        },
        plugins: {
          legend: { display: false },
        },
      },
    });
  }
});
