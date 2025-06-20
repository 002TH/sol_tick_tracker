const ctx = document.getElementById('chart').getContext('2d');
let chart;

async function fetchData() {
    const res = await fetch('/tick-ohlc');
    const data = await res.json();

    const labels = data.map(bar => bar.time);
    const highs = data.map(bar => bar.high);
    const lows = data.map(bar => bar.low);
    const opens = data.map(bar => bar.open);
    const closes = data.map(bar => bar.close);

    drawChart(labels, opens, highs, lows, closes);
    updateOHLC(opens, highs, lows, closes);
}

function drawChart(labels, opens, highs, lows, closes) {
    const datasets = labels.map((label, i) => {
        const color = closes[i] > opens[i] ? 'lime' : 'red';
        return {
            label: label,
            data: [{
                x: i,
                y: [opens[i], highs[i], lows[i], closes[i]]
            }],
            borderColor: color,
            backgroundColor: color,
            borderWidth: 2,
            type: 'bar',
            barThickness: 4,
            parsing: {
                yAxisKey: 'y'
            }
        };
    });

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets
        },
        options: {
            responsive: true,
            scales: {
                x: {
                    ticks: { color: '#888' },
                    grid: { color: '#222' }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#ccc' },
                    grid: { color: '#333' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function updateOHLC(opens, highs, lows, closes) {
    const i = opens.length - 1;
    document.getElementById("ohlc").innerText = `
SOL TICK (15m)
O: ${opens[i]}
H: ${highs[i]}
L: ${lows[i]}
C: ${closes[i]}
    `.trim();
}

setInterval(fetchData, 5000);
fetchData();