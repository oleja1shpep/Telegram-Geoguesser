let map, panorama, marker, loc;
let x, y, x_center, y_center, zoom;
let radius_index = 0;

let hash = window.location.hash.split('?')[0].split('&')

async function get_cords() {
    x = parseFloat(hash[1])
    y = parseFloat(hash[2])
    x_center = parseFloat(hash[3])
    y_center = parseFloat(hash[4])
    zoom = parseFloat(hash[5])
    radius_index = parseInt(hash[6])
}

const radiuses = [500, 2500, 12500, 50000, 100000, 300000, 600000, 50000000]
get_cords();

function get_panorama() {
    // Ищем панораму в переданной точке.
    console.log(x, y, x_center, y_center, zoom)
    const sv = new google.maps.StreetViewService();
    panorama = new google.maps.StreetViewPanorama(
      document.getElementById("pano"),
      {
        pov: {
          heading: 34,
          pitch: 10,
        },
        addressControl: false,
        fullscreenControl: false,
        showRoadLabels: false
      }
    );
    sv.getPanorama({ location: {lat: x, lng: y}, preference: "nearest", radius: radiuses[radius_index], source: "outdoor"}, processSVData);
};

function processSVData(data, status) {
    initMap()
    if (status == google.maps.StreetViewStatus.OK) {
        console.log('status: OK')
    } else if (status == google.maps.StreetViewStatus.ZERO_RESULTS) {
        console.log('status: zero results, radius:', radiuses[radius_index])
        radius_index = radius_index + 1;
        if (radius_index < radiuses.length) {
            get_panorama();
        }
        return;
    } else {
        console.log('status:', status)
        return;
    }
    loc = data.location;

    panorama.setPano(loc.pano);
    panorama.setPov({
      heading: 270,
      pitch: 0,
    });
    panorama.setVisible(true);
}

async function initMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    map = new Map(document.getElementById("map"), {
        controls: {},
        clickableIcons: false,
        disableDefaultUI: true,
        zoom: zoom,
        minZoom: 1, 
        center: {lat: x_center, lng: y_center},
        restriction: {
            latLngBounds: {
              north: 80,
              south: -80,
              east: 180,
              west: -180,
            },
        },
        mapId: "answer_map"
    });

    const markerImg = document.createElement("img");
    markerImg.src = "https://storage.yandexcloud.net/test-geoguessr/marker.png";

    marker = new AdvancedMarkerElement({
        map: map,
        gmpDraggable: true,
        position: {lat: x_center, lng: y_center},
        content: markerImg,
        title: "Answer",
    });

    map.addListener("click", (mapsMouseEvent) => {
        marker.position = mapsMouseEvent.latLng;
    })
}

function GetPanoramaCords() {
    try {
        var res = `${loc.latLng.lat()} ${loc.latLng.lng()} ${marker.position.Gg} ${marker.position.Hg}`
    } 
    catch (error) {
        console.log('error:', error)
        var res = `${loc.latLng.lat()} ${loc.latLng.lng()} 0 0`
    }
    console.log(res);
    return res;
}

function toHomePano() {
    panorama.setPano(loc.pano);
    panorama.setPov({
      heading: 270,
      pitch: 0,
    });
}