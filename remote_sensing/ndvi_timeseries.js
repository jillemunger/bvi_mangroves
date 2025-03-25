// NDVI Time Series Analysis for Selected Sites
 
// This script analyzes the Normalized Difference Vegetation Index (NDVI) over time 
// for specific mangrove sites in Tortola, Virgin Islands (UK) using Sentinel-2 imagery. 
// It extracts NDVI values for predefined GPS locations, generates time series plots  

// Define GPS points with site names
var sites = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([-64.63336, 18.40462]), {name: 'Sea Cows Bay'}),
    ee.Feature(ee.Geometry.Point([-64.57673, 18.41836]), {name: 'Paraquita Bay'}),
    ee.Feature(ee.Geometry.Point([-64.69911, 18.38597]), {name: 'Frenchmans Cay'}),
    ee.Feature(ee.Geometry.Point([-64.536303, 18.440171]), {name: 'Hans Creek A'})
  ]);
  
  // Define Sentinel-2 ImageCollection and calculate NDVI
  var S2 = ee.ImageCollection('COPERNICUS/S2')
    .filterBounds(sites) // Use sites as a FeatureCollection
    .filterDate('2017-01-01', '2024-12-31') // Adjust date range
    .map(function(image) {
      return image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        .copyProperties(image, ['system:time_start']);
    });
  
  // Define a color mapping for the sites
  var siteColors = {
    'Sea Cows Bay': '#1f77b4',    // Blue
    'Paraquita Bay': '#ff7f0e',   // Orange
    'Frenchmans Cay': '#2ca02c',  // Green
    'Hans Creek A': '#d62728'     // Red
  };
  
  // Base chart style properties
  var baseChartStyle = {
    hAxis: {
      title: 'Date',
      titleTextStyle: {italic: false, bold: true},
      gridlines: {color: 'FFFFFF'}
    },
    vAxis: {
      title: 'NDVI',
      titleTextStyle: {italic: false, bold: true},
      gridlines: {color: 'FFFFFF'},
      format: 'short',
      baselineColor: 'FFFFFF'
    },
    chartArea: {backgroundColor: 'EBEBEB'},
    legend: {position: 'none'} // Hide legend
  };
  
  // Function to generate a time series chart for each site
  function generateChart(siteFeature) {
    var siteName = ee.String(siteFeature.get('name')); // Convert EE String
    var color = siteColors[siteName.getInfo()]; // Assign color based on site name
    
    var siteChart = ui.Chart.image.seriesByRegion(
      S2,
      siteFeature,
      ee.Reducer.mean(),
      'NDVI',
      500,
      'system:time_start'
    )
    .setChartType('LineChart')
    .setOptions({
      title: siteName.getInfo(), // Convert EE String to JS String
      hAxis: baseChartStyle.hAxis,
      vAxis: baseChartStyle.vAxis,
      series: { 0: {lineWidth: 1, color: color, pointSize: 4} }, // Assign color dynamically
      chartArea: baseChartStyle.chartArea,
      legend: baseChartStyle.legend // Apply no legend
    });
  
    print(siteChart);
  }
  
  // Generate and display the charts for each site
  sites.evaluate(function(siteList) {
    siteList.features.forEach(function(siteDict) {
      var siteFeature = ee.Feature(ee.Geometry.Point(siteDict.geometry.coordinates), siteDict.properties);
      generateChart(siteFeature);
    });
  });
  