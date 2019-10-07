var popup = new Popup();
map.addOverlay(popup);


map.on('singleclick', function(evt) {
    document.getElementById('info').innerHTML = '';
    var viewResolution = /** @type {number} */ (view.getResolution());
    var url = wmsSource.getGetFeatureInfoUrl(
      evt.coordinate, viewResolution, 'EPSG:3857',
      {'INFO_FORMAT': 'text/html'});
    if (url) {
      document.getElementById('info').innerHTML =
          '<iframe seamless src="' + url + '"></iframe>';
    }
  });

  map.on('pointermove', function(evt) {
    if (evt.dragging) {
      return;
    }
    var pixel = map.getEventPixel(evt.originalEvent);
    var hit = map.forEachLayerAtPixel(pixel, function() {
      return true;
    });
    map.getTargetElement().style.cursor = hit ? 'pointer' : '';
  });