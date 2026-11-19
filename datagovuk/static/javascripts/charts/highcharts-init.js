// Draw each chart on the page with Highcharts, using the options built by the server.
// The chart container holds a message for users without JavaScript, which Highcharts replaces when it draws the chart.

if (window.Highcharts) {
  // Show full numbers on the axes (e.g. "6,000m") rather than shortening them (e.g. "6k"), which would clash with units
  // like "m" for millions. Always use a comma as the thousands separator and a full stop as the decimal point, like the
  // chart's data table, rather than following the user's browser language. These can only be set for all charts, not in
  // each chart's options.
  window.Highcharts.setOptions({
    lang: {
      numericSymbols: null,
      thousandsSep: ',',
      decimalPoint: '.',
      // Screen readers announce the key as "Key" and each item in it by its series name, rather than as "Toggle series
      // visibility" and "Show [series name]", since clicking it doesn't show or hide the series
      accessibility: {
        legend: { legendItem: '{itemName}', legendLabel: 'Key, {chartTitle}', legendLabelNoTitle: 'Key, {chartTitle}' }
      }
    },
    // Stop clicks on the key hiding and showing series. This needs a function, so it can't be in the options built by
    // the server.
    legend: { events: { itemClick: () => false } }
  })

  // Don't animate charts for users who've asked their device to reduce motion: no drawing in when the chart loads,
  // and no movement or fading when hovering over or focusing on the chart
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    window.Highcharts.setOptions({
      chart: { animation: false },
      tooltip: { animation: false },
      plotOptions: {
        series: {
          animation: false,
          states: { hover: { animation: false }, inactive: { animation: false } },
          marker: { states: { hover: { animation: false } } }
        }
      }
    })
  }
}

document.querySelectorAll('[data-datagovuk-chart]').forEach(($chart) => {
  const $options = document.getElementById($chart.dataset.datagovukChart)

  if ($options && window.Highcharts) {
    window.Highcharts.chart($chart, JSON.parse($options.textContent))
  }
})
