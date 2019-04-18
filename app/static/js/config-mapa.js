(function() {
    //Pegando variável através do atributo data do HTML
    var lyrListText = document.getElementById("map").getAttribute("data-layers");

    //A variável vem no formato JSON, Logo, é necessário converter para um objeto
    lyrListResponseObj = JSON.parse(lyrListText)
    
    let geoserverLayers = []
    //loop para adcionar camadas ao vetor geoserverLayers
    for(i=0; i < lyrListResponseObj.layers.layer.length; i++){
        geoserverLayers.push(new ol.layer.Tile({
            title: lyrListResponseObj.layers.layer[i].name,
            visible: false,
            source: new ol.source.TileWMS({
                url: 'http://localhost:8080/geoserver/wms',
                params: {'LAYERS': 'rnemmapas:'+lyrListResponseObj.layers.layer[i].name, 'TILED': true},
                serverType: 'geoserver',
                // Countries have transparency, so do not fade tiles:
                transition: 0
            })
        })
        )
    }

    var map = new ol.Map({
        target: 'map',
        layers: [
            new ol.layer.Group({
                'title': 'Mapas Base',
                'fold': 'open',
                layers: [
                    new ol.layer.Group({
                        title: 'Water color with labels',
                        type: 'base',
                        combine: true,
                        visible: false,
                        layers: [
                            new ol.layer.Tile({
                                source: new ol.source.Stamen({
                                    layer: 'watercolor'
                                })
                            }),
                            new ol.layer.Tile({
                                source: new ol.source.Stamen({
                                    layer: 'terrain-labels'
                                })
                            })
                        ]
                    }),
                    new ol.layer.Tile({
                        title: 'Water color',
                        type: 'base',
                        visible: false,
                        source: new ol.source.Stamen({
                            layer: 'watercolor'
                        })
                    }),
                    new ol.layer.Tile({
                        title: 'OSM',
                        type: 'base',
                        visible: true,
                        source: new ol.source.OSM()
                    }),
                    new ol.layer.Tile({
                        title: "Google Road Map",
                        type: 'base',
                        visible: false,
                        source: new ol.source.TileImage({ url: 'http://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}' }),
                    }),
                    new ol.layer.Tile({
                        title: "Google Satellite",
                        type: 'base',
                        visible: false,
                        source: new ol.source.TileImage({ url: 'http://mt1.google.com/vt/lyrs=s&hl=pl&&x={x}&y={y}&z={z}' }),
                    }),
                    new ol.layer.Tile({
                        title: "Google Satellite & Roads",
                        type: 'base',
                        visible: false,
                        source: new ol.source.TileImage({ url: 'http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}' }),
                    }),
                    new ol.layer.Tile({
                        title: "Google Terrain",
                        type: 'base',
                        visible: false,
                        source: new ol.source.TileImage({ url: 'http://mt1.google.com/vt/lyrs=t&x={x}&y={y}&z={z}' }),
                    }),
                    new ol.layer.Tile({
                        title: "Google Terrain & Roads",
                        type: 'base',
                        visible: false,
                        source: new ol.source.TileImage({ url: 'http://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}' }),
                    }),
                    new ol.layer.Tile({
                        title: "Google Road without Building",
                        type: 'base',
                        visible: false,
                        source: new ol.source.TileImage({ url: 'http://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}' }),
                    }),
                ]
            }),
            new ol.layer.Group({
                title: 'Mapas Temáticos',
                layers: geoserverLayers
            })
        ],
        view: new ol.View({
            center: ol.proj.transform([-36.91610435453907,-5.76974470264004], 'EPSG:4326', 'EPSG:3857'),
            zoom: 8
        }),
        controls: ol.control.defaults().extend([
            new ol.control.ScaleLine(),
            new ol.control.FullScreen()
        ])
    });

    // Get out-of-the-map div element with the ID "layers" and renders layers to it.
    // NOTE: If the layers are changed outside of the layer switcher then you
    // will need to call ol.control.LayerSwitcher.renderPanel again to refesh
    // the layer tree. Style the tree via CSS.
    var sidebar = new ol.control.Sidebar({ element: 'sidebar', position: 'left' });
    var toc = document.getElementById("layers");
    ol.control.LayerSwitcher.renderPanel(map, toc);
    map.addControl(sidebar);

})();
