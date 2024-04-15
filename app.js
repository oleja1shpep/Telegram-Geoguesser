let panorama;
let marker;
let start_lat, start_lng;
let coords;
let loc;

function getRandomArbitrary(min, max) {
    return Math.random() * (max - min) + min;
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

let x, delta_x, y, delta_y, zoom;

console.log(window.location.hash)
let hash = window.location.hash.split('?')[0]
console.log(hash)

async function generateCoords(hash) {
    let rand_case;
    if (hash == "#Moscow") {
        x = 55.6
        delta_x = 0.23
        y = 37.38
        delta_y = 0.4
        zoom = 10
    } else if (hash == "#SPB") {
        x = 59.81
        delta_x = 0.25
        y = 30.2
        delta_y = 0.27
        zoom = 10
    } else {
        x = -90
        delta_x = 180
        y = -180
        delta_y = 360
        zoom = 1
        rand_case = getRandomInt(1, 3);
        console.log(rand_case); 
        switch (rand_case) {
            // South America
            case 1:
                lat = -47.362302 + Math.random() * ( -9.733599 + 47.362302);
                lng = -71.624672 + Math.random() * (-65.100000 + 71.624672);
            case 2: 
                lat = -41.466691 + Math.random() * ( -9.733599 + 41.466691);
                lng = -65.067317 + Math.random() * (-56.807827 + 65.067317);
            case 3:
                lat = -35.169281 + Math.random() * ( -9.733599 + 35.169281);
                lng = -56.718168 + Math.random() * ( -48.613274 + 65.067317);
        }
    }
    coords = {lat, lng};
    console.log(hash, coords);
}

ymaps.ready(function () {
    // Ищем панораму в переданной точке.
    generateCoords();
    // const coords = { lat: -70 + Math.random() * 140, lng: -180 + 360 * Math.random()};
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

    sv.getPanorama({ location: coords, radius: 50000000, source: "outdoor" }).then(processSVData);

    myMap = new ymaps.Map("map", {
        center: [x + delta_x / 2, y + delta_y / 2],
        zoom: zoom,
        controls: []
    }, {
        searchControlProvider: 'yandex#search'
    }),
        // Создаем геообъект с типом геометрии "Точка".
        marker = new ymaps.GeoObject({
            // Описание геометрии.
            geometry: {
                type: "Point",
                coordinates: [x + delta_x / 2, y + delta_y / 2]
            },
            // Свойства.
            properties: {
                // Контент метки.
                iconContent: 'Тут!',
                hintContent: 'Тащи!'
            }
        }, {
            // Опции.
            // Иконка метки будет растягиваться под размер ее содержимого.
            preset: 'islands#blueDotIcon',
            // Метку можно перемещать.
            draggable: true
        })

    myMap.geoObjects
        .add(marker)

    myMap.events.add('click', function (e) {
        var coords = e.get('coords');
        marker.geometry.setCoordinates(coords);
    });
});

function processSVData({ data }) {
    loc = data.location;

    start_lat = loc.latLng.lat();
    start_lng = loc.latLng.lng();
    console.log("!", start_lat, start_lng);

    panorama.setPano(loc.pano);
    panorama.setPov({
      heading: 270,
      pitch: 0,
    });
    panorama.setVisible(true);
  }

function GetPanoramaCords() {
    // var res = `${panorama_pos} ${marker.geometry.getCoordinates().join(' ')}`;
    var res = `${start_lat} ${start_lng} ${marker.geometry.getCoordinates().join(' ')}`
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