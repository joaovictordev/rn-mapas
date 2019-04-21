(function() {
    //Configurando os dados vindo do geoserver
    
    //Pegando variável através do atributo data do HTML
    lyrListText = document.getElementById("map").getAttribute("data-layers");

    //A variável vem no formato JSON, Logo, é necessário converter para um objeto
    lyrListResponseObj = JSON.parse(lyrListText)

    //vetor para armazenar camadas do geoserver
    let geoserverLayers = []

    if(lyrListResponseObj.layers == ""){
        let geoserverLayers = []
    }
    else{
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
    }

    var map = new ol.Map({
        target: 'map',
        layers: [
            //Grupo de camadas que servem de base para as camadas temáticas
            new ol.layer.Group({
                'title': 'Camadas Base',
                'fold': 'open',
                layers: [
                    new ol.layer.Tile({
                        title: 'Open Street Map',
                        type: 'base',
                        visible: true,
                        source: new ol.source.OSM()
                    }),
                    new ol.layer.Tile({
                        title: 'Bing Maps Road',
                        type: 'base',
                        visible: false,
                        source: new ol.source.BingMaps({
                            imagerySet: 'Road',
                            key: 'ApGJr5FQj_2Q7lXo1IeWWMzzeiqzcKggZxBggH1IXTkxD01ZZL-281Jr89Xjf2Yd'
                        })
                    })
                ]
            }),
            //Grupo de camadas enviadas ao geoserver pelo usuário
            new ol.layer.Group({
                title: 'Camadas Temáticas',
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