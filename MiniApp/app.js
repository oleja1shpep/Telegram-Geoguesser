let map, panorama, marker, loc;
let mode, x, y, x_center, y_center, zoom;
let radius_index = 0;

let hash = window.location.hash.split('?')[0].split('&')

async function get_cords() {
    mode = hash[0].slice(1, hash[0].length);
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

    styles = []
    console.log(window.Telegram.WebApp.colorScheme)
    // if (window.Telegram.WebApp.colorScheme == "dark") {
    //     styles = [
        //     { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
        //     { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
        //     { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
        //     {
        //       featureType: "administrative.locality",
        //       elementType: "labels.text.fill",
        //       stylers: [{ color: "#d59563" }],
        //     },
        //     {
        //       featureType: "poi",
        //       elementType: "labels.text.fill",
        //       stylers: [{ color: "#d59563" }],
        //     },
        //     {
        //       featureType: "poi.park",
        //       elementType: "geometry",
        //       stylers: [{ color: "#263c3f" }],
        //     },
        //     {
        //       featureType: "poi.park",
        //       elementType: "labels.text.fill",
        //       stylers: [{ color: "#6b9a76" }],
        //     },
        //     {
        //       featureType: "road",
        //       elementType: "geometry",
        //       stylers: [{ color: "#38414e" }],
        //     },
        //     {
        //       featureType: "road",
        //       elementType: "geometry.stroke",
        //       stylers: [{ color: "#212a37" }],
        //     },
        //     {
        //       featureType: "road",
        //       elementType: "labels.text.fill",
        //       stylers: [{ color: "#9ca5b3" }],
        //     },
        //     {
        //       featureType: "road.highway",
        //       elementType: "geometry",
        //       stylers: [{ color: "#746855" }],
        //     },
        //     {
        //       featureType: "road.highway",
        //       elementType: "geometry.stroke",
        //       stylers: [{ color: "#1f2835" }],
        //     },
        //     {
        //       featureType: "road.highway",
        //       elementType: "labels.text.fill",
        //       stylers: [{ color: "#f3d19c" }],
        //     },
        //     {
        //       featureType: "transit",
        //       elementType: "geometry",
        //       stylers: [{ color: "#2f3948" }],
        //     },
        //     {
        //       featureType: "transit.station",
        //       elementType: "labels.text.fill",
        //       stylers: [{ color: "#d59563" }],
        //     },
        //     {
        //       featureType: "water",
        //       elementType: "geometry",
        //       stylers: [{ color: "#17263c" }],
        //     },
        //     {
        //       featureType: "water",
        //       elementType: "labels.text.fill",
        //       stylers: [{ color: "#515c6d" }],
        //     },
        //     {
        //       featureType: "water",
        //       elementType: "labels.text.stroke",
        //       stylers: [{ color: "#17263c" }],
        //     },
        //   ]
    // }

    map = new Map(document.getElementById("map"), {
        controls: {},
        clickableIcons: false,
        disableDefaultUI: true,
        zoom: zoom,
        // styles: styles,
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
        mapId: "799bb53730cb6698"
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

function CreateBotResponce() {
    try {
        var res = `${loc.latLng.lat()} ${loc.latLng.lng()} ${marker.position.Gg} ${marker.position.Hg}|${mode}|${window.Telegram.WebApp.colorScheme}`
    } 
    catch (error) {
        console.log('error:', error)
        var res = `${loc.latLng.lat()} ${loc.latLng.lng()} 0 0|${mode}|${window.Telegram.WebApp.colorScheme}`
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