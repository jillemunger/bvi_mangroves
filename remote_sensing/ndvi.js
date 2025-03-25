// This script uses Google Earth Engine (GEE) to calculate 
// and export the Normalized Difference Vegetation Index (NDVI) 
// for multiple sites on Tortola, British Virgin Islands.

// Define GPS points with site names
var sites = [
    {name: 'Sea Cows Bay', coordinates: [-64.63336, 18.40462]},
    {name: 'Paraquita Bay', coordinates: [-64.57673, 18.41836]},
    {name: 'Frenchmans Cay', coordinates: [-64.69911, 18.38597]},
    {name: 'Hans Creek A', coordinates: [-64.536303, 18.440171]}
  ];
  
  // Add the NDVI layer
  var s2 = ee.ImageCollection('COPERNICUS/S2')
             .filterDate('2024-01-10', '2024-02-28')
             .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
             .select(['B4', 'B8', 'B11']); // Red (B4), NIR (B8), SWIR (B11)
  
  // Compute median composite and NDVI
  var median = s2.median();
  var ndvi = median.normalizedDifference(['B8', 'B4']).rename('NDVI');
  
  // Mask out negative NDVI values (ocean and high cloud cover)
  var ndviMasked = ndvi.updateMask(ndvi.gte(0.001));
  
  // Loop through each site and calculate NDVI
  sites.forEach(function(site) {
    var point = ee.Geometry.Point(site.coordinates);
    
    // Calculate NDVI value for the site
    var ndviValue = ndviMasked.reduceRegion({
      reducer: ee.Reducer.mean(),
      geometry: point,
      scale: 10
    });
  
    print(site.name + ' NDVI:', ndviValue);
  });
  
  // NDVI Visualization parameters
  var ndviVisParams = {
    min: 0, max: 1, // Ensure the visualization parameters cover the full NDVI range
    palette: [
      '#1f449c', '#357a77', '#7ca1cc', '#a8b6cc', '#eebab4', '#e4ff7a',
      '#ffd200', '#ffb500', '#ff9a00', '#fc7f00', '#e63e00', '#b92b00'
    ] 
  };
  
  // Add NDVI layer to the map
  Map.addLayer(ndviMasked, ndviVisParams, 'Masked NDVI');
  
  // Create squares around sites
  var squares = sites.map(function(site) {
    var point = ee.Geometry.Point(site.coordinates);
    var square = point.buffer(300).bounds(); // Create a bounding box (square)
    
    return {
      name: site.name,
      geometry: square
    };
  });
  
  // Add squares to the map with visual parameters
  squares.forEach(function(site) {
    Map.addLayer(site.geometry, {color: 'red'}, site.name + ' (50x50m)');
  });
  
  // Center map on the first site
  Map.centerObject(ee.Geometry.Point(sites[0].coordinates), 12);
  
  // Create a region to export that includes all the sites
  var allSitesBounds = ee.Geometry.MultiPolygon(squares.map(function(site) {
    return site.geometry;
  })).bounds().buffer(1500);  // Add a 1500m buffer to make the bounding box larger
  
  // Function to create a dynamic legend based on actual map values
  function createDynamicLegend(title, image, palette, region, visParams) {
    var min = visParams.min; // Use the min value from visParams
    var max = visParams.max; // Use the max value from visParams
  
    var legend = ui.Panel({style: {position: 'bottom-left', padding: '8px 15px'}});
    legend.add(ui.Label({value: title, style: {fontWeight: 'bold', fontSize: '14px', margin: '0 0 4px 0'}}));
    
    // Create the color blocks for the legend
    var legendPanel = ui.Panel({layout: ui.Panel.Layout.flow('horizontal'), style: {margin: '0px'}});
    palette.forEach(function(color) {
      legendPanel.add(ui.Label({style: {backgroundColor: color, padding: '8px', margin: '0px', width: '24px', height: '12px'}}));
    });
    legend.add(legendPanel);
  
    // Generate labels based on palette size and actual range
    var numColors = palette.length;
    var labels = [];
    for (var i = 0; i < numColors; i++) {
      var value = min + (i * (max - min) / (numColors - 1));
      labels.push(value.toFixed(2)); // Format values to two decimals
    }
  
    // Create and style the label panel
    var labelPanel = ui.Panel({layout: ui.Panel.Layout.flow('horizontal'), style: {margin: '4px 0 0 0'}});
    labels.forEach(function(label) {
      labelPanel.add(ui.Label({value: label, style: {margin: '0px 8px', fontSize: '10px', color: 'black', textAlign: 'center'}}));
    });
    legend.add(labelPanel);
    Map.add(legend);
  }
  
  // Use the NDVI image for the legend and provide the bounding region for calculation
  createDynamicLegend('NDVI Scale', ndviMasked, ndviVisParams.palette, allSitesBounds, ndviVisParams);
  
  // Create an image with the site markers
  var siteMarkers = ee.FeatureCollection(sites.map(function(site) {
    return ee.Feature(ee.Geometry.Point(site.coordinates), {name: site.name});
  }));
  
  var siteMarkersImage = ee.Image().byte().paint({
    featureCollection: siteMarkers,
    color: 1,
    width: 5
  });
  
  // Create an image with the squares
  var squareImage = ee.Image().byte().paint({
    featureCollection: ee.FeatureCollection(squares.map(function(site) {
      return ee.Feature(site.geometry);
    })),
    color: 2,
    width: 2
  });
  
  // Loop through each square and export the corresponding NDVI image
  squares.forEach(function(site) {
    var ndviRegion = site.geometry; // Define the region for export
    
    // Export the NDVI image to Google Drive
    Export.image.toDrive({
      image: ndvi.visualize(ndviVisParams),
      description: site.name + '_NDVI',
      folder: 'NDVI',
      fileNamePrefix: site.name + '_NDVI_Tortola',
      scale: 10, // Match Sentinel-2 resolution
      region: ndviRegion,
      maxPixels: 1e13
    });
  });
  
  // Combine the NDVI image with site markers and squares
  var combinedImage = ndviMasked.visualize(ndviVisParams)
    .blend(squareImage.visualize({palette: 'red', opacity: 0.8}))
    .blend(siteMarkersImage.visualize({palette: 'black', opacity: 1}));
  
  // Export the combined image to Google Drive
  Export.image.toDrive({
    image: combinedImage,
    description: 'Whole_Map_NDVI',
    folder: 'NDVI',
    fileNamePrefix: 'Whole_Map_NDVI',
    scale: 10,
    region: allSitesBounds,
    maxPixels: 1e13
  });