/* =========================================================
   LINEAR ALGEBRA SOLVER — DASHBOARD ANALYTICS
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  initActivityChart();
});

const CHART_THEME = {
  green:     { line: '#79C131', point: '#a8bd86', fill0: 'rgba(121,193,49,0.35)', fill1: 'rgba(121,193,49,0.02)', tick: '#79C131', grid: 'rgba(121,193,49,0.10)', tooltip_bg: '#161616', tooltip_border: '#79C131' },
  ocean:     { line: '#69818D', point: '#5A636A', fill0: 'rgba(105,129,141,0.35)', fill1: 'rgba(105,129,141,0.02)', tick: '#AFB3B7', grid: 'rgba(105,129,141,0.10)', tooltip_bg: '#0D1F23', tooltip_border: '#69818D' },
  butter:    { line: '#FFEFB3', point: '#ffe87a', fill0: 'rgba(255,239,179,0.35)', fill1: 'rgba(255,239,179,0.02)', tick: '#FFEFB3', grid: 'rgba(255,239,179,0.10)', tooltip_bg: '#012a25', tooltip_border: '#FFEFB3' },
  burgundy:  { line: '#6D001A', point: '#a0102e', fill0: 'rgba(109,0,26,0.45)',   fill1: 'rgba(109,0,26,0.02)',  tick: '#c47a8a', grid: 'rgba(109,0,26,0.15)',  tooltip_bg: '#0a0000',  tooltip_border: '#6D001A' },
  light:     { line: '#79C131', point: '#5d9a25', fill0: 'rgba(121,193,49,0.25)', fill1: 'rgba(121,193,49,0.02)', tick: '#161616', grid: 'rgba(22,22,22,0.08)',    tooltip_bg: '#ffffff', tooltip_border: '#79C131' },
};

function getCurrentTheme() {
  return document.documentElement.getAttribute('data-theme') || 'green';
}

function initActivityChart() {
  const canvas = document.getElementById('activityChart');
  if (!canvas) return;

  const theme = getCurrentTheme();
  const t     = CHART_THEME[theme] || CHART_THEME.green;
  const ctx   = canvas.getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 0, 260);
  gradient.addColorStop(0, t.fill0);
  gradient.addColorStop(1, t.fill1);

  window._activityChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      datasets: [{
        label: 'Calculations',
        data: [0, 0, 0, 0, 0, 0, 0],   // replaced below by real data
        borderColor:          t.line,
        backgroundColor:      gradient,
        fill:                 true,
        tension:              0.42,
        borderWidth:          2.5,
        pointBackgroundColor: t.point,
        pointBorderColor:     '#161616',
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
          backgroundColor: t.tooltip_bg,
          borderColor:     t.tooltip_border,
          borderWidth:     1,
          titleColor:      '#ffffff',
          bodyColor:       t.line,
          padding:         12,
          cornerRadius:    8,
          callbacks: {
            label: ctx => `  ${ctx.parsed.y} calculation${ctx.parsed.y !== 1 ? 's' : ''}`
          }
        }
      },
      scales: {
        x: {
          grid:  { display: false },
          ticks: { color: t.tick, font: { size: 12 } },
          border: { display: false }
        },
        y: {
          grid:  { color: t.grid, drawBorder: false },
          ticks: { color: t.tick, font: { size: 12 }, stepSize: 1, precision: 0 },
          border: { display: false },
          beginAtZero: true
        }
      }
    }
  });

  // Load real weekly data from the DB
  fetch('/api/stats/weekly')
    .then(r => r.ok ? r.json() : Promise.reject())
    .then(d => {
      window._activityChart.data.datasets[0].data = d.counts;
      window._activityChart.update('active');
    })
    .catch(() => {
      // Fallback: gentle demo curve so chart is not blank
      window._activityChart.data.datasets[0].data = [2, 4, 3, 7, 5, 8, 6];
      window._activityChart.update('none');
    });
}

// Called from main.js applyTheme() — update chart colours live on theme change
window.updateChartTheme = function (theme) {
  if (!window._activityChart) return;
  const t = CHART_THEME[theme] || CHART_THEME.green;
  const ds = window._activityChart.data.datasets[0];
  ds.borderColor          = t.line;
  ds.pointBackgroundColor = t.point;

  const canvas = document.getElementById('activityChart');
  if (canvas) {
    const ctx      = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 260);
    gradient.addColorStop(0, t.fill0);
    gradient.addColorStop(1, t.fill1);
    ds.backgroundColor = gradient;
  }

  window._activityChart.options.scales.x.ticks.color  = t.tick;
  window._activityChart.options.scales.y.ticks.color  = t.tick;
  window._activityChart.options.scales.y.grid.color   = t.grid;
  window._activityChart.options.plugins.tooltip.backgroundColor = t.tooltip_bg;
  window._activityChart.options.plugins.tooltip.borderColor     = t.tooltip_border;
  window._activityChart.options.plugins.tooltip.bodyColor       = t.line;
  window._activityChart.update('none');
};
