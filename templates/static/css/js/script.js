document.addEventListener("DOMContentLoaded", function() {
    // This function will run after the page content has loaded

    // Example: Fetching data from the Flask backend and updating an element
    fetch('/api/dashboard_data')
        .then(response => response.json())
        .then(data => {
            // Update elements with the fetched data
            document.getElementById("customersCount").innerText = data.customers_count;
            document.getElementById("totalRevenue").innerText = data.total_revenue;
            document.getElementById("profitPercentage").innerText = data.profit_percentage;

            // If you want to update the chart
            updateChart(data.sales);
        })
        .catch(error => {
            console.error("Error fetching data: ", error);
        });
});

// Example of updating a chart dynamically using Chart.js
function updateChart(salesData) {
    var ctx = document.getElementById('salesChart').getContext('2d');
    var salesChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'Sales Over Time',
                data: salesData,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false
            }]
        }
    });
}
