let panorama;
let marker;
let start_lat, start_lng;
let loc;

function getRandomArbitrary(min, max) {
    return Math.random() * (max - min) + min;
}

function getRandomInt(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

let x, x_center, y, y_center, zoom;

console.log(window.location.hash)
let hash = window.location.hash.split('?')[0].split('|')
console.log(hash)

async function get_cords() {
    x = parseFloat(hash[1])
    y = parseFloat(hash[2])
    x_center = parseFloat(hash[3])
    y_center = parseFloat(hash[4])
    zoom = parseFloat(hash[5])
}

const radiuses = [500, 5000, 50000, 500000, 1500000, 5000000, 50000000]
let radius_index = 0;

function get_panorama() {
    // Ищем панораму в переданной точке.
    get_cords();
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

    // const pan_loc = {x, y};
    sv.getPanorama({ location: {lat: x, lng: y}, preference: "nearest", radius: radiuses[radius_index], source: "outdoor"}, processSVData);
};

function processSVData(data, status) {
    if (status == google.maps.StreetViewStatus.OK) {
        console.log('status: OK')
    } else if (status == google.maps.StreetViewStatus.ZERO_RESULTS) {
        console.log('status: zero results, radius:', radiuses[radius_index])
        radius_index = radius_index + 1;
        if (radius_index <= 6) {
            get_panorama();
        }
        return;
    } else {
        console.log('status:', status)
        return;
    }
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

ymaps.ready(function () {
    myMap = new ymaps.Map("map", {
        center: [x_center, y_center],
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
                coordinates: [x_center, y_center]
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

function GetPanoramaCords() {
    // var res = `${panorama_pos} ${marker.geometry.getCoordinates().join(' ')}`;
    try {
        var res = `${start_lat} ${start_lng} ${marker.geometry.getCoordinates().join(' ')}`
    } 
    catch (error) {
        var res = `${start_lat} ${start_lng} 0 0`
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