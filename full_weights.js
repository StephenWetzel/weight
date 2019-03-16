var chart = c3.generate({
  size: {
  },
  data: {
    url: 'weight_two.tsv',
    mimeType: 'tsv',
    x: 'date_time',
    xFormat: '%Y-%m-%d %H:%M:%S', // 'xFormat' can be used as custom format of 'x'
    axes: {
      weight: 'y',
      avg_weight: 'y',
      bmi: 'y2',
    },
    types: {
      weight: 'scatter',
      avg_weight: 'spline',
      bmi: 'scatter',
      date_time: 'x'
    }
  },
  axis: {
    x: {
      type: 'timeseries',
      tick: {
        format: '%Y %b %d',
        count: 25,
      }
    },
    y: {
      show: true,
      label: {
        text: "Weight (lbs)"
      }
    },
    y2: {
      show: true,
      label: {
        text: "BMI"
      }
    }
  },
  zoom: {
    enabled: true,
    rescale: true
  },
  grid: {
    y: {
      show: true
    }
  }
});

chart.hide('bmi');
