let map, panorama, marker, loc, answer_map;
let mode, x, y, x_center, y_center, zoom, seed, tele_id;
let radius_index = 0;

const markerImg = document.createElement("img");
markerImg.src = "https://storage.yandexcloud.net/test-geoguessr/marker.png";


var myHeaders = new Headers();
myHeaders.append("Content-Type", "application/json");

function getDictFromHash() {
    const hash = window.location.hash.split('?')[0].substring(1);
    const pairs = hash.split('&');
    const dict = {};
    pairs.forEach(pair => {
        const [key, value] = pair.split('=');
        const decodedKey = decodeURIComponent(key);
        const decodedValue = decodeURIComponent(value);
        dict[decodedKey] = decodedValue;
    });
    return dict;
}

// console.log(getDictFromHash())

let hash = window.location.hash.split('?')[0].split('&')

async function get_cords() {
    mode = hash[0].slice(1, hash[0].length);
    x = parseFloat(hash[1])
    y = parseFloat(hash[2])
    x_center = parseFloat(hash[3])
    y_center = parseFloat(hash[4])
    zoom = parseFloat(hash[5])
    radius_index = parseInt(hash[6])
    seed = hash[7]
    tele_id = parseInt(hash[8])
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
            showRoadLabels: false,
            zoomControl: false,
            // motionTrackingControl: false
        }
    );
    sv.getPanorama({ location: { lat: x, lng: y }, preference: "nearest", radius: radiuses[radius_index], source: "outdoor" }, processSVData);
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

    mapId = "799bb53730cb6698"
    if (window.Telegram.WebApp.colorScheme == "dark") {
        mapId = "96181ab43c554867";
    }

    map = new Map(document.getElementById("map"), {
        controls: {},
        clickableIcons: false,
        disableDefaultUI: true,
        zoom: zoom,
        minZoom: 1,
        center: { lat: x_center, lng: y_center },
        restriction: {
            latLngBounds: {
                north: 80,
                south: -80,
                east: 180,
                west: -180,
            },
        },
        mapId: mapId
    });

    marker = new AdvancedMarkerElement({
        map: map,
        gmpDraggable: true,
        position: { lat: x_center, lng: y_center },
        content: markerImg,
        title: "Your answer",
    });

    map.addListener("click", (mapsMouseEvent) => {
        marker.position = mapsMouseEvent.latLng;
    })
}

function EndGame() {
    var raw = JSON.stringify({
        "method": "end_solo_game",
        "tele_id": tele_id,
        "seed": seed,
        "mode": mode,
        "fields": {
            "x_correct": loc.latLng.lat(),
            "y_correct": loc.latLng.lng(),
            "x_player": marker.position.lat,
            "y_player": marker.position.lng,
            "color_scheme": window.Telegram.WebApp.colorScheme
        }
    });

    console.log(raw)

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };

    fetch("https://functions.yandexcloud.net/d4e3l97hmqij0jekpe3t", requestOptions)
        .then(response => response.text())
        .then(result => console.log(result))
        .catch(error => {
            console.log('error', error);
        }
    );
}

function CreateBotResponce() {
    // var res = `${loc.latLng.lat()} ${loc.latLng.lng()} ${marker.position.lat} ${marker.position.lng}|${mode}|${window.Telegram.WebApp.colorScheme}`
    console.log(mode);
    return mode;
}

function toHomePano() {
    panorama.setPano(loc.pano);
    panorama.setPov({
        heading: 270,
        pitch: 0,
    });
}

async function initAnswerMap() {
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    const abs_distance = Math.max(Math.abs(marker.position.lat - loc.latLng.lat()), Math.abs(marker.position.lng - loc.latLng.lng()));

    answer_zoom = 8.7558 - 1.4056 * Math.log(abs_distance)
    console.log(Math.max(Math.abs(marker.position.lat - loc.latLng.lat()), Math.abs(marker.position.lng - loc.latLng.lng())))
    console.log(answer_zoom)
    answer_x_center = (marker.position.lat + loc.latLng.lat()) / 2;
    answer_y_center = (marker.position.lng + loc.latLng.lng()) / 2;

    answer_map = new Map(document.getElementById("answer_map"), {
        controls: {},
        clickableIcons: false,
        disableDefaultUI: true,
        zoom: answer_zoom,
        minZoom: 1,
        center: { lat: answer_x_center, lng: answer_y_center },
        restriction: {
            latLngBounds: {
                north: 80,
                south: -80,
                east: 180,
                west: -180,
            },
        },
        mapId: mapId
    });

    const player_answer_marker = new AdvancedMarkerElement({
        map: answer_map,
        position: { lat: marker.position.lat, lng: marker.position.lng },
        content: markerImg,
        title: "Your answer",
    });

    const correct_answer_markerImg = document.createElement("img");
    correct_answer_markerImg.src = "https://storage.yandexcloud.net/test-geoguessr/correct_marker.png";

    const correct_answer_marker = new AdvancedMarkerElement({
        map: answer_map,
        position: { lat: loc.latLng.lat(), lng: loc.latLng.lng() },
        content: correct_answer_markerImg,
        title: "Correct answer",
    });

    const answerPath_coordinates = [
        { lat: loc.latLng.lat(), lng: loc.latLng.lng() },
        { lat: marker.position.lat, lng: marker.position.lng },
    ];

    const answerPath = new google.maps.Polyline({
        path: answerPath_coordinates,
        geodesic: true,
        strokeColor: "#0000FF",
        strokeOpacity: 0.5,
        strokeWeight: 5,
    });
    answerPath.setMap(answer_map);
}
