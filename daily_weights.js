
var date_long = d3.timeFormat('%Y %b %d %a');
var date_short = d3.timeFormat('%Y %b %d');
var chart = c3.generate({
  size: {
  },
  data: {
    url: 'weight_two_daily.tsv',
    mimeType: 'tsv',
    x: 'date',
    xFormat: '%Y-%m-%d', // 'xFormat' can be used as custom format of 'x'
    axes: {
      weight: 'y',
    },
    types: {
      weight: 'scatter',
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
    rescale: true
  },
  grid: {
    y: {
      show: true
    }
  }
});

