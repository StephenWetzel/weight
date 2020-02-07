
var date_long = d3.timeFormat('%Y %b %d %a %I:%M %p');
var date_short = d3.timeFormat('%Y %b %d');
var chart = c3.generate({
  bindto: '#chart',
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
        format: date_short,
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
  tooltip: {
    format: {
      title: function (d) {
        return date_long(d);
      }
    }
  },
  zoom: {
    enabled: true,
    type: 'scroll',
    rescale: true
  },
  grid: {
    y: {
      show: true
    }
  }
});

chart.hide('bmi');
