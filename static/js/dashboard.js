/* =========================================================
   LINEAR ALGEBRA SOLVER - DASHBOARD ANALYTICS
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  initActivityChart();
});

function initActivityChart() {
  const canvas = document.getElementById('activityChart');
  if (!canvas) return;

  const isDark  = (document.documentElement.getAttribute('data-theme') || 'dark') === 'dark';
  const tickClr = isDark ? '#e1b382' : '#2d545e';
  const gridClr = isDark ? 'rgba(225, 179, 130, 0.10)' : 'rgba(45, 84, 94, 0.08)';

  const ctx = canvas.getContext('2d');

  // Gradient fill using Sand Tan palette
  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0,   'rgba(225, 179, 130, 0.35)');
  gradient.addColorStop(1,   'rgba(225, 179, 130, 0.02)');

  window._activityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Calculations',
        data: [12, 19, 15, 25, 22, 30, 28],
        borderColor:      '#e1b382',
        backgroundColor:  gradient,
        fill:             true,
        tension:          0.42,
        borderWidth:      2.5,
        pointBackgroundColor: '#c89666',
        pointBorderColor:     '#12343b',
        pointBorderWidth:     2,
        pointRadius:          5,
        pointHoverRadius:     7,
      }]
    },
    options: {
      responsive:          true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#12343b',
          borderColor:     '#e1b382',
          borderWidth:     1,
          titleColor:      '#fef9f3',
          bodyColor:       '#e1b382',
          padding:         12,
          cornerRadius:    8,
          callbacks: {
            label: ctx => `  ${ctx.parsed.y} calculations`
          }
        }
      },
      scales: {
        x: {
          grid:  { display: false },
          ticks: { color: tickClr, font: { size: 12 } },
          border: { display: false }
        },
        y: {
          grid:  { color: gridClr, drawBorder: false },
          ticks: { color: tickClr, font: { size: 12 }, stepSize: 5 },
          border: { display: false },
          beginAtZero: true
        }
      }
    }
  });
}
